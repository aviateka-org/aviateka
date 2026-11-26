"""Свежесть данных: даты последних коммитов, статусы и ссылки.
Data freshness: last-commit dates, statuses and links.

    python scripts/freshness.py                      # только отчёт / report only
    python scripts/freshness.py --write              # записать новые даты в data/ / write new dates into data/
    python scripts/freshness.py --report out.md      # отчёт в файл / report to a file
    python scripts/freshness.py --only xfoil,avl     # только эти карточки / only these cards
    python scripts/freshness.py --no-links           # без проверки ссылок / skip link check

Дата берётся из неглубокого клона основной ветки (git clone --depth 1), токены не нужны.
The date comes from a shallow clone of the default branch; no tokens needed."""
import concurrent.futures as cf
import datetime, glob, os, re, subprocess, sys, tempfile, urllib.error, urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
GIT_HOSTS = ("github.com", "gitlab.com", "codeberg.org")
UA = "aviateka-freshness/1.0 (+https://github.com/aviateka-org/aviateka)"


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def repo_url(url):
    m = re.match(r"https?://(www\.)?([^/]+)/([^/#?]+)/([^/#?]+)", url or "")
    if not m or m.group(2) not in GIT_HOSTS:
        return None
    name = m.group(4)[:-4] if m.group(4).endswith(".git") else m.group(4)
    return f"https://{m.group(2)}/{m.group(3)}/{name}.git"


def last_commit(url):
    with tempfile.TemporaryDirectory() as d:
        try:
            subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none", "--no-checkout", "-q", url, d],
                           check=True, capture_output=True, timeout=180, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))
            out = subprocess.run(["git", "-C", d, "log", "-1", "--format=%cs"], check=True, capture_output=True, text=True, timeout=30)
            return out.stdout.strip() or None, None
        except subprocess.CalledProcessError as e:
            return None, (e.stderr.decode(errors="ignore") if isinstance(e.stderr, bytes) else str(e.stderr)).strip().splitlines()[-1:] or ["git error"]
        except Exception as e:
            return None, [str(e)]


def status_for(date, today, stale_days):
    if not date:
        return "unknown"
    return "active" if (today - datetime.date.fromisoformat(date)).days <= stale_days else "stale"


