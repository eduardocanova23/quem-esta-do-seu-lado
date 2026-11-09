#!/usr/bin/env python3
"""Lê docs/frentes.yaml, valida a rota e mostra onde trabalhar em seguida.

python3 scripts/rota.py           mostra a rota; sai sempre com 0 (é o que o hook usa)
python3 scripts/rota.py --check   só valida; sai com 1 se houver erro (é o que o CI usa)
"""

import sys
from pathlib import Path
from typing import Any

import yaml

ARQUIVO = Path(__file__).resolve().parent.parent / "docs" / "frentes.yaml"
STATUS = {"pendente", "andamento", "feito"}

# O YAML é validado por validar(), não pelo tipo: por isso os valores ficam como Any.
Frente = dict[str, Any]
Marco = dict[str, Any]
# (nome da frente, chave do marco, próximo passo, dependências em aberto, quantos marcos destrava)
Item = tuple[str, str, Any, list[str], int]


def carregar(caminho: Path) -> tuple[dict[str, Frente], dict[str, Marco]]:
    frentes: dict[str, Frente] = yaml.safe_load(caminho.read_text(encoding="utf-8"))["frentes"]
    marcos: dict[str, Marco] = {}  # "frente.marco" -> marco
    for nome, frente in frentes.items():
        for m in frente.get("marcos", []):
            m.setdefault("status", "pendente")
            m.setdefault("depende_de", [])
            marcos[f"{nome}.{m['id']}"] = m
    return frentes, marcos


def marco_atual(frente: Frente) -> Marco | None:
    """O primeiro marco que ainda não foi feito, ou None se a frente acabou."""
    return next((m for m in frente.get("marcos", []) if m["status"] != "feito"), None)


def faltando(m: Marco, marcos: dict[str, Marco]) -> list[str]:
    return [d for d in m["depende_de"] if marcos.get(d, {}).get("status") != "feito"]


def ciclos(marcos: dict[str, Marco]) -> list[str]:
    cor: dict[str, str] = {}
    erros: list[str] = []

    def visita(k: str, caminho: list[str]) -> None:
        cor[k] = "visitando"
        for dep in marcos[k]["depende_de"]:
            if dep not in marcos:
                continue
            if cor.get(dep) == "visitando":
                erros.append("ciclo: " + " -> ".join(caminho + [dep]))
            elif dep not in cor:
                visita(dep, caminho + [dep])
        cor[k] = "visto"

    for k in marcos:
        if k not in cor:
            visita(k, [k])
    return erros


def validar(frentes: dict[str, Frente], marcos: dict[str, Marco]) -> list[str]:
    erros: list[str] = []
    for chave, m in marcos.items():
        if m["status"] not in STATUS:
            erros.append(f"{chave}: status '{m['status']}' não existe")
        for dep in m["depende_de"]:
            if dep not in marcos:
                erros.append(f"{chave}: depende de '{dep}', que não existe")
        if m["status"] != "pendente" and faltando(m, marcos):
            erros.append(f"{chave}: está '{m['status']}', mas espera {', '.join(faltando(m, marcos))}")
    ativas = [n for n, f in frentes.items() if f.get("ativa")]
    if len(ativas) > 1:
        erros.append(f"mais de uma frente ativa: {', '.join(ativas)}")
    for nome, f in frentes.items():
        atual = marco_atual(f)
        if atual and not str(f.get("proximo_passo") or "").strip():
            erros.append(f"{nome}: tem marco aberto e nenhum próximo passo")
        if f.get("ativa") and atual and faltando(atual, marcos):
            erros.append(f"{nome}: está ativa, mas o marco atual espera {', '.join(faltando(atual, marcos))}")
    return erros + ciclos(marcos)


def destrava(marcos: dict[str, Marco]) -> dict[str, int]:
    """Quantos marcos dependem, direta ou indiretamente, de cada marco."""
    dependentes: dict[str, set[str]] = {k: set() for k in marcos}
    for k, m in marcos.items():
        for dep in m["depende_de"]:
            if dep in dependentes:
                dependentes[dep].add(k)

    def alcance(k: str, vistos: set[str]) -> set[str]:
        for d in dependentes[k] - vistos:
            vistos.add(d)
            alcance(d, vistos)
        return vistos

    return {k: len(alcance(k, set())) for k in marcos}


def main() -> None:
    frentes, marcos = carregar(ARQUIVO)
    erros = validar(frentes, marcos)
    if "--check" in sys.argv:
        for e in erros:
            print("ERRO:", e)
        sys.exit(1 if erros else 0)

    peso = destrava(marcos)
    ativa: Item | None = None
    livres: list[Item] = []
    bloqueadas: list[Item] = []
    concluidas: list[str] = []
    for nome, f in frentes.items():
        m = marco_atual(f)
        if m is None:
            concluidas.append(nome)
            continue
        chave = f"{nome}.{m['id']}"
        item: Item = (nome, chave, f.get("proximo_passo"), faltando(m, marcos), peso[chave])
        if f.get("ativa"):
            ativa = item
        elif item[3]:
            bloqueadas.append(item)
        else:
            livres.append(item)

    print("ROTA (docs/frentes.yaml)")
    if ativa:
        print(f"\nAtiva: {ativa[0]}, marco {ativa[1]}\n  próximo passo: {ativa[2]}")
    else:
        print("\nNenhuma frente ativa: escolha uma das livres e marque ativa: true.")
    if livres:
        print("\nLivres, da que destrava mais para a que destrava menos:")
        for _, chave, passo, _, n in sorted(livres, key=lambda i: -i[4]):
            print(f"  {chave} (destrava {n}) | próximo passo: {passo}")
    if bloqueadas:
        print("\nBloqueadas:")
        for _, chave, _, falta, _ in bloqueadas:
            print(f"  {chave} espera {', '.join(falta)}")
    if concluidas:
        print(f"\nConcluídas: {', '.join(concluidas)}")
    for e in erros:
        print("ERRO:", e)


if __name__ == "__main__":
    main()
