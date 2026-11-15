# Dicionário de dados

_Cada tabela e coluna explicada. O schema de cada mart é o contrato com o site._

Hoje cobre os marts da pergunta 2. As tabelas de `core` e `ia` estão em [modelo.md](modelo.md); como cada uma se atualiza, em [atualizacao.md](atualizacao.md).

## O contrato

A fonte única é [`db/marts/contrato.yaml`](../../db/marts/contrato.yaml): cada mart, a chave, as colunas, o tipo, se a coluna pode vir vazia, os valores permitidos e as referências entre marts. Esta página explica o que cada mart é e para que serve; o detalhe de cada coluna está no YAML, com uma descrição por coluna.

O contrato é conferido por [`pipeline/qualidade/contrato.py`](../../pipeline/qualidade/contrato.py) em dois momentos:

- **No CI**, contra a amostra do site (`db/marts/amostra/`, um CSV por mart) e contra ele mesmo (chave sem coluna nula, tipos que existem, referências que existem, toda coluna descrita).
- **Na publicação**, contra os marts montados no rascunho. Se houver erro, os marts não são trocados e o site continua com os do dia anterior.

Para conferir à mão: `uv run --locked python -m pipeline.qualidade.contrato db/marts/amostra`.

**Mudar o contrato** é mudar o que o site recebe: sobe `versao` no YAML, atualiza esta página e, se a mudança mexe num número, o [dicionário de métricas](../produto/metricas.md), tudo no mesmo PR.

## Regras que valem para todos os marts

- **O perfil é deputado × legislatura.** Todo mart de deputado tem `deputado_id` e `legislatura_id` na chave. Nenhum mart junta legislaturas.
- **Métrica de voto se separa por governo.** Placar, alinhamento e conflito têm `governo_id` na chave. Na 57ª há um governo só; a coluna existe para a legislatura que tiver dois.
- **O número vem com o n.** Todo placar traz o `k` e o `n`, nunca só a fração. A fração, se aparecer, é conta do site.
- **O lado escolhido nunca entra.** Nenhum mart sabe o que o visitante escolheu. "Votou na sua direção" é conta do navegador, com `voto_deputado` e `votacao_eixo` (H3.6).
- **Vazio é informação.** Coluna nula tem sentido escrito no YAML: "não orientou", "sem partido", "empate". O site mostra a frase certa para cada caso, em vez de zero.

## Os marts

| Mart | Uma linha por | Para que serve | Histórias |
| --- | --- | --- | --- |
| `publicacao` | legislatura publicada | "Dados até", versões do contrato e da taxonomia | H6.2 |
| `governo` | governo na legislatura | Separar as métricas de voto por governo e nomear o governo na página | H8.1 |
| `metrica_status` | métrica × legislatura | Se o número resumido de cada métrica pode aparecer, e a âncora do "como calculamos". Quando o teste de sensibilidade reprova, a página mostra só o voto a voto | H6.1 |
| `eixo` | eixo de direção | Nome e polos em linguagem comum | H2.1, H3.2 |
| `perfil_deputado` | mandato | Cabeçalho da página e endereço estável | H1 |
| `filiacao_deputado` | período de filiação no mandato | Partidos com datas no cabeçalho | H1.3 |
| `votacao` | votação nominal de Plenário que entra em alguma métrica | Lista de votações: data, proposição, resumo, resultado, orientação de Governo e Oposição, consenso, link oficial | H2.2, H2.3, H6.3 |
| `votacao_eixo` | votação de mérito × eixo | O sinal que transforma o voto em direção | H2.1, H3.3 |
| `voto_deputado` | mandato × votação | O voto, a bancada que orientou, se divergiu e como os colegas de partido votaram | H2.2, H2.4, H4 |
| `placar_eixo_deputado` | mandato × governo × eixo | Contagem por polo, consenso, abstenção, obstrução e ausência | H2.1 a H2.5 |
| `alinhamento_deputado` | mandato × governo | Alinhamento com Governo e Oposição, total de divergências e lado | H4.4, H8.1, H8.2 |
| `conflito_eixo_deputado` | mandato × governo × eixo | Tendência no eixo e o resumo das votações de conflito | H8.3 |
| `conflito_votacao_deputado` | mandato × votação de conflito × eixo | Cada votação de conflito e com quem ele votou | H8.3, H8.4 |
| `autoria_tema_deputado` | mandato × tema | Autoria e coautoria contra a média da legislatura | H5 |

## Os números publicados e de onde vêm

Cada número da página sai de uma coluna de mart, calculada no pipeline pela regra de [metricas.md](../produto/metricas.md). O site só formata.

