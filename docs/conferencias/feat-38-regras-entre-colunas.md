# Conferência: feat/38-regras-entre-colunas

Registro de `scripts/conferir.py` (skill `/conferir`). Evidência é comando e saída, não "parece certo".

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| Cada regra nova do validador tem teste que a pega | 6 mutações em `pipeline/qualidade/contrato.py`, com `assert` de que aplicaram e `PYTHONDONTWRITEBYTECODE=1`; cada uma derrubou o próprio teste | conferido |
| Com `.pyc` em cache, uma mutação pode testar o código da anterior | mutações 3 e 4 têm o mesmo tamanho; com cache, a 4 derrubou o teste da 3; rodada a 4 sozinha, derrubou `test_vazio_sse_pega_preenchido_quando_devia_ser_vazio` | conferido |
| As 18 mutações da #37 continuam valendo sem cache de bytecode | `mutar.py` rodado de novo com `PYTHONDONTWRITEBYTECODE=1`: as 18 derrubaram o teste certo | conferido |
| Com as regras, a amostra antiga quebrava só nas 4 votações de proposição sem rótulo | `python -m pipeline.qualidade.contrato db/marts/amostra`: 4 erros, todos `regra exige`, linhas 441, 442, 527 e 535 | conferido |
| As regras de `consenso`, `divergiu` e bancada valem na amostra inteira | mesma rodada: nenhum erro dessas regras; depois de corrigir os rótulos, 0 erro | conferido |
| Rótulo e ementa das 4 vêm de `proposicoes-<ano>.csv` | ids 2305816, 2190986 e 2175977 em `proposicoes-2021`, `2019` e `2018`: PL 3905/2021, PL 364/2019, PL 10273/2018 | conferido |
| A amostra nova difere da anterior só nessas 4 linhas e na `publicacao` | `cmp` dos 15 CSVs: 13 iguais; `votacao` com 4 linhas; `publicacao` com `gerado_em` e `versao_contrato` 2 | conferido |
| A API de proposições ficou fora por um tempo em 15/11 | `/proposicoes/2305816` e `/referencias/situacoesProposicao`: 504 depois de 15 s; `/deputados/204387`: 200 em 0,14 s; voltou a 200 minutos depois | conferido |
| `tendencia` vazia é empate, não falta de conflito | `placar_eixo_deputado`: 74084 com 3 a 3 em dois eixos, 236284 com 0 a 0 em `punicao`. A explicação do registro da #37 estava invertida e foi corrigida | conferido |

## Linhas refeitas da fonte

| Mart | Linha | Como refiz | Bate? |
| --- | --- | --- | --- |
| votacao | 2400068-20 | ficha de tramitação 2305816 na página da Câmara: "PL 3905/2021" aparece 16 vezes (149 KB; id inventado dá 38 KB sem proposição) | sim |
| votacao | 2400068-23 | mesma proposição 2305816 | sim |
| votacao | 2422887-23 | ficha 2190986: "PL 364/2019" aparece 9 vezes | sim |
| votacao | 2428615-16 | ficha 2175977: "PL 10273/2018" aparece 7 vezes | sim |
| votacao | 2383287-61 (sorteada, semente 20261116, entre as com consenso) | API `/votacoes/2383287-61/orientacoes`: Governo Não, Oposição Sim | sim: consenso false |

## Vazios

| Coluna | Vazias | Explicação |
| --- | --- | --- |
| governo.fim | 1 de 1 | o governo da 57ª ainda está em curso (governo.csv idêntico ao da #37) |
| metrica_status.motivo | 2 de 7 | arquivo idêntico byte a byte ao conferido em `feat-36-conferencia.md` (`cmp`); a explicação de lá vale: as duas publicáveis não têm motivo |
| filiacao_deputado.fim | 5 de 7 | arquivo idêntico byte a byte ao conferido em `feat-36-conferencia.md` (`cmp`); a explicação de lá vale: a filiação vigente de cada um dos 5 |
| votacao.proposicao_id | 19 de 1059 | As mesmas 19 votações `outro` sem proposição na v1 (12 sem proposição nem na fonte, 7 com a afetada na API, pendência de `dados.core`) |
| votacao.proposicao_rotulo | 19 de 1059 | Exatamente as 19 sem proposição; a regra `exige` garante que nenhuma com proposição fica sem rótulo |
| votacao.resumo | 23 de 1059 | As 19 sem proposição e as 4 proposições antigas, que não têm ficha na v1; a regra `exige: se resumo, entao proposicao_id` passa |
| votacao.ementa | 19 de 1059 | As mesmas 19 do rótulo (regra `juntos`) |
| votacao.aprovada | 183 de 1059 | As mesmas 183 da #37: todas `outro`, com `aprovacao` vazio na fonte |
| votacao.orientacao_governo | 156 de 1059 | As mesmas 156 da #37: Governo presente sem orientar na fonte |
| votacao.orientacao_oposicao | 61 de 1059 | As mesmas 61 da #37: Oposição presente sem orientar na fonte |
| votacao.consenso | 403 de 1059 | Garantido pela regra `vazio_sse`: vazio exatamente quando Governo ou Oposição não orientou Sim ou Não |
| voto_deputado.bancada_tipo | 8 de 3225 | arquivo idêntico byte a byte ao conferido em `feat-36-conferencia.md` (`cmp`); a explicação de lá vale: PSD nas 4 votações de março de 2023 com `Bloco Parlamentar` |
| voto_deputado.bancada_nome | 8 de 3225 | As mesmas 8 (regra `juntos` com `bancada_tipo`) |
| voto_deputado.bancada_orientacao | 819 de 3225 | arquivo idêntico byte a byte ao conferido em `feat-36-conferencia.md` (`cmp`); a explicação de lá vale: 8 sem bancada, 799 de bloco presente sem orientar, 12 de partido ou federação vazios na fonte |
| voto_deputado.divergiu | 1120 de 3225 | Garantido pela regra `vazio_sse`: vazio exatamente quando voto ou orientação ficam fora de Sim, Não e Obstrução |
| conflito_eixo_deputado.tendencia | 3 de 46 | Empate no eixo (3 a 3 duas vezes, 0 a 0 uma vez, em `placar_eixo_deputado`) |
