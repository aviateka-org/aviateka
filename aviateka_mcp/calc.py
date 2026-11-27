"""Small engineering calculators shared by the Aviateka MCP server.
The web page implements the same formulas in JavaScript (tests compare both)."""
import math

R = 287.053        # J/(kg K), dry air
G = 9.80665        # m/s^2
GAMMA = 1.4
OZ_PER_KG = 35.27396
FT2_PER_M2 = 10.76391


# U.S. Standard Atmosphere 1976 to 86 km (same as ISA up to 32 km): layers in geopotential metres, base temperature, lapse K/m.
# Источник/source: https://www.pdas.com/atmosdef.html
R_EARTH = 6356766.0
ATM_LAYERS = [(0.0, 288.15, -0.0065), (11000.0, 216.65, 0.0), (20000.0, 216.65, 0.001), (32000.0, 228.65, 0.0028),
              (47000.0, 270.65, 0.0), (51000.0, 270.65, -0.0028), (71000.0, 214.65, -0.002)]
ATM_TOP = 84852.0


def _layer_pressure(hb, tb, lapse, pb, h):
    if lapse == 0:
        return pb * math.exp(-G * (h - hb) / (R * tb))
    return pb * (tb / (tb + lapse * (h - hb))) ** (G / (R * lapse))


ATM_BASE_P = [101325.0]
for _i in range(1, len(ATM_LAYERS)):
    _hb, _tb, _l = ATM_LAYERS[_i - 1]
    ATM_BASE_P.append(_layer_pressure(_hb, _tb, _l, ATM_BASE_P[-1], ATM_LAYERS[_i][0]))


def geopotential(altitude_m: float) -> float:
    """Geometric altitude (m) to geopotential altitude (m)."""
    return R_EARTH * altitude_m / (R_EARTH + altitude_m)


