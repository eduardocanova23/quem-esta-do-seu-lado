"""Conferência de afirmações e dados antes de encerrar uma mudança em dados.

A branch que mexe em `db/marts`, `pipeline` ou `docs/dados` só fica "conferida" quando o registro em
`docs/conferencias/<branch>.md` está completo:

- **Afirmações:** cada fato sobre a fonte, o dado ou um número, com a evidência (comando e saída) ou marcado
  "não conferido".
- **Linhas refeitas da fonte** (se mexe em `db/marts`): ao menos 5 linhas de mart refeitas direto da Câmara.
- **Vazios** (se mexe em `db/marts`): a tabela é recontada daqui a cada execução; cada coluna com vazio
  precisa de explicação.

A marca de conferido é a impressão digital dos arquivos de dados (`.git/conferido`): mudou um dado, a
conferência vale de novo. Editar só o registro não desfaz a marca. O hook `exige-conferencia.sh` consulta
`--status` no fim de cada vez.

Uso: python scripts/conferir.py [--status | --dispensar MOTIVO]
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from pipeline.qualidade.contrato import carregar_contrato, carregar_csvs, validar  # noqa: E402

DADOS = ("db/marts", "pipeline", "docs/dados")
BASE = "main"
SITUACOES = ("conferido", "não conferido")
MINIMO_LINHAS = 5

ESQUELETO = """\
# Conferência: {branch}

Registro de `scripts/conferir.py` (skill `/conferir`). Evidência é comando e saída, não "parece certo".

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |

## Linhas refeitas da fonte

| Mart | Linha | Como refiz | Bate? |
| --- | --- | --- | --- |

## Vazios

