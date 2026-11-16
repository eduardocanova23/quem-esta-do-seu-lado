# 0004: Postgres em Docker no servidor Hetzner

Status: aceito, 2026-11-16. Issue #47. Proposto pelo Claude e aceito pelo Eduardo ("aceito como está").

## Contexto

Decidido pelo Eduardo em 16/11/2026, antes deste ADR:

- **A v1 sai de produção** e a v2 toma o lugar dela, no mesmo servidor Hetzner (CX23, 2 vCPU, ~3,7 GB de RAM, ~31 GB de disco livre segundo a nota do vault; não conferido no servidor hoje). O banco Neon da v1 deixa de ser necessário.
- **O Diário Oficial sai deste projeto.** A v2 tem um banco só, sem o `DO_DATABASE_URL` separado da v1.
- **Orçamento de ~R$ 20 por mês** para o banco, se isso der espaço para guardar a tramitação.

O que já está fixado por outros documentos:

- **O banco não serve páginas** ([ADR 0002](0002-forma-de-entrega-do-site.md)). O site é estático e o build lê os marts em arquivo. Na hora do acesso, o banco só atende a API de busca, com um papel que só lê.
- **O modelo de dados pede Postgres** ([modelo.md](../dados/modelo.md)): períodos em `daterange` com `EXCLUDE USING gist` (`btree_gist`), que impedem um deputado em dois partidos no mesmo dia. A busca textual da v1 usou `pg_trgm`, e o [método](../metodo.md) prevê embeddings para a busca (`pgvector`, se o ADR da busca mantiver os embeddings).
- **A tramitação precisa ser guardada.** A pergunta 1 mede há quanto tempo cada proposição está parada e por onde ela passou. A API não tem arquivo em lote de tramitações (uma chamada por proposição), cai (2 de 50 chamadas deram 504 na medição abaixo) e pode reescrever eventos. Sem cópia própria, um número publicado ontem não pode ser refeito.

## Quanto espaço o banco vai ocupar

Medido em 16/11/2026, sobre os arquivos em lote de `dados/raw/arquivos/2026-11-16/` (anos de 2023 a 2026) e uma amostra de 50 chamadas a `/proposicoes/{id}/tramitacoes`. Os scripts estão em `camara-lab/medicao_tramitacao/`.

| O que | Como saiu o número | Resultado |
| --- | --- | --- |
| Proposições de 2023 a 2026 | contadas no CSV | 283.322 |
| Eventos de tramitação, pela última sequência de cada proposição | soma de `ultimoStatus_sequencia` | 1.553.659 |
| Quantos eventos a API devolve de fato por número de sequência | amostra: 140 eventos para uma soma de sequências de 222 (48 respostas; 12 têm buracos na numeração) | 0,63 |
| Eventos de tramitação, corrigidos | 1.553.659 × 0,63 | **~980 mil** (amostra pequena: ordem de grandeza) |
| Só os tipos principais (PL, PLP, PEC, PDL, MPV, PLV, PRC) | 26.987 proposições, mesma correção | ~360 mil eventos |
| JSON da API por evento | medido na amostra; o `despacho` (texto livre) é o campo maior, 141 B | 644 B |

O tamanho em tabela é **estimado, não medido**: o Docker desta máquina recusou a conexão (`permission denied` no socket), então não houve Postgres para carregar a amostra. A conta usa o custo de armazenamento do Postgres: 24 B de cabeçalho e 4 B de ponteiro por linha, colunas tipadas e o índice da chave.

| Tabela | Linha enxuta (códigos e datas, ~95 B com o índice) | Com o texto do `despacho` (~235 B) |
| --- | --- | --- |
| `tramitacao`, todos os tipos | ~95 MB | ~230 MB |
| `tramitacao`, tipos principais | ~35 MB | ~85 MB |

