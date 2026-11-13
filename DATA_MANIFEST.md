
### `DATA_MANIFEST.md`

```markdown
# Analog Windows: Scientific Data Traceability

To comply with GitHub's file size limits while maintaining strict scientific provenance, our heavy DEMs and ephemeris kernels are hosted externally for local execution. The Analog Windows backend relies exclusively on the following authoritative space agency datasets:

| Dataset Name | Source/Agency | Product ID / DOI | Spatial/Temporal Resolution | Retrieval Date |
| :--- | :--- | :--- | :--- | :--- |
| **LOLA High-Resolution Site DEMs (Malapert)** | NASA PGDA | Product 78 | 5 meters/pixel (using ERR/EFFRES masks) | Nov 2026 |
| **NAIF SPICE Kernels (Planetary Ephemeris)** | NASA NAIF | de440s, moon_pa_de421, pck00010, naif0012 | High-precision orbital vectors | Nov 2026 |
| **ASTER Global Digital Elevation Model V003** | NASA LP DAAC | ASTGTM_003 (10.5067/ASTER/ASTGTM.003) | 30 meters (downsampled to 200m) | Nov 2026 |
| **Terra Land Surface Temperature (MODIS)** | NASA LP DAAC | MOD11A1.061 | 1 kilometer / Daily | Nov 2026 |
| **MOLA Mission Experiment Gridded Data Record** | NASA PDS | MEGDR | 463 meters/pixel | Nov 2026 |
| **Diviner Lunar Radiometer Experiment** | NASA PDS | Polar Resource Product | 240 meters/pixel | Nov 2026 |
