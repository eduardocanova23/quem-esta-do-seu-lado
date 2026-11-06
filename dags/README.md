# dags/

**Faz:** define as DAGs do Airflow (`ingestao_diaria`, `midia_diaria`, `enriquecimento`, `publicacao`, `manutencao_taxonomia`, `backfill`).
**Recebe:** a agenda e os gatilhos de dados prontos (assets).
**Entrega:** a ordem em que as funções do `pipeline/` rodam.
**Quem chama:** o agendador do Airflow.

Regra: DAG fina, sem lógica. Só chama funções do `pipeline/`; tudo o que dá para testar mora lá.

Vazia até o primeiro marco da frente de dados.
