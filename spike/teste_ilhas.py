"""Abre /teste/ num Chromium e exercita o ComboBox (React Aria), o Dialog (Radix) e o placar.

Uso: python -I teste_ilhas.py <dist>
Sai com código 1 se algum passo falhar. Imprime erros de console e requisições.
"""

import functools
import http.server
import sys
import threading

from playwright.sync_api import expect, sync_playwright


def main(dist: str) -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=dist)
    handler.log_message = lambda *a: None  # type: ignore[method-assign]
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}"
    erros: list[str] = []
    pedidos: list[str] = []
    falhas = 0
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page()
        pag.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
        pag.on("pageerror", lambda e: erros.append(str(e)))
        pag.goto(f"{base}/teste/")
        pag.wait_for_load_state("networkidle")
        pag.on("request", lambda r: pedidos.append(r.url))  # só o que sai depois de carregar
        passos = [
            (
                "combobox filtra",
                lambda: (pag.get_by_test_id("busca").fill("tab"), expect(pag.get_by_role("option")).to_have_count(1)),
            ),
            (
                "combobox escolhe",
                lambda: (
                    pag.get_by_role("option").first.click(),
                    expect(pag.get_by_test_id("escolhido")).to_have_text("escolhido: Tabata Amaral"),
                ),
            ),
            (
                "dialog abre",
                lambda: (pag.get_by_test_id("abrir").click(), expect(pag.get_by_role("dialog")).to_be_visible()),
            ),
            (
                "dialog fecha com Esc",
                lambda: (pag.keyboard.press("Escape"), expect(pag.get_by_role("dialog")).to_have_count(0)),
            ),
            (
                "placar recalcula",
                lambda: (
                    pag.get_by_role("button", name="a favor").click(),
                    expect(pag.get_by_text("votou na sua direção em 7 de 9")).to_be_visible(),
                ),
            ),
        ]
        for nome, passo in passos:
            try:
                passo()
                print(f"ok    {nome}")
            except Exception as e:  # noqa: BLE001
                falhas += 1
                print(f"FALHA {nome}: {str(e).splitlines()[0]}")
        nav.close()
    servidor.shutdown()
    print(f"erros de console: {erros or 'nenhum'}")
    print(f"requisições depois de carregar: {pedidos or 'nenhuma'}")
    return 1 if falhas or erros else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
