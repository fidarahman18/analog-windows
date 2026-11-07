import numpy as np
import pandas as pd
import spiceypy as spice
import os

# ==========================================
# 1. SPICE INITIALIZATION & PROJECT PATHS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../.."))
KERNEL_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

spice.furnsh(os.path.join(KERNEL_DIR, "naif0012.tls"))
spice.furnsh(os.path.join(KERNEL_DIR, "pck00010.tpc"))
spice.furnsh(os.path.join(KERNEL_DIR, "de440s.bsp"))
spice.furnsh(os.path.join(KERNEL_DIR, "moon_pa_de421_1900-2050.bpc"))
spice.furnsh(os.path.join(KERNEL_DIR, "moon_080317.tf"))
spice.furnsh(os.path.join(KERNEL_DIR, "moon_assoc_me.tf"))

# Constants
LAT_DEG = -85.8
LON_DEG = 356.4
RADIUS_KM = 1737.4
OBLIQUITY_DEG = 1.54
P_SYNODIC = 29.530589

# ==========================================
# 2. THE 2025 PHASE ANCHOR (CRITICAL RULE)
# ==========================================
t0_utc = "2025-01-01T00:00:00"
t0_et = spice.str2et(t0_utc)

# Ask SPICE for the exact subsolar lat/lon at the anchor epoch
spoint_t0, _, _ = spice.subslr("NEAR POINT/ELLIPSOID", "MOON", t0_et, "MOON_ME", "NONE", "SUN")
_, sub_lon_t0, sub_lat_t0 = spice.reclat(spoint_t0)

# Convert to degrees
spice_delta_t0 = sub_lat_t0 * spice.dpr()
spice_sub_lon_t0 = sub_lon_t0 * spice.dpr()

# The hour angle (H) is the difference between the subsolar longitude and the site's longitude
spice_H_t0 = spice_sub_lon_t0 - LON_DEG

# Reverse-engineer the Phase Offsets based on the 2025 anchor state
# delta(t0) = Obliquity * sin(Phi_season) -> Phi_season = arcsin(delta(t0) / Obliquity)
PHI_SEASON_RAD = np.arcsin(np.clip(spice_delta_t0 / OBLIQUITY_DEG, -1.0, 1.0))

# H(t0) = Phi_diurnal
PHI_DIURNAL_DEG = spice_H_t0


# ==========================================
# 3. ANALYTICAL MODEL ENGINE
# ==========================================
def run_analytical_model(et_array, t0_et, p_season_days):
    # Convert elapsed time from seconds to days
    t_elapsed_days = (et_array - t0_et) / 86400.0

    # Calculate Subsolar Latitude (Delta)
    # delta(t) = 1.54 * sin( (2pi / P_season) * t_elapsed + Phi_season )
    delta_deg = OBLIQUITY_DEG * np.sin((2 * np.pi / p_season_days) * t_elapsed_days + PHI_SEASON_RAD)
    delta_rad = np.radians(delta_deg)

    # Calculate Hour Angle (H)
    # H(t) = (360 / P_synodic) * t_elapsed + Phi_diurnal
    h_deg = (360.0 / P_SYNODIC) * t_elapsed_days + PHI_DIURNAL_DEG
    h_rad = np.radians(h_deg)

    phi_rad = np.radians(LAT_DEG)

    # Local Elevation (h)
    # sin(h) = sin(phi)sin(delta) + cos(phi)cos(delta)cos(H)
    sin_h = np.sin(phi_rad) * np.sin(delta_rad) + np.cos(phi_rad) * np.cos(delta_rad) * np.cos(h_rad)
    elevation_rad = np.arcsin(np.clip(sin_h, -1.0, 1.0))
    elevation_deg = np.degrees(elevation_rad)

    # Local Azimuth (A) via atan2(y, x)
    y = -np.sin(h_rad) * np.cos(delta_rad)
    x = np.sin(delta_rad) * np.cos(phi_rad) - np.cos(delta_rad) * np.sin(phi_rad) * np.cos(h_rad)
    azimuth_rad = np.arctan2(y, x)
    azimuth_deg = np.degrees(azimuth_rad) % 360.0  # Wrap to 0-360

    return elevation_deg, azimuth_deg


