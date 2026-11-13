# Analog Windows 
**NASA Space Apps Challenge 2026**

Analog Windows is a mathematically defensible, multi-planetary decision-support platform. Rather than simply returning the "closest" Earth location to a celestial target, our engine calculates physical similarity (terrain, illumination, thermal) and explicitly outputs the **Residual Scientific Gaps** (e.g., 1/6th gravity, thermal penetration depth, solar sweep rates). This allows mission planners to know exactly what an Earth analog successfully simulates, and exactly where the analogy physically breaks down.

**Official Project Page:** 

## Quick Start (Local Demo)
To ensure maximum reliability during judging, this application is designed to run entirely offline on a local server.

1. Clone the Repository

Bash
git clone https://github.com/fidarahman18/analog-windows
cd analog-windows

2. Download the Required Datasets (Google Drive)

The core physics engines cannot run without the raw planetary data.

1. Navigate to our public dataset directory: 
   https://drive.google.com/drive/folders/1lcrhBv9ptYRkOORfHacV8hqtM60ZXvMW?usp=sharing
2. Download the entire contents of the Drive folder as a ZIP (or individual folders).
3. Extract and place the extracted folders (`features`, `processed`, `raw`, and `results`) directly inside the root `data/` folder of your cloned repository. 
   *(Do not place the parent folder "Analog Windows - Space Apps Data" inside—the structure must match `data/raw/...`, `data/processed/...`, etc.)*

3. Setup the Python Environment
We recommend using a virtual environment.

# Create and activate a virtual environment
# On macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate  

# On Windows:
python -m venv .venv
.venv\Scripts\activate

# Install backend dependencies (including Rasterio and FastAPI)
pip install -r backend/requirements.txt

4. Boot the Server
Run the FastAPI backend using Uvicorn. This server acts as the bridge connecting the Python physics engines to the frontend UI.

uvicorn backend.server:app --reload

5. Launch the Dashboard
Open your web browser and navigate to the port mentioned in your terminal
