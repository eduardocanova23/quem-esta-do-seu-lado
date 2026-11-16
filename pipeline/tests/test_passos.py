"""A lista de passos é o que o make atualizar e as DAGs leem: ordem, dependências e parada no primeiro erro."""

import importlib
from datetime import date
from pathlib import Path

import pytest

from pipeline.passos import PASSOS, Passo, ordem, rodar


def nomes(passos: list[Passo]) -> list[str]:
    return [p.nome for p in passos]


def test_lista_real_valida() -> None:
    for passo in ordem():
        assert callable(getattr(importlib.import_module(passo.modulo), "main", None)), passo.modulo
    assert nomes(ordem()) == nomes(list(PASSOS))


def test_ordem_respeita_dependencia() -> None:
    passos = [Passo("C", "c", ("B",)), Passo("A", "a"), Passo("B", "b", ("A",))]
    assert nomes(ordem(passos)) == ["A", "B", "C"]


def test_ordem_estavel() -> None:
    assert nomes(ordem([Passo("X", "x"), Passo("Y", "y")])) == ["X", "Y"]


def test_ciclo() -> None:
    with pytest.raises(ValueError, match="ciclo"):
        ordem([Passo("A", "a", ("B",)), Passo("B", "b", ("A",))])


def test_dependencia_inexistente() -> None:
    with pytest.raises(ValueError, match="não existe: Z"):
        ordem([Passo("A", "a", ("Z",))])


def test_rodar_para_no_primeiro_que_falha(tmp_path: Path) -> None:
    for nome, corpo in {
        "ok": "open('marca_ok', 'w').close()",
        "falha": "import sys; sys.exit(3)",
        "depois": "open('marca_depois', 'w').close()",
    }.items():
        (tmp_path / f"{nome}.py").write_text(corpo + "\n", encoding="utf-8")
    passos = [Passo("ok", "ok"), Passo("falha", "falha", ("ok",)), Passo("depois", "depois", ("falha",))]
    assert rodar(date(2026, 11, 16), passos, cwd=tmp_path) == 3
    assert (tmp_path / "marca_ok").exists()
    assert not (tmp_path / "marca_depois").exists()