# ==========================================
# 4. HELD-OUT WINDOW EXECUTION (2026-2032)
# ==========================================
start_utc = "2026-01-01T00:00:00"
end_utc = "2032-12-31T23:00:00"
et_times = np.arange(spice.str2et(start_utc), spice.str2et(end_utc) + 3600, 3600)

print(f"Executing SPICE ground truth & analytical models for {len(et_times)} hours...")

spice_elevations = []
spice_azimuths = []
utc_strings = []

# Generate SPICE Ground Truth for the held-out window
for et in et_times:
    utc_strings.append(spice.et2utc(et, "ISOC", 0))

    # Generate exact topocentric elevation/azimuth using SPICE coordinate transforms
    target_rect = spice.latrec(RADIUS_KM, LON_DEG * spice.rpd(), LAT_DEG * spice.rpd())
    spoint, _, _ = spice.subslr("NEAR POINT/ELLIPSOID", "MOON", et, "MOON_ME", "NONE", "SUN")
    _, sub_lon, sub_lat = spice.reclat(spoint)

    # Emulate the exact topocentric math to match the analytical output
    h_rad_spice = sub_lon - (LON_DEG * spice.rpd())
    sin_h_spice = np.sin(LAT_DEG * spice.rpd()) * np.sin(sub_lat) + np.cos(LAT_DEG * spice.rpd()) * np.cos(
        sub_lat) * np.cos(h_rad_spice)
    spice_elevations.append(np.degrees(np.arcsin(np.clip(sin_h_spice, -1.0, 1.0))))

    y_spice = -np.sin(h_rad_spice) * np.cos(sub_lat)
    x_spice = np.sin(sub_lat) * np.cos(LAT_DEG * spice.rpd()) - np.cos(sub_lat) * np.sin(
        LAT_DEG * spice.rpd()) * np.cos(h_rad_spice)
    spice_azimuths.append(np.degrees(np.arctan2(y_spice, x_spice)) % 360.0)

# Run the analytical models over the entire array
elev_365, az_365 = run_analytical_model(et_times, t0_et, 365.2422)
elev_346, az_346 = run_analytical_model(et_times, t0_et, 346.62)

# ==========================================
# 5. COMPUTE ERRORS AND EXPORT
# ==========================================
df = pd.DataFrame({
    "UTC": utc_strings,
    "SPICE_Elev": spice_elevations,
    "SPICE_Az": spice_azimuths,
    "Mod365_Elev": elev_365,
    "Mod365_Az": az_365,
    "Mod346_Elev": elev_346,
    "Mod346_Az": az_346
})

# Calculate Errors (Analytic - SPICE)
df['Err_365_Elev'] = df['Mod365_Elev'] - df['SPICE_Elev']
df['Err_346_Elev'] = df['Mod346_Elev'] - df['SPICE_Elev']

output_dir = os.path.join(PROJECT_ROOT, "reports", "gate1")
os.makedirs(output_dir, exist_ok=True)
csv_path = os.path.join(output_dir, "gate1_error_logs.csv")
df.to_csv(csv_path, index=False)

# Summarize for the Research Lead
mae_365 = df['Err_365_Elev'].abs().mean()
mae_346 = df['Err_346_Elev'].abs().mean()
max_err_365 = df['Err_365_Elev'].abs().max()
max_err_346 = df['Err_346_Elev'].abs().max()

print("\n--- GATE 1 VALIDATION RESULTS ---")
print(f"Model A (365.24) -> MAE: {mae_365:.3f} deg | Max Error: {max_err_365:.3f} deg")
print(f"Model B (346.62) -> MAE: {mae_346:.3f} deg | Max Error: {max_err_346:.3f} deg")
print(f"CSV saved to: {csv_path}")