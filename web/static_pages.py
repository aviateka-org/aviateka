"""Статические страницы для поиска и ИИ / Static pages for search engines and AI.

Каталог рисуется скриптом в браузере, а поисковые роботы ИИ скрипты не запускают.
Поэтому для каждого инструмента собирается обычная HTML-страница, плюс список всех
инструментов, карта сайта (sitemap.xml) и краткие путеводители для ИИ (llms.txt, llms-full.txt).

The catalog is drawn by a script in the browser, and AI crawlers do not run scripts.
So every tool also gets a plain HTML page, plus a list of all tools, a sitemap and
short guides for AI agents (llms.txt, llms-full.txt)."""
import html
import json
import os

E = html.escape


def site_base(cat):
    owner, name = cat["repo"].split("/")
    return f"https://{owner}.github.io/{name}/"


def head_extra(cat, page, title, description, path, jsonld=None):
    """Метаданные для поисковиков и соцсетей / metadata for search engines and link previews."""
    base = site_base(cat)
    site = cat.get("site") or {}
    out = [
        f'<link rel="canonical" href="{E(base + path)}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Авиатека / Aviateka">',
        f'<meta property="og:title" content="{E(title)}">',
        f'<meta property="og:description" content="{E(description)}">',
        f'<meta property="og:url" content="{E(base + path)}">',
        '<meta property="og:locale" content="ru_RU">',
        '<meta property="og:locale:alternate" content="en_US">',
        '<meta name="twitter:card" content="summary">',
    ]
    if page != "index":
        out.insert(0, f'<meta name="description" content="{E(description)}">')
    if site.get("google_site_verification"):
        out.append(f'<meta name="google-site-verification" content="{E(site["google_site_verification"])}">')
    if site.get("goatcounter"):
        out.append(f'<script data-goatcounter="https://{E(site["goatcounter"])}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>')
    if jsonld:
        out.append('<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n".join(out) + "\n"


def dataset_jsonld(cat):
    base = site_base(cat)
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "Авиатека / Aviateka: каталог открытых инструментов проектирования летательных аппаратов",
        "alternateName": "Aviateka: catalog of open aircraft design tools",
        "description": (cat["tagline"]["ru"] + ". " + cat["tagline"]["en"] + ". "
                        "Карточки программ с уровнем точности, этапом проекта, статусом и источниками; "
                        "рабочие цепочки, пробелы, эталонные цифры и таблица сверки расчётов с опытом. "
                        "Tool cards with fidelity level, design stage, status and sources; workflows, gaps, "
                        "reference numbers and a validation matrix comparing codes with measurements."),
        "url": base,
        "sameAs": f"https://github.com/{cat['repo']}",
        "version": cat["version"],
        "dateModified": cat["as_of"],
        "inLanguage": ["ru", "en"],
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "keywords": ["aircraft design", "conceptual design", "open source", "vortex lattice", "WIG craft",
                     "ekranoplan", "hydrofoil", "MCP", "проектирование самолётов", "экраноплан",
                     "подводные крылья", "открытые программы"],
        "creator": {"@type": "Organization", "name": "Aviateka contributors", "url": f"https://github.com/{cat['repo']}"},
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": base + "data.json"}],
    }


