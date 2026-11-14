# Como cada tabela se atualiza

_Uma linha por tabela: fonte, frequência, chave natural, estratégia, janela de reprocessamento e o que dispara. Tem de estar escrito antes do primeiro CREATE TABLE._

Hoje cobre as tabelas da pergunta 2. Os nomes são provisórios até o `modelo.md`; o que vale aqui é a regra de cada uma. Checado contra a fonte em 14/11/2026.

## O que a fonte faz e o que isso obriga

- **Os arquivos em lote de todos os anos são refeitos toda madrugada** (`https://dadosabertos.camara.leg.br/arquivos/<conjunto>/csv/<conjunto>-<ano>.csv`). Em 14/11/2026 o `proposicoes-2019.csv` tinha `Last-Modified` das 04:34 UTC do mesmo dia. A data do arquivo não diz o que mudou: **o que mudou se descobre pelo hash de cada linha**.
- **Proposição antiga é votada hoje.** A 57ª votou o PL 759/2015 em 27/08/2025. O universo de proposições não é só o dos anos da legislatura.
- **O voto já traz o partido da época.** `votacoesVotos` tem `deputado_siglaPartido` gravado no voto. A filiação com datas continua necessária para o cabeçalho (H1.3) e para a autoria, e sai de `/deputados/{id}/historico` (evento "Alteração de partido", com data e hora).
- **No Plenário, quem orienta é quase sempre o bloco.** Em 2025, das 419 votações de Plenário com orientação, Governo, Oposição, Maioria, Minoria, Novo e a federação PSOL-REDE orientaram em todas, o PL em 122, e PP, PSD, MDB, União e Republicanos em 1 cada. O resto veio de blocos (`Bl PlUniPpPsd...`, `Bl AvanSolidPrd...`), com a sigla cortada.
- **A composição do bloco não tem data na API.** `/blocos?idLegislatura=57` lista os blocos e `/blocos/{id}/partidos` diz quem está neles hoje. Quem estava ontem só se sabe guardando a foto de cada dia.
- **Votação secreta vem sem votos.** Vira votação marcada, não erro.

## Regras que valem para todas

- **Data lógica.** Todo passo recebe `--data AAAA-MM-DD` e trabalha sobre o `raw` daquele dia. Reprocessar um dia é ler o `raw` dele de novo, sem baixar nada.
- **Idempotência.** Rodar o mesmo dia duas vezes deixa o banco igual. Upsert por chave natural e conjunto trocado inteiro onde a fonte pode tirar linhas.
- **Hash de linha.** Cada linha do `core` guarda o hash da linha de origem, calculado sobre as colunas normalizadas (espaços aparados, ordem fixa). Upsert só escreve se o hash mudou, e o passo conta quantas linhas foram novas, mudadas e iguais.
- **Nada some.** Linha de entidade (deputado, proposição, votação) que sai da fonte ganha `removida_em`, nunca `DELETE`. Arquivamento no fim da legislatura é mudança de situação, não remoção.
- **Legislatura em tudo.** A 58ª começa em 01/02/2027. Toda tabela que depende de mandato tem `legislatura_id`; a troca é um evento esperado ([runbook](../runbooks/trocar-de-legislatura.md)).
- **Anos quentes e anos frios.** Quentes: os anos da legislatura em curso. Frios: os anos anteriores que o universo usa (de proposição votada ou com autoria de deputado da legislatura). Quente se relê todo dia; frio, uma vez por semana. Depois de 31/01/2027, os anos da 57ª passam a frios.
- **Checkpoint por data, não por quem.** Cada passo grava até que data lógica processou. É dele que sai o "dados até DD/MM/AAAA" (H6.2).

## As tabelas

### raw: cópia exata do que veio

Fora do Postgres, em parquet (arquivos em lote) e JSON (API), com data de coleta, URL e hash.

