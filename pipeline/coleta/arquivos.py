"""Passo de coleta: os arquivos em lote da Câmara do dia para raw/arquivos/<data>/.

Uso: python -m pipeline.coleta.arquivos --data AAAA-MM-DD [--raiz dados/raw]

Regras (docs/superpowers/specs/2026-11-16-passos-coleta-arquivos-design.md):
- Só baixa quando a data lógica é hoje (Brasília): a fonte não guarda o passado, e gravar o arquivo de hoje
  com uma data antiga seria uma data falsa.
- A data com manifesto.json já foi processada: rodar de novo não faz nada (idempotência).
- Arquivo com o mesmo sha256 da última coleta não ganha cópia: a entrada aponta para a data onde ele está.
- manifesto.parcial.json guarda o que já chegou inteiro; uma queda retoma dali. Só o manifesto.json final
  diz que a data foi processada. O que estava ausente é pedido de novo na retomada: um 404 de minutos, enquanto a
  Câmara refaz os arquivos, não pode travar o dia.
- Ausente só vale para o ano de D (o ano novo pode ainda não ter arquivo). 404 em ano passado é falha.
- Uma execução por vez (trava em raw/arquivos/.trava): duas escrevendo no mesmo .parcial misturariam os bytes.
"""

import argparse
import fcntl
import gzip
import json
import os
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from pipeline.coleta.fonte import BASE_URL, CONJUNTOS_POR_ANO, CONJUNTOS_SEM_ANO, anos_quentes, nome_arquivo, url
from pipeline.coleta.http import Ausente, FalhaDeColeta, baixar

FUSO = ZoneInfo("America/Sao_Paulo")
FORMATO = 1
Entrada = dict[str, Any]


class DataInvalida(Exception):
    """A data lógica não pode ser coletada agora."""


@dataclass(frozen=True)
class Resumo:
    novos: int
    iguais: int
    ausentes: int
    nada_a_fazer: bool


