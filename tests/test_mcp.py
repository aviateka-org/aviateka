"""Сквозная проверка MCP-сервера: запустить по stdio, вызвать каждый инструмент, сверить ключевые числа.
End-to-end test: start the server over stdio, call every tool, check key numbers.

    python tests/test_mcp.py   (сначала / first: python scripts/build_catalog.py)"""
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(ROOT, "aviateka_mcp", "catalog.json"), encoding="utf-8"))


def payload(res):
    if getattr(res, "isError", False) or getattr(res, "is_error", False):
        raise AssertionError(res.content[0].text)
    sc = getattr(res, "structuredContent", None) or getattr(res, "structured_content", None)
    if sc:
        return sc.get("result", sc) if isinstance(sc, dict) and set(sc) == {"result"} else sc
    return json.loads(res.content[0].text)


async def main():
    params = StdioServerParameters(command=sys.executable, args=["-m", "aviateka_mcp"], cwd=ROOT)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            names = sorted(t.name for t in tools)
            print("tools:", names)
            assert len(names) == 18, names
            p = lambda n, a=None: s.call_tool(n, a or {})
            tax = payload(await p("get_taxonomy", {"lang": "en"}))
            assert tax["fidelity"][4]["name"] == "Measured"
            r1 = payload(await p("search_tools", {"query": "флаттер"}))
            print("search 'флаттер':", [t["id"] for t in r1["tools"]])
            assert "loadskernel" in [t["id"] for t in r1["tools"]]
            r2 = payload(await p("search_tools", {"discipline": "propulsion", "lang": "en"}))
            print("propulsion:", [t["id"] for t in r2["tools"]])
            r3 = payload(await p("get_tool", {"tool_id": "optvl", "lang": "en"}))
            assert "#72" in r3["caveat"] and r3["workflows"], r3
            r4 = payload(await p("get_tool", {"tool_id": "openvs"}))
            assert "openvsp" in r4["did_you_mean"], r4
            r5 = payload(await p("find_workflows", {"aircraft": "racer"}))
            print("racer workflows:", [w["id"] for w in r5["workflows"]])
            r6 = payload(await p("find_workflows", {"query": "flutter", "lang": "en"}))
            assert r6["workflows"][0]["id"] == "flutter"
            assert len(payload(await p("list_gaps"))["gaps"]) == len(CAT["gaps"])
            assert len(payload(await p("list_benchmarks", {"lang": "en"}))["benchmarks"]) == len(CAT["benchmarks"])
            assert payload(await p("glossary", {"query": "флаттер"}))["count"] >= 1
            case = payload(await p("get_case", {"lang": "en"}))
            assert case["backlog"][0]["name"] == "Loads Kernel"
            atm = payload(await p("atmosphere", {"altitude_m": 0}))
            assert abs(atm["density_kg_m3"] - 1.225) < 1e-3 and abs(atm["speed_of_sound_m_s"] - 340.29) < 0.05, atm
            atm11 = payload(await p("atmosphere", {"altitude_m": 11000}))
            assert abs(atm11["pressure_Pa"] - 22632) < 5 and abs(atm11["density_kg_m3"] - 0.3639) < 1e-3, atm11
            rm = payload(await p("reynolds_mach", {"speed_m_s": 226.4, "chord_m": 1.92, "altitude_m": 1119, "delta_t": 15}))
            print(f"Strizh race: Re {rm['reynolds']:.3g}, M {rm['mach']:.3f}")
            assert abs(rm["mach"] - 0.657) < 0.005
            vs = payload(await p("stall_speed", {"mass_kg": 2282, "wing_area_m2": 21.87, "cl_max": 1.05}))
            print(f"Strizh landing Vs {vs['stall_km_h']:.1f} km/h")
            wl = payload(await p("wing_loading", {"mass_kg": 0.218, "wing_area_m2": 0.0854, "lang": "en"}))
            print("1:16 model loading:", {k: round(v, 2) if isinstance(v, float) else v for k, v in wl.items()})
            fr = payload(await p("froude_model", {"scale": 16, "mass_kg": 2699.465, "speed_m_s": 55, "iyy": 13508.45, "rho_model": 1.17}))
            print(f"Froude model: {fr['model_mass_kg']*1000:.0f} g, V {fr['model_speed_km_h']:.1f} km/h, Iyy {fr['model_iyy_kg_m2']:.5f}")
            assert abs(fr["model_mass_kg"] - 0.6291) < 0.001 and abs(fr["model_iyy_kg_m2"] - 0.01230) < 0.0001
            ch = payload(await p("get_changelog", {"lang": "en"}))
            print("changelog:", ch["version"], [e["version"] for e in ch["changelog"]])
            assert ch["version"] == CAT["version"] and ch["changelog"][-1]["version"] == "0.1.0"
            wig = payload(await p("find_workflows", {"aircraft": "wig"}))
            print("wig workflows:", [w["id"] for w in wig["workflows"]])
            assert "wig" in [w["id"] for w in wig["workflows"]]
            hy = payload(await p("search_tools", {"aircraft": "hydrofoil", "lang": "en"}))
            print("hydrofoil tools:", [t["id"] for t in hy["tools"]])
            cav = payload(await p("cavitation", {"speed_m_s": 20.58, "depth_m": 0.5, "cp_min": -0.6, "water_temp_c": 28}))
            print(f"cavitation @40 kn, 0.5 m, Cpmin -0.6: sigma {cav['cavitation_number']:.3f}, cavitates {cav['cavitates']}, inception {cav['inception_speed_kn']:.1f} kn")
            assert 0.45 < cav["cavitation_number"] < 0.5 and cav["cavitates"] is True
            ch1 = payload(await p("parachute_descent", {"mass_kg": 1.0, "diameter_m": 1.0, "target_speed_m_s": 5.0, "lang": "en"}))
            print(f"parachute 1 kg, flat circular D0 1 m: {ch1['descent_m_s']:.2f} m/s, D0 for 5 m/s {ch1['needed_diameter_m']:.3f} m")
            assert abs(ch1["descent_m_s"] - 5.129) < 0.01 and abs(ch1["needed_diameter_m"] - 1.026) < 0.002
            assert ch1["descent_range_m_s"][0] < ch1["descent_m_s"] < ch1["descent_range_m_s"][1]
            bad = await p("parachute_descent", {"mass_kg": 1.0})
            assert getattr(bad, "isError", False) or getattr(bad, "is_error", False), bad
            va = payload(await p("get_validation", {"tool_id": "autowing", "quantity": "CL", "lang": "en"}))
            print("validation autowing CL:", [(x["at"], x["diff_pct"]) for x in va["rows"][0]["points"]])
            assert va["count"] == 1 and len(va["rows"][0]["points"]) == 4 and va["rows"][0]["points"][1]["direction"] == "over"
            assert "calculation.yml" in va["how_to_add"]
            aw = payload(await p("get_tool", {"tool_id": "autowing"}))
            assert aw["validation"] and aw["validation"][0]["id"].startswith("ombor2023")
            hc = payload(await p("how_to_contribute", {"lang": "en"}))
            assert hc["links"]["repo"].startswith("https://github.com/") and hc["license"]["data"] == "CC-BY-4.0"
            res = await s.list_resources()
            assert any(str(x.uri) == "aviateka://catalog" for x in res.resources)
            body = await s.read_resource("aviateka://catalog")
            assert len(json.loads(body.contents[0].text)["tools"]) == len(CAT["tools"])
            pr = await s.get_prompt("plan_design", {"aircraft_type": "racer", "goal": "минимальное время круга"})
            assert "find_workflows" in pr.messages[0].content.text
            bad = await s.call_tool("atmosphere", {"altitude_m": 50000})
            assert getattr(bad, "isError", False) or getattr(bad, "is_error", False); print("error text:", bad.content[0].text)
            print("ALL CHECKS PASSED")


asyncio.run(main())
