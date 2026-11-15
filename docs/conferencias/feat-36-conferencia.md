# Conferência: feat/36-conferencia

Primeira conferência pelo `/conferir`, em 15/11/2026. Cobre os dados e docs que a #35 trouxe (contrato, amostra, `atualizacao.md`, `dicionario.md`), porque esta branch parte dela. Os arquivos em lote são os baixados em 14 e 15/11/2026; a API foi consultada em 15/11/2026.

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| Ids de eixo e de tema são texto | `config/eixos.yaml` da v1: `punicao`, `armas`, `ambiente`; `temas.parquet`: `t0_0`, `t1_0` | conferido |
| `votacoes-<ano>.csv` traz o id da reunião (`idEvento`) | `head -1` de `votacoes-2023` a `2026` mostra `idEvento` e `uriEvento` | conferido |
| O link `votacao-portal?reuniao={idEvento}&itemVotacao={sufixo}` abre a votação certa | `reuniao=75386&itemVotacao=38` e `itemVotacao=99999` devolvem 200 com 46204 bytes cada: a página se monta no navegador | não conferido |
| A ficha de tramitação mostra a proposição da votação | `fichadetramitacao?idProposicao=106701`: 161014 bytes, contém "PL 5809/2025" e "PL 347/2003"; id inventado 999999999: 200 com 38189 bytes, sem a proposição | conferido |
| O id 106701 era o PL 347/2003 e hoje é o PL 5809/2025 | API `/proposicoes/106701`: PL 5809 2025; `/votacoes/106701-223`: descrição cita "Projeto de Lei nº 347, de 2003" | conferido |
| Os arquivos em lote são refeitos de madrugada | `Last-Modified` de `proposicoes-2019.csv`: 14/11 04:34 UTC e 15/11 04:33 UTC (dois dias seguidos) | conferido |
| A 57ª votou o PL 759/2015 em 27/08/2025 | `votacoesObjetos-2025`: votação 1029018-80, 2025-08-27, PL 759 2015 | conferido |
| O voto traz o partido da época (`deputado_siglaPartido`) | cabeçalho de `votacoesVotos-2023` a `2026` | conferido |
| A troca de partido sai do histórico, evento "Alteração de partido" com data e hora | API `/deputados/204387/historico`: 2026-03-06T14:39 PL "Alteração de partido" | conferido |
| Em 2025, 428 votações de Plenário em orientações; aparecer não é orientar (Governo orientou em 329, Oposição 393, Maioria 304, Minoria 379, Novo 410, PSOL-REDE 355; PL aparece em 122, orientou em 117) | contagem em `votacoesOrientacoes-2025`, `siglaOrgao = PLEN`, presença × orientação não vazia. A versão anterior (419, "orientaram em todas") estava errada e foi corrigida | conferido |
| Sigla de partido na orientação vem cortada em 10 caracteres | `Counter` das siglas de 2025 sem `Bl`/`Fdr`: `Republican`, `Solidaried` | conferido |
| `/blocos/{id}/partidos` pode vir vazia; a composição do 590 só está no nome | `/blocos/590/partidos` → `{"dados":[]}`; `/blocos/590` → nome "AVANTE, SOLIDARIEDADE, PRD"; `/blocos/999999/partidos` → 200 e lista vazia | conferido |
| `uriBancada` vem vazio para todo bloco | 2098 linhas de bloco em `votacoesOrientacoes-2023` a `2026`, 0 com `uriBancada` | conferido |
| Nove siglas de bloco na 57ª, a última desde 29/10/2025 | primeira data de cada sigla no Plenário: 9 contando a genérica `Bloco Parlamentar`; `Bl UniPpPsd...` desde 2025-10-29 | conferido |
| A eliminação reproduz o 589; o 590 sai da sigla e do nome | `camara-lab/amostra_marts` rodado em 15/11: `Bl UniPpPsd...` → CIDADANIA, MDB, PODE, PP, PSD, PSDB, REPUBLICANOS, UNIÃO = `/blocos/589/partidos`; o 590 vem de `COMPLETO_API` e dos tokens da sigla | conferido |
| O Cidadania votou em 194 das 202 votações da combinação e ficou calado em todas | mesma rodada: "CIDADANIA votou em 194 de 202; silenciosa: 194" | conferido |
| Cinco votações de março de 2023 têm a sigla genérica `Bloco Parlamentar` | 5 votações, de 2023-03-14 a 2023-03-22 | conferido |
| Votação secreta vem sem votos | nenhuma votação de Plenário de 2023 a 2026 tem placar sem voto nominal; não há caso para olhar | não conferido |
| Sargento Fahur: PSD até 05/03/2026, PL depois; 333 de 636 votações diferente da bancada (320 de 556 no bloco do PSD) | histórico da API; contagem em `voto_deputado.csv`. A frase anterior ("diverge do bloco do PSD em 333 de 636") estava errada e foi corrigida | conferido |
| Gilmar Machado tem 3 votações; Glaycon Franco é suplente e passou do PV para o PSDB | `voto_deputado.csv`: 3 linhas do 74581; partidos do 236284: PV, PSDB; `perfil_deputado.csv`: suplente | conferido |
| As 4 votações sem rótulo são de proposições fora do universo da v1 | 2305816, 2190986 e 2175977 ausentes de `props.parquet`; API: PL 3905/2021, PL 364/2019, PL 10273/2018 | conferido |
| 10 votações de mérito da v1 não têm proposição e viram `outro` na amostra | `votacoes_57.parquet`: `classe == merito` e `prop_id` nulo = 10; 2603342-42 (PDL 50/2026) é uma delas | conferido |
| O script do laboratório reproduz a amostra | rodado de `camara-lab` em 15/11: 12 marts idênticos byte a byte; `publicacao` difere só em `gerado_em`; `votacao` só na `ementa` (ver a próxima linha) | conferido |
| O pre-commit `trailing-whitespace` alterou 26 ementas da amostra no commit | diff entre a saída do script e o arquivo versionado: 26 linhas, todas na coluna `ementa`, só espaço antes de quebra de linha | conferido |
| Com a exclusão, o pre-commit não mexe mais em CSV de `db/` | CSV com espaço sobrando passou por `pre-commit run trailing-whitespace` e ficou igual (`cmp`); controle `scripts/_t.txt` foi aparado | conferido |
| Cada regra do `conferir.py` e dos hooks tem teste que a pega | 18 mutações com `assert` de que aplicaram; cada uma derrubou o teste da regra | conferido |
| O `Stop` roda a cada resposta; o `SessionEnd` não decide nada | `hooks.md` oficial: "Runs when the main Claude Code agent has finished responding"; tabela de decisão: SessionEnd "No decision control" | conferido |

