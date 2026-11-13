# Analog Windows (NASA Space Apps Challenge)

**Analog Windows** is a decision-support platform designed to help mission planners identify the highest-fidelity Earth-based analogs for lunar and Martian surface operations. Built for the NASA Space Apps Challenge, this platform evaluates environmental overlaps (illumination, terrain hazard, and thermal limits) to determine where, when, and how to test on Earth.

This prototype utilizes a "deep vertical plus mocked breadth" architecture. The core physics engines run live calculations against NASA SPICE ephemeris and elevation models for the Lunar South Pole, while secondary site data is statically mocked to demonstrate dashboard breadth.

## 🗂 Project Architecture
This repository strictly contains the codebase. Due to GitHub file size limits, massive NASA datasets (SPICE kernels, DEMs, Thermal matrices) are hosted externally on Google Drive.

```text
analog_windows/
├── backend/            # FastAPI server, UI data binding, and Physics Engines
├── frontend/           # HTML/CSS/JS progressive disclosure dashboard
├── data/               # Empty skeleton folder (Requires Google Drive download)
├── DATA_MANIFEST.md    # Full list of NASA open-source data utilized
├── AI_USE.md           # Required NASA Space Apps AI disclosure log
└── PROJECT_SUMMARY.md  # High-level scientific overview