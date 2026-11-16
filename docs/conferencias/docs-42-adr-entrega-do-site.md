# Conferência: docs/42-adr-entrega-do-site

Sessão de 16/11/2026: ADR 0002 (forma de entrega do site), proposto em `f9ba973` e aceito pelo Eduardo em `325a13e`, com READMEs de `web/` e `api/`, mapa e rota. A branch não mexe em `db/marts`, `pipeline` nem em dado gerado; a seção Dados não se aplica.

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| 644 deputados com voto registrado na 57ª | duckdb sobre `dados/raw/arquivos/2026-11-16/votacoesVotos-202*.csv.gz`: `count(distinct deputado_id)` = 644; `deputado_idLegislatura` só tem `57` (473.323 votos); `deputado_id` vazio: 0 | conferido |
| "Titulares e suplentes" | 644 é maior que as 513 cadeiras, então há quem entrou no lugar de outro. Não separei titular de suplente | não conferido |
| 1.128 votações nominais de Plenário (de 1.604 nominais) | Mesma fonte: `count(distinct idVotacao)` = 1.604; junção com `votacoes-202*.csv.gz` por `id`, contada por `siglaOrgao`: PLEN 1.128, CCJC 284, CDHMIR 39, CE 35, CSPCCO 22 | conferido |
| **Errado na 1ª versão:** "1.604 votações com voto nominal viram listas da fatia 1" | As de comissão ficam fora da fatia 1 (`docs/produto/nao-objetivos.md`). Corrigido para 1.128 de Plenário | conferido |
| 26.598 proposições de PL, PLP, PEC, PDL e MPV (283.322 de todos os tipos) | `proposicoes-202*.csv.gz`: `count(*)` = `count(distinct id)` = 26.598 com `siglaTipo in (...)`; total 283.322, sem duplicata de id; `siglaTipo` vazio: 0 | conferido |
| Da ordem de 30 mil páginas por legislatura | Soma de 644 + 26.598 = 27.242, mais votações e temas. Estimativa: o build real decide quais páginas existem | não conferido |
| Placar 44 × 32 × 29, máximo 48 | Notas lidas das linhas 43 a 49 do próprio ADR por script e ponderadas: `{'A': 44, 'B': 32, 'C': 29}`; máximo 3 × 16 = 48 | conferido |
| As notas de 1 a 3 de cada critério | Julgamento, dito como tal no ADR | não conferido |
| H2.1, H3.6, H7.1 e H7.2 dizem o que o ADR cita | `grep -n` em `docs/produto/historias.md`: linhas 74, 93, 137 e 138 | conferido |
| A busca acha tudo desde a primeira publicação (decisão de 13/11/2026) | `docs/produto/historias.md:52` | conferido |
| O robô de prévia do WhatsApp não roda JavaScript | Sem fonte aberta; marcado "não conferido" no ADR. O teste de H7.2 (`build`) confere | não conferido |
| O ranking de uma legislatura cabe em dezenas de KB | Estimativa, dita como tal no ADR | não conferido |
| `make ci` verde na branch | 16/11: `109 passed`, `no leaks found` | conferido |
| `make rota` mostra o próximo passo novo da frente infra | Saída: "próximo passo: escrever o ADR do framework, com um spike..." | conferido |

## Vazios

Não se aplica: a branch não gera nem transforma dado.

## Retrospectiva

- Contei 1.604 votações nominais sem separar por órgão e escrevi que viravam listas da fatia 1. Causa: tratei a contagem como pronta sem cruzar com o filtro que o produto já define (Plenário só). A regra "fato se confere na fonte" pegou só na `/conferir`; a contagem estava certa, o que ela representava não.
