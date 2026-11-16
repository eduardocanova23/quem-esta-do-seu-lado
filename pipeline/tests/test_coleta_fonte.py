"""O que a coleta baixa: conjuntos, URLs e anos quentes, com os bytes reais de legislaturas.csv."""

from datetime import date
from pathlib import Path

import pytest

from pipeline.coleta.fonte import BASE_URL, anos_quentes, nome_arquivo, url

LEGISLATURAS = (Path(__file__).parent / "fixtures" / "arquivos" / "legislaturas.csv").read_bytes()


def test_anos_quentes_57() -> None:
    assert anos_quentes(LEGISLATURAS, date(2026, 11, 16)) == [2023, 2024, 2025, 2026]


def test_anos_quentes_ultimo_dia_57() -> None:
    assert anos_quentes(LEGISLATURAS, date(2027, 1, 31)) == [2023, 2024, 2025, 2026, 2027]


def test_anos_quentes_58() -> None:
    assert anos_quentes(LEGISLATURAS, date(2027, 2, 1)) == [2027]


def test_sem_legislatura_vigente() -> None:
    with pytest.raises(ValueError, match="nenhuma legislatura vigente"):
        anos_quentes(LEGISLATURAS, date(2031, 2, 1))


def test_url() -> None:
    base = "https://dadosabertos.camara.leg.br/arquivos"
    assert BASE_URL == base
    assert url(BASE_URL, "deputados", None) == f"{base}/deputados/csv/deputados.csv"
    assert url(BASE_URL, "votacoes", 2025) == f"{base}/votacoes/csv/votacoes-2025.csv"


def test_nome_arquivo() -> None:
    assert nome_arquivo("votacoesVotos", 2026) == "votacoesVotos-2026.csv.gz"
    assert nome_arquivo("deputados", None) == "deputados.csv.gz"
