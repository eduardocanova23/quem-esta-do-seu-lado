"""Confere tabelas de marts contra o contrato em db/marts/contrato.yaml.

O contrato é a fonte única do que o site recebe: cada mart, a chave, as colunas, o tipo, se pode ser nula,
os valores permitidos e as referências entre marts. A publicação só troca os marts se esta checagem não
achar erro; a amostra do site passa pela mesma checagem no CI.

Uso: python -m pipeline.qualidade.contrato <pasta com um CSV por mart>
"""

import csv
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

Linha = dict[str, str]
Tabelas = dict[str, list[Linha]]

CONTRATO_PADRAO = Path(__file__).resolve().parents[2] / "db" / "marts" / "contrato.yaml"


def _inteiro(v: str) -> bool:
    return re.fullmatch(r"-?\d+", v) is not None


def _real(v: str) -> bool:
    return re.fullmatch(r"-?\d+(\.\d+)?", v) is not None


def _data(v: str) -> bool:
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) is not None


def _data_hora(v: str) -> bool:
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", v) is not None


# Como cada tipo do contrato aparece no CSV. Vazio é sempre nulo e é checado à parte.
TIPOS: dict[str, Callable[[str], bool]] = {
    "texto": lambda v: True,
    "inteiro": _inteiro,
    "real": _real,
    "data": _data,
    "data_hora": _data_hora,
    "booleano": lambda v: v in ("true", "false"),
}


def carregar_contrato(caminho: Path = CONTRATO_PADRAO) -> dict[str, Any]:
    with caminho.open(encoding="utf-8") as f:
        contrato: dict[str, Any] = yaml.safe_load(f)
    return contrato


def carregar_csvs(pasta: Path) -> Tabelas:
    """Um CSV por mart, com o nome do mart: votacao.csv vira a tabela votacao."""
    tabelas: Tabelas = {}
    for arquivo in sorted(pasta.glob("*.csv")):
        with arquivo.open(encoding="utf-8", newline="") as f:
            tabelas[arquivo.stem] = list(csv.DictReader(f))
    return tabelas


def validar_contrato(contrato: dict[str, Any]) -> list[str]:
    """Erros do próprio contrato: chave, tipo, descrição e referência."""
    erros: list[str] = []
    marts: dict[str, Any] = contrato.get("marts") or {}
    for nome, mart in marts.items():
        colunas: dict[str, Any] = mart.get("colunas") or {}
        if not mart.get("uma_linha_por"):
            erros.append(f"{nome}: sem 'uma_linha_por'")
        for c in mart.get("chave") or []:
            if c not in colunas:
                erros.append(f"{nome}: chave usa coluna inexistente: {c}")
            elif colunas[c].get("nulo"):
                erros.append(f"{nome}.{c}: coluna de chave não pode ser nula")
        if not mart.get("chave"):
            erros.append(f"{nome}: sem chave")
        for c, spec in colunas.items():
            if spec.get("tipo") not in TIPOS:
                erros.append(f"{nome}.{c}: tipo '{spec.get('tipo')}' não existe")
            if not spec.get("descricao"):
                erros.append(f"{nome}.{c}: sem descrição")
            ref = spec.get("referencia")
            if ref:
                alvo_mart, _, alvo_col = ref.partition(".")
                if alvo_col not in (marts.get(alvo_mart) or {}).get("colunas", {}):
                    erros.append(f"{nome}.{c}: referência para coluna inexistente: {ref}")
    return erros


def validar(contrato: dict[str, Any], tabelas: Tabelas) -> list[str]:
    """Erros das tabelas contra o contrato. Lista vazia quer dizer que pode publicar."""
    erros = validar_contrato(contrato)
    marts: dict[str, Any] = contrato.get("marts") or {}
    for nome in marts:
        if nome not in tabelas:
            erros.append(f"{nome}: mart faltando")
    for nome in tabelas:
        if nome not in marts:
            erros.append(f"{nome}: mart fora do contrato")

    for nome, linhas in tabelas.items():
        if nome not in marts:
            continue
        colunas: dict[str, Any] = marts[nome]["colunas"]
        presentes = set(linhas[0]) if linhas else set(colunas)
        for c in colunas:
            if c not in presentes:
                erros.append(f"{nome}: coluna faltando: {c}")
        for c in sorted(presentes - set(colunas)):
            erros.append(f"{nome}: coluna fora do contrato: {c}")

        chaves: set[tuple[str, ...]] = set()
        for i, linha in enumerate(linhas, start=1):
            for c, spec in colunas.items():
                if c not in linha:
                    continue
                v = linha[c]
                if v == "":
                    if not spec.get("nulo"):
                        erros.append(f"{nome} linha {i}: {c} vazia")
                    continue
                if not TIPOS[spec["tipo"]](v):
                    erros.append(f"{nome} linha {i}: {c} '{v}' não é {spec['tipo']}")
                if "valores" in spec and v not in [str(x) for x in spec["valores"]]:
                    erros.append(f"{nome} linha {i}: {c} '{v}' fora de {spec['valores']}")
            chave = tuple(linha.get(c, "") for c in marts[nome]["chave"])
            if chave in chaves:
                erros.append(f"{nome}: chave repetida {chave}")
            chaves.add(chave)

    erros += _referencias(marts, tabelas)
    return erros


def _referencias(marts: dict[str, Any], tabelas: Tabelas) -> list[str]:
    erros: list[str] = []
    for nome, linhas in tabelas.items():
        for c, spec in (marts.get(nome) or {}).get("colunas", {}).items():
            ref = spec.get("referencia")
            if not ref:
                continue
            alvo_mart, _, alvo_col = ref.partition(".")
            existentes = {linha.get(alvo_col) for linha in tabelas.get(alvo_mart, [])}
            for i, linha in enumerate(linhas, start=1):
                v = linha.get(c, "")
                if v != "" and v not in existentes:
                    erros.append(f"{nome} linha {i}: {c} '{v}' não existe em {ref}")
    return erros


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("uso: python -m pipeline.qualidade.contrato <pasta com um CSV por mart>", file=sys.stderr)
        return 2
    erros = validar(carregar_contrato(), carregar_csvs(Path(argv[0])))
    for e in erros:
        print(e, file=sys.stderr)
    print(f"{len(erros)} erro(s)")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
