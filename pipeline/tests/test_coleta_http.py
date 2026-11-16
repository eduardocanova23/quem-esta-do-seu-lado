"""Download de um arquivo: o que vem gravado é exatamente o que a fonte mandou, ou nada."""

import gzip
import hashlib
from pathlib import Path

import pytest

from pipeline.coleta.http import Ausente, FalhaDeColeta, baixar
from pipeline.tests.conftest import Rota, Servidor

CORPO = b'"id";"nome"\n"1";"Fulano de Tal"\n' * 50
SEM_ESPERA = (0.0, 0.0, 0.0)


def test_baixa_e_comprime(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(corpo=CORPO)
    destino = tmp_path / "a.parcial"
    baixado = baixar(f"{servidor.base}/a.csv", destino, esperas=SEM_ESPERA)
    assert gzip.decompress(destino.read_bytes()) == CORPO
    assert baixado.sha256 == hashlib.sha256(CORPO).hexdigest()
    assert baixado.bytes == len(CORPO)


def test_gzip_reprodutivel(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(corpo=CORPO)
    baixar(f"{servidor.base}/a.csv", tmp_path / "um", esperas=SEM_ESPERA)
    baixar(f"{servidor.base}/a.csv", tmp_path / "dois", esperas=SEM_ESPERA)
    assert (tmp_path / "um").read_bytes() == (tmp_path / "dois").read_bytes()


def test_404_ausente(servidor: Servidor, tmp_path: Path) -> None:
    destino = tmp_path / "a.parcial"
    with pytest.raises(Ausente):
        baixar(f"{servidor.base}/nao-existe.csv", destino, esperas=SEM_ESPERA)
    assert not destino.exists()
    assert len(servidor.pedidos) == 1


def test_5xx_tenta_de_novo(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(corpo=CORPO, falhas_antes=2)
    baixar(f"{servidor.base}/a.csv", tmp_path / "a.parcial", esperas=SEM_ESPERA)
    assert len(servidor.pedidos) == 3


def test_5xx_esgota(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(corpo=CORPO, falhas_antes=10)
    destino = tmp_path / "a.parcial"
    with pytest.raises(FalhaDeColeta):
        baixar(f"{servidor.base}/a.csv", destino, esperas=SEM_ESPERA)
    assert len(servidor.pedidos) == 4
    assert not destino.exists()


def test_outro_4xx_nao_tenta_de_novo(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(status=403)
    with pytest.raises(FalhaDeColeta):
        baixar(f"{servidor.base}/a.csv", tmp_path / "a.parcial", esperas=SEM_ESPERA)
    assert len(servidor.pedidos) == 1


def test_corte_no_meio(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(corpo=CORPO, cortar_em=5)
    destino = tmp_path / "a.parcial"
    with pytest.raises(FalhaDeColeta, match="cortad"):
        baixar(f"{servidor.base}/a.csv", destino, esperas=SEM_ESPERA)
    assert not destino.exists()


def test_guarda_etag(servidor: Servidor, tmp_path: Path) -> None:
    servidor.rotas["/a.csv"] = Rota(corpo=CORPO, cabecalhos={"ETag": '"x"', "Last-Modified": "Mon, 16 Nov 2026"})
    baixado = baixar(f"{servidor.base}/a.csv", tmp_path / "a.parcial", esperas=SEM_ESPERA)
    assert baixado.etag == '"x"'
    assert baixado.last_modified == "Mon, 16 Nov 2026"
