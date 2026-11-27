"""Small engineering calculators shared by the Aviateka MCP server.
The web page implements the same formulas in JavaScript (tests compare both)."""
import math

R = 287.053        # J/(kg K), dry air
G = 9.80665        # m/s^2
GAMMA = 1.4
OZ_PER_KG = 35.27396
FT2_PER_M2 = 10.76391


def atmosphere(altitude_m: float, delta_t: float = 0.0) -> dict:
    """International Standard Atmosphere 0–20 km with a temperature offset (pressure stays standard)."""
    h = float(altitude_m)
    if not -500 <= h <= 20000:
        raise ValueError("altitude_m must be between -500 and 20000 m")
    if h <= 11000:
        t_std = 288.15 - 0.0065 * h
        p = 101325.0 * (t_std / 288.15) ** 5.255877
    else:
        t_std = 216.65
        p = 22632.06 * math.exp(-G * (h - 11000) / (R * 216.65))
    t = t_std + float(delta_t)
    rho = p / (R * t)
    a = math.sqrt(GAMMA * R * t)
    mu = 1.458e-6 * t ** 1.5 / (t + 110.4)
    return {"altitude_m": h, "temperature_K": round(t, 3), "temperature_C": round(t - 273.15, 3),
            "pressure_Pa": round(p, 2), "density_kg_m3": round(rho, 5), "speed_of_sound_m_s": round(a, 3),
            "dynamic_viscosity_Pa_s": mu, "kinematic_viscosity_m2_s": mu / rho}


def reynolds_mach(speed_m_s: float, chord_m: float, altitude_m: float = 0.0, delta_t: float = 0.0) -> dict:
    atm = atmosphere(altitude_m, delta_t)
    re = speed_m_s * chord_m / atm["kinematic_viscosity_m2_s"]
    return {"reynolds": re, "mach": speed_m_s / atm["speed_of_sound_m_s"], "speed_km_h": speed_m_s * 3.6, "atmosphere": atm}


def stall_speed(mass_kg: float, wing_area_m2: float, cl_max: float, altitude_m: float = 0.0, delta_t: float = 0.0) -> dict:
    if mass_kg <= 0 or wing_area_m2 <= 0 or cl_max <= 0:
        raise ValueError("mass_kg, wing_area_m2 and cl_max must be positive")
    rho = atmosphere(altitude_m, delta_t)["density_kg_m3"]
    vs = math.sqrt(2 * mass_kg * G / (rho * wing_area_m2 * cl_max))
    return {"stall_m_s": vs, "stall_km_h": vs * 3.6, "approach_1_3vs_km_h": 1.3 * vs * 3.6, "density_kg_m3": rho}


WCL_CLASSES = [
    (4, {"ru": "очень лёгкая: комнатные модели", "en": "very light: indoor models"}),
    (7, {"ru": "парители и парк-флаеры", "en": "gliders and park flyers"}),
    (9, {"ru": "спортивные модели и тренеры", "en": "sport models and trainers"}),
    (13, {"ru": "копии и пилонные гонщики", "en": "scale and pylon racers"}),
    (25, {"ru": "реактивные с импеллером", "en": "EDF jets"}),
    (math.inf, {"ru": "выше обычного для моделей", "en": "above the usual model range"}),
]


def wing_loading(mass_kg: float, wing_area_m2: float, lang: str = "ru") -> dict:
    if mass_kg <= 0 or wing_area_m2 <= 0:
        raise ValueError("mass_kg and wing_area_m2 must be positive")
    wcl = (mass_kg * OZ_PER_KG) / (wing_area_m2 * FT2_PER_M2) ** 1.5
    label = next(c for lim, c in WCL_CLASSES if wcl < lim)[lang if lang in ("ru", "en") else "ru"]
    return {"kg_m2": mass_kg / wing_area_m2, "g_dm2": mass_kg * 1000 / (wing_area_m2 * 100),
            "cubic_oz_ft15": wcl, "cubic_class": label}


