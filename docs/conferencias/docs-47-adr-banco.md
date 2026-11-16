# Conferência: docs/47-adr-banco

Sessão de 16/11/2026: consulta ao vault e aos CLAUDE.md da v1 sobre o Neon, medição do tamanho da tramitação (scripts em `camara-lab/medicao_tramitacao/`, commit `579f8ed` daquele repositório) e ADR 0004. A branch não mexe em `db/marts`, `pipeline` nem em dado gerado; a seção Dados não se aplica.

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| 283.322 proposições de 2023 a 2026; soma de `ultimoStatus_sequencia` 1.553.659; nenhuma sequência vazia | `python3 -I universo.py dados/raw/arquivos/2026-11-16 ...`: `linhas 283322 eventos_estimados 1553659 sem_sequencia 0` | conferido |
| A sequência não é a contagem de eventos: 140 eventos para soma 222 nas 48 respostas, 12 com buracos | `amostra.py`: `eventos 140`, `sequencia == contagem: 36 difere: 12`, e a maior sequência devolvida costuma bater com a do CSV (`2482594` PL: 29 eventos, máxima 41 = 41), mas não sempre (`2361054` RIC: máxima 16 para 17 no CSV) | conferido |
| 2 de 50 chamadas deram 504 | Saída: `falhou 2550742 HTTP Error 504`, `falhou 2383901 HTTP Error 504` | conferido |
| ~980 mil eventos no total, ~360 mil nos tipos principais | 1.553.659 × 0,631 = 979.785; 570.718 × 0,631 = 360.123. A razão vem de 48 proposições, quase todas de tipos com poucos eventos (11 RPD, 8 REQ, 8 PRL; 3 PL): vale como ordem de grandeza | não conferido |
| 644 B de JSON por evento; `despacho` 141,5 B | `amostra.py`: `bytes_por_evento 644`, `despacho 141.5 B/evento` | conferido |
| Tramitação em tabela: ~95 B por linha enxuta, ~235 B com despacho; 93/230 MB e 34/85 MB | Conta de armazenamento do Postgres (cabeçalho 24 B, ponteiro 4 B, colunas tipadas, índice da chave). Não carreguei no Postgres: o Docker recusou a conexão (`permission denied ... docker.sock`) | não conferido |
| `core` e marts: ~150 a 300 MB; total da 57ª ~0,4 a 0,7 GB | Estimativa a partir das contagens de linhas de arquivo (`wc -l`, que conta a mais se houver campo com quebra de linha) | não conferido |
| Embeddings ~110 MB | 26.500 × 1.024 × 4 B = 108,5 MB; o 26,5 mil vem de `docs/metodo.md:276` | conferido (a conta) |
| 695,9 MB de CSV nos arquivos de 16/11 | Soma de `bytes` no `manifesto.json`: `total 695.9` | conferido |
| Neon grátis: 1 GB por projeto, dorme após 5 min sem poder desligar, histórico de 6 h; Launch: US$ 0,35 por GB-mês, US$ 0,106 por CU-hora, sem mínimo, histórico de até 7 dias | WebFetch em neon.com/pricing em 16/11/2026. A ferramenta devolve um resumo da página, não o texto cru | conferido (por resumo) |
| Ligado o mês todo com 0,25 CU custa ~US$ 19 | 0,25 × 730 × 0,106 = 19,3. Que 0,25 CU é o menor tamanho não está na página resumida | não conferido |
| Backup do Hetzner: 20% do preço do servidor, 7 cópias diárias | docs.hetzner.com/cloud/billing/faq: "monthly flat price, which is 20% of the price of the server"; docs.hetzner.com/cloud/servers/backups-snapshots/overview: "a total of seven Backup slots", diários | conferido |
| Backup do Hetzner sai por menos de R$ 10 | Preço do CX23 e câmbio não abertos | não conferido |
| Backups do Hetzner somem quando o servidor é apagado | Vem do resumo da busca (página regular-performance), não abri | não conferido |
| Hetzner: ~3,7 GB de RAM, ~31 GB de disco livre, sem Postgres nem Docker | Nota do vault `Eu/Servidor Hetzner - acesso e configuração` (38 GB − 6,9 GB usados); não olhei no servidor | não conferido |
| Neon da v1: 512 MB, 128 MB depois dos votos; pendência `group_id`, `is_representante`, `apensacao` | `CAPIVARA/CLAUDE.md:438` e `Capivara v1 - funcionalidades e decisões de produto.md:33`; o banco não foi aberto | conferido (na fonte escrita) |
| O `schema.sql` da v1 cria `pg_trgm` | `grep` em `CAPIVARA/scripts/schema.sql:401`: `CREATE EXTENSION IF NOT EXISTS pg_trgm;`. Se rodou no Neon, não conferi | conferido (o arquivo) |
| `pgvector` e `btree_gist` no Neon | Não abri a lista de extensões do Neon | não conferido |
| BGE-M3 ~2,5 GB e Airflow 4 GB no mínimo | `docs/metodo.md:277-278` | conferido (no método) |
| Placar 33 × 25 × 29, máximo 39 | Notas ponderadas por script: `A 33 B 25 C 29 max 39`. O primeiro rascunho dizia 24 e 28: pego antes do commit | conferido |
| As notas de 1 a 3 | Julgamento apoiado nos números acima | não conferido |
| `make rota` mostra o próximo passo novo | Saída: "próximo passo: escrever o ADR de hospedagem (site estático, API de busca e o Postgres do ADR 0004 no Hetzner)" | conferido |

## Vazios

Não se aplica: a branch não gera nem transforma dado.

## Retrospectiva

- Somei o placar de cabeça e errei duas colunas (24 e 28 em vez de 25 e 29). Pego por script antes do commit. A conferência do ADR 0003 já fazia a soma por script; a regra vale para todo placar.
- Escrevi no rascunho que a v1 "usou `pg_trgm` no Neon". O arquivo cria a extensão, mas não abri o banco: texto corrigido para "não conferido no banco".
- Antes da medição, eu disse ao Eduardo que o plano pago do Neon custava US$ 19 por mês, um número da época da v1. Hoje o Launch não tem mínimo e cobra por uso. Avisei que o preço de hoje não estava conferido, e a conferência mudou o desenho das opções.
