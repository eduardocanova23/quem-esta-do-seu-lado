"""Servidor HTTP local que faz o papel da Câmara nos testes da coleta: nenhum teste fala com a fonte de verdade."""

import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest


@dataclass
class Rota:
    status: int = 200
    corpo: bytes = b""
    falhas_antes: int = 0  # quantas respostas 500 antes da certa
    cortar_em: int | None = None  # manda o Content-Length inteiro e fecha a conexão depois de N bytes
    cabecalhos: dict[str, str] = field(default_factory=dict)


@dataclass
class Servidor:
    base: str
    rotas: dict[str, Rota]
    pedidos: list[str]


@pytest.fixture
def servidor() -> Iterator[Servidor]:
    rotas: dict[str, Rota] = {}
    pedidos: list[str] = []

    class Atendente(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            pedidos.append(self.path)
            rota = rotas.get(self.path)
            if rota is None:
                self.send_error(404)
                return
            if rota.falhas_antes > 0:
                rota.falhas_antes -= 1
                self.send_error(500)
                return
            if rota.status != 200:
                self.send_error(rota.status)
                return
            self.send_response(200)
            self.send_header("Content-Length", str(len(rota.corpo)))
            for nome, valor in rota.cabecalhos.items():
                self.send_header(nome, valor)
            self.end_headers()
            self.wfile.write(rota.corpo if rota.cortar_em is None else rota.corpo[: rota.cortar_em])
            self.close_connection = True

        def log_message(self, format: str, *args: object) -> None:
            pass

    http = ThreadingHTTPServer(("127.0.0.1", 0), Atendente)
    threading.Thread(target=http.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    try:
        yield Servidor(f"http://127.0.0.1:{http.server_address[1]}", rotas, pedidos)
    finally:
        http.shutdown()
        http.server_close()
