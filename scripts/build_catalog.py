"""Собирает каталог Авиатеки из файлов data/ в один catalog.json и проверяет его.
Builds the Aviateka catalog from data/ into one catalog.json and checks it.

    python scripts/build_catalog.py           # собрать / build
    python scripts/build_catalog.py --check   # только проверить, ничего не писать / check only, write nothing

Ошибки печатаются по-русски и по-английски с именем файла. Errors name the file."""
import datetime, glob, json, os, sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT_JSON = os.path.join(ROOT, "aviateka_mcp", "catalog.json")
OUT_CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")

errors = []
BROKEN = object()          # a file that failed to parse; already reported
REQUIRED = ["id", "name", "url", "org", "disciplines", "map", "fidelity", "stages", "aircraft", "summary", "use"]


def err(where, ru, en):
    errors.append(f"{where}: {ru} / {en}")


def plain(obj):
    """YAML turns 2026-11-26 into a date; the catalog keeps dates as text."""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()[:10]
    if isinstance(obj, dict):
        return {k: plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [plain(v) for v in obj]
    return obj


def load(rel):
    path = os.path.join(DATA, rel)
    try:
        with open(path, encoding="utf-8") as f:
            return plain(yaml.safe_load(f))
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        n = mark.line + 1 if mark else "?"
        err(os.path.relpath(path, ROOT), f"строка {n}: файл не читается как YAML — проверьте кавычки и двоеточия", f"line {n}: not valid YAML — check quotes and colons")
        return BROKEN


def schema_check(obj, schema_name, where):
    try:
        import jsonschema
    except ImportError:
        return False
    with open(os.path.join(ROOT, "schema", schema_name), encoding="utf-8") as f:
        schema = json.load(f)
    for e in sorted(jsonschema.Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path)):
        path = "/".join(str(p) for p in e.path) or "(root)"
        err(where, f"поле {path}: {e.message}", f"field {path}: {e.message}")
    return True


def changelog_md(meta, changelog):
    out = ["# Авиатека / Aviateka — журнал изменений / changelog", "", meta["versioning"]["ru"], "", meta["versioning"]["en"], ""]
    for e in changelog:
        out += [f"## {e['version']} — {e['date']}", ""]
        out += [f"- {c['ru']}" for c in e["changes"]] + [""] + [f"- {c['en']}" for c in e["changes"]] + [""]
    return "\n".join(out)