def froude_model(scale: float, mass_kg: float, speed_m_s: float | None = None, ixx: float | None = None,
                 iyy: float | None = None, izz: float | None = None, rho_full: float = 1.225, rho_model: float = 1.225) -> dict:
    """Dynamically similar (Froude-scaled) model. scale = full-size length / model length."""
    k = float(scale)
    if k <= 0 or mass_kg <= 0:
        raise ValueError("scale and mass_kg must be positive")
    dens = rho_model / rho_full
    out = {"scale": k, "model_mass_kg": mass_kg / k ** 3 * dens, "speed_factor": 1 / math.sqrt(k),
           "time_factor": 1 / math.sqrt(k), "frequency_factor": math.sqrt(k), "reynolds_factor": k ** -1.5,
           "note": "model_time = full_time * time_factor; replay video slowed by sqrt(scale) to see full-size motion"}
    if speed_m_s is not None:
        out["model_speed_m_s"] = speed_m_s / math.sqrt(k)
        out["model_speed_km_h"] = speed_m_s / math.sqrt(k) * 3.6
    for name, val in (("ixx", ixx), ("iyy", iyy), ("izz", izz)):
        if val is not None:
            out[f"model_{name}_kg_m2"] = val / k ** 5 * dens
    return out


def vapour_pressure(water_temp_c: float) -> float:
    """Saturation vapour pressure of water, Pa (Magnus-type fit, good for 0–50 °C)."""
    t = float(water_temp_c)
    return 610.94 * math.exp(17.625 * t / (t + 243.04))


def cavitation(speed_m_s: float, depth_m: float, cp_min: float, water_temp_c: float = 20.0,
               salt: bool = True, p_atm: float = 101325.0) -> dict:
    """Cavitation number at a foil and the speed where cavitation starts (sigma = -Cp_min)."""
    if speed_m_s <= 0 or depth_m < 0:
        raise ValueError("speed_m_s must be positive and depth_m non-negative")
    if cp_min >= 0:
        raise ValueError("cp_min must be negative (minimum pressure coefficient of the section)")
    if not 0 <= water_temp_c <= 50:
        raise ValueError("water_temp_c must be between 0 and 50 °C")
    rho = 1025.0 if salt else 998.2
    pv = vapour_pressure(water_temp_c)
    p_local = p_atm + rho * G * depth_m - pv
    sigma = p_local / (0.5 * rho * speed_m_s ** 2)
    v_inc = math.sqrt(p_local / (0.5 * rho * -cp_min))
    return {"cavitation_number": sigma, "minus_cp_min": -cp_min, "cavitates": sigma < -cp_min,
            "inception_speed_m_s": v_inc, "inception_speed_km_h": v_inc * 3.6, "inception_speed_kn": v_inc / 0.514444,
            "vapour_pressure_Pa": pv, "water_density_kg_m3": rho}


# Парашюты: коэффициент сопротивления CD0 отнесён к номинальной площади S0 —
# всей ткани купола вместе с полюсным отверстием и щелями; D0 = sqrt(4·S0/π).
# Parachutes: CD0 is based on the nominal area S0 — the whole canopy surface including vent and slots; D0 = sqrt(4·S0/π).
# Ranges: slotted types and guide surface — Recovery Systems Design Guide (AFFDL-TR-78-151) as tabulated in AGARD-AG-319,
# Table 3.1; flat circular and 10 % extended skirt — Knacke, Parachute Recovery Systems Design Manual (NWC TP 6575), Table 5-1.
PARACHUTE_SOURCES = {
    "agard": "https://www.sto.nato.int/publications/AGARD/AGARD-AG-319/AGARD-AG-319.pdf",
    "knacke": "https://apps.dtic.mil/sti/pdfs/ADA247666.pdf",
}
CANOPIES = {
    "flat_circular": (0.75, 0.80, {"ru": "плоский круглый", "en": "flat circular"}, "knacke"),
    "extended_skirt_10": (0.78, 0.87, {"ru": "с удлинённой кромкой 10 %", "en": "10 % extended skirt"}, "knacke"),
    "ringsail": (0.75, 0.90, {"ru": "ленточно-парусный (ringsail)", "en": "ringsail"}, "agard"),
    "ringslot": (0.56, 0.65, {"ru": "кольцевой щелевой (ringslot)", "en": "ringslot"}, "agard"),
    "disk_gap_band": (0.52, 0.58, {"ru": "диск-щель-лента", "en": "disk-gap-band"}, "agard"),
    "conical_ribbon": (0.50, 0.55, {"ru": "конический ленточный", "en": "conical ribbon"}, "agard"),
    "flat_ribbon": (0.45, 0.50, {"ru": "плоский ленточный", "en": "flat ribbon"}, "agard"),
    "guide_surface_ribbed": (0.28, 0.42, {"ru": "стабилизирующий с рёбрами (guide surface)", "en": "ribbed guide surface"}, "agard"),
}


