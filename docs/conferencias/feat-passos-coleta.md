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
