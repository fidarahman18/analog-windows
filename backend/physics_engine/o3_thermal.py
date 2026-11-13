import numpy as np
from pyhdf.SD import SD, SDC
from pathlib import Path
import pandas as pd
import warnings


def extract_earth_temperatures(site_folder_path: Path) -> dict:
    """
    Iterates through 365 daily MOD11A1 HDF files to extract the annual min, max, and median.
    """
    hdf_files = list(site_folder_path.glob("*.hdf"))
    if not hdf_files:
        raise FileNotFoundError(f"No HDF files found in {site_folder_path}")

    all_temps = []

    for file_path in hdf_files:
        try:
            # Use pyhdf to read the HDF4 file natively, bypassing rasterio
            file = SD(str(file_path), SDC.READ)

            # Extract both Day and Night temperatures for a true annual range
            data_day = file.select('LST_Day_1km').get()
            data_night = file.select('LST_Night_1km').get()

            # MOD11A1 valid range is roughly 7500 to 65535. Fill value is 0.
            valid_day = data_day[data_day > 0]
            valid_night = data_night[data_night > 0]

            # Scale factor is 0.02 to convert to Kelvin
            if valid_day.size > 0:
                all_temps.append(valid_day * 0.02)
            if valid_night.size > 0:
                all_temps.append(valid_night * 0.02)

        except Exception as e:
            print(f"Skipping {file_path.name} due to read error: {e}")

    if not all_temps:
        raise ValueError("Could not extract valid temperature data from the provided files.")

    combined_array = np.concatenate(all_temps)

    return {
        "annual_min_k": float(np.min(combined_array)),
        "annual_max_k": float(np.max(combined_array)),
        "annual_median_k": float(np.median(combined_array))
    }


def extract_lunar_temperatures(diviner_tab_path: Path) -> dict:
    """
    Parses the Diviner PRP South Pole dataset for baseline lunar temperatures.
    """
    if not diviner_tab_path.exists():
        raise FileNotFoundError(f"Diviner file not found at {diviner_tab_path}")

    # The file is comma-separated and already has headers!
    df = pd.read_csv(diviner_tab_path, sep=',', skipinitialspace=True, low_memory=False)

    # Strip out NASA's -999.0 fill values
    df = df.replace(-999.0, np.nan)

    # Extract the lowest average temperature and highest maximum temperature
    lunar_min = df['temp_avg'].min()
    lunar_max = df['temp_max'].max()

    return {
        "annual_min_k": float(lunar_min),
        "annual_max_k": float(lunar_max)
    }

def calculate_thermal_overlap(earth_temps: dict, lunar_temps: dict) -> dict:
    """
    Calculates the exact overlapping temperature window between an Earth site and a Lunar target.
    """
    earth_min = earth_temps["annual_min_k"]
    earth_max = earth_temps["annual_max_k"]

    lunar_min = lunar_temps["annual_min_k"]
    lunar_max = lunar_temps["annual_max_k"]

    overlap_min = max(earth_min, lunar_min)
    overlap_max = min(earth_max, lunar_max)

    overlap_range = overlap_max - overlap_min

    if overlap_range <= 0:
        overlap_range = 0.0
        overlap_min = None
        overlap_max = None

    return {
        "earth_range_k": [earth_min, earth_max],
        "lunar_range_k": [lunar_min, lunar_max],
        "overlap_window_k": [overlap_min, overlap_max] if overlap_range > 0 else [],
        "overlap_magnitude_k": float(overlap_range)
    }


if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent

    svalbard_dir = root_dir / "data" / "raw" / "modis_thermal" / "svalbard"
    atacama_dir = root_dir / "data" / "raw" / "modis_thermal" / "atacama"
    moon_tab = root_dir / "data" / "raw" / "diviner_thermal" / "moon" / "dlre_prp_south.tab"

    try:
        # 1. Earth Data
        print("Extracting Svalbard Annual Temperatures...")
        svalbard_metrics = extract_earth_temperatures(svalbard_dir)
        print(f"Svalbard: Min {svalbard_metrics['annual_min_k']:.1f}K, Max {svalbard_metrics['annual_max_k']:.1f}K")

        print("\nExtracting Atacama Annual Temperatures...")
        atacama_metrics = extract_earth_temperatures(atacama_dir)
        print(f"Atacama: Min {atacama_metrics['annual_min_k']:.1f}K, Max {atacama_metrics['annual_max_k']:.1f}K")

        # 2. Moon Data
        print("\nExtracting Lunar South Pole Temperatures...")
        moon_metrics = extract_lunar_temperatures(moon_tab)
        print(f"Moon: Min {moon_metrics['annual_min_k']:.1f}K, Max {moon_metrics['annual_max_k']:.1f}K")

        # 3. Overlap Calculations
        svalbard_results = calculate_thermal_overlap(svalbard_metrics, moon_metrics)
        print(f"\nSvalbard Total Overlap: {svalbard_results['overlap_magnitude_k']:.1f} Kelvin")

        atacama_results = calculate_thermal_overlap(atacama_metrics, moon_metrics)
        print(f"Atacama Total Overlap: {atacama_results['overlap_magnitude_k']:.1f} Kelvin")

    except Exception as e:
        print(f"Error during execution: {e}")