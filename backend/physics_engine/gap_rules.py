def get_fundamental_gaps():
    return [
        {"variable": "Gravity", "gap": "Fundamental",
         "detail": "Earth 1g fundamentally alters wheel-slip physics, regolith cohesion, and vehicle suspension dynamics compared to lunar 1/6th g."},
        {"variable": "Atmospheric Scattering", "gap": "Fundamental",
         "detail": "Earth's atmosphere provides ambient fill-light in shadows. Lunar polar shadows are absolute black, severely altering optical navigation."},
        {"variable": "Solar Sweep Rate", "gap": "Fundamental",
         "detail": "Earth's Sun sweeps ~15°/hr (29.5x faster than the Moon's ~0.51°/hr). Earth shadows move too fast to simulate lunar polar traverse timing."},
        {"variable": "Thermal Penetration", "gap": "Fundamental",
         "detail": "Due to the 29.5-day lunar cycle, thermal waves penetrate ~5.5x deeper into lunar regolith than on Earth. Subsurface thermal gradients cannot be matched."}
    ]


def calculate_terrain_gaps(earth_slope_200m, moon_slope_200m, hardware_limit=15.0):
    gaps = []
    diff = earth_slope_200m - moon_slope_200m

    if moon_slope_200m <= hardware_limit and earth_slope_200m > hardware_limit:
        gaps.append({"variable": "Hardware Limit Exceeded", "gap": "High",
                     "detail": f"Lunar target ({moon_slope_200m:.1f}°) is safe, but Earth analog ({earth_slope_200m:.1f}°) exceeds the {hardware_limit}° design limit. False negative for mobility."})
    elif diff < -5.0:
        gaps.append({"variable": "Terrain Hazard", "gap": "Medium",
                     "detail": f"Earth analog is {abs(diff):.1f}° flatter. Undertests hazard avoidance capabilities."})

    return gaps


def calculate_illumination_gaps(earth_sunlit_fraction, moon_sunlit_fraction):
    gaps = []
    diff = moon_sunlit_fraction - earth_sunlit_fraction

    if diff > 0.20:
        gaps.append({"variable": "Duty Cycle", "gap": "High",
                     "detail": f"Earth site receives significantly less continuous sunlight ({earth_sunlit_fraction * 100:.1f}%) than the lunar target ({moon_sunlit_fraction * 100:.1f}%). Fails to simulate power generation persistence."})

    return gaps


def calculate_thermal_gaps(earth_min_temp, moon_min_temp, moon_max_temp, earth_max_temp):
    gaps = []
    if moon_min_temp < 110 and earth_min_temp > 150:
        gaps.append({"variable": "Cryogenic Regime", "gap": "Fundamental",
                     "detail": f"Target reaches {moon_min_temp:.1f}K (volatile stability). Earth minimum is {earth_min_temp:.1f}K. Cryogenic vacuum testing mandatory."})

    moon_cycle = moon_max_temp - moon_min_temp
    earth_cycle = earth_max_temp - earth_min_temp
    if abs(moon_cycle - earth_cycle) > 50:
        # ADDED :.1f to format the floats perfectly!
        gaps.append({"variable": "Thermal Cycling", "gap": "Medium",
                     "detail": f"Earth diurnal amplitude ({earth_cycle:.1f}K) does not match lunar amplitude ({moon_cycle:.1f}K). Material fatigue profiles differ."})

    return gaps


def generate_full_gap_report(earth_slope, moon_slope, earth_sunlit, moon_sunlit, earth_min_t, moon_min_t, moon_max_t,
                             earth_max_t):
    """Synthesizes all rules to generate the final dictionary for the frontend."""
    fundamental = get_fundamental_gaps()
    measurable = []

    # Run the dynamic rules
    measurable.extend(calculate_terrain_gaps(earth_slope, moon_slope))
    measurable.extend(calculate_illumination_gaps(earth_sunlit, moon_sunlit))
    measurable.extend(calculate_thermal_gaps(earth_min_t, moon_min_t, moon_max_t, earth_max_t))

    return {
        "Fundamental_Gaps": fundamental,
        "Measurable_Mismatches": measurable,
        "Mitigation_Warning": "Success at this Earth site does NOT validate radiator performance or optical navigation in true lunar vacuum darkness."
    }