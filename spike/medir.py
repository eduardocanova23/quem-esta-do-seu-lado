"""Roda um comando e mede o tempo de relógio e o pico da memória somada da árvore de processos.

Uso: python -I medir.py <pasta> <comando...>
O /usr/bin/time -v só dá o pico do maior processo; o Next reparte o build em vários.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def arvore_rss_kb(raiz: int) -> int:
    filhos: dict[int, list[int]] = {}
    rss: dict[int, int] = {}
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            status = (p / "status").read_text()
        except OSError:
            continue
        campos = dict(linha.split(":", 1) for linha in status.splitlines() if ":" in linha)
        pid, ppid = int(p.name), int(campos["PPid"])
        filhos.setdefault(ppid, []).append(pid)
        rss[pid] = int(campos.get("VmRSS", "0 kB").split()[0])
    total, fila = 0, [raiz]
    while fila:
        pid = fila.pop()
        total += rss.get(pid, 0)
        fila.extend(filhos.get(pid, []))
    return total


def main() -> None:
    pasta, comando = sys.argv[1], sys.argv[2:]
    env = {**os.environ, "NEXT_TELEMETRY_DISABLED": "1", "ASTRO_TELEMETRY_DISABLED": "1"}
    inicio = time.monotonic()
    proc = subprocess.Popen(comando, cwd=pasta, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    pico = amostras = 0
    while proc.poll() is None:
        pico = max(pico, arvore_rss_kb(proc.pid))
        amostras += 1
        time.sleep(0.2)
    duracao = time.monotonic() - inicio
    erro = proc.stderr.read().decode()[-500:] if proc.stderr else ""
    print(f"saida={proc.returncode} tempo={duracao:.1f}s pico_soma={pico / 1024:.0f}MB amostras={amostras}")
    if proc.returncode:
        print(erro)


if __name__ == "__main__":
    main()
