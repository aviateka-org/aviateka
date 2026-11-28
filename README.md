# Авиатека / Aviateka

<!-- mcp-name: io.github.aviateka-org/aviateka -->

[![PyPI](https://img.shields.io/pypi/v/aviateka-mcp?label=PyPI)](https://pypi.org/project/aviateka-mcp/) [![Проверка / Check](https://github.com/aviateka-org/aviateka/actions/workflows/check.yml/badge.svg)](https://github.com/aviateka-org/aviateka/actions/workflows/check.yml) [![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey)](LICENSE-DATA.md) [![Code: MIT](https://img.shields.io/badge/code-MIT-lightgrey)](LICENSE)

**Открытая библиотека инструментов для проектирования летательных аппаратов всех видов: самолётов и винтокрылых, тканевых аппаратов и аэростатов, дирижаблей, гидросамолётов, экранопланов и судов на подводных крыльях, сверхзвуковых и спускаемых аппаратов, гражданских ракет.** Для людей — страница с картой, для ИИ-агентов — MCP-сервер. Данные на русском и английском.

**An open library of design tools for flying craft of every kind: aircraft and rotorcraft, fabric craft and balloons, airships, seaplanes, WIG and hydrofoil craft, high-speed and entry vehicles, civil rockets.** A chart page for people and an MCP server for AI agents. Data in Russian and English.

- О проекте / About: <https://aviateka-org.github.io/aviateka/>
- Каталог / Catalog: <https://aviateka-org.github.io/aviateka/catalog.html>
- Все инструменты списком / All tools as a list: <https://aviateka-org.github.io/aviateka/tools/>
- Для ИИ-агентов / For AI agents: [llms.txt](https://aviateka-org.github.io/aviateka/llms.txt), [data.json](https://aviateka-org.github.io/aviateka/data.json), `uvx aviateka-mcp`
- Как помочь / Contribute: [CONTRIBUTING.md](CONTRIBUTING.md)
- Журнал версий / Changelog: [CHANGELOG.md](CHANGELOG.md)

## Что внутри / What is inside

| Раздел | Section | Где / Where |
|---|---|---|
| Карточки 86 открытых программ: аэродинамика, профили, винты, устойчивость, моделирование полёта, конструкция, аэроупругость, оптимизация, гидродинамика, раскрой ткани | Cards for 86 open tools across aero, airfoils, propulsion, stability, flight simulation, structures, aeroelasticity, MDO, hydrodynamics, fabric patterns | `data/tools/` |
| Рабочие цепочки: с чего начать и чем проверить | Workflows: where to start and how to check | `data/workflows.yaml` |
| Таблица сверки: насколько программы совпали с опытом | Validation matrix: how well codes matched measurements | `data/validation.yaml` |
| Пустые ниши с разметкой «окно» и «запрещено» | Gaps marked "window" or "forbidden" | `data/gaps.yaml` |
| Эталонные цифры, термины, кейс «Стриж» | Reference numbers, glossary, the Strizh case | `data/` |
| Классификатор летательных аппаратов: 9 ветвей, 34 листа, покрытие каталога по каждому, сквозные признаки, деление у ИКАО, FAA, EASA, РФ и ИМО | Craft classifier: 9 branches, 34 leaves, catalog coverage of each, facets, ICAO, FAA, EASA, Russian and IMO splits | `data/classifier.yaml` |
| Порядок разработки малой командой: этапы с воротами, способы проверки, порядок доработки, карточка испытания, 11 стандартов-источников с датой и доступом | Development process for small teams: stages with gates, verification methods, change procedure, test card, 11 source standards with date and access | `data/process.yaml` |
| Калькуляторы: атмосфера, Рейнольдс и Мах, сваливание, нагрузка на крыло, подобие по Фруду, кавитация, спуск на парашюте | Calculators: atmosphere, Reynolds and Mach, stall, wing loading, Froude scaling, cavitation, parachute descent | `aviateka_mcp/calc.py`, `web/calc.js` |

## MCP-сервер / MCP server

```bash
uvx aviateka-mcp            # или / or: pip install aviateka-mcp && aviateka-mcp
aviateka-mcp --http --port 8000
```

Claude Desktop:

```json
{ "mcpServers": { "aviateka": { "command": "uvx", "args": ["aviateka-mcp"] } } }
```

24 инструмента MCP / 24 MCP tools: `search_tools`, `get_tool`, `find_workflows`, `list_gaps`, `list_benchmarks`, `get_validation`, `glossary`, `get_case`, `get_classifier`, `get_process`, `get_taxonomy`, `get_changelog`, `how_to_contribute`, `atmosphere`, `reynolds_mach`, `stall_speed`, `wing_loading`, `froude_model`, `cavitation`, `parachute_descent`, `buoyancy`, `rotor_hover`, `rocket_delta_v`, `entry_heating`. Работает с официальным MCP SDK 1.x и 2.x. / Works with the official MCP SDK 1.x and 2.x.

## Из исходников / From source

```bash
git clone https://github.com/aviateka-org/aviateka && cd aviateka
pip install pyyaml jsonschema -e .
python scripts/build_catalog.py      # data/ → aviateka_mcp/catalog.json
python web/build_page.py             # → web/dist/index.html (о проекте), catalog.html, data.json
python tests/test_mcp.py             # сквозная проверка / end-to-end test
```

## Как это развивается / How it grows

Люди присылают инструменты, исправления и свои расчёты через формы — Git не нужен. Хранители переводят вклад в формат каталога со ссылкой на источник. Раз в неделю робот обновляет даты последних коммитов и проверяет ссылки, а итог присылает запросом на слияние.

People send tools, corrections and their own calculations through forms — no Git needed. Maintainers turn each contribution into catalog format with a source link. Once a week a bot refreshes last-commit dates and checks links, and proposes the result as a pull request.

## Лицензии / Licences

Код — [MIT](LICENSE). Данные — [CC BY 4.0](LICENSE-DATA.md): берите что угодно, только укажите источник.

Code — [MIT](LICENSE). Data — [CC BY 4.0](LICENSE-DATA.md): use anything, just credit the source.

## Как цитировать / How to cite

См. / See [CITATION.cff](CITATION.cff).
