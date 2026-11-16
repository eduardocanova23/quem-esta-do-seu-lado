"""Spike #44: dado sintético com o volume da 57ª a partir de db/marts/amostra/.

Replica os 5 deputados da amostra até 644 (ids novos, mesmo conteúdo de votos e
placar) e cria 26.598 proposições reciclando as ementas da amostra. Só serve
para medir o build; não é dado publicável.

Uso: uv run python -I spike/build-astro/gerar_dados.py <amostra> <saida>
"""

import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

N_DEPUTADOS = 644  # deputados com voto na 57ª, raw de 16/11/2026 (ADR 0002)
N_PROPOSICOES = 26_598  # PL, PLP, PEC, PDL e MPV de 2023 a 2026, mesmo raw
SEMENTE = 44


def ler(amostra: Path, nome: str) -> list[dict[str, str]]:
    with (amostra / f"{nome}.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main(amostra: Path, saida: Path) -> None:
    random.seed(SEMENTE)
    perfis = ler(amostra, "perfil_deputado")
    votacoes = {v["votacao_id"]: v for v in ler(amostra, "votacao")}
    eixos = ler(amostra, "eixo")
    votos: dict[str, list[dict[str, str]]] = defaultdict(list)
    for v in ler(amostra, "voto_deputado"):
        votos[v["deputado_id"]].append(v)
    placar: dict[str, list[dict[str, str]]] = defaultdict(list)
    for p in ler(amostra, "placar_eixo_deputado"):
        placar[p["deputado_id"]].append(p)
    filiacao = {f["deputado_id"]: f["partido_sigla"] for f in ler(amostra, "filiacao_deputado")}

    pasta_dep = saida / "deputados"
    pasta_dep.mkdir(parents=True, exist_ok=True)
    indice, ranking = [], []
    for i in range(N_DEPUTADOS):
        base = perfis[i % len(perfis)]
        dep_id = str(900_000 + i)
        lista_votos = [
            {
                "votacao_id": v["votacao_id"],
                "data": votacoes[v["votacao_id"]]["data"],
                "rotulo": votacoes[v["votacao_id"]]["proposicao_rotulo"],
                "resumo": votacoes[v["votacao_id"]]["resumo"],
                "voto": v["voto"],
                "bancada": v["bancada_nome"],
                "orientacao": v["bancada_orientacao"],
                "colegas": [v["colegas_sim"], v["colegas_nao"], v["colegas_outros"]],
            }
            for v in votos[base["deputado_id"]]
            if v["votacao_id"] in votacoes
        ]
        placar_dep = [
            {"eixo": p["eixo_id"], "k_pos": int(p["k_positivo"]), "k_neg": int(p["k_negativo"]), "n": int(p["n"])}
            for p in placar[base["deputado_id"]]
        ]
        doc = {
            "id": dep_id,
            "nome": f"{base['nome_parlamentar']} {i}",
            "uf": base["uf"],
            "partido": filiacao.get(base["deputado_id"], ""),
            "placar": placar_dep,
            "votos": lista_votos,
        }
        (pasta_dep / f"{dep_id}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        indice.append(dep_id)
        ranking.append({"id": dep_id, "placar": placar_dep})

    ementas = [v for v in votacoes.values() if v["ementa"]]
    proposicoes = []
    for i in range(N_PROPOSICOES):
        v = random.choice(ementas)
        proposicoes.append(
            {
                "id": str(3_000_000 + i),
                "rotulo": f"PL {i}/2025",
                "resumo": v["resumo"],
                "ementa": v["ementa"],
                "autores": random.sample(indice, k=random.randint(1, 5)),
            }
        )

    (saida / "indice.json").write_text(json.dumps(indice), encoding="utf-8")
    (saida / "ranking.json").write_text(json.dumps(ranking), encoding="utf-8")
    (saida / "proposicoes.json").write_text(json.dumps(proposicoes, ensure_ascii=False), encoding="utf-8")
    (saida / "eixos.json").write_text(json.dumps(eixos, ensure_ascii=False), encoding="utf-8")
    sem_votos = sum(1 for i in range(len(perfis)) if not votos[perfis[i]["deputado_id"]])
    print(f"{N_DEPUTADOS} deputados, {N_PROPOSICOES} proposições, {len(eixos)} eixos; perfis sem voto: {sem_votos}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
