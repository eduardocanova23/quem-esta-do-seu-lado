# Conferência: feat/passos-coleta

Sessão de 16/11/2026: desenho, spec (`d6a089d`) e plano (`0391b52`) do `pipeline/passos.py` e da coleta dos arquivos em lote. Ainda sem código; a conferência do código e dos dados vem com o PR.

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| A Câmara não publica parquet dos arquivos em lote | `curl -sI .../votacoesVotos/parquet/votacoesVotos-2025.parquet`: `HTTP/2 404`; o CSV do mesmo ano: `200`, `content-length: 58233239`. Só esse caminho de parquet foi testado | conferido |
| Os 8 conjuntos por ano dão 200 em 2026 e 404 em 2027 | `curl -sI` em cada um, 16/11: os 8 `HTTP/2 200` em 2026 e os 8 `HTTP/2 404` em 2027 | conferido |
| `deputados` e `legislaturas` não têm ano | Sem ano: `200` (1.372.783 e 5.843 bytes); `-2025`: `404` nos dois | conferido |
| Conjunto ou ano inventado dá 404 (o 404 distingue ausência) | `inventado-2025.csv` e `votacoesVotos-1899.csv`: `HTTP/2 404`, contra `200` nos reais | conferido |
| `legislaturas.csv` está em UTF-8 com BOM, separado por `;`, e já traz a 58ª (01/02/2027 a 31/01/2031) | `file -`: `UTF-8 (with BOM)`; linha `"58";…;"2027-02-01";"2031-01-31";"2026"` | conferido |
| Os arquivos são refeitos de madrugada, entre 03:30 e 07:11 UTC | `last-modified` de 16/11: `legislaturas` 03:30:00, `votacoesVotos-2025` 07:11:11. Um dia só | não conferido |
| `dados/` está no `.gitignore` (eu disse isso, repetindo o `metodo.md:332`) | **Errado**: `grep dados .gitignore` saiu 1; `git check-ignore -v dados/raw/x.csv.gz` saiu 1. A correção e o teste estão na Tarefa 1 do plano | conferido |
| Frente ativa com marco bloqueado quebra o `rota-check` | `scripts/rota.py:82`: `if f.get("ativa") and atual and faltando(atual, marcos)` | conferido |
| `urllib` lendo em blocos não acusa corpo cortado antes do `Content-Length` | Script com socket local que declara `Content-Length: 100` e manda 5 bytes: `SEM ERRO: leu 5 de 100 bytes declarados` | conferido |
| Os anos quentes somam algumas centenas de MB por dia; o gzip reduz isso para dezenas | Estimativa a partir de três tamanhos | não conferido |
| A skill `/migracao` e o `infra/compose.yml` citados no CLAUDE.md não existem | `ls .claude/skills`: só `conferir`; `ls infra`: só `README.md` | conferido |
| As 10 fixtures em `pipeline/tests/fixtures/arquivos/` são os bytes reais da Câmara (cabeçalho + 2 linhas) | Rebaixadas com `curl -r 0-4095 <url>` cortado em 3 linhas com `head -3` e comparadas com `cmp`: `igual` nas 10 (legislaturas e deputados sem ano; os outros 8 de 2025) | conferido |
| O pre-commit não altera as fixtures | o `exclude` do `end-of-file-fixer` e do `trailing-whitespace` no `.pre-commit-config.yaml` passou a cobrir `pipeline/tests/fixtures/` além de `db/`; o `cmp` acima foi feito depois do commit, contra o arquivo versionado | conferido |
| Cada teste novo derruba a mutação que diz pegar | `<= fim`→`< fim`: `test_anos_quentes_ultimo_dia_57`; sem conferência do Content-Length: `test_corte_no_meio`; `.gz` mesmo com hash igual: `test_mesmo_conteudo_no_dia_seguinte`; manifesto antes do fim: `test_queda_e_retomada` e `test_conjunto_sem_nenhum_ano`; ignorar código de saída: `test_rodar_para_no_primeiro_que_falha`. Cada mutação conferida com `grep -c` e desfeita (`cmp`) | conferido |
| O BOM de `legislaturas.csv` muda os anos quentes (Review Focus 3 do plano) | **Errado**: a mutação sem `-sig` não derrubou teste nenhum; o BOM só gruda em `idLegislatura`, que não é lida | conferido |
| `dados/` no `.gitignore` ignora só a pasta da raiz | **Errado na 1ª versão**: `dados/` casava com `docs/dados/`. Corrigido para `/dados/`; `test_so_a_pasta_da_raiz` falhou antes e passa depois; `git check-ignore docs/dados/novo.md` → exit 1 | conferido |
| `make ci` verde na branch | `exit=0`: rota-check, ruff, mypy (21 arquivos), `105 passed`, `no leaks found`; depois do fix do `.gitignore`, `pytest` → `106 passed` | conferido |
| Data passada não faz requisição nem cria pasta | `make atualizar DATA=2026-11-15` → `erro: … a fonte não guarda o passado`, exit 2; `ls dados` → não existe | conferido |
| O passo baixa os 34 arquivos reais de hoje e o gzip reduz o raw | `make atualizar` ao vivo em andamento | não conferido |
