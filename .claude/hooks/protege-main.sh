#!/bin/bash
# Bloqueia commit e push no main do projeto, e push --force em qualquer lugar.
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
DIR=$(echo "$INPUT" | jq -r '.cwd // empty')

RE_FORCE='git.*push.*(--force|-f([[:space:]]|$))'
RE_ESCRITA='git.*(commit|push)'
RE_C='git[[:space:]]+-C[[:space:]]+("([^"]+)"|([^[:space:]]+))'

if [[ "$CMD" =~ $RE_FORCE ]]; then
  echo "Bloqueado: push --force não é permitido neste projeto." >&2
  exit 2
fi

# Com git -C <pasta>, vale a pasta do comando, não a da sessão
if [[ "$CMD" =~ $RE_C ]]; then
  DIR="${BASH_REMATCH[2]:-${BASH_REMATCH[3]}}"
fi

# Só o repositório do projeto é protegido; o vault e outros repositórios passam
ALVO=$(git -C "$DIR" rev-parse --show-toplevel 2>/dev/null)
PROJETO=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null)
[[ "$ALVO" != "$PROJETO" ]] && exit 0

BRANCH=$(git -C "$DIR" rev-parse --abbrev-ref HEAD 2>/dev/null)
if [[ "$BRANCH" == "main" && "$CMD" =~ $RE_ESCRITA ]]; then
  echo "Bloqueado: você está no main. Crie uma branch: git switch -c feat/<issue>-<slug>" >&2
  exit 2
fi

exit 0