def build():
    meta = load("meta.yaml")
    tax = load("taxonomy.yaml")
    workflows = load("workflows.yaml")
    gaps = load("gaps.yaml")
    benchmarks = load("benchmarks.yaml")
    glossary = load("glossary.yaml")
    changelog = load("changelog.yaml")
    validation = load("validation.yaml") or []
    classifier = load("classifier.yaml")
    cases = [load(os.path.relpath(p, DATA)) for p in sorted(glob.glob(os.path.join(DATA, "cases", "*.yaml")))]
    if errors or any(x is BROKEN for x in [meta, tax, workflows, gaps, benchmarks, glossary, changelog, validation, classifier] + cases):
        return None, None, None, False

    D = [d["id"] for d in tax["disciplines"]]
    F = [f["id"] for f in tax["fidelity"]]
    S = {s["id"] for s in tax["stages"]}
    A = {a["id"] for a in tax["aircraft"]}

    tools, validated = [], False
    for path in sorted(glob.glob(os.path.join(DATA, "tools", "*.yaml"))):
        rel = os.path.relpath(path, ROOT)
        t = load(os.path.relpath(path, DATA))
        if t is BROKEN:
            continue
        if not isinstance(t, dict):
            err(rel, "файл пуст или это не словарь", "file is empty or not a mapping")
            continue
        before = len(errors)
        validated = schema_check(t, "tool.schema.json", rel) or validated
        missing = [k for k in REQUIRED if k not in t]
        if missing and len(errors) == before:
            err(rel, f"нет обязательных полей: {missing}", f"missing required fields: {missing}")
        if len(errors) > before:
            continue
        stem = os.path.splitext(os.path.basename(path))[0]
        if t.get("id") != stem:
            err(rel, f"id «{t.get('id')}» должен совпадать с именем файла «{stem}»", f"id '{t.get('id')}' must match the file name '{stem}'")
        for k in ("disciplines",):
            for v in t.get(k, []):
                if v not in D:
                    err(rel, f"неизвестная дисциплина {v}", f"unknown discipline {v}")
        for v in t.get("aircraft", []):
            if v not in A:
                err(rel, f"неизвестный тип аппарата {v}", f"unknown aircraft type {v}")
        m = t.get("map") or ["", ""]
        if m[0] not in D or m[1] not in F:
            err(rel, f"клетка карты {m} не найдена", f"chart cell {m} not found")
        elif m[0] not in t.get("disciplines", []):
            err(rel, "дисциплина клетки карты должна быть среди disciplines", "the chart-cell discipline must be listed in disciplines")
        t.setdefault("sources", [t.get("url")])
        for k in ("last_commit", "license", "code", "caveat", "status"):
            t.setdefault(k, None)
        tools.append(t)

    ids = [t["id"] for t in tools]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        err("data/tools", f"повторяются id: {sorted(dup)}", f"duplicate ids: {sorted(dup)}")
    ids = set(ids)

    as_of = datetime.date.fromisoformat(meta["as_of"])
    for t in tools:
        if t["status"] is None:
            if t["last_commit"]:
                age = (as_of - datetime.date.fromisoformat(t["last_commit"])).days
                t["status"] = "active" if age <= meta["stale_days"] else "stale"
            else:
                t["status"] = "unknown"
    tools.sort(key=lambda t: (D.index(t["map"][0]) if t["map"][0] in D else 99, F.index(t["map"][1]) if t["map"][1] in F else 99, t["name"].lower()))

    for rel, items in (("data/workflows.yaml", workflows), ("data/gaps.yaml", gaps["gaps"]), ("data/glossary.yaml", glossary)):
        got = [x.get("id") for x in items]
        dup = sorted({i for i in got if got.count(i) > 1})
        if dup:
            err(rel, f"повторяются id: {dup}", f"duplicate ids: {dup}")
    for w in workflows:
        where = f"data/workflows.yaml [{w.get('id')}]"
        for s in w.get("steps", []):
            if s["tool"] not in ids:
                err(where, f"нет инструмента {s['tool']}", f"no tool {s['tool']}")
        if not set(w.get("aircraft", [])) <= A or w.get("stage") not in S:
            err(where, "неизвестный тип аппарата или этап", "unknown aircraft type or stage")
    for c in cases:
        for b in c.get("backlog", []):
            if b["tool"] not in ids:
                err(f"data/cases [{c.get('id')}]", f"нет инструмента {b['tool']}", f"no tool {b['tool']}")
    vids = set()
    for v in validation:
        where = f"data/validation.yaml [{v.get('id')}]"
        schema_check(v, "validation.schema.json", where)
        if v.get("id") in vids:
            err(where, "повтор id", "duplicate id")
        vids.add(v.get("id"))
        if v.get("tool") is None and not v.get("tool_name"):
            err(where, "нужно tool или tool_name", "tool or tool_name is required")
        if v.get("tool") is not None and v["tool"] not in ids:
            err(where, f"нет инструмента {v['tool']}", f"no tool {v['tool']}")

    vs = []
    for e in changelog:
        try:
            vs.append(tuple(map(int, e["version"].split("."))))
        except Exception:
            err("data/changelog.yaml", f"плохой номер версии {e.get('version')}", f"bad version {e.get('version')}")
    if vs != sorted(vs, reverse=True) or len(set(vs)) != len(vs):
        err("data/changelog.yaml", "версии должны идти сверху вниз от новой к старой и не повторяться", "versions must be newest-first and unique")

    classifier = build_classifier(classifier, tools, workflows, A)

    cat = {
        "name": meta["name"], "tagline": meta["tagline"],
        "version": changelog[0]["version"], "as_of": meta["as_of"],
        "repo": meta["repo"], "pypi_published": bool(meta.get("pypi_published")),
        "site": {k: (meta.get("site") or {}).get(k) for k in ("google_site_verification", "goatcounter")},
        "license": {"code": meta["license_code"], "data": meta["license_data"]},
        "versioning": meta["versioning"], "changelog": changelog, "method": meta["method"],
        "statuses": meta["statuses"],
        "disciplines": tax["disciplines"], "fidelity": tax["fidelity"], "stages": tax["stages"], "aircraft": tax["aircraft"],
        "tools": tools, "workflows": workflows,
        "gaps": gaps["gaps"], "gap_marks": meta["gap_marks"], "out_of_scope": gaps["out_of_scope"],
        "benchmarks": benchmarks, "glossary": glossary, "cases": cases,
        "validation": validation, "classifier": classifier,
    }
    return cat, meta, changelog, validated


