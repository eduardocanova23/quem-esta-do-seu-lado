# pipeline/passos.py e a coleta dos arquivos em lote para raw

_Desenho aprovado na conversa de 16/11/2026. Marco `dados.core`, primeiro passo da frente `dados`._

## O que este trabalho entrega

1. `pipeline/passos.py`: a lista de passos da coleta, num arquivo só, que o `make atualizar` roda hoje e as DAGs do Airflow leem na Fase 5 ([metodo.md](../../metodo.md), "Airflow depois, sem retrabalho").
2. O primeiro passo, `pipeline/coleta/arquivos.py`: baixa os arquivos em lote da Câmara para `dados/raw/arquivos/<D>/`, com `--data D`, idempotente.
3. Os testes que provam a idempotência, escritos antes do código.

Não precisa de banco: o `raw` mora fora do Postgres ([modelo.md](../../dados/modelo.md), "As camadas").

## Decisões

| Decisão | Escolhido | Por quê | Descartado |
| --- | --- | --- | --- |
| Formato do `raw` | CSV original, comprimido com gzip | Cópia exata do que veio; hash calculado sobre os bytes originais; só biblioteca padrão | Parquet: a Câmara não publica (`.../parquet/votacoesVotos-2025.parquet` dá 404), converter interpreta tipos e encoding e pede pyarrow. Foto semanal + delta: reconstruir um dia fica caro e o hash de linha é trabalho do `core` |
| Data lógica que não é hoje | Só baixa quando `D` é hoje (America/Sao_Paulo). `D` passada com raw completo: nada a fazer. `D` passada sem raw, ou futura: erro | A fonte não guarda o passado: baixar hoje e gravar como `D` antiga seria uma data falsa, a defasagem silenciosa da v1 | Aceitar ontem; baixar sempre marcando a hora real |
| Forma do `passos.py` | Lista de dados (`Passo(nome, modulo, depende_de)`), cada passo roda como `python -m <modulo> --data D` num processo próprio | É o que uma DAG consome sem importar o pipeline; o teste confere a lista sem executar nada | Decorador (a lista só existe depois de importar tudo); YAML (mais um formato, e o Airflow lê Python) |
| Onde fica o checkpoint | `manifesto.json` de cada data no próprio `raw` | Ainda não há banco nem schema `controle`; o manifesto é a prova de que a data foi processada | Tabela em `controle`: entra quando o banco nascer |

## pipeline/passos.py

```python
@dataclass(frozen=True)
class Passo:
    nome: str                       # "coleta_arquivos"
    modulo: str                     # "pipeline.coleta.arquivos"
    depende_de: tuple[str, ...] = ()

PASSOS: tuple[Passo, ...] = (
    Passo("coleta_arquivos", "pipeline.coleta.arquivos"),
)

def ordem(passos=PASSOS) -> list[Passo]: ...   # topológica e estável (empate: ordem da lista); erro em ciclo ou dependência que não existe
```

- `python -m pipeline.passos --data D` roda `ordem()` em sequência, cada passo com `sys.executable -m <modulo> --data D`. Para no primeiro que sair com código diferente de 0 e sai com o código dele, dizendo qual passo falhou.
- `make atualizar` chama isso com `DATA` ou, sem `DATA`, a data de hoje em Brasília.
- Todo passo é um módulo com `main(argv) -> int` e `if __name__ == "__main__"`, e aceita `--data AAAA-MM-DD`.

## pipeline/coleta/arquivos.py

### Entradas

- `--data D` (obrigatório) e `--raiz` (padrão `dados/raw`).
- URL base `https://dadosabertos.camara.leg.br/arquivos`, trocável por `CAMARA_ARQUIVOS_URL` (é o que os testes usam).
- O relógio, injetável nos testes.

### Conjuntos

Conferido em 16/11/2026 com HEAD:

