"""Aviateka MCP server: open aircraft-design tools, workflows, gaps, benchmarks, validation matrix, glossary and calculators (RU/EN).

Run (stdio, for Claude Desktop and other MCP clients):   aviateka-mcp          (or: python -m aviateka_mcp)
Run (HTTP, streamable):                                   aviateka-mcp --http [--port 8000]
Works with the official MCP Python SDK 1.x (FastMCP) and 2.x (MCPServer)."""
import json, os, re, sys
from typing import Any

try:                                    # MCP SDK 2.x
    from mcp.server.mcpserver import MCPServer
except ImportError:                     # MCP SDK 1.x
    from mcp.server.fastmcp import FastMCP as MCPServer

try:
    from . import calc
except ImportError:                     # run as a plain script: python server.py
    import calc

try:
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:
    from mcp.server.fastmcp.exceptions import ToolError


def _safe(fn, *a):
    """Report bad inputs as a clean tool error the agent can read."""
    try:
        return fn(*a)
    except ValueError as e:
        raise ToolError(str(e)) from None

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.environ.get("AVIATEKA_CATALOG") or os.path.join(HERE, "catalog.json"), encoding="utf-8") as f:
    CAT = json.load(f)
TOOLS = {t["id"]: t for t in CAT["tools"]}
STATUS_ORDER = {"active": 0, "unknown": 1, "freeware": 2, "on_request": 3, "announced": 4, "legacy": 5, "stale": 6, "proprietary": 7, "commercial": 8}


def L(obj: Any, lang: str) -> Any:
    """Pick one language from {ru, en} pairs, recursively."""
    if isinstance(obj, dict):
        if set(obj) == {"ru", "en"}:
            return obj.get(lang) or obj["ru"]
        return {k: L(v, lang) for k, v in obj.items()}
    if isinstance(obj, list):
        return [L(v, lang) for v in obj]
    return obj


def _lang(lang: str) -> str:
    return lang if lang in ("ru", "en") else "ru"


def _text(t: dict) -> str:
    parts = [t["name"], t["org"] or ""]
    for k in ("summary", "use", "caveat"):
        if t.get(k):
            parts += [t[k]["ru"], t[k]["en"]]
    return " ".join(parts).lower()


def _brief(t: dict, lang: str) -> dict:
    return L({k: t[k] for k in ("id", "name", "url", "status", "last_commit", "license", "disciplines", "fidelity", "aircraft", "summary", "use")}
             | {"status_label": CAT["statuses"][t["status"]]}, lang)


INSTRUCTIONS = (
    "Aviateka / Авиатека — a curated catalog of open aircraft-design tools (aerodynamics, propellers, stability, flight test, "
    "structures, aeroelasticity, MDO) with bilingual RU/EN data as of " + CAT["as_of"] + ". "
    "Start with find_workflows for a task or aircraft type, then search_tools / get_tool for details. "
    "Check list_gaps before promising that a tool exists, and list_benchmarks for expected accuracy. "
    "Statuses: active = code changed within 365 days; stale = older; unknown = date not checked. "
    "Licences marked null were not verified: check the repository. Calculators: atmosphere, reynolds_mach, stall_speed, wing_loading, froude_model, cavitation, parachute_descent. "
    "Covers aircraft, fabric craft (paragliders, hang gliders, parachutes, kites, balloons), WIG craft (ekranoplans) and hydrofoil craft. get_validation shows how well tools matched measurements. "
    "get_changelog lists versions and what changed; how_to_contribute says how to send corrections and calculations. "
    "Pass lang='en' for English, default is Russian."
)

try:
    server = MCPServer(name="aviateka", instructions=INSTRUCTIONS, version=CAT["version"])
except TypeError:                       # SDK 1.x has no version argument
    server = MCPServer(name="aviateka", instructions=INSTRUCTIONS)


@server.tool()
def get_taxonomy(lang: str = "ru") -> dict:
    """Disciplines, fidelity levels (L0 handbook, L1 potential flow, L2 mid, L3 CFD/FEM, EXP measured), design stages, aircraft types and status labels. Use the ids as filters in other tools."""
    lang = _lang(lang)
    return L({k: CAT[k] for k in ("disciplines", "fidelity", "stages", "aircraft", "statuses")} | {"version": CAT["version"], "as_of": CAT["as_of"], "method": CAT["method"]}, lang)