def check_link(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return url, r.status, None
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (403, 405, 501):
                continue
            return url, e.code, None
        except Exception as e:
            if method == "HEAD":
                continue
            return url, None, type(e).__name__
    return url, None, "unknown"


def collect_urls():
    urls = {}
    def add(u, where):
        if isinstance(u, str) and u.startswith("http"):
            urls.setdefault(u, set()).add(where)
    for p in glob.glob(os.path.join(DATA, "tools", "*.yaml")):
        t = yaml.safe_load(open(p, encoding="utf-8"))
        for u in [t.get("url")] + (t.get("sources") or []):
            add(u, f"tools/{t['id']}")
    g = yaml.safe_load(open(os.path.join(DATA, "gaps.yaml"), encoding="utf-8"))
    for x in g["gaps"]:
        for u in x.get("sources", []):
            add(u, f"gaps/{x['id']}")
    for x in yaml.safe_load(open(os.path.join(DATA, "benchmarks.yaml"), encoding="utf-8")):
        add(x.get("source"), f"benchmarks/{x['id']}")
    for x in yaml.safe_load(open(os.path.join(DATA, "validation.yaml"), encoding="utf-8")) or []:
        add(x.get("source"), f"validation/{x['id']}")
    return urls


def main():
    write = "--write" in sys.argv
    only = set(filter(None, (arg("--only") or "").split(",")))
    today = datetime.date.today()
    meta_path = os.path.join(DATA, "meta.yaml")
    meta = yaml.safe_load(open(meta_path, encoding="utf-8"))
    stale_days = meta["stale_days"]

    jobs = {}
    for p in sorted(glob.glob(os.path.join(DATA, "tools", "*.yaml"))):
        t = yaml.safe_load(open(p, encoding="utf-8"))
        if only and t["id"] not in only:
            continue
        r = repo_url(t.get("url"))
        if r:
            jobs[p] = (t, r)

    changed, failed, status_moves = [], [], []
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(last_commit, r): p for p, (t, r) in jobs.items()}
        for f in cf.as_completed(futs):
            p = futs[f]
            t, r = jobs[p]
            date, e = f.result()
            old = str(t.get("last_commit") or "") or None
            if not date:
                failed.append((t["id"], r, (e or ["?"])[0]))
                continue
            if t.get("status") is None:
                s_old = status_for(old, datetime.date.fromisoformat(str(meta["as_of"])), stale_days)
                s_new = status_for(date, today, stale_days)
                if s_old != s_new:
                    status_moves.append((t["id"], s_old, s_new))
            if date != old:
                changed.append((t["id"], old, date))
                if write:
                    text = open(p, encoding="utf-8").read()
                    if re.search(r"^last_commit:.*$", text, flags=re.M):
                        text = re.sub(r"^last_commit:.*$", f"last_commit: '{date}'", text, count=1, flags=re.M)
                    else:
                        text = re.sub(r"^(org:.*)$", rf"\1\nlast_commit: '{date}'", text, count=1, flags=re.M)
                    open(p, "w", encoding="utf-8").write(text)
    if write and not only:
        text = open(meta_path, encoding="utf-8").read()
        text = re.sub(r"^as_of:.*$", f"as_of: '{today.isoformat()}'", text, count=1, flags=re.M)
        open(meta_path, "w", encoding="utf-8").write(text)

    bad_links = []
    if "--no-links" not in sys.argv:
        urls = collect_urls()
        if only:
            urls = {u: w for u, w in urls.items() if any(x.split("/")[-1] in only for x in w)}
        with cf.ThreadPoolExecutor(8) as ex:
            for url, code, e in ex.map(check_link, urls):
                if code is not None and code < 400:
                    continue
                kind = ("битая / broken" if code in (404, 410) else
                        "закрыта для робота, проверить вручную / blocks robots, check by hand" if code in (401, 403, 429) else
                        f"не открылась / did not open ({code or e})")
                bad_links.append((url, kind, ", ".join(sorted(urls[url]))))

    lines = [f"# Свежесть данных / Data freshness — {today.isoformat()}", "",
             f"Проверено репозиториев / repositories checked: {len(jobs)}; новые даты / new dates: {len(changed)}; "
             f"не удалось / failed: {len(failed)}; проблемные ссылки / link problems: {len(bad_links)}.", ""]
    if changed:
        lines += ["## Новые даты коммитов / New commit dates", "", "| Инструмент / Tool | Было / Was | Стало / Now |", "|---|---|---|"]
        lines += [f"| {i} | {o or '—'} | {n} |" for i, o, n in sorted(changed)] + [""]
    if status_moves:
        lines += ["## Смена статуса / Status changes", "", "| Инструмент / Tool | Было / Was | Стало / Now |", "|---|---|---|"]
        lines += [f"| {i} | {o} | {n} |" for i, o, n in sorted(status_moves)] + [""]
    if failed:
        lines += ["## Не удалось прочитать репозиторий / Could not read repository", ""]
        lines += [f"- {i}: {r} — {e}" for i, r, e in sorted(failed)] + [""]
    if bad_links:
        lines += ["## Ссылки / Links", "", "| Ссылка / Link | Что / What | Где / Where |", "|---|---|---|"]
        lines += [f"| {u} | {k} | {w} |" for u, k, w in sorted(bad_links)] + [""]
    lines += ["Ссылки, закрытые для робота, не обязательно битые: их стоит открыть руками.",
              "Links that block robots are not necessarily broken: open them by hand."]
    report = "\n".join(lines) + "\n"
    if arg("--report"):
        open(arg("--report"), "w", encoding="utf-8").write(report)
    print(report)


if __name__ == "__main__":
    main()