def parachute_descent(mass_kg: float, canopy: str = "flat_circular", cd0: float | None = None,
                      area_m2: float | None = None, diameter_m: float | None = None,
                      target_speed_m_s: float | None = None, altitude_m: float = 0.0, delta_t: float = 0.0,
                      lang: str = "ru") -> dict:
    """Steady descent under a canopy, where drag equals weight: V = sqrt(2·m·g / (ρ·CD0·S0)).
    Give the canopy (area_m2 = S0 or diameter_m = D0) to get the speed, and/or target_speed_m_s to get the size needed."""
    lang = lang if lang in ("ru", "en") else "ru"
    if not mass_kg or mass_kg <= 0:
        raise ValueError("mass_kg must be positive (everything that hangs under the canopy, canopy included)")
    if cd0 is not None:
        if cd0 <= 0:
            raise ValueError("cd0 must be positive")
        lo = hi = mid = float(cd0)
        label, source = {"ru": "свой CD0", "en": "custom CD0"}[lang], None
    else:
        if canopy not in CANOPIES:
            raise ValueError("unknown canopy; use one of " + ", ".join(CANOPIES) + " or give cd0")
        lo, hi, names, src = CANOPIES[canopy]
        mid, label, source = (lo + hi) / 2, names[lang], PARACHUTE_SOURCES[src]
    if area_m2 is None and diameter_m is not None:
        if diameter_m <= 0:
            raise ValueError("diameter_m must be positive")
        area_m2 = math.pi * diameter_m ** 2 / 4
    if area_m2 is not None and area_m2 <= 0:
        raise ValueError("area_m2 must be positive")
    if area_m2 is None and target_speed_m_s is None:
        raise ValueError("give area_m2 or diameter_m (to get the descent rate) and/or target_speed_m_s (to size the canopy)")
    rho = atmosphere(altitude_m, delta_t)["density_kg_m3"]
    two_w = 2 * mass_kg * G
    out = {"canopy": label, "cd0": mid, "cd0_range": [lo, hi], "density_kg_m3": rho, "cd0_source": source,
           "note": {"ru": "S0 — вся ткань купола вместе с полюсным отверстием и щелями, D0 = √(4·S0/π). У полусферического купола S0 примерно вдвое больше площади его круга в плане.",
                    "en": "S0 is the whole canopy fabric including vent and slots, D0 = √(4·S0/π). For a hemispherical canopy S0 is about twice the area of its circle in plan."}[lang]}
    if area_m2 is not None:
        v = math.sqrt(two_w / (rho * mid * area_m2))
        out.update({"nominal_area_m2": area_m2, "nominal_diameter_m": math.sqrt(4 * area_m2 / math.pi),
                    "descent_m_s": v, "descent_range_m_s": [math.sqrt(two_w / (rho * hi * area_m2)), math.sqrt(two_w / (rho * lo * area_m2))],
                    "landing_energy_J": 0.5 * mass_kg * v ** 2, "equivalent_drop_height_m": v ** 2 / (2 * G)})
    if target_speed_m_s is not None:
        if target_speed_m_s <= 0:
            raise ValueError("target_speed_m_s must be positive")
        need = two_w / (rho * mid * target_speed_m_s ** 2)
        out.update({"target_speed_m_s": target_speed_m_s, "needed_area_m2": need,
                    "needed_area_range_m2": [two_w / (rho * hi * target_speed_m_s ** 2), two_w / (rho * lo * target_speed_m_s ** 2)],
                    "needed_diameter_m": math.sqrt(4 * need / math.pi)})
    return out