@server.tool()
def get_changelog(lang: str = "ru") -> dict:
    """Catalog version, numbering rules and the change history, newest first."""
    lang = _lang(lang)
    return L({"version": CAT["version"], "versioning": CAT["versioning"], "changelog": CAT["changelog"]}, lang)


@server.tool()
def search_tools(query: str = "", discipline: str = "", aircraft: str = "", stage: str = "", fidelity: str = "",
                 include_stale: bool = True, lang: str = "ru", limit: int = 20) -> dict:
    """Search open aircraft-design tools. query: free text in Russian or English (e.g. 'флаттер', 'propeller', 'low Reynolds').
    Filters take taxonomy ids: discipline (aero, airfoil, cfd, propulsion, stability, flightsim, sysid, structures, aeroelastic, mdo, geometry, hydro),
    aircraft (transport, ga, racer, glider, rc, uav, hale, evtol, rotorcraft, hpa, flapping, wig, hydrofoil, paraglider, hangglider, parachute, kite, balloon), stage (concept, preliminary, detail, test),
    fidelity (L0, L1, L2, L3, EXP). Active tools come first."""
    lang = _lang(lang)
    words = [w for w in re.split(r"\W+", query.lower()) if w]
    res = []
    for t in CAT["tools"]:
        if discipline and discipline not in t["disciplines"]:
            continue
        if aircraft and aircraft not in t["aircraft"]:
            continue
        if stage and stage not in t["stages"]:
            continue
        if fidelity and fidelity not in t["fidelity"]:
            continue
        if not include_stale and t["status"] in ("stale", "legacy"):
            continue
        text = _text(t)
        score = sum(text.count(w) for w in words) if words else 1
        if words and score == 0:
            continue
        res.append((score, t))
    res.sort(key=lambda x: (-x[0], STATUS_ORDER.get(x[1]["status"], 9), -(int((x[1]["last_commit"] or "0000").replace("-", "")[:8] or 0))))
    return {"count": len(res), "tools": [_brief(t, lang) for _, t in res[:max(1, min(limit, 60))]]}


@server.tool()
def get_tool(tool_id: str, lang: str = "ru") -> dict:
    """Full card of one tool: links, licence, last commit, status, disciplines, fidelity, stages, aircraft, summary, when to use, known issues, sources, and the workflows that use it."""
    lang = _lang(lang)
    t = TOOLS.get(tool_id)
    if not t:
        close = [i for i in TOOLS if tool_id.lower() in i or i in tool_id.lower()]
        return {"error": f"unknown tool_id '{tool_id}'", "did_you_mean": close[:5]}
    wf = [{"id": w["id"], "title": w["title"]} for w in CAT["workflows"] if any(s["tool"] == tool_id for s in w["steps"])]
    val = [{"id": v["id"], "summary": v["summary"]} for v in CAT.get("validation", []) if v.get("tool") == tool_id]
    return L(dict(t, status_label=CAT["statuses"][t["status"]], workflows=wf, validation=val), lang)


@server.tool()
def find_workflows(aircraft: str = "", stage: str = "", query: str = "", lang: str = "ru") -> dict:
    """Recommended tool chains for a design task: ordered steps (tool + what to do) and a check that tells when the result can be trusted.
    Filter by aircraft type id, stage id, or free text (e.g. 'флаттер', 'propeller')."""
    lang = _lang(lang)
    words = [w for w in re.split(r"\W+", query.lower()) if w]
    out = []
    for w in CAT["workflows"]:
        if aircraft and aircraft not in w["aircraft"]:
            continue
        if stage and stage != w["stage"]:
            continue
        if words:
            text = " ".join([w["title"]["ru"], w["title"]["en"], w["goal"]["ru"], w["goal"]["en"]] + [s["what"]["ru"] + " " + s["what"]["en"] + " " + s["tool"] for s in w["steps"]]).lower()
            if not any(x in text for x in words):
                continue
        steps = [dict(s, name=TOOLS[s["tool"]]["name"], url=TOOLS[s["tool"]]["url"], status=TOOLS[s["tool"]]["status"]) for s in w["steps"]]
        out.append(dict(w, steps=steps))
    return {"count": len(out), "workflows": L(out, lang)}


@server.tool()
def list_gaps(lang: str = "ru") -> dict:
    """Niches where no ready open tool was found. mark 'window' = partial solutions nearby, can be filled; 'forbidden' = blocked by physics for cheap methods. Also lists what the catalog does not cover."""
    lang = _lang(lang)
    return L({"gaps": CAT["gaps"], "marks": CAT["gap_marks"], "out_of_scope": CAT["out_of_scope"]}, lang)


