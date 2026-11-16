"""Baixa um arquivo da Câmara para o disco: os bytes que vieram, comprimidos, ou nada.

Três cuidados que o urllib não tem sozinho:
- Corpo cortado: lendo em blocos, o urllib termina sem erro quando a conexão cai antes do Content-Length
  (conferido em 16/11/2026: leu 5 de 100 bytes sem reclamar). Aqui o total é conferido contra o cabeçalho.
- Gzip reprodutível: mtime=0 e sem nome no cabeçalho, para os mesmos bytes darem o mesmo .gz.
- Falha passageira (5xx, timeout, conexão caída) tenta de novo; 404 é ausência; outro 4xx para na hora.
"""

import gzip
import hashlib
import http.client
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

BLOCO = 1 << 20
USER_AGENT = "camara-v2-pipeline"


@dataclass(frozen=True)
class Baixado:
    sha256: str  # dos bytes originais, antes de comprimir
    bytes: int
    etag: str | None
    last_modified: str | None


class Ausente(Exception):
    """A fonte respondeu 404."""


class FalhaDeColeta(Exception):
    """O arquivo não veio inteiro: outro status, 5xx depois das tentativas, timeout ou conexão caída."""


class _Passageira(Exception):
    pass


def _uma_vez(url: str, destino: Path, timeout: float) -> Baixado:
    pedido = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        resposta = urllib.request.urlopen(pedido, timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise Ausente(url) from e
        if 500 <= e.code < 600:
            raise _Passageira(f"HTTP {e.code}") from e
        raise FalhaDeColeta(f"{url}: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException) as e:
        raise _Passageira(str(e)) from e
    soma, total = hashlib.sha256(), 0
    try:
        with resposta, destino.open("wb") as bruto, gzip.GzipFile(filename="", mode="wb", fileobj=bruto, mtime=0) as gz:
            while bloco := resposta.read(BLOCO):
                soma.update(bloco)
                total += len(bloco)
                gz.write(bloco)
            declarado = resposta.headers.get("Content-Length")
            etag, last_modified = resposta.headers.get("ETag"), resposta.headers.get("Last-Modified")
    except (TimeoutError, ConnectionError, http.client.HTTPException) as e:
        raise _Passageira(str(e)) from e
    if declarado is not None and int(declarado) != total:
        raise _Passageira(f"corpo cortado: {total} de {declarado} bytes")
    return Baixado(soma.hexdigest(), total, etag, last_modified)


def baixar(url: str, destino: Path, *, esperas: Sequence[float] = (2.0, 8.0, 30.0), timeout: float = 60.0) -> Baixado:
    """Grava em `destino` o gzip do que `url` serve. Em qualquer erro, `destino` não fica no disco."""
    for tentativa in range(len(esperas) + 1):
        try:
            return _uma_vez(url, destino, timeout)
        except _Passageira as e:
            destino.unlink(missing_ok=True)
            if tentativa == len(esperas):
                raise FalhaDeColeta(f"{url}: {e} (depois de {tentativa + 1} tentativas)") from e
            time.sleep(esperas[tentativa])
        except BaseException:
            destino.unlink(missing_ok=True)
            raise
    raise AssertionError("inalcançável")
