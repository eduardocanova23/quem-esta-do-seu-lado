#!/bin/bash
# UserPromptSubmit: quando o Eduardo fala em encerrar, o Claude roda a conferência completa antes de responder.
PROMPT=$(jq -r '.prompt // empty')
if echo "$PROMPT" | grep -qiE '(terminamos|encerr|acab(ou|amos)|fechar a sess|fim da sess|por hoje é só|podemos parar)'; then
  echo "O Eduardo está fechando a sessão. Antes de responder, rode a skill /conferir completa, com a retrospectiva:"
  echo "reveja as afirmações que você fez na sessão inteira, procure erro, corrija o que achar e registre no vault."
fi
exit 0
