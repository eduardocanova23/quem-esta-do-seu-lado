"""O raw tem centenas de MB por dia: nunca pode entrar num commit."""

import subprocess


def test_dados_fora_do_git() -> None:
    assert subprocess.run(["git", "check-ignore", "-q", "dados/raw/x.csv.gz"]).returncode == 0


def test_so_a_pasta_da_raiz() -> None:
    """`dados/` sem barra no começo casaria também com docs/dados/ e esconderia doc novo do git."""
    assert subprocess.run(["git", "check-ignore", "-q", "docs/dados/novo.md"]).returncode == 1
