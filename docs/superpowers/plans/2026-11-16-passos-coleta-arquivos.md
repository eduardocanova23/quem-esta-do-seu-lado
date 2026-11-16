# passos.py e coleta dos arquivos em lote: plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Objetivo:** `make atualizar` roda `pipeline/passos.py`, que roda o passo `pipeline.coleta.arquivos --data D`, que grava os arquivos em lote da Câmara em `dados/raw/arquivos/D/` de forma idempotente.

**Arquitetura:** três módulos de coleta, cada um com uma responsabilidade:
- `fonte.py`: o que baixar (conjuntos, URLs, anos quentes);
- `http.py`: como baixar (streaming, sha256, gzip, tentativas);
- `arquivos.py`: o passo (datas, manifesto, deduplicação, CLI).

O `passos.py` é uma lista de dados e um runner por subprocesso.

**Stack:** Python 3.13, só biblioteca padrão (`urllib.request`, `gzip`, `hashlib`, `json`, `zoneinfo`, `http.server` nos testes), pytest, mypy strict.

**Spec:** `docs/superpowers/specs/2026-11-16-passos-coleta-arquivos-design.md`

## Restrições globais

- Nenhuma dependência nova no `pyproject.toml`.
- `mypy --strict` e `ruff` (linha de 120) passam. Os comandos rodam com `uv run --locked`.
- Fuso: `ZoneInfo("America/Sao_Paulo")`. Datas no formato `AAAA-MM-DD`.
- URL base padrão: `https://dadosabertos.camara.leg.br/arquivos`; trocável pela variável de ambiente `CAMARA_ARQUIVOS_URL`.
- User-Agent: `camara-v2-pipeline`.
- O gzip é gravado com `mtime=0` e `filename=""`. O sha256 é calculado sobre os bytes **descomprimidos**, que são os originais.
- Nenhum teste fala com a Câmara.
- TDD: cada teste é visto falhando antes do código. Cada teste novo também é visto falhando por uma mutação no código pronto, e a mutação é conferida antes de valer.
- Commit em português, no formato Conventional Commits, com o trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. `git add` arquivo por arquivo.

## Pontos para a revisão olhar

1. **Data `D` igual a hoje, com `manifesto.json` de outra execução de hoje:** dá "nada a fazer", sem baixar de novo. Rodar duas vezes no mesmo dia não pega uma versão mais nova da Câmara. Isso é esperado e o teste da Tarefa 3 fixa.
2. **Resposta 200 cortada no meio** (a conexão cai durante o streaming): o `.parcial` nunca é aceito, e a próxima execução baixa de novo. Teste na Tarefa 2.
3. **`legislaturas.csv` com BOM e aspas:** se o BOM não for tirado, a primeira coluna vira `﻿idLegislatura` e nenhuma legislatura é achada. Teste na Tarefa 1 com os bytes reais.
4. **Virada de legislatura:** em 31/01/2027 a 57ª vale (2023 a 2027); em 01/02/2027 vale a 58ª (só 2027). Teste na Tarefa 1.
5. **`--raiz` relativo rodado de outra pasta pelo runner:** o subprocesso herda o cwd do runner, e o teste do runner usa `cwd` explícito. Teste na Tarefa 4.

---

### Tarefa 1: o que baixar (`fonte.py`) e `dados/` fora do git

**Arquivos:**
- Criar: `pipeline/coleta/__init__.py`, `pipeline/coleta/fonte.py`, `pipeline/tests/test_coleta_fonte.py`, `pipeline/tests/test_gitignore.py`, `pipeline/tests/fixtures/arquivos/legislaturas.csv`
- Modificar: `.gitignore`

**Interfaces que esta tarefa produz:**
- `CONJUNTOS_SEM_ANO: tuple[str, ...] = ("legislaturas", "deputados")`, nesta ordem, porque o `legislaturas` vem primeiro.
- `CONJUNTOS_POR_ANO: tuple[str, ...] = ("votacoes", "votacoesVotos", "votacoesOrientacoes", "votacoesProposicoes", "votacoesObjetos", "proposicoes", "proposicoesAutores", "proposicoesTemas")`
- `BASE_URL = "https://dadosabertos.camara.leg.br/arquivos"`
- `def url(base: str, conjunto: str, ano: int | None) -> str` devolve `f"{base}/{c}/csv/{c}.csv"` sem ano e `f"{base}/{c}/csv/{c}-{ano}.csv"` com ano.
- `def nome_arquivo(conjunto: str, ano: int | None) -> str` devolve `"votacoesVotos-2026.csv.gz"` ou `"deputados.csv.gz"`.
- `def anos_quentes(legislaturas_csv: bytes, data: date) -> list[int]` levanta `ValueError("nenhuma legislatura vigente em <data>")`.

