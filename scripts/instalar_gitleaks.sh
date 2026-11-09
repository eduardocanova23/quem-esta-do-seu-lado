#!/usr/bin/env bash
# Instala o gitleaks em .venv/bin, com a versão fixada e o SHA256 conferido.
#
#     scripts/instalar_gitleaks.sh
#
# Reexecutável: se a versão certa já está lá, não faz nada. Único lugar com a versão do
# gitleaks: o pre-commit e o `make ci` usam este binário. Para atualizar, troque VERSAO e
# SHA256 (arquivo gitleaks_<versão>_checksums.txt da release).
set -euo pipefail

VERSAO=8.30.1
SHA256=551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb

RAIZ=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DESTINO="$RAIZ/.venv/bin/gitleaks"

if [[ ! -d "$RAIZ/.venv/bin" ]]; then
  echo "Ambiente não encontrado: rode make setup." >&2
  exit 1
fi

if [[ -x "$DESTINO" && "$("$DESTINO" version)" == *"$VERSAO"* ]]; then
  exit 0
fi

if [[ "$(uname -sm)" != "Linux x86_64" ]]; then
  echo "Sem binário configurado para $(uname -sm): o projeto roda em Linux x86_64 (WSL2 e CI)." >&2
  exit 1
fi

TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT

ARQUIVO="gitleaks_${VERSAO}_linux_x64.tar.gz"
curl -fsSL -o "$TEMP/$ARQUIVO" "https://github.com/gitleaks/gitleaks/releases/download/v${VERSAO}/${ARQUIVO}"
echo "$SHA256  $TEMP/$ARQUIVO" | sha256sum --check --quiet -
tar -xzf "$TEMP/$ARQUIVO" -C "$TEMP" gitleaks
install -m 755 "$TEMP/gitleaks" "$DESTINO"
echo "gitleaks $VERSAO instalado em .venv/bin"
