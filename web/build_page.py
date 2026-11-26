"""Собирает сайт в web/dist из aviateka_mcp/catalog.json:
  index.html   — страница «о проекте» / the about page (landing.html)
  catalog.html — каталог / the catalog (template.html)
  data.json    — весь каталог одним файлом / the whole catalog as one file
Builds the site from the compiled catalog. Run scripts/build_catalog.py first."""
import json, os

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(H)
cat = json.load(open(os.path.join(ROOT, "aviateka_mcp", "catalog.json"), encoding="utf-8"))


def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


summary = {
    "version": cat["version"], "as_of": cat["as_of"], "repo": cat["repo"],
    "pypi_published": cat["pypi_published"], "license": cat["license"],
    "latest": cat["changelog"][0],
    "counts": {
        "tools": len(cat["tools"]),
        "active": sum(t["status"] == "active" for t in cat["tools"]),
        "workflows": len(cat["workflows"]), "gaps": len(cat["gaps"]),
        "benchmarks": len(cat["benchmarks"]), "glossary": len(cat["glossary"]),
        "validation": len(cat.get("validation", [])),
    },
}
dist = os.path.join(H, "dist")
os.makedirs(dist, exist_ok=True)
read = lambda n: open(os.path.join(H, n), encoding="utf-8").read()
catalog = read("template.html").replace("__CATALOG__", js(cat)).replace("/*CALC*/", read("calc.js"))
landing = read("landing.html").replace("__SUMMARY__", js(summary))
for name, text in (("catalog.html", catalog), ("index.html", landing)):
    open(os.path.join(dist, name), "w", encoding="utf-8").write(text)
json.dump(cat, open(os.path.join(dist, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("index.html", len(landing.encode()), "· catalog.html", len(catalog.encode()), "· data.json", os.path.getsize(os.path.join(dist, "data.json")))