def _gravar_json(caminho: Path, conteudo: object) -> None:
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_text(json.dumps(conteudo, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporario, caminho)


class _Historico:
    """A última coleta anterior de cada arquivo, lida dos manifestos das datas anteriores."""

    def __init__(self, raiz: Path, data: date) -> None:
        pastas = (raiz / "arquivos").glob("*/manifesto.json")
        self._manifestos = sorted((p for p in pastas if p.parent.name < data.isoformat()), reverse=True)
        self._lidos: dict[Path, list[Entrada]] = {}

    def ultima(self, conjunto: str, ano: int | None) -> Entrada | None:
        for caminho in self._manifestos:
            if caminho not in self._lidos:
                self._lidos[caminho] = json.loads(caminho.read_text(encoding="utf-8"))["arquivos"]
            for e in self._lidos[caminho]:
                if e["conjunto"] == conjunto and e["ano"] == ano and e["status"] != "ausente":
                    return e
        return None


def _coletar_um(
    conjunto: str,
    ano: int | None,
    pasta: Path,
    data: date,
    base: str,
    agora: Callable[[], datetime],
    historico: _Historico,
    esperas: Sequence[float],
) -> Entrada:
    endereco = url(base, conjunto, ano)
    nome = nome_arquivo(conjunto, ano)
    entrada: Entrada = {"conjunto": conjunto, "ano": ano, "url": endereco}
    parcial = pasta / (nome + ".parcial")
    try:
        baixado = baixar(endereco, parcial, esperas=esperas)
    except Ausente:
        if ano != data.year:
            raise FalhaDeColeta(
                f"{endereco}: 404 num arquivo que tem de existir (só o ano de {data.year} pode faltar)"
            ) from None
        vazio = dict.fromkeys(("sha256", "bytes", "etag", "last_modified", "em"))
        return entrada | vazio | {"status": "ausente", "coletado_em": agora().isoformat(timespec="seconds")}
    anterior = historico.ultima(conjunto, ano)
    if anterior is not None and anterior["sha256"] == baixado.sha256:
        parcial.unlink()
        status, em = "igual", anterior["em"]
    else:
        os.replace(parcial, pasta / nome)
        status, em = "novo", data.isoformat()
    return entrada | {
        "status": status,
        "sha256": baixado.sha256,
        "bytes": baixado.bytes,
        "etag": baixado.etag,
        "last_modified": baixado.last_modified,
        "coletado_em": agora().isoformat(timespec="seconds"),
        "em": em,
    }


def coletar(
    data: date,
    raiz: Path,
    *,
    base: str = BASE_URL,
    agora: Callable[[], datetime] = lambda: datetime.now(FUSO),
    anos_frios: Sequence[int] = (),
    esperas: Sequence[float] = (2.0, 8.0, 30.0),
) -> Resumo:
    pasta = raiz / "arquivos" / data.isoformat()
    final = pasta / "manifesto.json"
    if final.exists():
        return Resumo(0, 0, 0, nada_a_fazer=True)
    hoje = agora().astimezone(FUSO).date()
    if data < hoje:
        raise DataInvalida(f"{data.isoformat()} não tem raw, e a fonte não guarda o passado: só dá para coletar hoje")
    if data > hoje:
        raise DataInvalida(f"{data.isoformat()} é data futura (hoje é {hoje.isoformat()})")

    (raiz / "arquivos").mkdir(parents=True, exist_ok=True)
    with open(raiz / "arquivos" / ".trava", "w") as trava:
        try:
            fcntl.flock(trava, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise FalhaDeColeta("outra coleta está rodando neste raw; espere ela terminar") from None
        if final.exists():  # a outra execução pode ter terminado enquanto esta esperava
            return Resumo(0, 0, 0, nada_a_fazer=True)
        return _coletar_travado(data, raiz, pasta, final, base, agora, anos_frios, esperas)


def _coletar_travado(
    data: date,
    raiz: Path,
    pasta: Path,
    final: Path,
    base: str,
    agora: Callable[[], datetime],
    anos_frios: Sequence[int],
    esperas: Sequence[float],
) -> Resumo:
    pasta.mkdir(parents=True, exist_ok=True)
    parcial = pasta / "manifesto.parcial.json"
    feitas: dict[tuple[str, int | None], Entrada] = {}
    if parcial.exists():
        for e in json.loads(parcial.read_text(encoding="utf-8")):
            feitas[(e["conjunto"], e["ano"])] = e
    historico = _Historico(raiz, data)

    def um(conjunto: str, ano: int | None) -> Entrada:
        if (conjunto, ano) not in feitas or feitas[(conjunto, ano)]["status"] == "ausente":
            feitas[(conjunto, ano)] = _coletar_um(conjunto, ano, pasta, data, base, agora, historico, esperas)
            _gravar_json(parcial, list(feitas.values()))
        return feitas[(conjunto, ano)]

    for conjunto in CONJUNTOS_SEM_ANO:
        um(conjunto, None)
    legislaturas = feitas[("legislaturas", None)]
    origem = raiz / "arquivos" / legislaturas["em"] / nome_arquivo("legislaturas", None)
    quentes = anos_quentes(gzip.decompress(origem.read_bytes()), data)
    anos = sorted(set(quentes) | set(anos_frios))
    for conjunto in CONJUNTOS_POR_ANO:
        status = [um(conjunto, ano)["status"] for ano in anos]  # lista, não gerador: o all() pararia no 1º
        if all(s == "ausente" for s in status):
            raise FalhaDeColeta(f"{conjunto}: nenhum dos anos {anos} veio (404 em todos); o endereço mudou?")

    arquivos = [feitas[(c, None)] for c in CONJUNTOS_SEM_ANO]
    arquivos += [feitas[(c, a)] for c in CONJUNTOS_POR_ANO for a in anos]
    conteudo = {
        "formato": FORMATO,
        "data": data.isoformat(),
        "anos_quentes": quentes,
        "anos_frios": sorted(anos_frios),
        "arquivos": arquivos,
    }
    _gravar_json(final, conteudo)
    parcial.unlink()
    contagem = [e["status"] for e in arquivos]
    return Resumo(contagem.count("novo"), contagem.count("igual"), contagem.count("ausente"), nada_a_fazer=False)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Arquivos em lote da Câmara do dia para raw/arquivos/<data>/")
    parser.add_argument("--data", required=True, type=date.fromisoformat, help="data lógica, AAAA-MM-DD")
    parser.add_argument("--raiz", default="dados/raw", type=Path, help="pasta do raw (padrão: dados/raw)")
    args = parser.parse_args(argv)
    try:
        resumo = coletar(args.data, args.raiz, base=os.environ.get("CAMARA_ARQUIVOS_URL", BASE_URL))
    except (DataInvalida, FalhaDeColeta, ValueError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    if resumo.nada_a_fazer:
        print(f"{args.data.isoformat()}: nada a fazer, a data já foi coletada")
    else:
        print(f"{args.data.isoformat()}: {resumo.novos} novos, {resumo.iguais} iguais, {resumo.ausentes} ausentes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
