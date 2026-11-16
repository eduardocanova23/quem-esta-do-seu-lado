"""O passo de coleta dos arquivos em lote: idempotente, sem cópia repetida, sem data falsa, sem manifesto mentiroso."""

import gzip
import hashlib
import json
from datetime import date, datetime
from pathlib import Path

import pytest

from pipeline.coleta.arquivos import FUSO, DataInvalida, Resumo, coletar, main
from pipeline.coleta.fonte import CONJUNTOS_POR_ANO, CONJUNTOS_SEM_ANO
from pipeline.coleta.http import FalhaDeColeta
from pipeline.tests.conftest import Rota, Servidor

FIXTURES = Path(__file__).parent / "fixtures" / "arquivos"
ANOS = (2023, 2024, 2025, 2026)
SEM_ESPERA = (0.0, 0.0, 0.0)
D16, D17 = date(2026, 11, 16), date(2026, 11, 17)


def as_9h(dia: date) -> datetime:
    return datetime(dia.year, dia.month, dia.day, 9, 0, tzinfo=FUSO)


def caminho(conjunto: str, ano: int | None = None) -> str:
    return f"/{conjunto}/csv/{conjunto}{'' if ano is None else f'-{ano}'}.csv"


def servir_tudo(servidor: Servidor) -> None:
    for c in CONJUNTOS_SEM_ANO:
        servidor.rotas[caminho(c)] = Rota(corpo=(FIXTURES / f"{c}.csv").read_bytes())
    for c in CONJUNTOS_POR_ANO:
        for ano in ANOS:
            servidor.rotas[caminho(c, ano)] = Rota(corpo=(FIXTURES / f"{c}.csv").read_bytes())


def rodar(servidor: Servidor, raiz: Path, data: date, hoje: date | None = None) -> Resumo:
    return coletar(data, raiz, base=servidor.base, agora=lambda: as_9h(hoje or data), esperas=SEM_ESPERA)


def retrato(pasta: Path) -> dict[str, bytes]:
    return {str(p.relative_to(pasta)): p.read_bytes() for p in sorted(pasta.rglob("*")) if p.is_file()}


def manifesto(raiz: Path, dia: date) -> dict[str, object]:
    arquivo = raiz / "arquivos" / dia.isoformat() / "manifesto.json"
    conteudo: dict[str, object] = json.loads(arquivo.read_text(encoding="utf-8"))
    return conteudo


def entradas(raiz: Path, dia: date) -> list[dict[str, object]]:
    arquivos = manifesto(raiz, dia)["arquivos"]
    assert isinstance(arquivos, list)
    return arquivos


def test_idempotente(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    primeiro = rodar(servidor, tmp_path, D16)
    antes, pedidos = retrato(tmp_path), len(servidor.pedidos)
    segundo = rodar(servidor, tmp_path, D16)
    assert retrato(tmp_path) == antes
    assert len(servidor.pedidos) == pedidos
    assert primeiro.nada_a_fazer is False and segundo.nada_a_fazer is True
    assert primeiro.novos == 2 + len(CONJUNTOS_POR_ANO) * len(ANOS)
    assert manifesto(tmp_path, D16)["anos_quentes"] == list(ANOS)


def test_mesmo_conteudo_no_dia_seguinte(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    rodar(servidor, tmp_path, D16)
    rodar(servidor, tmp_path, D17)
    assert sorted(p.name for p in (tmp_path / "arquivos" / "2026-11-17").iterdir()) == ["manifesto.json"]
    for e in entradas(tmp_path, D17):
        assert e["status"] == "igual" and e["em"] == "2026-11-16"
    votos = next(e for e in entradas(tmp_path, D17) if e["conjunto"] == "votacoesVotos" and e["ano"] == 2026)
    gz = tmp_path / "arquivos" / "2026-11-16" / "votacoesVotos-2026.csv.gz"
    assert hashlib.sha256(gzip.decompress(gz.read_bytes())).hexdigest() == votos["sha256"]


def test_conteudo_diferente(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    rodar(servidor, tmp_path, D16)
    servidor.rotas[caminho("votacoes", 2026)] = Rota(corpo=b'"id"\n"novo"\n')
    rodar(servidor, tmp_path, D17)
    e = next(e for e in entradas(tmp_path, D17) if e["conjunto"] == "votacoes" and e["ano"] == 2026)
    assert e["status"] == "novo" and e["em"] == "2026-11-17"
    gz = tmp_path / "arquivos" / "2026-11-17" / "votacoes-2026.csv.gz"
    assert gzip.decompress(gz.read_bytes()) == b'"id"\n"novo"\n'


def test_data_passada_sem_raw(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    with pytest.raises(DataInvalida, match="não guarda o passado"):
        rodar(servidor, tmp_path, date(2026, 11, 15), hoje=D16)
    assert servidor.pedidos == []


def test_data_futura(servidor: Servidor, tmp_path: Path) -> None:
    with pytest.raises(DataInvalida, match="futura"):
        rodar(servidor, tmp_path, D17, hoje=D16)
    assert servidor.pedidos == []


def test_data_passada_com_raw(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    rodar(servidor, tmp_path, D16)
    servidor.pedidos.clear()
    assert rodar(servidor, tmp_path, D16, hoje=date(2026, 11, 18)).nada_a_fazer is True
    assert servidor.pedidos == []


def test_ano_ausente(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    del servidor.rotas[caminho("proposicoes", 2026)]
    resumo = rodar(servidor, tmp_path, D16)
    e = next(e for e in entradas(tmp_path, D16) if e["conjunto"] == "proposicoes" and e["ano"] == 2026)
    assert e["status"] == "ausente" and e["sha256"] is None and e["em"] is None
    assert resumo.ausentes == 1


def test_conjunto_sem_nenhum_ano(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    for ano in ANOS:
        del servidor.rotas[caminho("votacoes", ano)]
    with pytest.raises(FalhaDeColeta, match="votacoes"):
        rodar(servidor, tmp_path, D16)
    assert not (tmp_path / "arquivos" / "2026-11-16" / "manifesto.json").exists()


def test_legislaturas_404(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    del servidor.rotas[caminho("legislaturas")]
    with pytest.raises(FalhaDeColeta):
        rodar(servidor, tmp_path, D16)


def test_queda_e_retomada(servidor: Servidor, tmp_path: Path) -> None:
    servir_tudo(servidor)
    servidor.rotas[caminho("votacoesVotos", 2023)].falhas_antes = 99
    with pytest.raises(FalhaDeColeta):
        rodar(servidor, tmp_path, D16)
    pasta = tmp_path / "arquivos" / "2026-11-16"
    assert not (pasta / "manifesto.json").exists()
    assert list(pasta.glob("*.parcial")) == []
    servidor.rotas[caminho("votacoesVotos", 2023)].falhas_antes = 0
    servidor.pedidos.clear()
    rodar(servidor, tmp_path, D16)
    assert caminho("legislaturas") not in servidor.pedidos
    assert caminho("deputados") not in servidor.pedidos
    assert caminho("votacoesVotos", 2023) in servidor.pedidos
    assert (pasta / "manifesto.json").exists() and not (pasta / "manifesto.parcial.json").exists()


def test_main_codigo_de_saida(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--data", "2026-11-15", "--raiz", str(tmp_path)]) == 1
    assert "erro:" in capsys.readouterr().err