- [ ] **Passo 1: Fixture com bytes reais.** Grave o cabeçalho e as linhas da 57ª e da 58ª de `legislaturas.csv` sem mexer no conteúdo, com BOM e aspas:
  `curl -s https://dadosabertos.camara.leg.br/arquivos/legislaturas/csv/legislaturas.csv | head -3 > pipeline/tests/fixtures/arquivos/legislaturas.csv`
  Confira com `file` (tem de dizer `with BOM`) e com `head -c 3 | xxd` (`efbbbf`).

- [ ] **Passo 2: Testes que falham.**
  - `test_anos_quentes_57`: na data 2026-11-16 dá `[2023, 2024, 2025, 2026]`.
  - `test_anos_quentes_ultimo_dia_57`: na data 2027-01-31 dá `[2023, 2024, 2025, 2026, 2027]`.
  - `test_anos_quentes_58`: na data 2027-02-01 dá `[2027]`.
  - `test_sem_legislatura_vigente`: a data 2031-02-01 levanta `ValueError`.
  - `test_url`: `url(BASE_URL, "deputados", None) == ".../arquivos/deputados/csv/deputados.csv"` e `url(BASE_URL, "votacoes", 2025) == ".../arquivos/votacoes/csv/votacoes-2025.csv"`.
  - `test_dados_fora_do_git` (em `test_gitignore.py`): `subprocess.run(["git", "check-ignore", "-q", "dados/raw/x.csv.gz"]).returncode == 0`.

- [ ] **Passo 3: Ver falhar.** Rode `uv run --locked pytest pipeline/tests/test_coleta_fonte.py pipeline/tests/test_gitignore.py -v`. Esperado: FAIL, com `ModuleNotFoundError: pipeline.coleta` e returncode 1 no gitignore.

- [ ] **Passo 4: Implementar.** Em `fonte.py`, leia com `bytes.decode("utf-8-sig")` e `csv.DictReader(delimiter=";")`, e compare datas com `date.fromisoformat`. No `.gitignore`, acrescente o bloco `# Dados do pipeline (raw, saídas locais): nunca no git\ndados/`.

- [ ] **Passo 5: Ver passar.** Mesmo comando. Esperado: PASS. Em seguida, mutação: tirar o `-sig` faz `test_anos_quentes_57` falhar. Confira e desfaça.

- [ ] **Passo 6: Commit.** `feat(coleta): conjuntos, URLs e anos quentes dos arquivos em lote; dados/ fora do git`

### Tarefa 2: baixar um arquivo (`http.py`)

**Arquivos:**
- Criar: `pipeline/coleta/http.py`, `pipeline/tests/servidor_falso.py`, `pipeline/tests/test_coleta_http.py`

**Interfaces que esta tarefa produz:**
- `@dataclass(frozen=True) class Baixado: sha256: str; bytes: int; etag: str | None; last_modified: str | None`
- `class Ausente(Exception)`: a resposta foi 404.
- `class FalhaDeColeta(Exception)`: outro status, 5xx depois das tentativas, timeout ou conexão caída.
- `def baixar(url: str, destino: Path, *, esperas: Sequence[float] = (2.0, 8.0, 30.0), timeout: float = 60.0) -> Baixado`
  - Grava em `destino` (o caminho `.parcial` que quem chama escolhe) o gzip dos bytes, com `mtime=0` e `filename=""`, em blocos de 1 MiB.
  - Confere o total recebido contra o `Content-Length` quando ele vem. Se a conta não bate, levanta `FalhaDeColeta`.
  - Em erro, apaga o `destino`.
  - Tenta de novo em 5xx, timeout e conexão caída: `len(esperas)` tentativas extras, com `time.sleep(espera)`. 404 levanta `Ausente` na hora; outro 4xx levanta `FalhaDeColeta` na hora.
- `servidor_falso.py`: fixture pytest `servidor` com `.base: str`, `.rotas: dict[str, Rota]` e `.pedidos: list[str]` (os caminhos pedidos, em ordem). `Rota` tem `status: int = 200`, `corpo: bytes = b""`, `falhas_antes: int = 0` (quantas respostas 500 dá antes da resposta certa) e `cortar_em: int | None = None` (manda `Content-Length` cheio e fecha a conexão depois de N bytes). Usa `ThreadingHTTPServer` na porta 0, numa thread, e responde 404 a rota que não existe. Registre-o como plugin em `pipeline/tests/conftest.py` com `pytest_plugins = ["pipeline.tests.servidor_falso"]`, ou importe a fixture direto. Escolha um jeito e use só ele.

