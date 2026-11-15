#!/bin/bash
# Stop: a vez não termina com dado mudado (db/marts, pipeline, docs/dados) que não foi conferido.
# Quem marca como conferido é scripts/conferir.py, depois de checar o registro em docs/conferencias/.
INPUT=$(cat)

# Já segurou uma vez nesta vez: libera, senão o Claude nunca termina
[[ "$(echo "$INPUT" | jq -r '.stop_hook_active // false')" == "true" ]] && exit 0

cd "$CLAUDE_PROJECT_DIR" || exit 0
if ! SAIDA=$(make -s conferir-status 2>&1); then
  {
    echo "$SAIDA"
    echo "Rode a skill /conferir: registre as afirmações com evidência, refaça linhas da fonte, explique os vazios"
    echo "e rode 'make conferir' até dar 0 pendência. Só o Eduardo dispensa (make conferir-dispensar MOTIVO=...)."
  } >&2
  exit 2
fi
exit 0
