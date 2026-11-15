"""scripts/conferir.py: registro da conferência e marca de estado conferido, num repositório git de mentira."""

import subprocess
from pathlib import Path

import pytest

import conferir

CONTRATO = """\
versao: 1
marts:
  voto:
    uma_linha_por: voto
    chave: [id]
    colunas:
      id: {tipo: inteiro, descricao: Id}
      partido: {tipo: texto, nulo: true, descricao: Partido na data}
"""

AMOSTRA = "id,partido\n1,PT\n2,\n3,\n"

REGISTRO_OK = """\
# Conferência

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| O arquivo tem a coluna idEvento | head -1 votacoes-2025.csv mostra idEvento | conferido |
| O link da votação abre a votação certa | página montada no navegador | não conferido |

## Linhas refeitas da fonte

| Mart | Linha | Como refiz | Bate? |
| --- | --- | --- | --- |
| voto | 1 | API /votacoes/1/votos | sim |
| voto | 2 | API /votacoes/2/votos | sim |
| voto | 3 | API /votacoes/3/votos | sim |
| voto | 4 | API /votacoes/4/votos | sim |
| voto | 5 | API /votacoes/5/votos | não: partido errado, corrigido em abc123 |

## Vazios

| Coluna | Vazias | Explicação |
| --- | --- | --- |
| voto.partido | 2 de 3 | Deputados sem partido (S.PART.) na data do voto |
"""


