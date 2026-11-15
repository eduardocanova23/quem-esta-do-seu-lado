#!/bin/bash
# Stop: resposta com palavra de certeza ("bate", "confirmado", "funciona", "responde 200"...) precisa trazer
# a evidência num bloco "Conferência" ou marcar "não conferido". Devolve o Claude uma vez por vez.
INPUT=$(cat)
[[ "$(echo "$INPUT" | jq -r '.stop_hook_active // false')" == "true" ]] && exit 0

MSG=$(echo "$INPUT" | jq -r '.last_assistant_message // empty')
CERTEZA='(\bbat(e|em|eu|ia|eram)\b|confirmad|verificad|\b100 ?%|\bfunciona|\bpassa(m|ram|ou)?\b|responde 200|está (tudo )?certo|deu certo|corrigid)'
if echo "$MSG" | grep -qiE "$CERTEZA" && ! echo "$MSG" | grep -qiE '(conferência|não conferid)'; then
  {
    echo "Sua resposta afirma que algo está certo, mas não mostra a prova."
    echo "Acrescente um bloco **Conferência**: cada afirmação com o comando e a saída que a provam."
    echo "O que não conferiu, marque como 'não conferido'."
    echo "Sinal fraco não vale: HTTP 200 sem comparar com id inventado, teste que nunca falhou, 'bate' sem dizer o que ficou de fora."
  } >&2
  exit 2
fi
exit 0