- [ ] **Passo 1: Testes que falham** (todos chamam com `esperas=(0, 0, 0)`):
  - `test_baixa_e_comprime`: `gzip.decompress(destino.read_bytes())` é igual ao corpo, `sha256` é o `hashlib` do corpo e `bytes` é `len(corpo)`.
  - `test_gzip_reprodutivel`: baixar duas vezes para dois destinos dá `.gz` byte a byte iguais.
  - `test_404_ausente`: levanta `Ausente`, e `destino` não existe.
  - `test_5xx_tenta_de_novo`: com `falhas_antes=2`, dá certo e `len(pedidos) == 3`.
  - `test_5xx_esgota`: com `falhas_antes=10`, levanta `FalhaDeColeta`, `len(pedidos) == 4` e `destino` não existe.
  - `test_corte_no_meio`: com `cortar_em=5`, levanta `FalhaDeColeta`, e `destino` não existe.
  - `test_guarda_etag`: a rota manda `ETag: "x"`, e `Baixado.etag == '"x"'`.

- [ ] **Passo 2: Ver falhar.** Rode `uv run --locked pytest pipeline/tests/test_coleta_http.py -v`. Esperado: FAIL na importação.

- [ ] **Passo 3: Implementar `baixar`** com `urllib.request.urlopen(Request(url, headers={"User-Agent": "camara-v2-pipeline"}), timeout=timeout)`. `HTTPError` com código 404 vira `Ausente`. `IncompleteRead`, `URLError`, `TimeoutError` e `ConnectionError` contam como falha que pode tentar de novo.

- [ ] **Passo 4: Ver passar.** Esperado: PASS. Mutação: tirar a conferência do `Content-Length` faz `test_corte_no_meio` falhar. Confira e desfaça.

- [ ] **Passo 5: Commit.** `feat(coleta): download em streaming com sha256, gzip reprodutível e tentativas`

### Tarefa 3: o passo (`arquivos.py`)

**Arquivos:**
- Criar: `pipeline/coleta/arquivos.py`, `pipeline/tests/test_coleta_arquivos.py`, e em `pipeline/tests/fixtures/arquivos/` um CSV pequeno por conjunto (cabeçalho e 2 linhas reais, de `curl -s --range 0-4095 <url> | head -3`; 10 arquivos, cerca de 40 KB transferidos no total)

**Interfaces que esta tarefa consome:** as da Tarefa 1 e as da Tarefa 2.

**Interfaces que esta tarefa produz:**
- `FUSO = ZoneInfo("America/Sao_Paulo")`
- `class DataInvalida(Exception)`
- `@dataclass(frozen=True) class Resumo: novos: int; iguais: int; ausentes: int; nada_a_fazer: bool`
- `def coletar(data: date, raiz: Path, *, base: str = BASE_URL, agora: Callable[[], datetime] = lambda: datetime.now(FUSO), anos_frios: Sequence[int] = (), esperas: Sequence[float] = (2.0, 8.0, 30.0)) -> Resumo`
- `def main(argv: Sequence[str] | None = None) -> int`
  - Recebe `--data` (obrigatório) e `--raiz` (padrão `dados/raw`). A base vem de `os.environ.get("CAMARA_ARQUIVOS_URL", BASE_URL)`.
  - Imprime o resumo e devolve 0. Em `DataInvalida`, `FalhaDeColeta` ou `ValueError`, imprime `erro: <msg>` no stderr e devolve 1.
- **Disco:** `raiz/arquivos/<D>/`, com `manifesto.json`, `manifesto.parcial.json` e os `.csv.gz`. O manifesto tem `{"formato": 1, "data", "anos_quentes", "anos_frios", "arquivos": [entrada...]}`, com a entrada exatamente como na spec. `status` é `novo`, `igual` ou `ausente`. Na entrada ausente, `sha256`, `bytes`, `etag` e `last_modified` ficam `null` e `em` também é `null`. O JSON é gravado com `indent=2, ensure_ascii=False, sort_keys=True` e escrita atômica (`tmp` e depois `os.replace`).
- **Última coleta anterior de um arquivo:** percorra as pastas de data menores que `D`, da mais nova para a mais antiga, que tenham `manifesto.json`. Pegue a primeira entrada do mesmo `conjunto` e `ano` com `status != "ausente"` e use o `sha256` e o `em` dela.

