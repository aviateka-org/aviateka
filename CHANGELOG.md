# Авиатека / Aviateka — журнал изменений / changelog

Номер версии MAJOR.MINOR.PATCH. MINOR растёт, когда добавляются инструменты, типы аппаратов, разделы или инструменты MCP. PATCH — исправления данных без новых разделов. MAJOR — несовместимые изменения схемы данных или имён инструментов MCP. Каждая версия записывается в журнал с датой и списком изменений.

Version MAJOR.MINOR.PATCH. MINOR grows when tools, aircraft types, sections or MCP tools are added. PATCH means data fixes without new sections. MAJOR means breaking changes to the data schema or MCP tool names. Every version is logged with its date and changes.

## 0.5.5 — 2026-11-26

- Исправлена ошибка версии 0.5.4: файлы Autowing на странице кафедры не свободные — все ссылки ведут на вход для сотрудников и студентов. Статус возвращён на «по запросу»; открыт без входа только учебный пример potentialVortex, к проектированию он не относится.

- Corrected a mistake in 0.5.4: the Autowing files on the chair page are not free — every link leads to a staff and student login. Status is back to on request; only the potentialVortex teaching case is public, and it is unrelated to design.

## 0.5.4 — 2026-11-26

- Autowing: программа, учебник, справка и описание математических моделей скачиваются со страницы кафедры в Ростоке свободно; статус сменён с «по запросу» на «бесплатно, без исходников». Условия лицензии на странице не указаны, за ними — к автору.

- Autowing: the program, tutorial, help file and description of the mathematical models can be downloaded freely from the Rostock chair page; status changed from on request to freeware. Licence terms are not stated there; ask the author.

## 0.5.3 — 2026-11-26

- Сайт подключён к Google Search Console: на страницах стоит метка владельца.

- The site is connected to Google Search Console: pages carry the owner verification tag.

## 0.5.2 — 2026-11-26

- Включён счётчик посещений GoatCounter (aviateka.goatcounter.com): без cookies, считает только просмотры страниц.

- The GoatCounter visit counter is on (aviateka.goatcounter.com): no cookies, counts page views only.

## 0.5.1 — 2026-11-26

- Первый проход робота свежести: новые даты коммитов у ArduPilot, FluidX3D и pyOptSparse, FluidX3D отмечен как живой.
- Исправлена ссылка на ветку форума boatdesign.net в карточке OpenPlaning.

- First freshness-bot pass: new commit dates for ArduPilot, FluidX3D and pyOptSparse; FluidX3D marked active.
- Fixed the boatdesign.net forum thread link on the OpenPlaning card.

## 0.5.0 — 2026-11-26

- Каждый инструмент получил свою обычную страницу (tools/…), есть общий список. Их видят поисковики и роботы ИИ, которые не запускают скрипты: раньше карточки каталога рисовались только скриптом и для них были невидимы.
- Карта сайта sitemap.xml, путеводители для ИИ llms.txt и llms-full.txt, описание набора данных для Google Dataset Search, превью ссылок в мессенджерах.
- Заготовки под счётчик посещений GoatCounter и проверку в Google Search Console: включаются одной строкой в data/meta.yaml. В README — значки версии и проверки.

- Every tool now has its own plain page (tools/…), plus a full list. Search engines and AI crawlers that do not run scripts can read them; before, the catalog cards were drawn only by a script and were invisible to them.
- A sitemap.xml, AI guides llms.txt and llms-full.txt, a dataset description for Google Dataset Search, link previews in messengers.
- Hooks for a GoatCounter visit counter and Google Search Console verification, switched on by one line in data/meta.yaml. Version and check badges in the README.

## 0.4.2 — 2026-11-26

- Сервер опубликован: пакет aviateka-mcp на PyPI и запись io.github.aviateka-org/aviateka в каталоге MCP (выпуск 0.4.1). Страница теперь предлагает ставить его одной командой uvx aviateka-mcp.

- The server is published: the aviateka-mcp package on PyPI and the io.github.aviateka-org/aviateka entry in the MCP Registry (release 0.4.1). The page now suggests installing it with one command, uvx aviateka-mcp.

## 0.4.1 — 2026-11-26

- Постоянный адрес проекта: организация aviateka-org на GitHub, репозиторий aviateka-org/aviateka, страница aviateka-org.github.io/aviateka, имя в каталоге MCP io.github.aviateka-org/aviateka.

- Permanent home: the aviateka-org organisation on GitHub, repository aviateka-org/aviateka, page aviateka-org.github.io/aviateka, MCP Registry name io.github.aviateka-org/aviateka.

## 0.4.0 — 2026-11-26

