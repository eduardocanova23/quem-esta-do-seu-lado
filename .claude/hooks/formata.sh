#!/bin/bash
# PostToolUse em Edit/Write: formata o .py que o Claude acabou de editar, só aquele arquivo.
# Corrige o que é seguro; o que o ruff não corrige sozinho volta para o Claude (exit 2) arrumar.
INPUT=$(cat)
ARQ=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

[[ "$ARQ" == *.py || "$ARQ" == *.pyi ]] || exit 0
[[ -f "$ARQ" ]] || exit 0

# Só arquivos do projeto: rascunho no scratchpad ou em outro repositório fica como está
PROJETO=$(cd "$CLAUDE_PROJECT_DIR" && pwd -P)
ABS=$(realpath "$ARQ")
[[ "$ABS" == "$PROJETO"/* ]] || exit 0

cd "$PROJETO" || exit 0
# Lint antes do formato: um --fix (import removido, por exemplo) pode deixar algo para formatar
SAIDA=$(uv run --locked --quiet ruff check --fix --force-exclude "$ABS" 2>&1)
STATUS=$?
uv run --locked --quiet ruff format --force-exclude --quiet "$ABS"

if [[ $STATUS -ne 0 ]]; then
  echo "$SAIDA" >&2
  exit 2
fi
exit 0