- [ ] **Passo 1: Testes que falham.** Use a fixture `servidor` da Tarefa 2 servindo as fixtures, `tmp_path` como raiz e `agora` fixo em `datetime(2026, 11, 16, 9, 0, tzinfo=FUSO)`. Com a fixture de legislaturas, os anos quentes são de 2023 a 2026, e cada conjunto por ano é servido nos 4 anos.
  - `test_idempotente`: depois de `coletar` duas vezes, o retrato `{caminho: bytes}` da pasta da data é igual, e `len(pedidos)` não muda na segunda vez. A segunda devolve `nada_a_fazer=True`.
  - `test_mesmo_conteudo_no_dia_seguinte`: depois de coletar 16/11 e 17/11 (com o `agora` de 17/11) sem mudar nada, a pasta de 17/11 só tem `manifesto.json`, todas as entradas são `igual` com `em == "2026-11-16"`, e o `.gz` de 16/11 descomprimido bate com o `sha256` da entrada de 17/11.
  - `test_conteudo_diferente`: muda o corpo de `votacoes-2026` antes de 17/11. Essa entrada fica `novo` com `em == "2026-11-17"`, e o `.gz` existe na pasta de 17/11.
  - `test_data_passada_sem_raw`, com `data` em 15/11: levanta `DataInvalida`, a mensagem contém `"não guarda o passado"`, e `pedidos == []`.
  - `test_data_futura`, com `data` em 17/11: levanta `DataInvalida` com `"futura"`.
  - `test_data_passada_com_raw`: depois de coletar 16/11, chamar 16/11 com o `agora` em 18/11 dá `nada_a_fazer=True` sem nenhum pedido.
  - `test_ano_ausente`: remove `proposicoes-2026` do servidor. A entrada fica `ausente` e o resumo tem `ausentes == 1`.
  - `test_conjunto_sem_nenhum_ano`: remove `votacoes-2023` a `votacoes-2026`. Levanta `FalhaDeColeta`, e `manifesto.json` não existe.
  - `test_legislaturas_404`: levanta `FalhaDeColeta`.
  - `test_queda_e_retomada`: `votacoesVotos-2023` com `falhas_antes=99` levanta `FalhaDeColeta`. Depois disso não existe `manifesto.json` nem `*.parcial`. Volte a rota para `falhas_antes=0`, limpe `pedidos` e colete de novo: `legislaturas.csv` e `deputados.csv` não estão em `pedidos` e o `manifesto.json` existe.
  - `test_main_codigo_de_saida`: `main(["--data", "2026-11-15", "--raiz", str(tmp_path)])` devolve 1. Como `main` usa o relógio real, use uma data claramente no passado.

- [ ] **Passo 2: Ver falhar.** Rode `uv run --locked pytest pipeline/tests/test_coleta_arquivos.py -v`. Esperado: FAIL na importação.

- [ ] **Passo 3: Implementar `coletar`** na ordem do fluxo da spec ("Fluxo para uma data D", passos 1 a 5). A regra de "conjunto sem nenhum ano" vale para os anos quentes mais os frios, e é conferida ao terminar cada conjunto.

- [ ] **Passo 4: Ver passar.** Esperado: PASS. Mutações:
  - gravar o `.gz` mesmo quando o hash é igual faz `test_mesmo_conteudo_no_dia_seguinte` falhar;
  - escrever o `manifesto.json` antes do fim faz `test_queda_e_retomada` falhar.

  Confira cada uma e desfaça.

- [ ] **Passo 5: Commit.** `feat(coleta): passo idempotente dos arquivos em lote para raw, com manifesto e retomada`

### Tarefa 4: `pipeline/passos.py`, `make atualizar` e os docs

**Arquivos:**
- Criar: `pipeline/passos.py`, `pipeline/tests/test_passos.py`
- Modificar: `Makefile`, `pipeline/README.md`, `CLAUDE.md` (linha do `make atualizar`), `docs/dados/atualizacao.md`, `docs/dados/modelo.md`, `docs/metodo.md` (as linhas que dizem parquet para os arquivos em lote, e a 332)