CSS = """:root{color-scheme:light dark;--bg:light-dark(#fbfbf2,#0d1c24);--ink:light-dark(#13242e,#e6eee8);--sea:light-dark(#bfe3ee,#123341);--line:light-dark(#c9d3cf,#2a4351);--muted:light-dark(#4a5d66,#a9bcc2);--route:light-dark(#d6127e,#ff5fb0)}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Overpass,system-ui,sans-serif}
a{color:inherit;text-underline-offset:3px}a:hover{color:var(--route)}
header,main,footer{max-width:860px;margin:0 auto;padding:16px max(4vw,16px)}
header{display:flex;gap:16px;flex-wrap:wrap;align-items:baseline;border-bottom:1px solid var(--line)}
header .brand{font-weight:800;font-size:20px;text-decoration:none;margin-right:auto}
h1{font-size:clamp(28px,4vw,40px);line-height:1.1;margin:24px 0 8px;letter-spacing:-.02em}
h2{font-size:22px;margin:32px 0 8px}h3{font-size:18px;margin:24px 0 6px}
.lead{font-size:19px;margin:0 0 16px}.muted{color:var(--muted)}
dl{display:grid;grid-template-columns:minmax(120px,190px) 1fr;gap:6px 16px;margin:12px 0}dt{color:var(--muted)}dd{margin:0}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:15px}td,th{border-top:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
ul{padding-left:20px}li{margin:4px 0}main{overflow-wrap:anywhere}table{table-layout:fixed}td:last-child{width:2.5em}
section+section{border-top:2px solid var(--line);margin-top:32px}
footer{border-top:1px solid var(--line);font-size:15px;color:var(--muted)}
@media(max-width:560px){dl{grid-template-columns:1fr}dt{margin-top:8px}}"""


