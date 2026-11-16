"""Cada regra do validador do contrato dos marts: se uma checagem sumir, o teste dela falha."""

from pathlib import Path

import yaml

from pipeline.qualidade.contrato import carregar_contrato, carregar_csvs, validar, validar_contrato

CONTRATO = yaml.safe_load("""
versao: 1
marts:
  votacao:
    uma_linha_por: votação
    chave: [votacao_id]
    colunas:
      votacao_id: {tipo: texto, descricao: id da Câmara}
      data: {tipo: data, descricao: dia}
      consenso: {tipo: booleano, nulo: true, descricao: governo e oposição iguais}
  voto_deputado:
    uma_linha_por: mandato × votação
    chave: [deputado_id, votacao_id]
    colunas:
      deputado_id: {tipo: inteiro, descricao: id da Câmara}
      votacao_id: {tipo: texto, referencia: votacao.votacao_id, descricao: votação}
      voto: {tipo: texto, valores: [Sim, Não, Ausente], descricao: o que ele fez}
      colegas_pct: {tipo: real, nulo: true, descricao: fração}
""")


def tabelas_validas() -> dict[str, list[dict[str, str]]]:
    return {
        "votacao": [
            {"votacao_id": "2458405-38", "data": "2025-02-04", "consenso": "true"},
            {"votacao_id": "106701-223", "data": "2025-11-05", "consenso": ""},
        ],
        "voto_deputado": [
            {"deputado_id": "204379", "votacao_id": "2458405-38", "voto": "Sim", "colegas_pct": "0.7"},
            {"deputado_id": "204379", "votacao_id": "106701-223", "voto": "Ausente", "colegas_pct": ""},
        ],
    }


def test_caminho_feliz_sem_erros() -> None:
    assert validar(CONTRATO, tabelas_validas()) == []


def test_mart_faltando() -> None:
    t = tabelas_validas()
    del t["votacao"]
    assert any("votacao: mart faltando" in e for e in validar(CONTRATO, t))


def test_mart_fora_do_contrato() -> None:
    t = tabelas_validas()
    t["extra"] = []
    assert any("extra: mart fora do contrato" in e for e in validar(CONTRATO, t))


def test_coluna_faltando() -> None:
    t = tabelas_validas()
    for linha in t["votacao"]:
        del linha["consenso"]
    assert any("votacao: coluna faltando: consenso" in e for e in validar(CONTRATO, t))


def test_coluna_a_mais() -> None:
    t = tabelas_validas()
    for linha in t["votacao"]:
        linha["sobra"] = "x"
    assert any("votacao: coluna fora do contrato: sobra" in e for e in validar(CONTRATO, t))


def test_tipo_errado() -> None:
    t = tabelas_validas()
    t["voto_deputado"][0]["deputado_id"] = "doze"
    t["votacao"][0]["data"] = "04/02/2025"
    t["votacao"][1]["consenso"] = "talvez"
    t["voto_deputado"][1]["colegas_pct"] = "70%"
    erros = validar(CONTRATO, t)
    assert any("voto_deputado linha 1: deputado_id 'doze' não é inteiro" in e for e in erros)
    assert any("votacao linha 1: data '04/02/2025' não é data" in e for e in erros)
    assert any("votacao linha 2: consenso 'talvez' não é booleano" in e for e in erros)
    assert any("voto_deputado linha 2: colegas_pct '70%' não é real" in e for e in erros)


def test_nulo_proibido() -> None:
    t = tabelas_validas()
    t["votacao"][0]["data"] = ""
    assert any("votacao linha 1: data vazia" in e for e in validar(CONTRATO, t))


def test_valor_fora_da_lista() -> None:
    t = tabelas_validas()
    t["voto_deputado"][0]["voto"] = "Talvez"
    assert any("voto_deputado linha 1: voto 'Talvez' fora de" in e for e in validar(CONTRATO, t))


def test_chave_duplicada() -> None:
    t = tabelas_validas()
    t["votacao"].append(dict(t["votacao"][0]))
    assert any("votacao: chave repetida ('2458405-38',)" in e for e in validar(CONTRATO, t))


def test_referencia_quebrada() -> None:
    t = tabelas_validas()
    t["voto_deputado"][0]["votacao_id"] = "999-1"
    assert any(
        "voto_deputado linha 1: votacao_id '999-1' não existe em votacao.votacao_id" in e for e in validar(CONTRATO, t)
    )


def test_contrato_com_chave_inexistente() -> None:
    ruim = yaml.safe_load("""
versao: 1
marts:
  m:
    uma_linha_por: x
    chave: [fantasma]
    colunas:
      a: {tipo: texto, descricao: a}
""")
    assert any("m: chave usa coluna inexistente: fantasma" in e for e in validar_contrato(ruim))


def test_contrato_com_tipo_desconhecido_e_sem_descricao() -> None:
    ruim = yaml.safe_load("""
versao: 1
marts:
  m:
    uma_linha_por: x
    chave: [a]
    colunas:
      a: {tipo: numero}
""")
    erros = validar_contrato(ruim)
    assert any("m.a: tipo 'numero' não existe" in e for e in erros)
    assert any("m.a: sem descrição" in e for e in erros)


