# Data Manifest (Analog Windows)

This document serves as the official data manifest for the Analog Windows project, outlining all NASA and open-source datasets utilized in our core engines.

## 1. Ephemeris & Geometry (O1 Illumination Engine)
* **Provider:** NASA NAIF (Navigation and Ancillary Information Facility)
* **Datasets (SPICE Kernels):**
  * `de440s.bsp`: Planetary Ephemeris (Sun/Moon orbital trajectories)
  * `pck00010.tpc`: Planetary Constants (Moon radii and orientation)
  * `naif0012.tls`: Leapseconds Kernel (Time conversions)
  * `moon_pa_de421_1900-2050.bpc`: Lunar principal axes orientation
  * `moon_080317.tf` / `moon_assoc_me.tf`: Reference frames

## 2. Lunar Terrain & Elevation (O1 & O2 Engines)
* **Provider:** NASA PGDA (Planetary Geodynamics Data Archive)
* **Dataset:** Product 78 (Site 23 - Malapert Massif)
  * `Site23_final_adj_5mpp_surf.tif`: 5m/pixel Digital Elevation Model
  * `Site23_final_adj_5mpp_toterr.tif`: Total Error masking layer
  * `Site23_final_adj_5mpp_ldec.tif`: Effective Resolution masking layer
* **Provider:** Zenodo (Record 17084058)
  * `wueller_shapefiles`: Lunar target bounding geometries

## 3. Earth Terrain (O2 Terrain Engine)
* **Provider:** NASA LP DAAC (Land Processes Distributed Active Archive Center)
* **Dataset:** ASTER Global Digital Elevation Model (GDEM) v3
  * `aster_svalbard.tif`: Extracted elevation map for Svalbard, Norway

## 4. Thermal Environments (O3 Thermal Engine)
* **Provider:** NASA PDS (Planetary Data System)
* **Dataset:** LRO Diviner Lunar Radiometer Experiment
  * `dlre_prp_south.tab`: South Pole gridded thermal profiles
* **Provider:** NASA LP DAAC
* **Dataset:** Terra/Aqua MODIS (Moderate Resolution Imaging Spectroradiometer)
  * `modis_thermal/svalbard`: Terrestrial surface temperatures
  * `modis_thermal/atacama`: Terrestrial surface temperatures