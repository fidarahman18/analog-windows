from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from pathlib import Path

# Updated imports to point to the new physics_engine directory
from .physics_engine.o2_terrain import compute_terrain_distance
from .physics_engine.o3_thermal import (
    extract_earth_temperatures,
    extract_lunar_temperatures,
    calculate_thermal_overlap
)
from .physics_engine.gap_rules import generate_full_gap_report

app = FastAPI(title="Analog Windows Backend")

# BASE_DIR is now analog_windows/backend/
BASE_DIR = Path(__file__).resolve().parent
# ROOT_DIR is analog_windows/
ROOT_DIR = BASE_DIR.parent

# Mount templates pointing to the new frontend/ directory
templates = Jinja2Templates(directory=str(ROOT_DIR / "frontend"))


@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/analysis", response_class=HTMLResponse)
async def serve_analysis(request: Request):
    return templates.TemplateResponse(request=request, name="analysis.html")


# --- REAL ENGINE ENDPOINTS (Phase 1 - Illumination O1) ---
@app.get("/api/metrics")
def get_illumination_metrics():
    # Point directly to the new data_mocks folder
    metrics_path = BASE_DIR / "data_mocks" / "o1_illumination_metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            return json.load(f)
    return {"error": "Illumination metrics not found"}


# --- MOCK DATA ENDPOINTS ---
@app.get("/api/costs")
def get_costs():
    # Point directly to the new data_mocks folder
    costs_path = BASE_DIR / "data_mocks" / "mock_cost_logistics.json"
    if costs_path.exists():
        with open(costs_path, "r") as f:
            return json.load(f)
    return {"error": "Costs data not found"}


@app.get("/api/gaps")
def get_gaps():
    # Lunar Malapert Summit Baseline
    moon_slope = 12.0
    moon_sunlit = 0.522
    moon_min_t = 50.0
    moon_max_t = 250.0

    # Svalbard (Earth) Test Parameters
    svalbard_slope = 6.0  # Flatter than moon
    svalbard_sunlit = 0.15  # 15% duty cycle
    svalbard_min_t = 207.5
    svalbard_max_t = 308.3

    # Atacama (Earth) Test Parameters
    atacama_slope = 18.0  # Steeper than hardware limit (15.0)
    atacama_sunlit = 0.60
    atacama_min_t = 239.1
    atacama_max_t = 332.1

    # Run the engine for both sites
    svalbard_gaps = generate_full_gap_report(
        svalbard_slope, moon_slope, svalbard_sunlit, moon_sunlit, svalbard_min_t, moon_min_t, moon_max_t, svalbard_max_t
    )

    atacama_gaps = generate_full_gap_report(
        atacama_slope, moon_slope, atacama_sunlit, moon_sunlit, atacama_min_t, moon_min_t, moon_max_t, atacama_max_t
    )

    # Return the dictionary format expected by your JS frontend
    return {
        "Svalbard_Longyearbyen": svalbard_gaps,
        "Atacama_Desert": atacama_gaps
    }


# --- REAL ENGINE ENDPOINTS (Phase 2 - Terrain) ---
@app.get("/api/terrain-distance")
def get_real_terrain_distance():
    # Dynamically point to the heavy data folder in the root directory
    earth_dem = str(ROOT_DIR / "data" / "aster_svalbard.tif")
    mars_dem = str(ROOT_DIR / "data" / "lola_jezero_mars.tif")

    # Execute the real O2 terrain engine
    try:
        results = compute_terrain_distance(earth_dem, mars_dem)
        return results
    except Exception as e:
        return {"error": f"Failed to calculate terrain distance: {str(e)}"}


# --- REAL ENGINE ENDPOINTS (Phase 3 - Thermal) ---

# Global variable to hold our cached thermal data in memory
THERMAL_CACHE = None


@app.get("/api/thermal/compare")
def get_thermal_comparison():
    global THERMAL_CACHE

    if THERMAL_CACHE is not None:
        return THERMAL_CACHE

    # Point to the data/raw folder at the root
    svalbard_dir = ROOT_DIR / "data" / "raw" / "modis_thermal" / "svalbard"
    atacama_dir = ROOT_DIR / "data" / "raw" / "modis_thermal" / "atacama"
    moon_tab = ROOT_DIR / "data" / "raw" / "diviner_thermal" / "moon" / "dlre_prp_south.tab"

    try:
        moon_metrics = extract_lunar_temperatures(moon_tab)
        svalbard_metrics = extract_earth_temperatures(svalbard_dir)
        atacama_metrics = extract_earth_temperatures(atacama_dir)

        svalbard_results = calculate_thermal_overlap(svalbard_metrics, moon_metrics)
        atacama_results = calculate_thermal_overlap(atacama_metrics, moon_metrics)

        THERMAL_CACHE = {
            "lunar_baseline": moon_metrics,
            "sites": {
                "svalbard": {
                    "earth_metrics": svalbard_metrics,
                    "overlap": svalbard_results
                },
                "atacama": {
                    "earth_metrics": atacama_metrics,
                    "overlap": atacama_results
                }
            }
        }
        return THERMAL_CACHE

    except Exception as e:
        return {"error": f"Failed to calculate thermal overlap: {str(e)}"}