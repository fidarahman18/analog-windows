import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow the frontend to fetch data without CORS blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_json(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {"error": f"File {filename} not found."}

@app.get("/api/metrics")
def get_metrics():
    return load_json("o1_illumination_metrics.json")

@app.get("/api/costs")
def get_costs():
    return load_json("mock_cost_logistics.json")

@app.get("/api/gaps")
def get_gaps():
    return load_json("mock_gap_report.json")

if __name__ == "__main__":
    import uvicorn
    print("Starting API Bridge on localhost:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)