@server.tool()
def list_benchmarks(lang: str = "ru") -> dict:
    """Published reference numbers for sanity checks (wind-tunnel L/D of a 200 g model, open vs commercial flutter speed, OpenVSP propeller error, etc.) with sources."""
    return {"benchmarks": L(CAT["benchmarks"], _lang(lang))}


@server.tool()
def glossary(query: str = "", lang: str = "ru") -> dict:
    """Short RU/EN definitions of aircraft-design terms, with Chinese/Japanese search keywords where useful. Empty query returns all terms."""
    lang = _lang(lang)
    q = query.lower().strip()
    items = [g for g in CAT["glossary"] if not q or q in (g["id"] + g["term"]["ru"] + g["term"]["en"] + g["definition"]["ru"] + g["definition"]["en"]).lower()]
    return {"count": len(items), "terms": L(items, lang)}


@server.tool()
def get_case(case_id: str = "strizh", lang: str = "ru") -> dict:
    """A worked design case and its backlog of checks mapped to catalog tools. Available: 'strizh' (joined-diamond-wing pylon racer)."""
    lang = _lang(lang)
    for c in CAT["cases"]:
        if c["id"] == case_id:
            c = dict(c, backlog=[dict(b, name=TOOLS[b["tool"]]["name"]) for b in c["backlog"]])
            return L(c, lang)
    return {"error": f"unknown case '{case_id}'", "available": [c["id"] for c in CAT["cases"]]}


@server.tool()
def atmosphere(altitude_m: float, delta_t: float = 0.0) -> dict:
    """International Standard Atmosphere 0–20 km: temperature, pressure, density, speed of sound, viscosity. delta_t shifts temperature (°C) at standard pressure."""
    return _safe(calc.atmosphere, altitude_m, delta_t)


@server.tool()
def reynolds_mach(speed_m_s: float, chord_m: float, altitude_m: float = 0.0, delta_t: float = 0.0) -> dict:
    """Reynolds number (speed × chord / kinematic viscosity) and Mach number at a given altitude."""
    return _safe(calc.reynolds_mach, speed_m_s, chord_m, altitude_m, delta_t)


@server.tool()
def stall_speed(mass_kg: float, wing_area_m2: float, cl_max: float, altitude_m: float = 0.0, delta_t: float = 0.0) -> dict:
    """Stall speed from mass, wing area and maximum lift coefficient; also 1.3·Vs approach speed."""
    return _safe(calc.stall_speed, mass_kg, wing_area_m2, cl_max, altitude_m, delta_t)


@server.tool()
def wing_loading(mass_kg: float, wing_area_m2: float, lang: str = "ru") -> dict:
    """Wing loading in kg/m² and g/dm², plus cubic wing loading (oz/ft^1.5) with the usual RC-model class, to compare aircraft of different size."""
    return _safe(calc.wing_loading, mass_kg, wing_area_m2, _lang(lang))


@server.tool()
def froude_model(scale: float, mass_kg: float, speed_m_s: float | None = None, ixx: float | None = None, iyy: float | None = None,
                 izz: float | None = None, rho_full: float = 1.225, rho_model: float = 1.225) -> dict:
    """Dynamically similar (Froude-scaled) flying model: model mass, speed and inertias for a length scale (full/model), plus time and Reynolds factors.
    Use rho_full/rho_model when the full-size aircraft and the model fly at different air densities."""
    return _safe(calc.froude_model, scale, mass_kg, speed_m_s, ixx, iyy, izz, rho_full, rho_model)


@server.tool()
def cavitation(speed_m_s: float, depth_m: float, cp_min: float, water_temp_c: float = 20.0, salt: bool = True, p_atm: float = 101325.0) -> dict:
    """Hydrofoil cavitation check: cavitation number at the given speed and depth, and the speed where cavitation starts (sigma = -Cp_min).
    cp_min is the section's minimum pressure coefficient (negative, e.g. from XFOIL). Salt water by default."""
    return _safe(calc.cavitation, speed_m_s, depth_m, cp_min, water_temp_c, salt, p_atm)


