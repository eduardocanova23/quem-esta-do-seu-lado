"""O raw tem centenas de MB por dia: nunca pode entrar num commit."""

import subprocess


def test_dados_fora_do_git() -> None:
    assert subprocess.run(["git", "check-ignore", "-q", "dados/raw/x.csv.gz"]).returncode == 0
