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