def test_contrato_com_chave_anulavel() -> None:
    ruim = yaml.safe_load("""
versao: 1
marts:
  m:
    uma_linha_por: x
    chave: [a]
    colunas:
      a: {tipo: texto, nulo: true, descricao: a}
""")
    assert any("m.a: coluna de chave não pode ser nula" in e for e in validar_contrato(ruim))


def test_contrato_com_referencia_inexistente() -> None:
    ruim = yaml.safe_load("""
versao: 1
marts:
  m:
    uma_linha_por: x
    chave: [a]
    colunas:
      a: {tipo: texto, referencia: outro.b, descricao: a}
""")
    assert any("m.a: referência para coluna inexistente: outro.b" in e for e in validar_contrato(ruim))


def test_contrato_do_repositorio_e_valido() -> None:
    raiz = Path(__file__).resolve().parents[2]
    assert validar_contrato(carregar_contrato(raiz / "db" / "marts" / "contrato.yaml")) == []


def test_carregar_csvs_le_um_arquivo_por_mart(tmp_path: Path) -> None:
    (tmp_path / "votacao.csv").write_text("votacao_id,data,consenso\n2458405-38,2025-02-04,\n", encoding="utf-8")
    assert carregar_csvs(tmp_path) == {"votacao": [{"votacao_id": "2458405-38", "data": "2025-02-04", "consenso": ""}]}


def test_amostra_do_repositorio_passa_no_contrato() -> None:
    raiz = Path(__file__).resolve().parents[2]
    contrato = carregar_contrato(raiz / "db" / "marts" / "contrato.yaml")
    assert validar(contrato, carregar_csvs(raiz / "db" / "marts" / "amostra")) == []


# --- regras entre colunas ---

REGRAS = yaml.safe_load("""
versao: 2
marts:
  votacao:
    uma_linha_por: votação
    chave: [votacao_id]
    colunas:
      votacao_id: {tipo: texto, descricao: id}
      proposicao_id: {tipo: inteiro, nulo: true, descricao: proposição}
      rotulo: {tipo: texto, nulo: true, descricao: rótulo}
      ementa: {tipo: texto, nulo: true, descricao: ementa}
      governo: {tipo: texto, nulo: true, descricao: orientação do governo}
      oposicao: {tipo: texto, nulo: true, descricao: orientação da oposição}
      consenso: {tipo: booleano, nulo: true, descricao: iguais}
    regras:
      - juntos: [rotulo, ementa]
      - exige: {se: proposicao_id, entao: [rotulo]}
      - vazio_sse: {coluna: consenso, algum_fora: {governo: [Sim, Não], oposicao: [Sim, Não]}}
""")


def linha(**kw: str) -> dict[str, str]:
    base = {
        "votacao_id": "1-1",
        "proposicao_id": "10",
        "rotulo": "PL 1/2025",
        "ementa": "Altera a lei",
        "governo": "Sim",
        "oposicao": "Não",
        "consenso": "false",
    }
    return {**base, **kw}


def test_regras_caminho_feliz() -> None:
    linhas = [
        linha(),
        linha(votacao_id="1-2", proposicao_id="", rotulo="", ementa="", governo="Liberado", consenso=""),
        linha(votacao_id="1-3", oposicao="", consenso=""),
    ]
    assert validar(REGRAS, {"votacao": linhas}) == []


def test_juntos_pega_uma_vazia_e_outra_nao() -> None:
    erros = validar(REGRAS, {"votacao": [linha(ementa="")]})
    assert any("juntos" in e and "linha 1" in e for e in erros), erros


def test_exige_pega_proposicao_sem_rotulo() -> None:
    erros = validar(REGRAS, {"votacao": [linha(rotulo="", ementa="")]})
    assert any("exige" in e and "proposicao_id" in e for e in erros), erros


def test_vazio_sse_pega_vazio_sem_motivo() -> None:
    erros = validar(REGRAS, {"votacao": [linha(consenso="")]})
    assert any("vazio_sse" in e and "consenso" in e for e in erros), erros


def test_vazio_sse_pega_preenchido_quando_devia_ser_vazio() -> None:
    erros = validar(REGRAS, {"votacao": [linha(governo="Liberado", consenso="true")]})
    assert any("vazio_sse" in e and "consenso" in e for e in erros), erros


def test_regra_com_coluna_inexistente_e_erro_do_contrato() -> None:
    contrato = yaml.safe_load(yaml.safe_dump(REGRAS))
    contrato["marts"]["votacao"]["regras"].append({"juntos": ["rotulo", "nao_existe"]})
    assert any("nao_existe" in e for e in validar_contrato(contrato))


def test_regra_de_tipo_desconhecido_e_erro_do_contrato() -> None:
    contrato = yaml.safe_load(yaml.safe_dump(REGRAS))
    contrato["marts"]["votacao"]["regras"].append({"talvez": ["rotulo"]})
    assert any("talvez" in e for e in validar_contrato(contrato))