O resto do banco, também estimado. Os arquivos em lote de 2023 a 2026 somam 695,9 MB de CSV, mas repetem nomes, URIs e colunas que o `core` não guarda. Em linhas de arquivo: votos 473 mil, autorias 481 mil, objetos de votação 277 mil, temas 114 mil, votações 53 mil, orientações 16 mil. Com tipos e índices, isso dá **~150 a 300 MB para o `core`** e os marts. Os embeddings de 26,5 mil proposições em 1.024 dimensões somam **~110 MB** fora o índice (26.500 × 1.024 × 4 B), se o ADR da busca os mantiver.

**Total para a 57ª legislatura: ~0,4 a 0,7 GB.** A 58ª começa em 1/2/2027 e acumula sobre a 57ª: o banco passa de 1 GB durante ela.

## Opções

| | A. Postgres em Docker no Hetzner | B. Neon, plano grátis | C. Neon, plano Launch |
| --- | --- | --- | --- |
| Espaço | o disco do servidor (~31 GB livres, não conferido hoje) | 1 GB por projeto | US$ 0,35 por GB-mês |
| Custo por mês | backup do Hetzner: 20% do preço do servidor, menos de R$ 10 (preço do CX23 não conferido) | zero | sem mínimo; computação a US$ 0,106 por CU-hora: ligado o mês todo com 0,25 CU (menor tamanho; não conferido), ~US$ 19 (~R$ 100, câmbio não conferido) |
| Busca na hora do acesso | Postgres na mesma máquina da API (se o ADR de hospedagem puser a API no Hetzner) | o banco dorme após 5 min sem uso, e isso não se desliga no plano grátis; a primeira busca depois acorda o banco (atraso não medido) | dormir é configurável, mas ficar acordado é o que custa |
| Restauração | nossa: dump diário e cópia fora do servidor; o backup do Hetzner guarda 7 dias, mas some se o servidor for apagado | histórico de 6 h | histórico de até 7 dias |
| Extensões (`btree_gist`, `pg_trgm`, `pgvector`) | qualquer uma, escolhendo a imagem | o `schema.sql` da v1, aplicado no Neon, cria `pg_trgm` (não conferido no banco); as outras não conferidas | idem |
| Manutenção | nossa: atualização de versão, disco, segurança | do Neon | do Neon |

Preços do Neon conferidos em neon.com/pricing em 16/11/2026. Backup do Hetzner conferido no FAQ de cobrança (docs.hetzner.com/cloud/billing/faq). Ficaram de fora: Supabase (Postgres gerenciado com autenticação e API próprias, que o ADR 0002 não usa; plano grátis não conferido) e Postgres local na máquina do Eduardo (a busca precisa do banco ligado o tempo todo).

## Critérios, com peso

Nota de 1 (atende mal) a 3 (atende bem).

| Critério | Peso | A. Hetzner | B. Neon grátis | C. Neon Launch |
| --- | --- | --- | --- | --- |
| 1. Espaço para a 57ª e a 58ª, com a tramitação | 3 | 3: ~31 GB | 1: a 57ª cabe em 1 GB, a 58ª passa | 3: paga por GB |
| 2. Cabe nos ~R$ 20 por mês | 3 | 3: menos de R$ 10 com backup | 3: zero | 1: a busca mantém o banco acordado e a computação passa do teto |
| 3. Busca rápida em toda requisição | 2 | 3: na mesma máquina, sem acordar | 1: dorme após 5 min; quase toda busca de um site com pouco acesso acorda o banco | 2: só sem dormir, que custa |
| 4. Restauração pronta | 2 | 1: dump e teste são nossos | 2: 6 h | 3: 7 dias |
| 5. Extensões do modelo e da busca | 2 | 3: a imagem decide | 2: `pgvector` e `btree_gist` não conferidos | 2: idem |
| 6. Pouca manutenção | 1 | 1: nossa | 3 | 3 |
| **Total (máximo 39)** | | **33** | **25** | **29** |

## Decisão