def atmosphere(altitude_m: float, delta_t: float = 0.0, geometric: bool = False) -> dict:
    """U.S. Standard Atmosphere 1976 (equal to ISA below 32 km) from −500 m to 84 852 m geopotential (86 km geometric),
    with a temperature offset (pressure stays standard). altitude_m is geopotential, as in ISA tables, unless geometric=True."""
    h = float(altitude_m)
    if geometric:
        h = geopotential(h)
    if not -500 <= h <= ATM_TOP + 1:
        raise ValueError("altitude_m must be between -500 and 84852 m geopotential (86 km geometric)")
    i = max(k for k, layer in enumerate(ATM_LAYERS) if h >= layer[0]) if h >= 0 else 0
    hb, tb, lapse = ATM_LAYERS[i]
    t_std = tb + lapse * (h - hb)
    p = _layer_pressure(hb, tb, lapse, ATM_BASE_P[i], h)
    t = t_std + float(delta_t)
    rho = p / (R * t)
    a = math.sqrt(GAMMA * R * t)
    mu = 1.458e-6 * t ** 1.5 / (t + 110.4)
    return {"altitude_m": float(altitude_m), "geopotential_altitude_m": round(h, 1), "temperature_K": round(t, 3), "temperature_C": round(t - 273.15, 3),
            "pressure_Pa": float(f"{p:.6g}"), "density_kg_m3": float(f"{rho:.6g}"), "speed_of_sound_m_s": round(a, 3),
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


# Аэростаты: подъёмная сила газа при давлении газа, равном наружному (открытый низ или нулевое избыточное давление), сухой воздух.
# Lighter-than-air lift with gas pressure equal to ambient (open appendix or zero-pressure envelope), dry air.
RU = 8.314462618                 # J/(mol K), SI 2019 exact
LTA_SOURCES = {"gases": "https://iupac.qmul.ac.uk/AtWt/AtWt13.html",
               "hot_air_check": "https://engineeringtoolbox.com/hot-air-balloon-lifting-force-d_562.html"}
LTA_GASES = {
    "helium": (4.002602e-3, {"ru": "гелий", "en": "helium"}),
    "hydrogen": (2.01588e-3, {"ru": "водород", "en": "hydrogen"}),
    "hot_air": (None, {"ru": "горячий воздух", "en": "hot air"}),
}


def buoyancy(volume_m3: float | None = None, gas: str = "helium", gas_temp_c: float | None = None, purity: float = 1.0,
             mass_kg: float | None = None, altitude_m: float = 0.0, ambient_temp_c: float | None = None,
             delta_t: float = 0.0, lang: str = "ru") -> dict:
    """Lift of a lighter-than-air craft: L = V·(ρ_air − ρ_gas). Give volume_m3 to get lift, and/or mass_kg
    (envelope, structure and load, gas excluded) to get the net lift or the volume needed."""
    lang = lang if lang in ("ru", "en") else "ru"
    if gas not in LTA_GASES:
        raise ValueError("unknown gas; use one of " + ", ".join(LTA_GASES))
    if volume_m3 is None and mass_kg is None:
        raise ValueError("give volume_m3 (to get the lift) and/or mass_kg (to get the net lift or the volume needed)")
    if volume_m3 is not None and volume_m3 <= 0:
        raise ValueError("volume_m3 must be positive")
    if mass_kg is not None and mass_kg < 0:
        raise ValueError("mass_kg must not be negative")
    if ambient_temp_c is not None:
        delta_t = ambient_temp_c + 273.15 - atmosphere(altitude_m)["temperature_K"]
    a = atmosphere(altitude_m, delta_t)
    p, t = a["pressure_Pa"], a["temperature_K"]
    rho_air = p / (R * t)
    molar, names = LTA_GASES[gas]
    if gas == "hot_air":
        tg = (100.0 if gas_temp_c is None else gas_temp_c) + 273.15
        if tg <= t:
            raise ValueError("gas_temp_c must be above the ambient air temperature")
        rho_gas = p / (R * tg)
        purity = 1.0
    else:
        tg = t if gas_temp_c is None else gas_temp_c + 273.15
        if tg <= 0:
            raise ValueError("gas_temp_c is below absolute zero")
        if not 0 < purity <= 1:
            raise ValueError("purity must be above 0 and at most 1 (share of lifting gas, the rest is air)")
        rho_gas = purity * p * molar / (RU * tg) + (1 - purity) * p / (R * tg)
    lift = rho_air - rho_gas
    if lift <= 0:
        raise ValueError("no lift: the gas is not lighter than the surrounding air")
    out = {"gas": names[lang], "purity": purity, "ambient_temp_C": t - 273.15, "gas_temp_C": tg - 273.15,
           "pressure_Pa": p, "air_density_kg_m3": rho_air, "gas_density_kg_m3": rho_gas, "lift_kg_per_m3": lift,
           "sources": LTA_SOURCES,
           "note": {"ru": "Давление газа равно наружному, воздух сухой. Подъём считается в килограммах груза, который можно поднять; масса самого газа уже вычтена.",
                    "en": "Gas pressure equals ambient, dry air. Lift is in kilograms of load that can be carried; the gas mass is already subtracted."}[lang]}
    if volume_m3 is not None:
        out.update({"volume_m3": volume_m3, "gross_lift_kg": volume_m3 * lift, "gas_mass_kg": volume_m3 * rho_gas})
        if mass_kg is not None:
            net = volume_m3 * lift - mass_kg
            out.update({"mass_kg": mass_kg, "net_lift_kg": net, "net_lift_N": net * G})
    if mass_kg is not None and mass_kg > 0:
        need = mass_kg / lift
        out.update({"mass_kg": mass_kg, "needed_volume_m3": need, "needed_sphere_diameter_m": (6 * need / math.pi) ** (1 / 3)})
    return out


# Висение винта по теории импульса с коэффициентом качества (figure of merit):
# T = m·g/n, v_i = sqrt(T / (2·ρ·A)), P_ideal = T·v_i, P_shaft = P_ideal / FM.
# Hover by momentum theory with a figure of merit. NASA measured FM 0.58–0.72 for production 9–15 in drone rotors,
# motor-and-controller efficiency 50–77 % and body download 5–15 % (Russell et al. 2016); smaller rotors can fall below 0.5.
HOVER_SOURCES = {"nasa_multicopter_tests": "https://rotorcraft.arc.nasa.gov/Publications/files/72-2016-374.pdf",
                 "fm_small_rotors": "https://arxiv.org/pdf/2608.25150",
                 "fm_definition": "https://rotorcraft.arc.nasa.gov/Publications/files/Young_AIAA_2002.PDF",
                 "measured_props": "https://m-selig.ae.illinois.edu/props/propDB.html"}


def rotor_hover(mass_kg: float, diameter_m: float, rotors: int = 4, fm: float = 0.6, altitude_m: float = 0.0,
                delta_t: float = 0.0, drive_efficiency: float | None = None, battery_wh: float | None = None,
                usable_fraction: float = 1.0, download: float = 0.0, lang: str = "ru") -> dict:
    """Power to hover on n equal, separate rotors; optionally electrical power and hover time from a battery."""
    lang = lang if lang in ("ru", "en") else "ru"
    if not mass_kg or mass_kg <= 0:
        raise ValueError("mass_kg must be positive (the whole aircraft in hover)")
    if not diameter_m or diameter_m <= 0:
        raise ValueError("diameter_m must be positive (rotor diameter)")
    if int(rotors) != rotors or rotors < 1:
        raise ValueError("rotors must be a whole number, 1 or more")
    if not 0 < fm <= 1:
        raise ValueError("fm (figure of merit) must be above 0 and at most 1")
    if drive_efficiency is not None and not 0 < drive_efficiency <= 1:
        raise ValueError("drive_efficiency must be above 0 and at most 1")
    if battery_wh is not None and battery_wh <= 0:
        raise ValueError("battery_wh must be positive")
    if not 0 < usable_fraction <= 1:
        raise ValueError("usable_fraction must be above 0 and at most 1")
    if not 0 <= download < 0.5:
        raise ValueError("download must be at least 0 and below 0.5 (share of rotor thrust lost on the body)")
    rho = atmosphere(altitude_m, delta_t)["density_kg_m3"]
    n = int(rotors)
    t = mass_kg * G / n / (1 - download)
    area = math.pi * diameter_m ** 2 / 4
    vi = math.sqrt(t / (2 * rho * area))
    p_ideal = t * vi
    p_shaft = p_ideal / fm
    out = {"rotors": n, "density_kg_m3": rho, "thrust_per_rotor_N": t, "thrust_per_rotor_g": t / G * 1000,
           "disk_loading_N_m2": t / area, "induced_velocity_m_s": vi, "ideal_power_per_rotor_W": p_ideal,
           "shaft_power_per_rotor_W": p_shaft, "shaft_power_total_W": p_shaft * n, "fm": fm, "download": download,
           "power_loading_g_per_W": mass_kg * 1000 / (p_shaft * n), "sources": HOVER_SOURCES,
           "note": {"ru": "Винты отдельные и не мешают друг другу; соосные пары и перекрытие не учтены. NASA намерило у серийных винтов дронов 9–15 дюймов FM 0,58–0,72, КПД мотора с регулятором 50–77 % и потерю тяги на корпус 5–15 %; у винтов мельче FM бывает ниже 0,5.",
                    "en": "Rotors are separate and do not interfere; coaxial pairs and overlap are not modelled. NASA measured FM 0.58–0.72 for production 9–15 in drone rotors, motor-and-controller efficiency 50–77 % and body download 5–15 %; smaller rotors can have FM below 0.5."}[lang]}
    p_draw = p_shaft * n
    if drive_efficiency is not None:
        p_draw = p_shaft * n / drive_efficiency
        out.update({"drive_efficiency": drive_efficiency, "electrical_power_W": p_draw})
    if battery_wh is not None:
        out.update({"battery_wh": battery_wh, "usable_fraction": usable_fraction,
                    "hover_time_min": battery_wh * usable_fraction / p_draw * 60})
    return out


# Ракета: формула Циолковского, без потерь на тяготение и сопротивление. Rocket: ideal rocket equation, no gravity or drag losses.
ROCKET_SOURCES = {"rocket_equation": "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation",
                  "specific_impulse": "https://www.grc.nasa.gov/www/BGH/specimp.html"}


def rocket_delta_v(isp_s: float, initial_mass_kg: float, final_mass_kg: float | None = None,
                   propellant_kg: float | None = None, thrust_N: float | None = None, lang: str = "ru") -> dict:
    """Ideal velocity gain Δv = Isp·g0·ln(m0/mf) for one stage; with thrust also start thrust-to-weight and burn time."""
    lang = lang if lang in ("ru", "en") else "ru"
    if not isp_s or isp_s <= 0:
        raise ValueError("isp_s must be positive (specific impulse in seconds)")
    if not initial_mass_kg or initial_mass_kg <= 0:
        raise ValueError("initial_mass_kg must be positive (everything at lift-off, propellant included)")
    if final_mass_kg is None and propellant_kg is None:
        raise ValueError("give final_mass_kg (mass after burnout) or propellant_kg")
    if final_mass_kg is None:
        final_mass_kg = initial_mass_kg - propellant_kg
    if not 0 < final_mass_kg < initial_mass_kg:
        raise ValueError("final mass must be positive and less than the initial mass")
    prop = initial_mass_kg - final_mass_kg
    ve = isp_s * G
    out = {"isp_s": isp_s, "exhaust_velocity_m_s": ve, "initial_mass_kg": initial_mass_kg, "final_mass_kg": final_mass_kg,
           "propellant_kg": prop, "mass_ratio": initial_mass_kg / final_mass_kg, "propellant_fraction": prop / initial_mass_kg,
           "delta_v_m_s": ve * math.log(initial_mass_kg / final_mass_kg), "sources": ROCKET_SOURCES,
           "note": {"ru": "Идеальный прирост скорости одной ступени: без потерь на тяготение, сопротивление и управление. Реальная ракета набирает заметно меньше.",
                    "en": "Ideal velocity gain of one stage: no gravity, drag or steering losses. A real rocket gains noticeably less."}[lang]}
    if thrust_N is not None:
        if thrust_N <= 0:
            raise ValueError("thrust_N must be positive")
        mdot = thrust_N / ve
        out.update({"thrust_N": thrust_N, "thrust_to_weight_at_start": thrust_N / (initial_mass_kg * G),
                    "thrust_to_weight_at_burnout": thrust_N / (final_mass_kg * G), "mass_flow_kg_s": mdot, "burn_time_s": prop / mdot})
    return out


# Нагрев в критической точке носка по Саттону и Грейвсу: q = k·sqrt(ρ/Rn)·V³, конвекция, холодная стенка, воздух Земли.
# Stagnation-point convective heating (Sutton–Graves), cold wall, Earth air. Other sources give k from 1.63e-4 to 1.83e-4.
SUTTON_GRAVES_K_EARTH = 1.7415e-4
ENTRY_SOURCES = {"sutton_graves_k": "https://arxiv.org/pdf/2611.16291",
                 "k_spread": "https://arxiv.org/pdf/2107.13513",
                 "atmosphere": "https://www.pdas.com/atmosdef.html"}


def entry_heating(speed_m_s: float, altitude_m: float, nose_radius_m: float, k: float = SUTTON_GRAVES_K_EARTH,
                  lang: str = "ru") -> dict:
    """Convective heat flux at the nose stagnation point during atmospheric entry, plus dynamic pressure and Mach.
    altitude_m is geometric (height above sea level), up to 86 km."""
    lang = lang if lang in ("ru", "en") else "ru"
    if not speed_m_s or speed_m_s <= 0:
        raise ValueError("speed_m_s must be positive")
    if not nose_radius_m or nose_radius_m <= 0:
        raise ValueError("nose_radius_m must be positive")
    if not k or k <= 0:
        raise ValueError("k must be positive")
    a = atmosphere(altitude_m, geometric=True)
    rho = a["density_kg_m3"]
    q = k * math.sqrt(rho / nose_radius_m) * speed_m_s ** 3
    return {"speed_m_s": speed_m_s, "altitude_m": altitude_m, "nose_radius_m": nose_radius_m, "k": k,
            "density_kg_m3": rho, "mach": speed_m_s / a["speed_of_sound_m_s"],
            "dynamic_pressure_Pa": 0.5 * rho * speed_m_s ** 2,
            "heat_flux_W_m2": q, "heat_flux_W_cm2": q / 1e4,
            "heat_flux_range_W_cm2": [q / k * 1.63e-4 / 1e4, q / k * 1.83e-4 / 1e4],
            "sources": ENTRY_SOURCES,
            "note": {"ru": "Только конвекция в критической точке носка при холодной стенке, воздух Земли. Излучение горячего газа за ударной волной не учтено — на очень больших скоростях оно добавляет заметно. Разброс — по разным значениям постоянной в литературе.",
                     "en": "Convection at the nose stagnation point only, cold wall, Earth air. Radiation from the hot shock layer is not included — at very high speeds it adds noticeably. The range reflects different values of the constant in the literature."}[lang]}