## Linhas refeitas da fonte

Semente `random.seed(20261115)`, 4 linhas sorteadas de `voto_deputado.csv` e 1 caso difícil sorteado entre as divergências do Fahur no bloco. Cada uma refeita pela API (`/votacoes/{id}/votos` e `/votacoes/{id}/orientacoes`), sem passar pelo script.

| Mart | Linha | Como refiz | Bate? |
| --- | --- | --- | --- |
| voto_deputado | 74084 × 2376169-62 | API: voto Sim, PSD; `Bl MdbPsdRepPode` Liberado | sim: bancada bloco, orientação Liberado, divergiu vazio |
| voto_deputado | 204387 × 2377518-12 | API: voto Sim, PSD; `Bl MdbPsdRepPode` Sim | sim: divergiu false |
| voto_deputado | 74084 × 2579832-62 | API: voto Sim, PSD; `Bl UniPpPsd...` Sim | sim: divergiu false |
| voto_deputado | 188097 × 2318217-81 | API: voto Sim, PT; `Fdr PT-PCdoB-PV` Sim | sim: bancada federação, divergiu false |
| voto_deputado | 204387 × 2601522-8 | API: voto Não, PSD; `Bl UniPpPsd...` Sim | sim: divergiu true |
| votacao | 106701-223 | API `/votacoes/106701-223` e `/proposicoes/106701` | sim: PL 5809/2025, 2025-11-05, Plenário |
| filiacao_deputado | 204387, PL desde 06/03/2026 | API `/deputados/204387/historico` | sim |

## Vazios

| Coluna | Vazias | Explicação |
| --- | --- | --- |
| governo.fim | 1 de 1 | O governo da 57ª ainda está em curso |
| metrica_status.motivo | 2 de 7 | As duas publicáveis (direcao_eixo e autoria) não têm motivo de bloqueio; as 5 bloqueadas têm |
| filiacao_deputado.fim | 5 de 7 | A filiação vigente de cada um dos 5 deputados (5 deputados distintos) |
| votacao.proposicao_id | 19 de 1059 | Todas `outro` na v1, sem `prop_id`. 12 não têm proposição nem na fonte; 7 têm a proposição afetada na API, que a v1 não ligou (ver as pendências do dicionário) |
| votacao.proposicao_rotulo | 23 de 1059 | 19 sem proposição mais 4 com proposição fora do universo da v1 |
| votacao.resumo | 23 de 1059 | As mesmas 23 do rótulo (conferido linha a linha) |
| votacao.ementa | 23 de 1059 | As mesmas 23 do rótulo (conferido linha a linha) |
| votacao.aprovada | 183 de 1059 | Todas `outro`; o campo `aprovacao` da fonte vem vazio nas 183 |
| votacao.orientacao_governo | 156 de 1059 | O Governo aparece na votação sem orientar: vazio na fonte nas 156; as não vazias são iguais à fonte |
| votacao.orientacao_oposicao | 61 de 1059 | Mesmo caso: vazio na fonte nas 61; as não vazias iguais à fonte |
| votacao.consenso | 403 de 1059 | Exatamente as 403 em que Governo ou Oposição não orientou Sim ou Não |
| voto_deputado.bancada_tipo | 8 de 3225 | Votos do PSD em 4 votações de março de 2023 com a sigla genérica `Bloco Parlamentar`, sem composição conhecida |
| voto_deputado.bancada_nome | 8 de 3225 | As mesmas 8 |
| voto_deputado.bancada_orientacao | 819 de 3225 | 8 sem bancada; 799 de blocos que aparecem sem orientar, quase todas dos blocos que juntaram PL e PT em 2025 (`Bl PlFdrPTUniPp...`, `Bl PlFdrPtUniPp...`) e do bloco seguinte; 6 de partido e 6 de federação vazios na fonte |
| voto_deputado.divergiu | 1120 de 3225 | Exatamente as 1120 em que o voto ou a orientação fica fora de Sim, Não e Obstrução: 799 orientações vazias, 231 Liberado, 88 ausências e 2 abstenções |
| conflito_eixo_deputado.tendencia | 3 de 46 | Os 3 com `n_conflito = 0`: sem votação de conflito no eixo, não há tendência |