| Tabela | Fonte | Frequência | Chave natural | Estratégia | Janela | Dispara |
| --- | --- | --- | --- | --- | --- | --- |
| `raw.arquivo` | Arquivos em lote: `votacoes`, `votacoesVotos`, `votacoesOrientacoes`, `votacoesProposicoes`, `votacoesObjetos`, `proposicoes`, `proposicoesAutores`, `proposicoesTemas`, `deputados`, `legislaturas` | Diária (anos quentes e arquivos sem ano); semanal (anos frios) | conjunto, ano, data lógica | Só acrescenta. Arquivo com hash igual ao da coleta anterior registra a coleta e não grava outra cópia | Nenhuma: é a própria história | Agenda diária e semanal |
| `raw.api` | API: `/deputados?idLegislatura=`, `/deputados/{id}/historico`, `/blocos?idLegislatura=`, `/blocos/{id}/partidos` | Conforme a tabela do `core` que pede | endpoint, id, data lógica | Só acrescenta | Nenhuma | Passo do `core` que precisa dela |

### core: entidades limpas, com as chaves da Câmara

| Tabela | Fonte | Frequência | Chave natural | Estratégia | Janela | Dispara |
| --- | --- | --- | --- | --- | --- | --- |
| `legislatura` | `legislaturas.csv` | Diária | `id` | Upsert por hash | Arquivo inteiro | `raw.arquivo` do dia |
| `deputado` | `deputados.csv` (pessoa: nome civil, nascimento) e `/deputados?idLegislatura=` (quem exerceu mandato na legislatura) | Diária | `id` | Upsert por hash. A pessoa não tem partido nem UF: isso é do mandato e da filiação | Arquivo inteiro | `raw.arquivo` do dia |
| `mandato` | `/deputados/{id}/historico` | Diária para deputado novo ou com sinal de mudança; semanal para todos da legislatura (cerca de 600 chamadas) | `deputado_id`, `legislatura_id`, `inicio` | Recompõe todos os períodos do deputado a partir do histórico inteiro e troca o conjunto dele. Guarda condição (titular, suplente, efetivado) e cada período de exercício | Histórico inteiro do deputado | Deputado novo na lista; voto de quem não tem período de exercício naquela data; semanal |
| `filiacao` | `/deputados/{id}/historico` (mesma chamada do `mandato`) | Junto com `mandato` | `deputado_id`, `inicio` | Recompõe do histórico e troca o conjunto do deputado. `fim` vazio na filiação vigente | Histórico inteiro do deputado | Junto com `mandato`; voto com `deputado_siglaPartido` diferente da filiação vigente naquela data |
| `proposicao` | `proposicoes-<ano>.csv` | Diária (anos quentes); semanal (anos frios) | `id` | Upsert por hash. Guarda `ultimoStatus` (situação, órgão, regime) e `uriPropPrincipal` (apensada) | Anos quentes todo dia; anos frios toda semana | `raw.arquivo` do dia |
| `proposicao_tema_camara` | `proposicoesTemas-<ano>.csv` | Junto com `proposicao` | `proposicao_id`, `cod_tema` | Troca o conjunto da proposição quando o hash do conjunto muda. Guarda o `codTema`, que a v1 perdia | Igual a `proposicao` | `raw.arquivo` do dia |
| `autoria` | `proposicoesAutores-<ano>.csv` | Junto com `proposicao` | `proposicao_id`, `uri_autor` | Troca o conjunto da proposição quando o hash do conjunto muda (autor pode ser retirado). Autor principal: `ordemAssinatura = 1` e `proponente = 1`. Autor que não é deputado (Senado, Executivo, órgão) fica com `deputado_id` vazio | Igual a `proposicao` | `raw.arquivo` do dia |
| `votacao` | `votacoes-<ano>.csv` | Diária (anos quentes); semanal (anos frios) | `id` (texto, como `2458405-38`) | Upsert por hash. Guarda todos os órgãos; o recorte do Plenário é dos marts. Votação sem nenhum voto nominal fica marcada | Anos quentes todo dia; frios toda semana | `raw.arquivo` do dia |
| `votacao_proposicao` | `votacoesProposicoes-<ano>.csv` (afetadas) e `votacoesObjetos-<ano>.csv` (objeto votado) | Junto com `votacao` | `votacao_id`, `proposicao_id`, `relacao` | Troca o conjunto da votação. `relacao` diz se é afetada ou objeto; a direção do voto depende de qual é qual | Igual a `votacao` | `raw.arquivo` do dia |
| `voto` | `votacoesVotos-<ano>.csv` | Junto com `votacao` | `votacao_id`, `deputado_id` | Troca o conjunto da votação. Guarda o partido e a UF publicados no voto como fato | Igual a `votacao` | `raw.arquivo` do dia |
| `orientacao` | `votacoesOrientacoes-<ano>.csv` | Junto com `votacao` | `votacao_id`, `sigla_bancada` | Troca o conjunto da votação. Guarda a orientação como veio (Sim, Não, Obstrução, Liberado, vazio) e o tipo da bancada: governo, oposição, maioria, minoria, partido, federação (`Fdr ...`) ou bloco (`Bl ...`), com o id de `uriBancada` | Igual a `votacao` | `raw.arquivo` do dia |
| `bloco` e `bloco_partido` | `/blocos?idLegislatura=` e `/blocos/{id}/partidos` | Diária | `bloco_id`; `bloco_id`, `partido_id`, `inicio` | Compara a composição do dia com a vigente: partido que entrou abre período, partido que saiu fecha. Começa a coletar o quanto antes, porque cada dia sem coleta é composição perdida | Nenhuma: o passado não volta pela API | Agenda diária |

