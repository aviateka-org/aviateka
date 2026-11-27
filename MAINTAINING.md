# Для хранителей / For maintainers

## Как разбирать вклад / How to process contributions

Вклад приходит через формы свободным текстом. Хранитель переводит его в формат каталога — это второй, строгий слой.

1. **Ответить в течение недели.** Даже коротко: «спасибо, смотрю». Первый ответ решает, придёт ли человек снова.
2. **Проверить источник.** Открыть ссылку, найти дату. Число без первоисточника не принимается или идёт с пометкой «заявлено».
3. **Перевести в формат.** Карточка — `data/tools/<id>.yaml`, сверка — `data/validation.yaml`. Тексты на двух языках.
4. **Указать автора.** В сверке — поле `added_by`; в запросе на слияние — `Co-authored-by` или ссылка на обращение.
5. **Закрыть обращение** ссылкой на запрос на слияние и словами благодарности.

Если обращение не подходит, объяснить почему и что можно сделать вместо. Не закрывать молча.

## Выпуск / Release

1. `python scripts/bump.py --ru "Что изменилось" --en "What changed"` — запись в `data/changelog.yaml` и новый номер в `pyproject.toml`, `server.json`, `CITATION.cff` одной командой (`--part minor` или `--part major` для крупных изменений). Робот свежести делает это сам, если изменились карточки.
2. `python scripts/build_catalog.py` — проверка сама сверит версии во всех файлах.
3. Слить в `main`. Метку ставить не нужно: `release.yml` сам видит, что такой версии ещё нет на PyPI, и выпускает её — PyPI, каталог MCP, релиз GitHub с меткой `vX.Y.Z` (Zenodo выдаст DOI, если включён). Если версия не менялась, выпуск пропускается.
4. После первого выпуска на PyPI поставить `pypi_published: true` в `data/meta.yaml`, чтобы страница показывала установку одной командой.

## Разовая настройка / One-time setup

```bash
bash scripts/setup_repo.sh owner/name
```

Вручную: PyPI → Publishing → trusted publisher (репозиторий, `release.yml`, окружение `pypi`); в окружении `pypi` на GitHub не ограничивать ветки (или разрешить `main`); по желанию Zenodo → GitHub → включить репозиторий.

Если владелец или имя репозитория не `aviateka-org/aviateka`, заменить их во всех файлах:

```bash
grep -rl "aviateka-org/aviateka" --exclude-dir=.git . | xargs sed -i "s#aviateka-org/aviateka#OWNER/NAME#g"
grep -rl "io.github.aviateka-org/" --exclude-dir=.git . | xargs sed -i "s#io.github.aviateka-org/#io.github.OWNER/#g"
grep -rl "aviateka-org.github.io/aviateka" --exclude-dir=.git . | xargs sed -i "s#aviateka-org.github.io/aviateka#OWNER.github.io/NAME#g"
```

---

**English, in short.** Contributions arrive as free text through forms; maintainers turn them into catalog format (the strict second layer). Reply within a week, check the source, write both `ru` and `en`, credit the author, close with thanks. To release: `python scripts/bump.py --ru ... --en ...` (adds the changelog entry and bumps `pyproject.toml`, `server.json`, `CITATION.cff`; the freshness bot does it itself when cards change), run `python scripts/build_catalog.py`, merge into `main`. No tag needed: `release.yml` sees the version is not on PyPI yet and releases it (PyPI, MCP Registry, GitHub release tagged `vX.Y.Z`); unchanged versions are skipped. One-time setup: `scripts/setup_repo.sh`, a PyPI trusted publisher, optionally Zenodo.