- Страница «О проекте» стала главной: что такое Авиатека, зачем она, как растёт (круг вклада), что внутри, как помочь, что нового. Числа и новости берутся из каталога сами.
- Каталог переехал по адресу catalog.html; название в шапке каталога ведёт на главную.

- An About page is now the front page: what Aviateka is, why, how it grows (the contribution loop), what is inside, how to help, what is new. Numbers and news come from the catalog automatically.
- The catalog moved to catalog.html; the name in its header links back to the front page.

## 0.3.0 — 2026-11-26

- Открытый проект: каталог разложен на файлы (одна карточка — один файл), появились схемы данных и проверка каждого изменения.
- Таблица сверки «кто чем считал и насколько совпало с опытом»; первые строки — Autowing и модель Ombor по диссертации 2023 года.
- Формы вклада без Git (инструмент, правка, свой расчёт, тема), раздел «Как помочь» и ссылка «Предложить правку» на каждой карточке.
- Инструменты MCP get_validation и how_to_contribute; сервер ставится пакетом aviateka-mcp.
- Робот раз в неделю обновляет даты коммитов, статусы и проверяет ссылки; выпуск по метке публикует пакет и сервер в каталоге MCP.
- Лицензии: код — MIT, данные — CC BY 4.0. Карточки внутри клетки карты теперь идут по алфавиту.

- Open project: the catalog is split into files (one card per file), with data schemas and a check on every change.
- Validation matrix "who computed what and how well it matched"; first rows are Autowing and Ombor's model from the 2023 thesis.
- Contribution forms without Git (tool, correction, calculation, topic), a Contribute section and a "Suggest a correction" link on every card.
- MCP tools get_validation and how_to_contribute; the server installs as the aviateka-mcp package.
- A weekly bot refreshes commit dates and statuses and checks links; a tagged release publishes the package and the MCP Registry entry.
- Licences: code MIT, data CC BY 4.0. Cards within a chart cell are now in alphabetical order.

## 0.2.2 — 2026-11-26

- Карточка Autowing: по спискам публикаций кафедры добавлены период активной работы (1997–2014, последняя статья 2019) и ссылка на бесплатный учебник автора с главой о динамике экраноплана.

- Autowing card: from the chair's publication lists, added the active period (1997–2014, last paper 2019) and the author's free textbook with a chapter on WIG dynamics.

## 0.2.1 — 2026-11-26

- Карточка Autowing уточнена по разбору: история метода (1992 → версия 2.4 в 1998 → 2019), нелинейный нестационарный метод, оговорка о точности по независимой сверке 2023 года, пять источников.

- Autowing card refined after a deep review: method history (1992 → v2.4 in 1998 → 2019), nonlinear unsteady method, accuracy caveat from an independent 2023 check, five sources.

## 0.2.0 — 2026-11-26

- Новые типы аппаратов: экраноплан и судно на подводных крыльях; новая дисциплина «Гидродинамика».
- 11 новых инструментов: Autowing, PUFFIn, Typhoon, MachUpHydro, DCFoil.jl, OpenPlaning, FreeCAD Ship, LEModeler, FASTSHIPS, симулятор Hydroptère, комплекс устойчивости экраноплана.
- У AVL, OpenVSP, flow5, XFOIL, NeuralFoil, OpenFOAM, SU2, OpenProp и ArduPilot добавлено применение к экранопланам и крыльям в воде.
- 2 цепочки (экраноплан, судно на крыльях), 3 ниши, 3 эталона, 9 терминов.
- Калькулятор кавитации; инструменты MCP get_changelog и cavitation.
- Журнал версий и правила нумерации в каталоге, на странице и в MCP.

- New craft types: WIG craft and hydrofoil craft; new discipline 'Hydrodynamics'.
- 11 new tools: Autowing, PUFFIn, Typhoon, MachUpHydro, DCFoil.jl, OpenPlaning, FreeCAD Ship, LEModeler, FASTSHIPS, Hydroptère simulator, WIG stability tool.
- AVL, OpenVSP, flow5, XFOIL, NeuralFoil, OpenFOAM, SU2, OpenProp and ArduPilot now tagged for WIG and hydrofoil use.
- 2 workflows (WIG, hydrofoil), 3 gaps, 3 benchmarks, 9 terms.
- Cavitation calculator; MCP tools get_changelog and cavitation.
- Version log and numbering rules in the catalog, page and MCP.

## 0.1.0 — 2026-11-26

- Первая версия: 54 инструмента, 12 цепочек, 5 ниш, 6 эталонов, 22 термина, кейс «Стриж».
- Страница с картой «дисциплина × точность» и MCP-сервер с 13 инструментами и 5 калькуляторами.

- First release: 54 tools, 12 workflows, 5 gaps, 6 benchmarks, 22 terms, the Strizh case.
- Page with a discipline × fidelity chart and an MCP server with 13 tools and 5 calculators.