**Interfaces que esta tarefa produz:**
- `@dataclass(frozen=True) class Passo: nome: str; modulo: str; depende_de: tuple[str, ...] = ()`
- `PASSOS: tuple[Passo, ...] = (Passo("coleta_arquivos", "pipeline.coleta.arquivos"),)`
- `def ordem(passos: Sequence[Passo] = PASSOS) -> list[Passo]`: ordem topológica e estável (o empate segue a ordem da lista). Levanta `ValueError` com `"ciclo"` ou com `"não existe: <nome>"`.
- `def rodar(data: date, passos: Sequence[Passo] = PASSOS, *, cwd: Path | None = None) -> int`: roda `subprocess.run([sys.executable, "-m", p.modulo, "--data", data.isoformat()], cwd=cwd)` em sequência e para no primeiro que sair com código diferente de 0, imprimindo `passo <nome> falhou (<código>)`.
- `def main(argv: Sequence[str] | None = None) -> int`, com `--data` obrigatório.
- No `Makefile`: `atualizar: uv run --locked python -m pipeline.passos --data $(or $(DATA),$(shell TZ=America/Sao_Paulo date +%F))`, com o comentário de uma linha e o alvo no `.PHONY`.

- [ ] **Passo 1: Testes que falham.**
  - `test_lista_real_valida`: `ordem()` não levanta erro, e cada `importlib.import_module(p.modulo)` tem `main`.
  - `test_ordem_respeita_dependencia`: com `[C(dep B), A, B(dep A)]`, a ordem é `A, B, C`.
  - `test_ordem_estavel`: com `[X, Y]` sem dependência, a ordem fica `X, Y`.
  - `test_ciclo`: levanta `ValueError` com "ciclo".
  - `test_dependencia_inexistente`: levanta `ValueError` com "não existe".
  - `test_rodar_para_no_primeiro_que_falha`: crie em `tmp_path` os módulos `ok.py` (cria `marca_ok`), `falha.py` (`sys.exit(3)`) e `depois.py` (cria `marca_depois`), e rode com `cwd=tmp_path`. Devolve 3, `marca_ok` existe e `marca_depois` não existe. O `cwd` como pasta de importação já cobre o ponto 5 da revisão.

- [ ] **Passo 2: Ver falhar.** Rode `uv run --locked pytest pipeline/tests/test_passos.py -v`. Esperado: FAIL na importação.

- [ ] **Passo 3: Implementar** `passos.py` (com o algoritmo de Kahn, que escolhe a cada rodada o primeiro pronto na ordem da lista) e o alvo `atualizar`.

- [ ] **Passo 4: Ver passar.** Esperado: PASS. Mutação: ignorar o código de saída no `rodar` faz `test_rodar_para_no_primeiro_que_falha` falhar. Confira e desfaça.

- [ ] **Passo 5: Atualizar os docs.**
  - Em `atualizacao.md`, `modelo.md` e `metodo.md`: os arquivos em lote ficam em "CSV original comprimido (gzip)", e a API continua em JSON.
  - Em `metodo.md:332`: `dados/` está no `.gitignore`, que agora é verdade.
  - No `pipeline/README.md`: `coleta/` e `passos.py` existem, e a frase "Vazia até o marco" sai.
  - No `CLAUDE.md`: `make atualizar` perde "(nasce com o marco dados.core)".

  Confira com `grep -n -i parquet docs/dados/*.md docs/metodo.md`: o que sobrar não pode falar de arquivo em lote.

- [ ] **Passo 6: `make ci` inteiro.** Esperado: verde.

- [ ] **Passo 7: Commit.** `feat(pipeline): passos.py e make atualizar; raw em CSV com gzip nos docs`

### Tarefa 5: rota, conferência e PR

- [ ] **Passo 1: Perguntar ao Eduardo qual frente fica ativa** (a sugestão é `infra`). Depois, em `docs/frentes.yaml`:
  - marco `dados.raw` com `status: feito`, antes de `core`;
  - `dados.core` com `depende_de: [dados.raw, infra.adrs]`;
  - `proximo_passo` de `dados` passa a ser "escrever o primeiro passo do core (legislatura e deputado) depois do ADR do banco";
  - `ativa` vai para a frente escolhida.

  Rode `make rota-check`. Esperado: sem erro.

- [ ] **Passo 2: `/conferir`.** O PR mexe em `pipeline/` e em `docs/dados/`. As afirmações da spec sobre a fonte (URLs, 404, BOM, anos) vão para o registro com comando e saída.

- [ ] **Passo 3: Teste ao vivo, só com o ok do Eduardo.** `make atualizar` baixa algumas centenas de MB da Câmara, sem custo em dinheiro. Ele mede o tamanho real do `raw` do dia (sem e com gzip), e o número entra em `atualizacao.md`.

- [ ] **Passo 4:** Criar a issue, renomear a branch para `feat/<n>-passos-coleta`, fazer push e `gh pr create`, que fecha a issue. O corpo do PR justifica que não há dependência nova e diz o que testar.
