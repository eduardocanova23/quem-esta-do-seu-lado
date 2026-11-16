# Estado: passagem de sessão

_Anotação de passagem quando uma tarefa para no meio: o que estava sendo feito, onde parou e o próximo comando. Vazio quando nada está parado. O histórico do que já foi feito fica nos PRs._

## pipeline/passos.py e coleta dos arquivos em lote (16/11/2026)

- Branch `feat/passos-coleta`, só local, ainda sem issue: o `gh issue create` foi barrado pela permissão. Texto da issue no plano, Tarefa 5.
- Feito: a spec `docs/superpowers/specs/2026-11-16-passos-coleta-arquivos-design.md`, aprovada pelo Eduardo, e o plano `docs/superpowers/plans/2026-11-16-passos-coleta-arquivos.md`, que espera a revisão dele.
- Parou em: o Eduardo revisar o plano e escolher a execução (recomendação: Native) e dar ok às fixtures (10 × 4 KB da Câmara).
- Próximo comando: Tarefa 1 do plano, `uv run --locked pytest pipeline/tests/test_coleta_fonte.py pipeline/tests/test_gitignore.py -v` falhando.
- Decisões pendentes para o PR: qual frente fica ativa (sugestão: `infra`) e o ok para o `make atualizar` ao vivo.
