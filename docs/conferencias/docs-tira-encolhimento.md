# Conferência: docs/tira-encolhimento

Registro de `scripts/conferir.py` (skill `/conferir`). Evidência é comando e saída, não "parece certo".

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| Nenhum código calculava o placar ajustado; ele só existia nos docs | `git ls-files` sem `docs/`: o Python está só em `pipeline/coleta`, `pipeline/qualidade` e `scripts/`; `grep -rniE "encolh\|shrink\|bayes\|prior\|pseudo"` sem achado em `.py` ou `.sql` | conferido |
| O contrato de `placar_eixo_deputado` guarda só contagens cruas | `sed -n 147,156p db/marts/contrato.yaml`: `k_positivo`, `k_negativo`, `n`, `n_consenso`, `n_abstencao`, `n_obstrucao`, `n_ausencia`; nenhuma coluna ajustada | conferido |
| Não sobra vestígio do placar ajustado no repositório | `grep -rniE "encolh\|shrink\|ajustad\|puxad\|m[eé]dia do partido\|taxa dos colegas\|m ?= ?5\|n m[ií]nimo\|placar-ajustado\|\(k \+ m"` fora de `.git`: só sobram "encolhe a superfície de ataque" (`metodo.md:259`), a decisão "Sem n mínimo" (`metricas.md:188`) e `cortar_em=5` em teste de HTTP, nenhum sobre o tema. O histórico do git e o vault ficaram de fora | conferido |
| O "n mínimo" de perguntas, método e personas contrariava a decisão de 14/11 | `grep -n "Sem n mínimo" docs/produto/metricas.md` → linha 188, decisão 2 de 14/11 | conferido |
| Exemplos do saldo: A (2 a favor, 0 contra, 8 votações) = +0,25; B (2, 6, 8) = −0,50; "+2 em 2" empata com "+8 em 8" | `(k − c) / T` recalculado em Python: 0.25, −0.5, 1.0 e 1.0 | conferido |
| `T` = `n` + abstenções + obstruções + ausências é o total de votações do eixo em que o deputado estava no mandato | O mart ainda não existe; depende de `n_ausencia` ser contado sobre o mesmo conjunto de votações que `n` e de a janela de 15 dias acertar o exercício do mandato | não conferido |

## Vazios

Sem mudança de dado: a branch só mexe em docs de produto e de método.
