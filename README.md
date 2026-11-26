# Авиатека / Aviateka

<!-- mcp-name: io.github.aviateka-org/aviateka -->

**Открытая библиотека инструментов для проектирования летательных аппаратов, экранопланов и судов на подводных крыльях.** Для людей — страница с картой, для ИИ-агентов — MCP-сервер. Данные на русском и английском.

**An open library of design tools for aircraft, WIG craft and hydrofoil craft.** A chart page for people and an MCP server for AI agents. Data in Russian and English.

- О проекте / About: <https://aviateka-org.github.io/aviateka/>
- Каталог / Catalog: <https://aviateka-org.github.io/aviateka/catalog.html>
- Как помочь / Contribute: [CONTRIBUTING.md](CONTRIBUTING.md)
- Журнал версий / Changelog: [CHANGELOG.md](CHANGELOG.md)

## Что внутри / What is inside

| Раздел | Section | Где / Where |
|---|---|---|
| Карточки 65 открытых программ: аэродинамика, профили, винты, устойчивость, моделирование полёта, конструкция, аэроупругость, оптимизация, гидродинамика | Cards for 65 open tools across aero, airfoils, propulsion, stability, flight simulation, structures, aeroelasticity, MDO, hydrodynamics | `data/tools/` |
| Рабочие цепочки: с чего начать и чем проверить | Workflows: where to start and how to check | `data/workflows.yaml` |
| Таблица сверки: насколько программы совпали с опытом | Validation matrix: how well codes matched measurements | `data/validation.yaml` |
| Пустые ниши с разметкой «окно» и «запрещено» | Gaps marked "window" or "forbidden" | `data/gaps.yaml` |
| Эталонные цифры, термины, кейс «Стриж» | Reference numbers, glossary, the Strizh case | `data/` |
| Калькуляторы: атмосфера, Рейнольдс и Мах, сваливание, нагрузка на крыло, подобие по Фруду, кавитация | Calculators: atmosphere, Reynolds and Mach, stall, wing loading, Froude scaling, cavitation | `aviateka_mcp/calc.py`, `web/calc.js` |

## MCP-сервер / MCP server

```bash
uvx aviateka-mcp            # или / or: pip install aviateka-mcp && aviateka-mcp
aviateka-mcp --http --port 8000
```

Claude Desktop:

```json
{ "mcpServers": { "aviateka": { "command": "uvx", "args": ["aviateka-mcp"] } } }
```

17 инструментов MCP / 17 MCP tools: `search_tools`, `get_tool`, `find_workflows`, `list_gaps`, `list_benchmarks`, `get_validation`, `glossary`, `get_case`, `get_taxonomy`, `get_changelog`, `how_to_contribute`, `atmosphere`, `reynolds_mach`, `stall_speed`, `wing_loading`, `froude_model`, `cavitation`. Работает с официальным MCP SDK 1.x и 2.x. / Works with the official MCP SDK 1.x and 2.x.

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