| Coluna | Vazias | Explicação |
| --- | --- | --- |
"""


def _git(raiz: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, check=False)
    return r.stdout


def _branch(raiz: Path) -> str:
    return _git(raiz, "rev-parse", "--abbrev-ref", "HEAD").strip()


def toca_dados(raiz: Path) -> list[str]:
    """Arquivos de dados que a branch mudou em relação ao main, commitados ou não."""
    base = _git(raiz, "merge-base", BASE, "HEAD").strip()
    mudados = set(_git(raiz, "diff", "--name-only", base, "--", *DADOS).split()) if base else set()
    mudados |= set(_git(raiz, "ls-files", "--others", "--exclude-standard", "--", *DADOS).split())
    return sorted(m for m in mudados if "__pycache__" not in m)


def _impressao(raiz: Path) -> str:
    h = hashlib.sha256()
    arquivos = _git(raiz, "ls-files", "--cached", "--others", "--exclude-standard", "--", *DADOS).split()
    for nome in sorted(set(arquivos)):
        caminho = raiz / nome
        if caminho.is_file() and "__pycache__" not in nome:
            h.update(nome.encode() + b"\0" + caminho.read_bytes() + b"\0")
    return h.hexdigest()


def _marca(raiz: Path) -> Path:
    return raiz / _git(raiz, "rev-parse", "--git-path", "conferido").strip()


def conferido(raiz: Path) -> bool:
    if not toca_dados(raiz):
        return True
    marca = _marca(raiz)
    return marca.exists() and marca.read_text(encoding="utf-8").strip() == _impressao(raiz)


def caminho_registro(raiz: Path) -> Path:
    return raiz / "docs" / "conferencias" / f"{_branch(raiz).replace('/', '-')}.md"


def _secoes(texto: str) -> dict[str, list[list[str]]]:
    """Linhas de tabela de cada seção `## Título`, sem cabeçalho e separador."""
    secoes: dict[str, list[list[str]]] = {}
    atual = ""
    for linha in texto.splitlines():
        if linha.startswith("## "):
            atual = linha[3:].strip()
            secoes[atual] = []
        elif atual and linha.startswith("|"):
            secoes[atual].append([c.strip() for c in linha.strip().strip("|").split("|")])
    return {k: v[2:] for k, v in secoes.items()}


def _contar_vazios(raiz: Path) -> list[tuple[str, int, int]]:
    contrato = carregar_contrato(raiz / "db" / "marts" / "contrato.yaml")
    tabelas = carregar_csvs(raiz / "db" / "marts" / "amostra")
    saida = []
    for mart, spec in contrato["marts"].items():
        linhas = tabelas.get(mart, [])
        for coluna, col in spec["colunas"].items():
            vazias = sum(1 for linha in linhas if linha.get(coluna, "") == "")
            if col.get("nulo") and vazias:
                saida.append((f"{mart}.{coluna}", vazias, len(linhas)))
    return saida


def _reescrever_vazios(texto: str, vazios: list[tuple[str, int, int]]) -> str:
    explicacoes = {linha[0]: linha[2] for linha in _secoes(texto).get("Vazios", []) if len(linha) >= 3}
    tabela = "| Coluna | Vazias | Explicação |\n| --- | --- | --- |\n"
    tabela += "".join(f"| {c} | {v} de {n} | {explicacoes.get(c, '')} |\n" for c, v, n in vazios)
    if "## Vazios" not in texto:
        return texto.rstrip("\n") + "\n\n## Vazios\n\n" + tabela
    antes, _, depois = texto.partition("## Vazios")
    resto = re.search(r"\n## ", depois)
    return antes + "## Vazios\n\n" + tabela + (depois[resto.start() :] if resto else "")


def checar(raiz: Path) -> list[str]:
    """Erros do registro da conferência. Sem erro, marca o estado atual como conferido."""
    mudados = toca_dados(raiz)
    if not mudados:
        return []
    registro = caminho_registro(raiz)
    if not registro.exists():
        registro.parent.mkdir(parents=True, exist_ok=True)
        registro.write_text(ESQUELETO.format(branch=_branch(raiz)), encoding="utf-8")
    texto = registro.read_text(encoding="utf-8")
    mexe_marts = any(m.startswith("db/marts/") for m in mudados)
    erros: list[str] = []

    if mexe_marts:
        vazios = _contar_vazios(raiz)
        texto = _reescrever_vazios(texto, vazios)
        registro.write_text(texto, encoding="utf-8")
        contrato = carregar_contrato(raiz / "db" / "marts" / "contrato.yaml")
        erros += [f"amostra: {e}" for e in validar(contrato, carregar_csvs(raiz / "db" / "marts" / "amostra"))]

    secoes = _secoes(texto)
    afirmacoes = secoes.get("Afirmações", [])
    if not afirmacoes:
        erros.append("Afirmações: nenhuma listada. Liste cada fato sobre fonte, dado ou número desta branch")
    for a in afirmacoes:
        if len(a) < 3 or a[2] not in SITUACOES:
            erros.append(f"Afirmações: Situação tem de ser {' ou '.join(SITUACOES)}: {a}")
        elif a[2] == "conferido" and not a[1]:
            erros.append(f"Afirmações: conferido sem evidência: {a[0]}")

    if mexe_marts:
        refeitas = secoes.get("Linhas refeitas da fonte", [])
        if len(refeitas) < MINIMO_LINHAS:
            erros.append(f"Linhas refeitas da fonte: {len(refeitas)}; refaça ao menos {MINIMO_LINHAS} linhas da Câmara")
        for linha in refeitas:
            if len(linha) < 4 or not linha[3]:
                erros.append(f"Linhas refeitas da fonte: falta o Bate? em {linha}")
        for linha in _secoes(texto).get("Vazios", []):
            if len(linha) < 3 or not linha[2]:
                erros.append(f"Vazios: explique os vazios de {linha[0]}")

    if not erros:
        _marca(raiz).write_text(_impressao(raiz), encoding="utf-8")
    return erros


def dispensar(raiz: Path, motivo: str) -> None:
    """Só quando o Eduardo dispensa. O motivo fica no registro, que entra no PR."""
    registro = caminho_registro(raiz)
    registro.parent.mkdir(parents=True, exist_ok=True)
    texto = registro.read_text(encoding="utf-8") if registro.exists() else f"# Conferência: {_branch(raiz)}\n"
    registro.write_text(texto.rstrip("\n") + f"\n\n## Dispensa\n\n{motivo}\n", encoding="utf-8")
    _marca(raiz).write_text(_impressao(raiz), encoding="utf-8")


def main(argv: list[str]) -> int:
    raiz = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel").strip())
    if argv[:1] == ["--status"]:
        if conferido(raiz):
            return 0
        print("Dados mudados sem conferência: " + ", ".join(toca_dados(raiz)), file=sys.stderr)
        return 1
    if argv[:1] == ["--dispensar"] and len(argv) == 2:
        dispensar(raiz, argv[1])
        print(f"Dispensado; motivo em {caminho_registro(raiz).relative_to(raiz)}")
        return 0
    if argv:
        print(__doc__, file=sys.stderr)
        return 2
    erros = checar(raiz)
    for e in erros:
        print(e, file=sys.stderr)
    alvo = caminho_registro(raiz).relative_to(raiz) if toca_dados(raiz) else "nada a conferir"
    print(f"{len(erros)} pendência(s); registro: {alvo}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
