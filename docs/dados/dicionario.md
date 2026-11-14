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

`db/marts/amostra/` traz os marts de 5 deputados reais da 57ª, escolhidos para cobrir os casos difíceis: troca de partido, suplente, partido de bloco, federação e quase nenhuma votação. Serve para o site e os wireframes trabalharem com dado de verdade antes do pipeline. É gerada uma vez, por script descartável, e não é publicada.