def page(cat, path, title, description, body, depth):
    up = "../" * depth
    extra = head_extra(cat, "static", title, description, path)
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Overpass:wght@400;600;800&display=swap" rel="stylesheet">
{extra}<style>{CSS}</style>
</head>
<body>
<header><a class="brand" href="{up}index.html">Авиатека</a><a href="{up}catalog.html">Каталог / Catalog</a><a href="{up}tools/index.html">Все инструменты / All tools</a></header>
<main>
{body}
</main>
<footer><p>Авиатека {E(cat['version'])} · данные / data CC BY 4.0 · код / code MIT · <a href="https://github.com/{E(cat['repo'])}">GitHub</a> · <a href="{up}llms.txt">llms.txt</a> · <a href="{up}data.json">data.json</a></p></footer>
</body>
</html>
"""


def build(cat, dist):
    base = site_base(cat)
    repo = f"https://github.com/{cat['repo']}"
    names = {}
    for key in ("disciplines", "fidelity", "stages", "aircraft"):
        names[key] = {x["id"]: x["name"] for x in cat[key]}
    st = cat["statuses"]
    by_tool_val = {}
    for v in cat.get("validation", []):
        by_tool_val.setdefault(v["tool"], []).append(v)
    by_tool_wf = {}
    for w in cat["workflows"]:
        for s in w["steps"]:
            by_tool_wf.setdefault(s["tool"], []).append(w)
    os.makedirs(os.path.join(dist, "tools"), exist_ok=True)

    def listnames(key, ids, lang):
        return ", ".join(names[key][i][lang] for i in ids if i in names[key]) or "—"

    def fix_link(t):
        from urllib.parse import quote
        return f"{repo}/issues/new?template=correction.yml&tool={quote(t['id'])}&title={quote('[правка / fix] ' + t['name'])}"

    pages = []
    for t in cat["tools"]:
        sec = []
        for lang, L in (("ru", {"use": "Для чего", "cav": "Оговорки", "disc": "Раздел", "fid": "Уровень точности",
                                "stg": "Этапы проекта", "air": "Аппараты", "status": "Статус", "commit": "последний коммит",
                                "lic": "Лицензия", "code": "Язык", "org": "Разработчик", "links": "Ссылки",
                                "site": "Сайт или репозиторий", "src": "Источники", "val": "Сверка с опытом",
                                "wf": "Входит в рабочие цепочки", "none": "не указана", "fix": "Предложить правку карточки"}),
                        ("en", {"use": "Use", "cav": "Caveats", "disc": "Discipline", "fid": "Fidelity level",
                                "stg": "Design stages", "air": "Aircraft", "status": "Status", "commit": "last commit",
                                "lic": "Licence", "code": "Language", "org": "Developer", "links": "Links",
                                "site": "Website or repository", "src": "Sources", "val": "Validation against tests",
                                "wf": "Used in workflows", "none": "not stated", "fix": "Suggest a correction to this card"})):
            status = st.get(t["status"], {}).get(lang, t["status"])
            if t.get("last_commit"):
                status += f" ({L['commit']} {t['last_commit']})"
            rows = [(L["use"], E(t["use"][lang]))]
            if t.get("caveat"):
                rows.append((L["cav"], E(t["caveat"][lang])))
            rows += [(L["disc"], E(listnames("disciplines", t["disciplines"], lang))),
                     (L["fid"], E(listnames("fidelity", t["fidelity"], lang))),
                     (L["stg"], E(listnames("stages", t["stages"], lang))),
                     (L["air"], E(listnames("aircraft", t["aircraft"], lang))),
                     (L["status"], E(status)),
                     (L["lic"], E(t.get("license") or L["none"])),
                     (L["code"], E(t.get("code") or "—")),
                     (L["org"], E(t.get("org") or "—"))]
            dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
            srcs = "".join(f'<li><a href="{E(s)}">{E(s)}</a></li>' for s in t.get("sources", []))
            h = "h1" if lang == "ru" else "h2"
            s = [f'<section lang="{lang}">', f"<{h}>{E(t['name'])}</{h}>", f'<p class="lead">{E(t["summary"][lang])}</p>', f"<dl>{dl}</dl>",
                 f"<h3>{L['links']}</h3><ul><li>{L['site']}: <a href=\"{E(t['url'])}\">{E(t['url'])}</a></li></ul>"]
            if srcs:
                s.append(f"<h3>{L['src']}</h3><ul>{srcs}</ul>")
            vals = by_tool_val.get(t["id"], [])
            if vals:
                s.append(f"<h3>{L['val']}</h3><table>" + "".join(
                    f'<tr><td>{E(v["case"][lang])}</td><td>{E(v["summary"][lang])}</td><td><a href="{E(v["source"])}">↗</a></td></tr>' for v in vals) + "</table>")
            wfs = by_tool_wf.get(t["id"], [])
            if wfs:
                s.append(f"<h3>{L['wf']}</h3><ul>" + "".join(f"<li>{E(w['title'][lang])}: {E(w['goal'][lang])}</li>" for w in wfs) + "</ul>")
            s.append(f'<p><a href="{E(fix_link(t))}">{L["fix"]}</a></p></section>')
            sec.append("\n".join(s))
        title = f"{t['name']} — {t['summary']['ru']} | Авиатека"
        desc = f"{t['summary']['ru']} {t['summary']['en']}"
        path = f"tools/{t['id']}.html"
        open(os.path.join(dist, path), "w", encoding="utf-8").write(page(cat, path, title, desc, "\n".join(sec), 1))
        pages.append(path)

    # список всех инструментов / list of all tools
    groups = []
    for d in cat["disciplines"]:
        ts = sorted((t for t in cat["tools"] if t["map"][0] == d["id"]), key=lambda t: t["name"].lower())
        if not ts:
            continue
        items = "".join(
            f'<li><a href="{E(t["id"])}.html">{E(t["name"])}</a> — {E(t["summary"]["ru"])} <span class="muted" lang="en">{E(t["summary"]["en"])}</span> '
            f'<span class="muted">· {E(st.get(t["status"], {}).get("ru", t["status"]))}</span></li>' for t in ts)
        groups.append(f'<h2>{E(d["name"]["ru"])} <span class="muted" lang="en">/ {E(d["name"]["en"])}</span></h2><ul>{items}</ul>')
    body = (f'<h1>Все инструменты <span class="muted" lang="en">/ All tools</span></h1>'
            f'<p class="lead">{E(cat["tagline"]["ru"])}. <span lang="en">{E(cat["tagline"]["en"])}.</span></p>'
            f'<p>{len(cat["tools"])} карточек. Интерактивная карта, поиск и фильтры — в <a href="../catalog.html">каталоге</a>. '
            f'<span lang="en">{len(cat["tools"])} cards. The interactive chart, search and filters are in the <a href="../catalog.html">catalog</a>.</span></p>'
            + "".join(groups))
    open(os.path.join(dist, "tools/index.html"), "w", encoding="utf-8").write(
        page(cat, "tools/index.html", "Все инструменты / All tools | Авиатека",
             f"{len(cat['tools'])} открытых программ для проектирования самолётов, экранопланов и судов на подводных крыльях. "
             f"{len(cat['tools'])} open tools for designing aircraft, WIG craft and hydrofoils.", body, 1))
    pages.append("tools/index.html")

    # карта сайта / sitemap
    urls = ["", "catalog.html"] + pages
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{E(base + u)}</loc><lastmod>{cat['as_of']}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    open(os.path.join(dist, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")

    # путеводители для ИИ / guides for AI agents (https://llmstxt.org)
    lt = [f"# Авиатека / Aviateka", "",
          f"> {cat['tagline']['en']}. {cat['tagline']['ru']}. Version {cat['version']}, data as of {cat['as_of']}. "
          f"Data CC BY 4.0, code MIT.", "",
          "Aviateka is an open catalog of design tools for aircraft, WIG craft (ekranoplans) and hydrofoils: what each "
          "program computes, its fidelity level, design stage, whether it is alive, and how well its numbers matched "
          "experiments. It also ships an MCP server so AI assistants can query it: `uvx aviateka-mcp` "
          "(MCP Registry name io.github." + cat["repo"] + ").", "",
          "## Data", "",
          f"- [Whole catalog as JSON]({base}data.json): tools, workflows, gaps, benchmarks, glossary, validation matrix",
          f"- [Full text of every card]({base}llms-full.txt): the same content as Markdown",
          f"- [All tools]({base}tools/index.html): one static page per tool", "",
          "## Contribute", "",
          f"- [Forms: new tool, correction, calculation, topic]({repo}/issues/new/choose)",
          f"- [Repository]({repo})", "",
          "## Tools", ""]
    lt += [f"- [{t['name']}]({base}tools/{t['id']}.html): {t['summary']['en']}" for t in sorted(cat["tools"], key=lambda t: t["name"].lower())]
    open(os.path.join(dist, "llms.txt"), "w", encoding="utf-8").write("\n".join(lt) + "\n")

    full = [f"# Авиатека / Aviateka {cat['version']} ({cat['as_of']})", "", cat["tagline"]["en"] + ". " + cat["tagline"]["ru"] + ".", "",
            "Licence: data CC BY 4.0, code MIT. Source: " + repo, "", "## Tools", ""]
    for t in sorted(cat["tools"], key=lambda t: t["name"].lower()):
        full += [f"### {t['name']}", "",
                 f"- URL: {t['url']}",
                 f"- EN: {t['summary']['en']} Use: {t['use']['en']}" + (f" Caveat: {t['caveat']['en']}" if t.get("caveat") else ""),
                 f"- RU: {t['summary']['ru']} Для чего: {t['use']['ru']}" + (f" Оговорки: {t['caveat']['ru']}" if t.get("caveat") else ""),
                 f"- Discipline: {listnames('disciplines', t['disciplines'], 'en')}; fidelity: {listnames('fidelity', t['fidelity'], 'en')}; "
                 f"stages: {listnames('stages', t['stages'], 'en')}; aircraft: {listnames('aircraft', t['aircraft'], 'en')}",
                 f"- Status: {st.get(t['status'], {}).get('en', t['status'])}" + (f", last commit {t['last_commit']}" if t.get("last_commit") else "")
                 + f"; licence: {t.get('license') or 'not stated'}; language: {t.get('code') or '—'}; developer: {t.get('org') or '—'}",
                 f"- Sources: {', '.join(t.get('sources', []))}", ""]
    full += ["## Workflows", ""]
    for w in cat["workflows"]:
        full += [f"### {w['title']['en']} / {w['title']['ru']}", "", w["goal"]["en"], ""]
        full += [f"{i}. {s['tool']}: {s['what']['en']}" for i, s in enumerate(w["steps"], 1)]
        full += [""]
    full += ["## Validation matrix", ""]
    for v in cat.get("validation", []):
        full += [f"- {v['tool']}: {v['case']['en']}. {v['summary']['en']} Source: {v['source']}"]
    open(os.path.join(dist, "llms-full.txt"), "w", encoding="utf-8").write("\n".join(full) + "\n")
    return len(pages)
