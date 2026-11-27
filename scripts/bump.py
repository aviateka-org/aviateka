"""Поднять версию и записать её в журнал одной командой.
Bump the version and log it in one command.

    python scripts/bump.py --ru "Что изменилось" --en "What changed"            # PATCH: 0.5.6 → 0.5.7
    python scripts/bump.py --part minor --ru "..." --en "..."                   # MINOR: 0.5.6 → 0.6.0
    python scripts/bump.py --part major --ru "..." --en "..."                   # MAJOR: 0.5.6 → 1.0.0

Что делает / what it does:
- добавляет запись сверху в data/changelog.yaml с сегодняшней датой (UTC);
- ставит новый номер в pyproject.toml, server.json (сервер и пакет) и CITATION.cff (и дату выпуска);
- печатает новый номер.
После слияния в main release.yml сам выпустит эту версию: PyPI, каталог MCP, релиз GitHub.
After merging into main, release.yml releases this version by itself."""
import datetime, json, os, re, sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def q(text):
    """YAML-строка в одинарных кавычках / single-quoted YAML string."""
    return "'" + text.replace("'", "''") + "'"


def main():
    ru, en = arg("--ru"), arg("--en")
    part = arg("--part", "patch")
    if not ru or not en or part not in ("patch", "minor", "major"):
        print(__doc__)
        sys.exit(2)
    today = arg("--date", datetime.datetime.now(datetime.timezone.utc).date().isoformat())

    p = os.path.join(ROOT, "data", "changelog.yaml")
    text = open(p, encoding="utf-8").read()
    old = yaml.safe_load(text)[0]["version"]
    a, b, c = map(int, old.split("."))
    new = {"patch": f"{a}.{b}.{c + 1}", "minor": f"{a}.{b + 1}.0", "major": f"{a + 1}.0.0"}[part]

    entry = f"- version: {new}\n  date: {q(today)}\n  changes:\n  - ru: {q(ru)}\n    en: {q(en)}\n"
    i = text.index("\n- version:") + 1 if "\n- version:" in text else (0 if text.startswith("- version:") else len(text))
    open(p, "w", encoding="utf-8").write(text[:i] + entry + text[i:])

    pp = os.path.join(ROOT, "pyproject.toml")
    s = open(pp, encoding="utf-8").read()
    s, n = re.subn(r'^version = "[^"]*"', f'version = "{new}"', s, count=1, flags=re.M)
    assert n == 1, "pyproject.toml: нет строки version / no version line"
    open(pp, "w", encoding="utf-8").write(s)

    sj = os.path.join(ROOT, "server.json")
    d = json.load(open(sj, encoding="utf-8"))
    d["version"] = new
    for pkg in d.get("packages", []):
        pkg["version"] = new
    open(sj, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")

    cf = os.path.join(ROOT, "CITATION.cff")
    if os.path.exists(cf):
        s = open(cf, encoding="utf-8").read()
        s = re.sub(r'^version: "[^"]*"', f'version: "{new}"', s, count=1, flags=re.M)
        s = re.sub(r'^date-released: "[^"]*"', f'date-released: "{today}"', s, count=1, flags=re.M)
        open(cf, "w", encoding="utf-8").write(s)

    print(new)


if __name__ == "__main__":
    main()