def build_classifier(cl, tools, workflows, types):
    """Checks the classifier and adds coverage to every leaf: tools and workflows tagged with its types."""
    rel = "data/classifier.yaml"
    seen = set()
    total = {"covered": 0, "partial": 0, "none": 0}
    for b in cl.get("branches", []):
        for leaf in b.get("leaves", []):
            if leaf["id"] in seen:
                err(rel, f"повторяется лист {leaf['id']}", f"duplicate leaf {leaf['id']}")
            seen.add(leaf["id"])
            lt = set(leaf.get("types") or [])
            for t in lt - types:
                err(rel, f"лист {leaf['id']}: неизвестный тип {t}", f"leaf {leaf['id']}: unknown aircraft type {t}")
            nt = sum(1 for t in tools if lt & set(t["aircraft"]))
            nw = sum(1 for w in workflows if lt & set(w["aircraft"]))
            status = "none" if not lt else ("covered" if nt >= 20 and nw >= 5 else "partial")
            leaf["coverage"] = {"tools": nt, "workflows": nw, "status": status}
            total[status] += 1
    cl["summary"] = {"branches": len(cl.get("branches", [])), "leaves": len(seen), **total}
    return cl


def version_files(v):
    """The version in changelog.yaml must match pyproject.toml, server.json and CITATION.cff."""
    import re
    def read(name):
        p = os.path.join(ROOT, name)
        return open(p, encoding="utf-8").read() if os.path.exists(p) else None
    pp = read("pyproject.toml")
    if pp is not None and not re.search(r'^version = "' + re.escape(v) + '"', pp, flags=re.M):
        err("pyproject.toml", f"версия должна быть {v}", f"version must be {v}")
    sj = read("server.json")
    if sj is not None:
        d = json.loads(sj)
        if d.get("version") != v or any(p.get("version") != v for p in d.get("packages", [])):
            err("server.json", f"версия должна быть {v}", f"version must be {v}")
    cf = read("CITATION.cff")
    if cf is not None and f'version: "{v}"' not in cf:
        err("CITATION.cff", f"версия должна быть {v}", f"version must be {v}")


def main():
    check = "--check" in sys.argv
    cat, meta, changelog, validated = build()
    if cat is None or errors:
        print("Найдены ошибки / errors found:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    if not validated:
        print("ВНИМАНИЕ: пакет jsonschema не установлен, проверка по схеме пропущена / WARNING: jsonschema not installed, schema check skipped")
    md = changelog_md(meta, changelog)
    if check:
        cur = open(OUT_CHANGELOG, encoding="utf-8").read() if os.path.exists(OUT_CHANGELOG) else ""
        if cur != md:
            err("CHANGELOG.md", "устарел: запустите python scripts/build_catalog.py", "out of date: run python scripts/build_catalog.py")
        version_files(cat["version"])
    if errors:
        print("Найдены ошибки / errors found:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    st = {}
    for t in cat["tools"]:
        st[t["status"]] = st.get(t["status"], 0) + 1
    print(f"version {cat['version']}; tools {len(cat['tools'])}, workflows {len(cat['workflows'])}, gaps {len(cat['gaps'])}, "
          f"benchmarks {len(cat['benchmarks'])}, glossary {len(cat['glossary'])}, validation {len(cat['validation'])}; status {st}")
    if check:
        print("OK: данные в порядке / data is valid")
        return
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)
    with open(OUT_CHANGELOG, "w", encoding="utf-8") as f:
        f.write(md)
    print("written", os.path.relpath(OUT_JSON, ROOT), os.path.getsize(OUT_JSON), "bytes; CHANGELOG.md")


if __name__ == "__main__":
    main()
