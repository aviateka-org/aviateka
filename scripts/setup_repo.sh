#!/usr/bin/env bash
# Разовая настройка репозитория на GitHub через gh. / One-time repository setup with the gh CLI.
#   bash scripts/setup_repo.sh owner/name
set -euo pipefail
REPO="${1:?укажите owner/name / pass owner/name}"

# Метки для форм и робота / labels for the forms and the bot
for spec in "new-tool:0e8a16:Новый инструмент / new tool" \
            "correction:d93f0b:Исправление / correction" \
            "validation:1d76db:Таблица сверки / validation matrix" \
            "new-topic:5319e7:Новая тема / new topic" \
            "freshness:c5def5:Робот свежести / freshness bot" \
            "good first issue:7057ff:Хорошо для первого раза / good first issue"; do
  IFS=: read -r name color desc <<<"$spec"
  gh label create "$name" --repo "$REPO" --color "$color" --description "$desc" --force
done

# Страница из GitHub Actions / Pages built by Actions
gh api -X POST "repos/$REPO/pages" -f build_type=workflow 2>/dev/null || gh api -X PUT "repos/$REPO/pages" -f build_type=workflow

# Разрешить роботу открывать запросы на слияние / let workflows open pull requests
gh api -X PUT "repos/$REPO/actions/permissions/workflow" -f default_workflow_permissions=write -F can_approve_pull_request_reviews=true

# Окружение для выпуска на PyPI / environment for PyPI releases
gh api -X PUT "repos/$REPO/environments/pypi" >/dev/null

echo "Готово / done. Осталось вручную / still manual: PyPI trusted publisher, Zenodo (по желанию / optional)."