### ia: o que vem de modelo

Calcula só o que falta. Cada linha guarda versão da taxonomia, modelo, versão do prompt e hash do texto de entrada. A regra detalhada fica em [taxonomia.md](taxonomia.md) (marco `taxonomia.incremental`).

| Tabela | Fonte | Frequência | Chave natural | Estratégia | Janela | Dispara |
| --- | --- | --- | --- | --- | --- | --- |
| `proposicao_tema` | Ficha e classificação da proposição na taxonomia vigente | Diária | `proposicao_id`, `tema_id`, `versao_taxonomia` | Só calcula proposição sem linha na versão vigente ou com hash de ementa novo | Nenhuma além do que falta | Proposição nova ou com ementa mudada; taxonomia nova (só os temas afetados) |
| `proposicao_eixo` | Classificação de direção (sinal `+`, `−` ou misto) por eixo | Diária | `proposicao_id`, `eixo_id`, `versao_taxonomia` | Igual a `proposicao_tema` | Igual | Igual |

### marts: tabelas prontas para as telas

| Tabela | Fonte | Frequência | Chave natural | Estratégia | Janela | Dispara |
| --- | --- | --- | --- | --- | --- | --- |
| Marts da pergunta 2 (schema no marco `dados.contrato_marts`) | `core` e `ia` | A cada execução completa | A de cada mart | Recálculo total num schema de rascunho, testes de dados, troca pelo publicado de uma vez | Tudo | Fim de `core` e `ia` do dia |

## Em aberto

- **Orientação de bloco na divergência.** A métrica de divergência (`docs/produto/metricas.md`) compara o voto com a orientação do partido, que os partidos de bloco quase nunca dão. Saber a qual bloco o partido pertencia em cada data exige a composição com data: a partir do início da coleta de `bloco_partido` ela existe; para o passado da 57ª, um spike do marco `dados.modelo` mede se a sigla cortada (`Bl PlUniPpPsd...`) e o `uriBancada` bastam para reconstruí-la. A métrica é revista com o resultado, no mesmo PR que atualiza `metricas.md`.
- **Período de exercício no lugar da janela de 15 dias.** `mandato` guarda os períodos de exercício do histórico. Se forem completos, a ausência deixa de ser aproximação; o teste vem com o dado real.