**A. Postgres em Docker no servidor Hetzner, que a v2 herda da v1.** A versão principal da imagem se fixa no `infra/compose.yml` do marco `infra.deploy` (com `pgvector`, se o ADR da busca mantiver os embeddings).

1. **Por que não o Neon grátis:** hoje cabe, mas a regra do método é decidir pelo tamanho que já se sabe que vem. A 58ª começa em fevereiro de 2027 e o banco passa de 1 GB durante ela. Além disso, o banco dormindo põe o atraso de acordar justamente na busca, a única coisa que roda na hora do acesso.
2. **Por que não o Neon Launch:** o armazenamento é barato, mas a computação é cobrada por hora acordada, e a busca o mantém acordado. Para ficar dentro dos R$ 20, o banco teria de dormir, e aí a busca volta a pagar o atraso.
3. **O preço da escolha é operar o banco:** backup, teste de restauração, atualização de versão e disco passam a ser nossos. O critério 4 é o único em que o Hetzner perde, e o marco `infra.deploy` já exige "backup restaurado uma vez".
4. **O banco Neon da v1 pode ser apagado** quando a v1 sair do ar. A limpeza pendente nele (`group_id`, `is_representante`, `apensacao`) deixa de importar.

### O que acontece por baixo

O Postgres roda num contêiner Docker. Os arquivos do banco ficam num volume, uma pasta do servidor que sobrevive quando o contêiner é recriado. O contêiner só escuta dentro do servidor: a porta 5432 nunca fica aberta para a internet. A API de busca conecta pela rede interna do Docker, com o papel `app` (só lê `marts`, como em [modelo.md](../dados/modelo.md#papéis-no-banco)). O pipeline, enquanto rodar na máquina do Eduardo, conecta por um túnel SSH, que leva a conexão até o servidor dentro da sessão SSH já autenticada, com o papel `pipeline`.

O backup tem duas camadas. Toda madrugada, depois do pipeline, o `pg_dump` grava uma cópia lógica comprimida, que é copiada para fora do servidor. Ela serve para restaurar o banco em qualquer máquina e qualquer versão. O backup do Hetzner fotografa o disco inteiro uma vez por dia e guarda 7 dias. Ele é rápido de voltar, mas depende do servidor existir, e uma foto do disco com o Postgres escrevendo só é tão boa quanto a recuperação depois de uma queda de energia. Por isso o `pg_dump` é o backup de verdade.

## Consequências

- **O marco `infra.deploy`** cria o `infra/compose.yml` (citado no CLAUDE.md, ainda não existe), o volume, os papéis, o `pg_dump` diário com cópia fora do servidor e um teste de restauração. Onde guardar a cópia de fora (Storage Box do Hetzner, armazenamento de objetos) se decide lá, com preço conferido.
- **Desenvolvimento local** usa a mesma imagem no mesmo compose. O CI não precisa do banco (ADR 0002).
- **RAM:** o Postgres divide os ~3,7 GB do servidor com a API de busca e, mais tarde, com o orquestrador. O método já registra que o BGE-M3 (~2,5 GB) e o Airflow (4 GB no mínimo) não cabem junto: isso é dos ADRs da busca e de `escala.airflow`, que podem pedir um servidor maior, não um banco gerenciado.
- **A tramitação cabe com o texto do despacho** (~230 MB estimados para todos os tipos). Quais tipos e colunas entram se decide no marco `dados.tramitacao`, pela métrica da pergunta 1, não pelo espaço.
- **`docs/dados/modelo.md`** continua valendo como está: ele assumia Postgres.

## Quando revisitar

- Se o disco do servidor passar de 70% ou o banco passar de 10 GB.
- Se manter o banco tomar mais de algumas horas por mês, ou se uma restauração falhar no teste.
- Se o orçamento mudar a ponto de um Postgres gerenciado sempre acordado caber nele.
- Se vier a camada paga com login e dados de usuário (o ADR 0002 já pede ADR novo para isso).
