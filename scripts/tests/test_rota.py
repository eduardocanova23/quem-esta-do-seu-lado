"""Cada regra do `rota.py --check`: se uma validação sumir, o teste dela falha."""

from pathlib import Path

import pytest

import rota

ROTA_VALIDA = """
frentes:
  base:
    ativa: true
    proximo_passo: fazer a base
    marcos:
      - {id: a, status: andamento}
  depois:
    proximo_passo: fazer o resto
    marcos:
      - {id: b, depende_de: [base.a]}
"""

STATUS_INEXISTENTE = """
frentes:
  f:
    proximo_passo: p
    marcos:
      - {id: a, status: talvez}
"""

DEPENDENCIA_INEXISTENTE = """
frentes:
  f:
    proximo_passo: p
    marcos:
      - {id: a, depende_de: [f.fantasma]}
"""

ANDAMENTO_COM_DEPENDENCIA_ABERTA = """
frentes:
  f:
    proximo_passo: p
    marcos:
      - {id: a}
  g:
    proximo_passo: q
    marcos:
      - {id: b, status: andamento, depende_de: [f.a]}
"""

DUAS_ATIVAS = """
frentes:
  f:
    ativa: true
    proximo_passo: p
    marcos:
      - {id: a}
  g:
    ativa: true
    proximo_passo: q
    marcos:
      - {id: b}
"""

SEM_PROXIMO_PASSO = """
frentes:
  f:
    proximo_passo: ""
    marcos:
      - {id: a}
"""

ATIVA_BLOQUEADA = """
frentes:
  f:
    proximo_passo: p
    marcos:
      - {id: a}
  g:
    ativa: true
    proximo_passo: q
    marcos:
      - {id: b, depende_de: [f.a]}
"""

CICLO = """
frentes:
  f:
    proximo_passo: p
    marcos:
      - {id: a, depende_de: [f.b]}
      - {id: b, depende_de: [f.a]}
"""


def erros_de(tmp_path: Path, conteudo: str) -> list[str]:
    arquivo = tmp_path / "frentes.yaml"
    arquivo.write_text(conteudo, encoding="utf-8")
    frentes, marcos = rota.carregar(arquivo)
    return rota.validar(frentes, marcos)


def test_rota_valida_nao_tem_erros(tmp_path: Path) -> None:
    assert erros_de(tmp_path, ROTA_VALIDA) == []


@pytest.mark.parametrize(
    ("conteudo", "esperado"),
    [
        pytest.param(STATUS_INEXISTENTE, "f.a: status 'talvez' não existe", id="status-inexistente"),
        pytest.param(DEPENDENCIA_INEXISTENTE, "f.a: depende de 'f.fantasma', que não existe", id="dep-inexistente"),
        pytest.param(ANDAMENTO_COM_DEPENDENCIA_ABERTA, "g.b: está 'andamento', mas espera f.a", id="andamento-aberto"),
        pytest.param(DUAS_ATIVAS, "mais de uma frente ativa: f, g", id="duas-ativas"),
        pytest.param(SEM_PROXIMO_PASSO, "f: tem marco aberto e nenhum próximo passo", id="sem-proximo-passo"),
        pytest.param(ATIVA_BLOQUEADA, "g: está ativa, mas o marco atual espera f.a", id="ativa-bloqueada"),
        pytest.param(CICLO, "ciclo: f.a -> f.b -> f.a", id="ciclo"),
    ],
)
def test_rota_invalida_aponta_o_erro(tmp_path: Path, conteudo: str, esperado: str) -> None:
    assert esperado in erros_de(tmp_path, conteudo)
