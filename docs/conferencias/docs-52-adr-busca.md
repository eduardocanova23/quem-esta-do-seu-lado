# Conferência: docs/52-adr-busca

Sessão de 18/11/2026: ADR 0006 (busca), proposto, a partir do spike em `camara-lab/spike_busca/` (branch `spike/52-busca`, commits `8276f90`, `563ae80`, `de85357`). A branch não mexe em `db/marts`, `pipeline` nem em dado gerado; a seção Dados não se aplica. Os arquivos citados como `saida/...` estão em `camara-lab/spike_busca/saida/` (fora do git, como manda o lab).

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| v1: híbrida 80,7%, só embedding 76,7%, só BM25 70,7% em 150 independentes; coloquiais 89/80/66% | `CAPIVARA/definitivo/dag_temas/eval/busca_modos.md`, tabelas "Por modo" e "Por tipo" | conferido |
| A v1 guardava os vetores em fp16 | `fase1_embeddings.py` e `embeddings.py`: `.astype(np.float16)` | conferido |
| Dois vetores por proposição, vale o maior | `busca_modos.py`: `np.maximum(q @ self.eb.T, q @ self.eo.T)`; textos em `fase1_embeddings.py` | conferido |
| 23.036 fichas e 333 temas; ~46 mil vetores | `saida/acervo_int8.log`: "23036 fichas (46072 textos) e 333 temas" | conferido |
| Pesos 0,20 / 0,10 / 0,05 | `busca_modos.py` (`PESO_BM25 = 0.20`) e `run_all.py` (`PESOS = {"emb": 1.0, "bm25": 0.10, "props": 0.05, ...}`) | conferido |
| Listas julgadas saíram com 0,10 e 0,02 | Comentários em `busca_modos.py` e `run_all.py` ("0,10 até 03/11/2026"; "0,02 até a v1") e reprodução: com esses pesos, 311 de 311 iguais | conferido |
| A referência reproduz as proposições da híbrida nas 311 listas | `avaliar.py --conferir-v1`: `"c": {"props_iguais": 311}` | conferido |
| 27 temas diferentes por três temas retirados na v1.1 | `cat_conselheiros`, `cat_domesticas`, `cat_pescadores` nas listas julgadas e fora do `temas.parquet` atual (script na sessão); horários dos arquivos: julgamento 10:03, taxonomia 11:31 | conferido |
| 12 listas só-embedding diferem por empate exato | Script na sessão: em todas, menor diferença entre escores = 0; 10 com o mesmo conjunto, 2 com conjunto diferente | conferido |
| ONNX fp32 = vetor da v1 | `saida/acervo_fp32_amostra.json`: cosseno mínimo 0,99999988 em 4.000 textos (2.000 fichas) | conferido |
| Tamanhos 2.162 / 1.082 / 543 MB e cossenos contra o PyTorch | `dados/modelos/conferencia.json` | conferido |
| Acervo int8 19 min (40,5 textos/s), fp16 53 min (14,4), fp32 14,5 textos/s | `saida/acervo_{int8,fp16,fp32_amostra}.json` (1.137 s, 3.194 s) | conferido |
| fp32 levaria ~53 min no acervo inteiro | Conta: 46.011 / 14,5 = 53 min; não rodado | não conferido (estimativa) |
| RAM e tempo em 2 núcleos (694/726 MB, 23/30 ms etc.) | `taskset -c 0,1 ... medir.py`, saída na sessão; `nucleos_permitidos: 2` | conferido |
| Um dia: 2,1 + 1,4 s no int8 | `saida/acervo_int8.json`, `um_dia` | conferido |
| Pico de 615 proposições num dia, ~30 s | 615 vem da issue #52 (não refeito hoje); 1.230 textos / 40,5 = 30 s | não conferido (o 615) |
| fp16 99% das listas iguais; int8 23 a 25% idênticas, 54 a 59% mesmo conjunto | `saida/comparacao.json` | conferido |
| Juiz: tabela por grupo e precisão; 267 válidas de 267; US$ 0,2285 | `juiz.py --relatorio` e `--julgar`, saída na sessão | conferido |
| Bootstrap: nDCG −0,004 [−0,014; +0,006], acharia +0,011, preferida +0,107 | Script na sessão, 5.000 reamostras, semente 52 | conferido |
| Híbrida ganhou do BM25 por 0,095 de nDCG@5 na v1 | `busca_modos.md`: 0,828 − 0,733 = 0,095 | conferido |
| fp16 é lento na CPU porque o ONNX Runtime converte para fp32 | Explicação mais provável para o tempo igual ao do fp32 e o RSS maior; não li o código | não conferido |
| Servidor 3.815 MB, sem swap; v1 usa 927 MB; o resto, 293 MB | `ssh hetzner 'free -m'`, `swapon --show` vazio, soma do RSS com `ps` em 18/11/2026 | conferido |
| Postgres ~0,5 GB, resto da API ~0,15 GB, sobra ~2,1 GB | Estimativa; 3.815 − 300 − 730 − 150 − 500 − 30 | não conferido |
| halfvec ~91 MB | (2 × 23.036 + 333) × 1.024 × 2 B = 90,6 MiB | conferido (a conta) |
| Varredura numpy de 46 mil vetores ~12 ms em 2 núcleos | `medir.py` int8: `varredura_numpy_ms: 11.8` | conferido |
| `ts_rank` não usa estatística do acervo | postgresql.org/docs/current/textsearch-controls.html: "the ranking functions do not use any global information" | conferido (por resumo) |
| ParadeDB tem índice `USING bm25` | paradedb.com/docs/documentation/indexing/create-index: "`USING bm25` remains supported as a backwards-compatible alias" | conferido (por resumo) |
| Airflow pede 4 GB no mínimo | `docs/metodo.md:277-278` (método, não a fonte do Airflow) | conferido (no método) |
| Placar 47 / 40 / 27 / 42, máximo 48 | Script: `{'A': 47, 'B': 40, 'C': 27, 'D': 42} max 48` | conferido |
| As notas de 1 a 3 | Julgamento sobre a tabela e o spike | não conferido |

## Vazios

Não se aplica: a branch não gera nem transforma dado.

## Retrospectiva

- O ADR dizia "~170 MB" para o servidor sem a v1, somando só as 7 primeiras linhas do `ps`. A soma de todos os processos dá 293 MB. Corrigido, e a sobra passou de ~2,2 para ~2,1 GB.
- O ADR atribuía as consultas coloquiais às personas de `docs/produto/personas.md`, mas elas vêm do teste da v1. Corrigido.
- Na sessão, encerrei o lançador do venv no Windows e disse que a exportação tinha parado, mas o processo filho continuou. Só a listagem seguinte mostrou isso.
- A primeira tentativa de ler a chave do OpenRouter não achou a linha, porque o `.env` tem espaço antes do nome. Nada vazou.
