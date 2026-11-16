"""O que a coleta dos arquivos em lote baixa: conjuntos, endereços e anos.

Conferido na fonte em 16/11/2026: os conjuntos sem ano só existem sem ano (a versão com ano dá 404), e os
conjuntos por ano dão 404 no ano que ainda não começou. legislaturas.csv vem em UTF-8 com BOM, separado por ";".
"""

import csv
from datetime import date

BASE_URL = "https://dadosabertos.camara.leg.br/arquivos"

# legislaturas primeiro: os anos quentes saem dele.
CONJUNTOS_SEM_ANO: tuple[str, ...] = ("legislaturas", "deputados")
CONJUNTOS_POR_ANO: tuple[str, ...] = (
    "votacoes",
    "votacoesVotos",
    "votacoesOrientacoes",
    "votacoesProposicoes",
    "votacoesObjetos",
    "proposicoes",
    "proposicoesAutores",
    "proposicoesTemas",
)


def url(base: str, conjunto: str, ano: int | None) -> str:
    sufixo = "" if ano is None else f"-{ano}"
    return f"{base}/{conjunto}/csv/{conjunto}{sufixo}.csv"


def nome_arquivo(conjunto: str, ano: int | None) -> str:
    sufixo = "" if ano is None else f"-{ano}"
    return f"{conjunto}{sufixo}.csv.gz"


def anos_quentes(legislaturas_csv: bytes, data: date) -> list[int]:
    """Do ano em que começou a legislatura vigente em `data` até o ano de `data`."""
    for linha in csv.DictReader(legislaturas_csv.decode("utf-8-sig").splitlines(), delimiter=";"):
        inicio, fim = date.fromisoformat(linha["dataInicio"]), date.fromisoformat(linha["dataFim"])
        if inicio <= data <= fim:
            return list(range(inicio.year, data.year + 1))
    raise ValueError(f"nenhuma legislatura vigente em {data.isoformat()}")
