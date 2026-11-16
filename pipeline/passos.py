"""A lista de passos da atualização, num lugar só (docs/metodo.md, "Airflow depois, sem retrabalho").

O `make atualizar` roda esta lista na ordem; na Fase 5, as DAGs leem a mesma lista e criam uma tarefa por passo.
Passo novo nasce aqui: um módulo com main() que aceita --data AAAA-MM-DD e é idempotente.

Uso: python -m pipeline.passos --data AAAA-MM-DD
"""

import argparse
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Passo:
    nome: str
    modulo: str  # roda como: python -m <modulo> --data AAAA-MM-DD
    depende_de: tuple[str, ...] = ()


PASSOS: tuple[Passo, ...] = (Passo("coleta_arquivos", "pipeline.coleta.arquivos"),)


def ordem(passos: Sequence[Passo] = PASSOS) -> list[Passo]:
    """Ordem que respeita as dependências; no empate, a ordem da lista (Kahn, pegando sempre o primeiro pronto)."""
    nomes = {p.nome for p in passos}
    for p in passos:
        for d in p.depende_de:
            if d not in nomes:
                raise ValueError(f"{p.nome} depende de um passo que não existe: {d}")
    feitos: set[str] = set()
    resultado: list[Passo] = []
    while len(resultado) < len(passos):
        pronto = next((p for p in passos if p.nome not in feitos and set(p.depende_de) <= feitos), None)
        if pronto is None:
            presos = [p.nome for p in passos if p.nome not in feitos]
            raise ValueError(f"ciclo entre os passos: {', '.join(presos)}")
        feitos.add(pronto.nome)
        resultado.append(pronto)
    return resultado


def rodar(data: date, passos: Sequence[Passo] = PASSOS, *, cwd: Path | None = None) -> int:
    """Roda cada passo num processo próprio, como o Airflow fará; para no primeiro que falhar."""
    for passo in ordem(passos):
        print(f"== {passo.nome}", flush=True)
        codigo = subprocess.run([sys.executable, "-m", passo.modulo, "--data", data.isoformat()], cwd=cwd).returncode
        if codigo != 0:
            print(f"passo {passo.nome} falhou ({codigo})", file=sys.stderr)
            return codigo
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Roda os passos da atualização para uma data lógica")
    parser.add_argument("--data", required=True, type=date.fromisoformat, help="data lógica, AAAA-MM-DD")
    return rodar(parser.parse_args(argv).data)


if __name__ == "__main__":
    sys.exit(main())
