# pipeline/

**Faz:** coleta os dados da Câmara e da mídia, limpa, enriquece com IA, testa a qualidade e publica os marts.
**Recebe:** arquivos em lote e API da Câmara, matérias da mídia.
**Entrega:** as camadas `raw` (fora do Postgres), `core`, `ia` e `marts`.
**Quem chama:** as DAGs de `dags/` ou você à mão, pela CLI de cada etapa (`python -m pipeline.ingestao --data AAAA-MM-DD`).

Um módulo por etapa: `coleta/`, `transformacao/`, `ia/`, `qualidade/`, `publicacao/`. Transformação em funções puras, entrada e saída nas bordas. Testes em `tests/`, com respostas reais e pequenas da Câmara em `tests/fixtures/`.

Vazia até o marco `dados.core`.
