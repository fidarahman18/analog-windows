import numpy as np
import rasterio
from rasterio.enums import Resampling
from scipy import ndimage


def analyze_terrain(dem_path: str, target_resolution: int = 200) -> dict:
    """
    Downsamples a DEM to a matched baseline and extracts physical terrain metrics.
    """
    with rasterio.open(dem_path) as src:
        scale_factor_x = src.res[0] / target_resolution
        scale_factor_y = src.res[1] / target_resolution

        resampled_dem = src.read(
            1,
            out_shape=(
                int(src.height * scale_factor_y),
                int(src.width * scale_factor_x)
            ),
            resampling=Resampling.bilinear
        )

        dy, dx = np.gradient(resampled_dem, target_resolution, target_resolution)
        slope_grid = np.degrees(np.arctan(np.sqrt(dx ** 2 + dy ** 2)))

        slope_90th = np.percentile(slope_grid, 90)

        mean_elevation = np.mean(resampled_dem)
        rms_roughness = np.sqrt(np.mean(np.square(resampled_dem - mean_elevation)))

        return {
            "slope_90th": float(slope_90th),
            "rms_roughness": float(rms_roughness)
        }


def compute_terrain_distance(earth_dem_path: str, target_dem_path: str) -> dict:
    """
    Calculates the real computed terrain distance between an Earth candidate and the Moon/Mars.
    """
    earth_metrics = analyze_terrain(earth_dem_path)
    target_metrics = analyze_terrain(target_dem_path)

    slope_difference = abs(earth_metrics["slope_90th"] - target_metrics["slope_90th"])

    return {
        "earth_metrics": earth_metrics,
        "target_metrics": target_metrics,
        "slope_difference": slope_difference
    }


if __name__ == "__main__":
    from pathlib import Path

    # Resolve paths relative to this file's new location inside app/
    root_dir = Path(__file__).resolve().parent.parent
    earth_path = str(root_dir / "data" / "aster_svalbard.tif")
    target_path = str(root_dir / "data" / "lola_jezero_mars.tif")

    try:
        results = compute_terrain_distance(earth_path, target_path)
        print(f"Mars Test Complete. Slope Difference: {results['slope_difference']:.2f} degrees")
    except Exception as e:
        print("Waiting on local DEM files...")