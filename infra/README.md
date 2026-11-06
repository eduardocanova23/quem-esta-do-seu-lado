# infra/

**Faz:** descreve o ambiente: Docker compose local (Postgres, Airflow) e o deploy no servidor.
**Recebe:** decisões dos ADRs de banco, Airflow em produção e hospedagem.
**Entrega:** arquivos de compose, configuração do servidor e scripts de deploy.
**Quem chama:** você, com `docker compose`, e o CI no deploy.

Regra: nenhum segredo aqui. Valores ficam em `.env` local, nos secrets do GitHub Actions e nas variáveis do servidor.

Vazia até o marco `infra.deploy`.
