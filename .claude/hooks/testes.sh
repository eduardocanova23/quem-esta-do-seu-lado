#!/bin/bash
# Stop: não deixa o Claude encerrar a vez com teste rápido quebrado (make test).
# exit 2 devolve a falha ao Claude, que continua trabalhando.
INPUT=$(cat)

# Se este hook já segurou o Claude nesta vez, libera: senão ele nunca termina
[[ "$(echo "$INPUT" | jq -r '.stop_hook_active // false')" == "true" ]] && exit 0

cd "$CLAUDE_PROJECT_DIR" || exit 0
if ! SAIDA=$(make test 2>&1); then
  {
    echo "Testes rápidos falhando (make test). Corrija antes de encerrar:"
    echo "$SAIDA" | tail -40
  } >&2
  exit 2
fi
exit 0