- **Sem ano:** `legislaturas`, `deputados`. O endereço é `<base>/<conjunto>/csv/<conjunto>.csv`; a versão com ano dá 404.
- **Por ano:** `votacoes`, `votacoesVotos`, `votacoesOrientacoes`, `votacoesProposicoes`, `votacoesObjetos`, `proposicoes`, `proposicoesAutores`, `proposicoesTemas`. O endereço é `<base>/<conjunto>/csv/<conjunto>-<ano>.csv`. Todos dão 200 em 2026 e 404 em 2027.

### Anos

- **Quentes:** os anos que vão de `ano(dataInicio)` da legislatura vigente em `D` até `ano(D)`. A legislatura vigente é a linha de `legislaturas.csv` com `dataInicio ≤ D ≤ dataFim`. O arquivo vem em UTF-8 com BOM e separado por `;`, e já traz a 58ª (01/02/2027 a 31/01/2031). Em 16/11/2026 os anos quentes são 2023 a 2026; a partir de 01/02/2027, só 2027.
- Por isso `legislaturas` é baixado primeiro.
- Data sem legislatura vigente dá erro.
- **Frios:** parâmetro `anos_frios`, vazio neste PR. Quem diz quais anos entram é o `core` (proposição votada ou com autoria de deputado da legislatura). O agendamento semanal fica para depois.

### Fluxo para uma data D

1. `manifesto.json` existe em `D/`: imprime "nada a fazer" e sai com 0, sem nenhuma requisição.
2. Não existe e `D` não é hoje: sai com erro. Se `D` é passada, a mensagem é "a fonte não guarda o passado"; se é futura, "data futura".
3. Para cada arquivo, nesta ordem: `legislaturas`, `deputados`, depois conjunto × ano quente.
   - Se ele já está em `manifesto.parcial.json` (retomada depois de uma queda), pula.
   - Senão, baixa em streaming para um `.parcial`, calcula o sha256 dos bytes originais e grava o gzip com `mtime=0` e sem nome de arquivo no cabeçalho, para que os mesmos bytes deem o mesmo `.gz`.
   - Compara o sha256 com a última coleta anterior do mesmo arquivo, buscando a data mais recente com manifesto em que ele foi registrado. Se for igual, apaga a cópia nova e a entrada aponta para a data onde os bytes moram (`em: "<data>"`, sempre a data física e nunca uma cadeia de ponteiros). Se for diferente, renomeia o `.parcial` para `<conjunto>[-<ano>].csv.gz`.
   - Registra a entrada em `manifesto.parcial.json`, com escrita atômica: arquivo temporário e depois `os.replace`.
4. No fim, `manifesto.parcial.json` vira `manifesto.json` com `os.replace`. Só nesse ponto a data conta como processada.
5. Imprime a contagem de arquivos novos, iguais e ausentes.

### Entrada do manifesto

```json
{"conjunto": "votacoesVotos", "ano": 2026, "url": "...", "status": "novo|igual|ausente",
 "sha256": "...", "bytes": 17665811, "coletado_em": "2026-11-16T09:12:03-03:00",
 "etag": "...", "last_modified": "...", "em": "2026-11-16"}
```

O manifesto também leva `data`, `anos_quentes`, `anos_frios` e a versão do formato.

### Erros

- **404 de conjunto com ano:** `status: ausente` (é o ano novo que ainda não tem arquivo), não é erro.
- **404 de `legislaturas` ou `deputados`:** erro.
- **Conjunto com ano sem nenhum ano quente disponível** (todos deram 404): erro. É endereço mudado, não ano novo.
- **5xx ou timeout:** três tentativas com espera crescente (a API deu 504 por minutos em 15/11). Esgotadas as tentativas, o passo sai com erro e o manifesto final não é escrito.
- **Qualquer outro status:** erro, sem tentar de novo.
- O User-Agent é genérico (`camara-v2-pipeline`), sem dado pessoal.

## Testes (escritos primeiro; mostro falhando e depois passando)

Os testes usam um servidor HTTP local (`http.server` numa thread) com fixtures pequenas cortadas de CSVs reais, guardadas em `pipeline/tests/fixtures/arquivos/`. Nenhum teste fala com a Câmara.

