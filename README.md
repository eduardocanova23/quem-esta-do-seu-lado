# Quem está do seu lado

Site que responde, em linguagem comum, três perguntas sobre a Câmara dos Deputados: quais assuntos ela prioriza e quais abandona, se um deputado está do lado de quem pergunta e quem é o mais aliado ou o mais inimigo.

Em construção (Fase 0). O método está em [docs/metodo.md](docs/metodo.md).

## Pastas

| Pasta | O que tem |
| --- | --- |
| [docs/](docs/) | Requisitos, decisões (ADRs), modelo de dados, design e runbooks |
| [pipeline/](pipeline/) | Coleta, transformação, IA, qualidade e publicação dos dados |
| [dags/](dags/) | DAGs do Airflow, que só chamam o pipeline |
| [db/](db/) | Migrations e SQL dos marts |
| [taxonomia/](taxonomia/) | Árvore de temas e apelidos |
| [avaliacao/](avaliacao/) | Gabaritos e conjunto congelado das personas |
| [api/](api/) | API de busca |
| [web/](web/) | O site |
| [scripts/](scripts/) | Utilitários reexecutáveis |
| [infra/](infra/) | Docker compose e deploy |

Direção das dependências: `dags` → `pipeline` → banco → `web` e `api`. Nada importa de `dags`, e o `web` nunca importa o `pipeline`.
