"""Собирает сайт в web/dist из aviateka_mcp/catalog.json:
  index.html   — страница «о проекте» / the about page (landing.html)
  catalog.html — каталог / the catalog (template.html)
  data.json    — весь каталог одним файлом / the whole catalog as one file
  tools/       — по странице на инструмент и общий список (для поиска и ИИ) / a page per tool and a list (for search and AI)
  sitemap.xml, llms.txt, llms-full.txt — карта сайта и путеводители для ИИ / sitemap and AI guides
Builds the site from the compiled catalog. Run scripts/build_catalog.py first."""
import json, os
import static_pages

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

# Метаданные и обычные ссылки, видимые без скриптов / metadata and plain links visible without scripts
tag = cat["tagline"]
landing = landing.replace("</head>", static_pages.head_extra(
    cat, "index", "Авиатека — " + tag["ru"], tag["ru"] + ". " + tag["en"] + ".", "",
    static_pages.dataset_jsonld(cat)) + "</head>", 1)
catalog = catalog.replace("</head>", static_pages.head_extra(
    cat, "catalog", "Каталог / Catalog | Авиатека",
    "Карта открытых инструментов проектирования: самолёты, экранопланы, суда на подводных крыльях. "
    "Chart of open design tools: aircraft, WIG craft, hydrofoils.", "catalog.html") + "</head>", 1)
plain = ('<nav class="wrap" style="padding-top:12px;font-size:15px">'
         '<a href="tools/index.html">Все инструменты списком / All tools as a list</a> · '
         '<a href="data.json">data.json</a> · <a href="llms.txt">llms.txt</a> · '
         f'<a href="https://github.com/{cat["repo"]}">GitHub</a></nav></footer>')
landing = landing.replace("</footer>", plain, 1)
catalog = catalog.replace("</footer>", plain, 1)

for name, text in (("catalog.html", catalog), ("index.html", landing)):
    open(os.path.join(dist, name), "w", encoding="utf-8").write(text)
json.dump(cat, open(os.path.join(dist, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
n = static_pages.build(cat, dist)
print("index.html", len(landing.encode()), "· catalog.html", len(catalog.encode()), "· data.json", os.path.getsize(os.path.join(dist, "data.json")),
      f"· static pages {n} · sitemap.xml · llms.txt · llms-full.txt")
