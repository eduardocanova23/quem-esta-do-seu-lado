"""Hooks do Claude Code em .claude/hooks/: cada um recebe o JSON do evento no stdin, como o Claude Code manda."""

import json
import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
HOOKS = RAIZ / ".claude" / "hooks"


def rodar(hook: str, evento: dict[str, object], projeto: Path = RAIZ) -> subprocess.CompletedProcess[str]:
    ambiente = {**os.environ, "CLAUDE_PROJECT_DIR": str(projeto)}
    return subprocess.run(
        [str(HOOKS / hook)], input=json.dumps(evento), capture_output=True, text=True, env=ambiente, check=False
    )


# --- formata.sh (PostToolUse em Edit/Write) ---


@pytest.fixture
def arquivo_no_projeto() -> Iterator[Path]:
    """Um .py mal formatado dentro do projeto, apagado no fim do teste."""
    caminho = RAIZ / "scripts" / "_tmp_hook_formata.py"
    yield caminho
    caminho.unlink(missing_ok=True)


def test_formata_arruma_py_editado(arquivo_no_projeto: Path) -> None:
    arquivo_no_projeto.write_text("import os\nx=1\n", encoding="utf-8")
    r = rodar("formata.sh", {"tool_input": {"file_path": str(arquivo_no_projeto)}})
    assert r.returncode == 0, r.stderr
    assert arquivo_no_projeto.read_text(encoding="utf-8") == "x = 1\n"


def test_formata_avisa_o_claude_do_que_nao_corrige_sozinho(arquivo_no_projeto: Path) -> None:
    arquivo_no_projeto.write_text("print(nome_que_nao_existe)\n", encoding="utf-8")
    r = rodar("formata.sh", {"tool_input": {"file_path": str(arquivo_no_projeto)}})
    assert r.returncode == 2
    assert "F821" in r.stderr


def test_formata_ignora_o_que_nao_e_py() -> None:
    md = RAIZ / "docs" / "_tmp_hook.md"
    md.write_text("x=1  \n", encoding="utf-8")
    try:
        r = rodar("formata.sh", {"tool_input": {"file_path": str(md)}})
        assert r.returncode == 0
        assert md.read_text(encoding="utf-8") == "x=1  \n"
    finally:
        md.unlink()


def test_formata_ignora_py_fora_do_projeto(tmp_path: Path) -> None:
    fora = tmp_path / "rascunho.py"
    fora.write_text("x=1\n", encoding="utf-8")
    r = rodar("formata.sh", {"tool_input": {"file_path": str(fora)}})
    assert r.returncode == 0
    assert fora.read_text(encoding="utf-8") == "x=1\n"


# --- testes.sh (Stop) ---


def projeto_falso(tmp_path: Path, passa: bool) -> Path:
    """Um projeto cujo `make test` passa ou falha de propósito, sem rodar o pytest de verdade."""
    receita = "@echo tudo verde" if passa else "@echo 'FAILED test_x' && exit 1"
    (tmp_path / "Makefile").write_text(f"test:\n\t{receita}\n", encoding="utf-8")
    return tmp_path


def test_stop_libera_com_testes_verdes(tmp_path: Path) -> None:
    r = rodar("testes.sh", {"stop_hook_active": False}, projeto_falso(tmp_path, passa=True))
    assert r.returncode == 0


def test_stop_segura_o_claude_com_teste_quebrado(tmp_path: Path) -> None:
    r = rodar("testes.sh", {"stop_hook_active": False}, projeto_falso(tmp_path, passa=False))
    assert r.returncode == 2
    assert "FAILED test_x" in r.stderr


def test_stop_nao_entra_em_laco(tmp_path: Path) -> None:
    # Já segurou uma vez nesta vez do Claude: libera, senão ele nunca termina.
    r = rodar("testes.sh", {"stop_hook_active": True}, projeto_falso(tmp_path, passa=False))
    assert r.returncode == 0
