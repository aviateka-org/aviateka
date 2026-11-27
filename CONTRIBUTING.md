# Как помочь Авиатеке / Contributing to Aviateka

[Русский](#русский) · [English](#english)

## Русский

Авиатека — открытый каталог программ для проектирования летательных аппаратов всех видов: самолётов и винтокрылых, тканевых аппаратов и аэростатов, дирижаблей, гидросамолётов, экранопланов и судов на подводных крыльях, сверхзвуковых и спускаемых аппаратов, гражданских ракет. Её улучшают те, кто ею пользуется. Знать Git не нужно.

### Четыре способа помочь без Git

Откройте [новое обращение](https://github.com/aviateka-org/aviateka/issues/new/choose) и выберите форму:

| Форма | Когда |
|---|---|
| Новый инструмент | Знаете открытую программу, которой нет в каталоге |
| Исправление | Нашли ошибку, устаревшую дату или битую ссылку |
| Свой расчёт | Считали случай и сравнили с опытом — это пойдёт в таблицу сверки |
| Новая тема | Нужен раздел, которого нет: дирижабли, ракеты, парусные крылья |

Пишите своими словами. Хранители переведут вклад в формат каталога, найдут или проверят источник и ответят в обращении. Цель — первый ответ в течение недели.

### Если знаете Git

Каталог — это файлы в папке `data/`:

| Файл | Что в нём |
|---|---|
| `data/tools/<id>.yaml` | Карточка одного инструмента; поля описаны в `schema/tool.schema.json` |
| `data/validation.yaml` | Таблица сверки; поля — в `schema/validation.schema.json` |
| `data/workflows.yaml` | Рабочие цепочки |
| `data/gaps.yaml` | Пустые ниши с разметкой «окно» или «запрещено» |
| `data/benchmarks.yaml` | Эталонные цифры |
| `data/glossary.yaml` | Термины |
| `data/taxonomy.yaml` | Справочники: дисциплины, уровни точности, этапы, типы аппаратов |
| `data/changelog.yaml` | Журнал версий (ведут хранители) |

Порядок работы:

1. Сделайте ответвление (fork) и ветку.
2. Правьте YAML. Каждый текст — на двух языках: `ru` и `en`.
3. Проверьте: `pip install pyyaml jsonschema` и `python scripts/build_catalog.py --check`.
4. Откройте запрос на слияние (pull request). Проверка запустится сама.

### Правила данных

- **У каждого факта есть источник.** Ссылка на репозиторий, документацию, статью или обсуждение. Число без источника не принимается.
- **Дата у всего.** Дата последнего коммита — по основной ветке. Год у статьи.
- **«Заявлено» ≠ «измерено».** Цифры из рекламы и описаний помечаются как заявленные.
- **Ничего не копируем.** Только своими словами и ссылкой. Статьи, PDF и чужой код в репозиторий не кладём.
- **Отрицательный результат — тоже результат.** «Не совпало с опытом» в таблице сверки ценно.
- **Спорное — с оговоркой.** Если источник заинтересован (сравнивает со своей моделью), это пишется в `caveats`.

### Лицензии вклада

Присылая вклад, вы соглашаетесь, что он публикуется под теми же лицензиями, что и проект: данные — [CC BY 4.0](LICENSE-DATA.md), код — [MIT](LICENSE).

### Как мы общаемся

Уважительно и по делу. Критикуем данные, а не людей. Новичкам отвечаем так, чтобы им захотелось прийти снова.

### Версии

Номер версии MAJOR.MINOR.PATCH ведут хранители. PATCH — исправления данных. MINOR — новые инструменты, разделы, типы аппаратов или инструменты MCP. MAJOR — несовместимые изменения схемы или имён инструментов MCP.

---

## English

Aviateka is an open catalog of design tools for flying craft of every kind: aircraft and rotorcraft, fabric craft and balloons, airships, seaplanes, WIG and hydrofoil craft, high-speed and entry vehicles, civil rockets. The people who use it make it better. No Git needed.

### Four ways to help without Git

Open a [new issue](https://github.com/aviateka-org/aviateka/issues/new/choose) and pick a form:

| Form | When |
|---|---|
| New tool | You know an open code missing from the catalog |
| Correction | You found a mistake, an outdated date or a dead link |
| Your calculation | You computed a case and compared it with a test — it goes into the validation matrix |
| New topic | A missing section: airships, rockets, sail wings |

Write in your own words. Maintainers turn it into catalog format, find or check the source and reply in the issue. The goal is a first reply within a week.

### If you know Git

The catalog is the files in `data/` (see the table above). Edit the YAML, keep every text in both `ru` and `en`, run `python scripts/build_catalog.py --check` and open a pull request. The checks run by themselves.

### Data rules

- **Every fact has a source** — repository, docs, paper or thread. No number without a source.
- **Date everything** — last commit on the default branch, year of a paper.
- **Claimed ≠ measured** — marketing numbers are marked as claimed.
- **Copy nothing** — your own words and a link. No papers, PDFs or third-party code in the repository.
- **Negative results count** — "did not match the test" is valuable in the validation matrix.
- **Flag interest** — if a source compares against its own model, say so in `caveats`.

### Licence of contributions

By contributing you agree that your contribution is published under the project's licences: data under [CC BY 4.0](LICENSE-DATA.md), code under [MIT](LICENSE).

### How we talk

Respectfully and to the point. Criticise data, not people. Answer newcomers so they want to come back.