1. **Idempotência:** rodar `D` duas vezes deixa a árvore de `D/` byte a byte igual, e a segunda execução não faz nenhuma requisição.
2. **Conteúdo igual no dia seguinte:** `D+1` com os mesmos bytes não grava `.gz`, a entrada fica `igual` com `em: D`, e o `.gz` de `D` descomprimido tem o sha256 do manifesto.
3. **Conteúdo diferente:** grava um `.gz` novo com `status: novo`.
4. **Datas:** `D` passada sem raw dá erro; `D` futura dá erro; `D` passada com raw dá "nada a fazer".
5. **404 de ano:** vira `ausente`; 404 de `legislaturas` faz o passo sair com erro; um conjunto com 404 em todos os anos quentes também.
6. **Queda no meio:** o servidor falha no 3º arquivo. Não sobra `.parcial` aceito nem `manifesto.json`. A nova execução retoma pelo `manifesto.parcial.json` sem baixar de novo os 2 primeiros.
7. **5xx:** tenta de novo e acaba aceitando; sempre 5xx esgota as tentativas e dá erro.
8. **Anos quentes:** em 16/11/2026 são 2023 a 2026; em 15/01/2027, 2023 a 2027; em 01/02/2027, só 2027.
9. **`passos.py`:** sem ciclo, toda dependência existe, todo módulo importa e tem `main`; `ordem()` acusa ciclo e dependência que não existe; o runner para no primeiro passo que falha.
10. **`.gitignore`:** `git check-ignore dados/raw/x.csv.gz` sai com 0.

Cada teste novo é visto falhando por uma mutação conferida antes de ser aceito.

## Mudanças nos docs, no mesmo PR

- **`.gitignore`:** ganha `dados/`. Hoje não tem; o `metodo.md:332` diz que tem.
- **parquet → CSV com gzip:** em `docs/dados/atualizacao.md` (tabela `raw.arquivo`), `docs/dados/modelo.md` (camada `raw`) e `docs/metodo.md` (linha das camadas).
- **`pipeline/README.md`:** o módulo `coleta/` e o `passos.py`.
- **`CLAUDE.md`:** `make atualizar` deixa de ser "nasce com o marco".
- **`Makefile`:** alvo `atualizar`.
- **`docs/frentes.yaml`:**
  - um marco novo, `dados.raw` ("passos.py e coleta dos arquivos em lote para raw, idempotente"), antes de `dados.core`, feito neste PR;
  - `dados.core` passa a depender de `dados.raw` e de `infra.adrs`, porque o `core` precisa do banco e o ADR do banco sai nessa ordem ([metodo.md](../../metodo.md), linha 251).
  - Com isso a frente `dados` fica com o marco atual bloqueado, e o `rota-check` falha (`scripts/rota.py:82`). Por isso o mesmo PR troca a frente ativa, e **o Eduardo decide qual vai ser a próxima ativa ao revisar o PR** (a sugestão é `infra`).

## Fora deste PR

Anos frios de verdade, agenda semanal, `raw.api`, `core`, banco, schema `controle`, limpeza ou retenção do `raw`.

## Riscos

- **Disco.** Os anos quentes somam algumas centenas de MB por dia sem comprimir. A estimativa sai dos tamanhos de 2025 e 2026 (`votacoesVotos-2025` tem 58 MB e `proposicoes-2025` tem 90 MB) e não foi conferida; com gzip, a quantidade de MB por dia também não. O primeiro `make atualizar` de verdade mede e anota em `atualizacao.md`, e a retenção vira tarefa própria se precisar.
- **A Câmara muda o endereço ou o encoding.** O 404 nos conjuntos sem ano para o passo, mas um 404 em todos os anos passaria por "ausente". Para não deixar passar, o passo sai com erro quando nenhum ano quente de um conjunto vem (ver Erros).
- **A hora em que a Câmara refaz os arquivos varia entre 03:30 e 07:11 UTC** (Last-Modified de 16/11). Rodar antes disso pega o arquivo da véspera. O manifesto guarda o `last_modified`, e a agenda (Fase 5) roda depois das 08:00 UTC.