def git(raiz: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, check=True).stdout


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Repositório com main e uma branch que mexe na amostra dos marts."""
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@t")
    git(tmp_path, "config", "user.name", "t")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    git(tmp_path, "add", "README.md")
    git(tmp_path, "commit", "-q", "-m", "inicio")
    git(tmp_path, "switch", "-q", "-c", "feat/9-amostra")
    (tmp_path / "db" / "marts" / "amostra").mkdir(parents=True)
    (tmp_path / "db" / "marts" / "contrato.yaml").write_text(CONTRATO, encoding="utf-8")
    (tmp_path / "db" / "marts" / "amostra" / "voto.csv").write_text(AMOSTRA, encoding="utf-8")
    git(tmp_path, "add", "db")
    git(tmp_path, "commit", "-q", "-m", "amostra")
    return tmp_path


def registro(raiz: Path) -> Path:
    return raiz / "docs" / "conferencias" / "feat-9-amostra.md"


def test_branch_sem_dados_nao_precisa_de_conferencia(repo: Path) -> None:
    git(repo, "switch", "-q", "main")
    assert conferir.toca_dados(repo) == []
    assert conferir.conferido(repo)


def test_mudanca_em_dados_sem_conferencia_nao_esta_conferida(repo: Path) -> None:
    assert conferir.toca_dados(repo) == ["db/marts/amostra/voto.csv", "db/marts/contrato.yaml"]
    assert not conferir.conferido(repo)


def test_mudanca_nao_commitada_em_dados_conta(repo: Path) -> None:
    git(repo, "switch", "-q", "main")
    (repo / "pipeline").mkdir()
    (repo / "pipeline" / "passo.py").write_text("x = 1\n", encoding="utf-8")
    assert conferir.toca_dados(repo) == ["pipeline/passo.py"]


def test_sem_registro_cria_o_esqueleto_e_falha(repo: Path) -> None:
    erros = conferir.checar(repo)
    assert registro(repo).exists()
    assert any("Afirmações" in e for e in erros)
    assert not conferir.conferido(repo)


def test_registro_completo_marca_conferido(repo: Path) -> None:
    registro(repo).parent.mkdir(parents=True)
    registro(repo).write_text(REGISTRO_OK, encoding="utf-8")
    assert conferir.checar(repo) == []
    assert conferir.conferido(repo)


def test_mudar_dado_depois_de_conferir_exige_nova_conferencia(repo: Path) -> None:
    registro(repo).parent.mkdir(parents=True)
    registro(repo).write_text(REGISTRO_OK, encoding="utf-8")
    assert conferir.checar(repo) == []
    (repo / "db" / "marts" / "amostra" / "voto.csv").write_text(AMOSTRA + "4,PL\n", encoding="utf-8")
    assert not conferir.conferido(repo)


def test_editar_o_registro_nao_desfaz_a_conferencia(repo: Path) -> None:
    registro(repo).parent.mkdir(parents=True)
    registro(repo).write_text(REGISTRO_OK, encoding="utf-8")
    assert conferir.checar(repo) == []
    registro(repo).write_text(REGISTRO_OK + "\nNota.\n", encoding="utf-8")
    assert conferir.conferido(repo)


@pytest.mark.parametrize(
    ("trocar", "por", "erro"),
    [
        ("| conferido |", "| acho que sim |", "Situação"),
        ("| head -1 votacoes-2025.csv mostra idEvento |", "|  |", "sem evidência"),
        ("| voto | 5 | API /votacoes/5/votos | não: partido errado, corrigido em abc123 |\n", "", "5 linhas"),
        ("| voto | 1 | API /votacoes/1/votos | sim |", "| voto | 1 | API /votacoes/1/votos |  |", "Bate?"),
        ("Deputados sem partido (S.PART.) na data do voto", "", "voto.partido"),
    ],
)
def test_cada_regra_do_registro(repo: Path, trocar: str, por: str, erro: str) -> None:
    assert REGISTRO_OK.count(trocar) == 1, "a mutação não achou o alvo"
    registro(repo).parent.mkdir(parents=True)
    registro(repo).write_text(REGISTRO_OK.replace(trocar, por), encoding="utf-8")
    erros = conferir.checar(repo)
    assert any(erro in e for e in erros), erros
    assert not conferir.conferido(repo)


def test_vazios_sao_recontados_e_a_explicacao_fica(repo: Path) -> None:
    registro(repo).parent.mkdir(parents=True)
    registro(repo).write_text(REGISTRO_OK, encoding="utf-8")
    (repo / "db" / "marts" / "amostra" / "voto.csv").write_text(AMOSTRA + "4,\n", encoding="utf-8")
    assert conferir.checar(repo) == []
    texto = registro(repo).read_text(encoding="utf-8")
    assert "| voto.partido | 3 de 4 | Deputados sem partido (S.PART.) na data do voto |" in texto


def test_amostra_fora_do_contrato_falha(repo: Path) -> None:
    registro(repo).parent.mkdir(parents=True)
    registro(repo).write_text(REGISTRO_OK, encoding="utf-8")
    (repo / "db" / "marts" / "amostra" / "voto.csv").write_text("id,partido\nx,PT\n", encoding="utf-8")
    assert any("não é inteiro" in e for e in conferir.checar(repo))


def test_so_docs_de_dados_nao_pede_linhas_nem_vazios(repo: Path) -> None:
    git(repo, "switch", "-q", "main")
    git(repo, "switch", "-q", "-c", "feat/9-amostra-docs")
    (repo / "docs" / "dados").mkdir(parents=True)
    (repo / "docs" / "dados" / "x.md").write_text("A API devolve 200.\n", encoding="utf-8")
    reg = repo / "docs" / "conferencias" / "feat-9-amostra-docs.md"
    reg.parent.mkdir(parents=True)
    so_afirmacoes = REGISTRO_OK.split("## Linhas")[0]
    reg.write_text(so_afirmacoes, encoding="utf-8")
    assert conferir.checar(repo) == []


def test_dispensa_marca_conferido_e_guarda_o_motivo(repo: Path) -> None:
    conferir.dispensar(repo, "Eduardo dispensou: só renomeia um arquivo")
    assert conferir.conferido(repo)
    assert "Eduardo dispensou: só renomeia um arquivo" in registro(repo).read_text(encoding="utf-8")
