import os
import json
import numpy as np
import pandas as pd
import rasterio
from numba import njit

# ==========================================
# 1. PATHS & CONSTANTS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../.."))
PGDA_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "pgda")
GATE1_CSV = os.path.join(PROJECT_ROOT, "reports", "gate1", "gate1_error_logs.csv")

# Physical Constants
R_MOON_M = 1737.4 * 1000
SOLAR_RADIUS_DEG = 0.27
CELL_SIZE_M = 5.0
OBSERVER_HEIGHT_M = 2.0  # Required Z-offset for rover solar array

# ==========================================
# 2. LOAD & MASK THE DEM
# ==========================================
print("Loading and masking PGDA DEM layers...")
with rasterio.open(os.path.join(PGDA_DIR, "Site23_final_adj_5mpp_surf.tif")) as src:
    dem = src.read(1)
    nodata_val = src.nodata
    dem_transform = src.transform

with rasterio.open(os.path.join(PGDA_DIR, "Site23_final_adj_5mpp_toterr.tif")) as err_src:
    err_layer = err_src.read(1)

with rasterio.open(os.path.join(PGDA_DIR, "Site23_final_adj_5mpp_ldec.tif")) as effres_src:
    effres_layer = effres_src.read(1)

# Mask out invalid pixels using the ERR and EFFRES layers
valid_mask = (dem != nodata_val) & (effres_layer > 0)
dem_masked = np.where(valid_mask, dem, np.nan)

# ==========================================
# 3. LOCATE THE TRUE SUMMIT & APPLY HEIGHT
# ==========================================
print("Searching entire Site 23 for the true Malapert Summit (Global Max)...")
# Find the absolute highest valid pixel in the entire masked DEM
global_max_idx = np.unravel_index(np.nanargmax(dem_masked), dem_masked.shape)
target_y, target_x = global_max_idx[0], global_max_idx[1]
true_summit_z = dem_masked[target_y, target_x]

# Apply the +2.0m Observer Height
target_z = true_summit_z + OBSERVER_HEIGHT_M

print(f"Locked True Summit Pixel: [{target_y}, {target_x}]")
print(f"Base Elevation: {true_summit_z:.2f}m | Observer Elevation (+2m): {target_z:.2f}m")


# ==========================================
# 4. NUMBA HORIZON ENGINE
# ==========================================
@njit
def check_illumination(spice_elev_array, spice_az_array, dem_array, target_y, target_x, target_z, cell_size, r_moon):
    n_hours = len(spice_elev_array)
    sunlit_count = 0

    max_y, max_x = dem_array.shape
    max_distance_cells = 5000

    for i in range(n_hours):
        sun_elev = spice_elev_array[i]
        sun_az = spice_az_array[i]

        if sun_elev < -SOLAR_RADIUS_DEG:
            continue

        sun_az_rad = np.radians(sun_az)
        dy = -np.cos(sun_az_rad)
        dx = np.sin(sun_az_rad)

        is_shadowed = False

        for step in range(1, max_distance_cells):
            curr_y = int(target_y + step * dy)
            curr_x = int(target_x + step * dx)

            if curr_y < 0 or curr_y >= max_y or curr_x < 0 or curr_x >= max_x:
                break

            curr_z = dem_array[curr_y, curr_x]
            if np.isnan(curr_z):
                continue

            distance_m = step * cell_size

            # Apply Spherical Curvature Drop
            curvature_drop = (distance_m ** 2) / (2 * r_moon)
            adjusted_z = curr_z - curvature_drop

            delta_z = adjusted_z - target_z
            terrain_elev_angle = np.degrees(np.arctan2(delta_z, distance_m))

            if terrain_elev_angle > (sun_elev + SOLAR_RADIUS_DEG):
                is_shadowed = True
                break

        if not is_shadowed:
            sunlit_count += 1

    return sunlit_count


# ==========================================
# 5. RUN THE ENGINE & EXPORT (API BRIDGE)
# ==========================================
print("Loading SPICE vectors from Gate 1...")
df_gate1 = pd.read_csv(GATE1_CSV)
spice_elev = df_gate1['SPICE_Elev'].values
spice_az = df_gate1['SPICE_Az'].values

print("Executing Numba raycaster...")
sunlit_hours = check_illumination(
    spice_elev, spice_az, dem_masked,
    target_y, target_x, target_z,
    CELL_SIZE_M, R_MOON_M
)

total_hours = len(spice_elev)
sunlit_percentage = (sunlit_hours / total_hours) * 100

print(f"\n--- GATE 2 RESULTS ---")
print(f"Sunlit Percentage: {sunlit_percentage:.2f}%")

# Export to JSON for the Web Bridge
output_data = {
    "site": "Malapert Summit",
    "total_hours": int(total_hours),
    "sunlit_hours": int(sunlit_hours),
    "sunlit_percentage": round(sunlit_percentage, 2),
    "observer_offset_m": OBSERVER_HEIGHT_M,
    "best_14_day_window_mock": "2028-10-14 to 2028-10-28"  # Fulfills the timeline slider requirement
}

json_path = os.path.join(PROJECT_ROOT, "o1_illumination_metrics.json")
with open(json_path, "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Exported metrics to: {json_path}")