@server.tool()
def parachute_descent(mass_kg: float, canopy: str = "flat_circular", cd0: float | None = None, area_m2: float | None = None,
                      diameter_m: float | None = None, target_speed_m_s: float | None = None, altitude_m: float = 0.0,
                      delta_t: float = 0.0, lang: str = "ru") -> dict:
    """Parachute steady descent rate, or the canopy size for a target rate: V = sqrt(2·m·g / (rho·CD0·S0)).
    mass_kg: everything under the canopy, canopy included. Give the canopy as area_m2 (nominal area S0 = whole fabric incl. vent)
    or diameter_m (nominal D0), and/or target_speed_m_s. canopy: flat_circular, extended_skirt_10, ringsail, ringslot,
    disk_gap_band, conical_ribbon, flat_ribbon, guide_surface_ribbed (CD0 ranges from Knacke / AFFDL-TR-78-151), or pass cd0.
    Returns the rate with its range over the CD0 range, landing energy and the equivalent free-fall height."""
    return _safe(calc.parachute_descent, mass_kg, canopy, cd0, area_m2, diameter_m, target_speed_m_s, altitude_m, delta_t, _lang(lang))


@server.tool()
def get_validation(tool_id: str = "", quantity: str = "", lang: str = "ru") -> dict:
    """Validation matrix: who computed what with which tool and how far it was from measurements (diff_pct, direction over/under).
    Filter by tool_id (catalog id) or quantity (CL, CD, Cm…). Each row names its source, the comparison case and caveats.
    Use it before trusting a tool's absolute numbers."""
    lang = _lang(lang)
    rows = [v for v in CAT.get("validation", []) if (not tool_id or v.get("tool") == tool_id)]
    if quantity:
        q = quantity.lower()
        rows = [dict(v, points=[p for p in v["points"] if p["quantity"].lower() == q]) for v in rows]
        rows = [v for v in rows if v["points"]]
    return L({"count": len(rows), "rows": rows, "how_to_add": _contribute_links()["calculation"]}, lang)


def _contribute_links() -> dict:
    base = f"https://github.com/{CAT['repo']}"
    return {"repo": base,
            "new_tool": f"{base}/issues/new?template=new_tool.yml",
            "correction": f"{base}/issues/new?template=correction.yml",
            "calculation": f"{base}/issues/new?template=calculation.yml",
            "new_topic": f"{base}/issues/new?template=new_topic.yml",
            "guide": f"{base}/blob/main/CONTRIBUTING.md"}


@server.tool()
def how_to_contribute(lang: str = "ru") -> dict:
    """Where to send a new tool, a correction, your own calculation for the validation matrix or a new topic.
    Agents: offer these links to the user; do not file issues on the user's behalf without asking."""
    lang = _lang(lang)
    return L({"links": _contribute_links(),
              "license": {"code": CAT["license"]["code"], "data": CAT["license"]["data"]},
              "note": {"ru": "Формы не требуют знания Git: опишите своими словами, хранители переведут в формат каталога со ссылкой на источник.",
                       "en": "The forms need no Git: describe it in your own words; maintainers turn it into catalog format with a source link."}}, lang)


@server.resource("aviateka://catalog", name="catalog", mime_type="application/json", description="The whole Aviateka catalog (RU/EN) as JSON.")
def catalog_resource() -> str:
    return json.dumps(CAT, ensure_ascii=False)


@server.prompt()
def plan_design(aircraft_type: str, goal: str, lang: str = "ru") -> str:
    """Prompt template: plan the analysis chain for an aircraft concept using Aviateka."""
    if _lang(lang) == "en":
        return (f"Plan the design analysis for a {aircraft_type} with the goal: {goal}. Use find_workflows (aircraft='{aircraft_type}'), "
                "then get_tool for each step. Prefer active tools, say which tools are stale or unverified, check list_gaps for missing capabilities "
                "and list_benchmarks for expected accuracy. End with an ordered plan: step, tool, input, output, acceptance check.")
    return (f"Спланируй расчёты для аппарата типа {aircraft_type}, цель: {goal}. Начни с find_workflows (aircraft='{aircraft_type}'), "
            "затем get_tool по каждому шагу. Предпочитай живые инструменты, отметь устаревшие и непроверенные, проверь list_gaps на отсутствующие возможности "
            "и list_benchmarks на ожидаемую точность. В конце — упорядоченный план: шаг, инструмент, вход, выход, критерий приёмки.")


def main() -> None:
    if "--http" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8000
        try:
            server.run("streamable-http", port=port)
        except TypeError:                       # SDK 1.x takes port from settings
            server.settings.port = port
            server.run("streamable-http")
    else:
        server.run("stdio")


if __name__ == "__main__":
    main()