| Frase na página | Colunas |
| --- | --- |
| "Em gasto e benefício, votou 6 vezes por ampliar e 2 por reduzir" | `placar_eixo_deputado.k_positivo`, `k_negativo`, com `eixo.polo_positivo` e `polo_negativo` |
| "2 delas de consenso entre governo e oposição" | `placar_eixo_deputado.n_consenso` |
| "Obstruiu 1, absteve-se 1, faltou 2" | `n_obstrucao`, `n_abstencao`, `n_ausencia` |
| "Votou na sua direção em 7 de 9" | Conta do navegador: `voto_deputado.voto` × `votacao_eixo.sinal`, só Sim e Não |
| "Votou diferente da bancada em 12 das 80 votações em que ela orientou" | `alinhamento_deputado.divergencia_k`, `divergencia_n` |
| "Votou como o Governo orientou em 210 de 260" | `alinhamento_deputado.governo_k`, `governo_n` (e `oposicao_*`) |
| "Em 5 votações em que a Oposição orientou contra o que ele costuma votar em punição, seguiu a Oposição em 4" | `conflito_eixo_deputado.n_conflito`, `seguiu_lado`, `seguiu_tendencia` |
| "Autor de 8 proposições sobre saúde; a média é 3" | `autoria_tema_deputado.n_autor`, `media_autor` |

## Amostra

[`db/marts/amostra/`](../../db/marts/amostra/) traz os 15 marts de 5 deputados reais da 57ª, com dados até 15/10/2026, para o site e os wireframes trabalharem com dado de verdade antes do pipeline. Não é publicada. O CI confere a amostra contra o contrato (`test_amostra_do_repositorio_passa_no_contrato`).

| Deputado | Caso que cobre |
| --- | --- |
| Sargento Fahur (PR) | Trocou de partido: PSD até 05/03/2026, PL depois. Votou diferente da bancada em 333 das 636 votações em que ela orientou Sim, Não ou Obstrução e ele votou; só no bloco do PSD, 320 de 556 |
| Raimundo Santos (PA) | Partido de bloco (PSD) o mandato inteiro |
| Merlong Solano (PI) | Federação (PT) |
| Glaycon Franco (MG) | Suplente; trocou do PV (federação) para o PSDB (bloco) |
| Gilmar Machado (MG) | Suplente com quase nenhuma votação (3) |

Como foi feita (15/11/2026), pelo script `amostra_marts/` do repositório do laboratório (`camara-lab`, privado):

- **Câmara:** arquivos em lote de votações, votos, orientações e autores de 2023 a 2026; histórico e detalhe dos 5 pela API.
- **Taxonomia:** a da v1 (DAG v1.1): classe da votação (`merito` e as outras), sinal por eixo e temas. Os ids de eixo e de tema são texto (`punicao`, `t145_2`).
- **Regras:** as de [metricas.md](../produto/metricas.md) e a bancada pela regra de [atualizacao.md](atualizacao.md#em-aberto). Bloco que aparece na votação sem orientação conta como bancada que não orientou (o bloco que juntou PL e PT em 2025 ficou sem orientar em boa parte das votações).
- **Texto:** a ementa vem com os espaços juntados num parágrafo só (a fonte traz quebras de linha e espaço sobrando).
- **`metrica_status`:** só direção do voto e autoria saem como publicáveis; as outras esperam o teste de sensibilidade.

Pendências que a amostra mostrou:

- **Link da votação.** A página oficial da votação precisa do id da reunião, e ele vem no próprio `votacoes-<ano>.csv` (`idEvento`). O candidato é `camara.leg.br/presenca-comissoes/votacao-portal?reuniao={idEvento}&itemVotacao={parte do id depois do hífen}`, mas não está conferido: a página se monta no navegador e responde 200 com o mesmo conteúdo até para um item inventado. Confere-se abrindo no navegador. Até lá, a amostra usa a ficha de tramitação da proposição, que mostra a proposição certa (o 200 sozinho não prova nada: id inventado também responde 200).
- **Votação de mérito sem proposição ligada vira `outro`.** A v1 tem 10 votações de mérito da 57ª sem `prop_id`. Sem proposição, não há sinal de eixo, e a amostra as trata como `outro`. Exemplo: 2603342-42, que aprova o PDL 50/2026, fica fora do placar. A API traz a proposição afetada (`proposicoesAfetadas`; a 2487358-48 aponta para o PRC 27/2025), e `votacao_proposicao` em `dados.core` lê dela, não da v1.
- **O rótulo da proposição muda.** O id 106701 era o PL 347/2003 e hoje a API o chama de PL 5809/2025; a descrição da votação de 05/11/2025 ainda diz "PL 347, de 2003". Quem procurar pelo número antigo não acha. Guardar os rótulos anteriores entra com `proposicao` em `dados.core`.
- **Votação de proposição antiga fica sem rótulo.** 4 votações da amostra têm `proposicao_id` e não têm rótulo, ementa nem resumo: as proposições (PL 3905/2021, PL 364/2019 e PL 10273/2018) estão fora do universo de proposições da v1, de onde a amostra tira rótulo e ementa. É o caso "proposição antiga é votada hoje" de [atualizacao.md](atualizacao.md). O validador não pegou porque o rótulo pode ser vazio; falta a ele regra entre colunas (rótulo vazio só quando `proposicao_id` é vazio).
- **Condição na legislatura.** Sai do primeiro `condicaoEleitoral` do histórico; "efetivado" se algum evento fala em efetivação. A regra definitiva entra com `mandato` em `dados.core`.
