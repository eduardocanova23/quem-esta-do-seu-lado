# 0006: busca híbrida com o BGE-M3 em int8 dentro da API, no servidor

Status: aceito, 2026-11-19. Issue #52. Proposto pelo Claude a partir do spike da issue e aceito pelo Eduardo ("aceito").

## Contexto

Esta é a última decisão da lista do método antes do `infra.deploy`. A busca é a única parte do site que roda na hora do acesso ([ADR 0002](0002-forma-de-entrega-do-site.md)): a API em FastAPI recebe o texto digitado e consulta o Postgres ([ADR 0004](0004-banco-de-dados.md)), no mesmo servidor que serve o site ([ADR 0005](0005-hospedagem.md)). A caixa da página inicial acha deputado, partido, tema e proposição desde a primeira publicação (`site.busca`).

O ponto de partida é o teste de busca da v1 (03/11/2026): 150 consultas de personas escritas à parte da taxonomia, julgadas às cegas por um modelo no papel da persona. A pessoa "acharia" o que queria em 80,7% das consultas com a busca híbrida (BM25 mais embedding do BGE-M3), 76,7% só com embedding e 70,7% só com BM25. Nas consultas coloquiais, a distância cresce: 89%, 80% e 66%. Ver `CAPIVARA/definitivo/dag_temas/eval/busca_modos.md`.

O que pesa contra manter o BGE-M3: o modelo em fp32 tem 2,27 GB, e o servidor CX23 tem 3.815 MB de RAM e 2 núcleos, **sem swap** (conferido por SSH em 18/11/2026). O método previa que ele não caberia ao lado do Postgres e do Airflow.

O que a v1 faz por baixo, e a v2 herda:

- **Dois vetores por proposição**, os dois tirados da ficha que o LLM escreve: um de `objeto | público` e outro dos termos de busca. Vale o maior dos dois cossenos. Os 333 temas têm vetor próprio (nome, apelidos e definição). São ~46 mil vetores na 57ª legislatura, não 26,5 mil.
- **A v1 já guardava os vetores em fp16**: o 80,7% foi medido com vetor de meia precisão.
- **Pesos:** proposições = embedding + 0,20 × BM25 normalizado; temas = embedding + 0,10 × BM25 + 0,05 × soma das proposições do tema. Mais a rota direta para "PL 2630" e "Lei 13.103".

## O spike

Pasta `camara-lab/spike_busca/` (branch `spike/52-busca`), com os números completos no README de lá. Pergunta: o BGE-M3 quantizado mantém o acerto da híbrida e cabe no CX23?

1. O código da v1 rodou sem alteração, trocando só o modelo de embedding. **A referência reproduz o julgamento da v1:** as proposições da híbrida saíram iguais nas 311 listas julgadas. As diferenças restantes têm causa conhecida: três temas que saíram da taxonomia depois do julgamento e empates exatos de escore.
2. O modelo foi exportado para ONNX em fp32, fp16 e int8. **O ONNX fp32 dá o mesmo vetor da v1** (cosseno mínimo 0,9999999 em 4.000 textos), o que prova que a exportação está certa.
3. Cada precisão refez o acervo inteiro, os temas e as consultas com o próprio modelo, porque acervo e consulta saem sempre do mesmo modelo.
4. As medidas de RAM e tempo foram tomadas num processo só com o que a API carregaria (ONNX Runtime, tokenizador, numpy), preso a 2 núcleos. A máquina do spike tem 3,8 GB, como o CX23.
5. Um juiz às cegas, com o prompt e o modelo da v1, comparou as três listas nas 267 consultas em que alguma mudou. Custo: US$ 0,23.

| | fp32 | fp16 | **int8** |
| --- | --- | --- | --- |
| Arquivo do modelo | 2.162 MB | 1.082 MB | **543 MB** |
| RAM do processo, em repouso / pico (2 núcleos) | 1.550 / 1.596 MB | 2.016 / 2.038 MB | **694 / 726 MB** |
| Tempo por consulta, mediana / p95 (2 núcleos) | 90 / 349 ms | 81 / 175 ms | **23 / 30 ms** |
| Acervo inteiro (46 mil textos, 8 núcleos) | ~53 min pela taxa da amostra (14,5 textos/s) | 53 min | **19 min** |
| Proposições novas de um dia (22), com a carga do modelo | 14 s | 14 s | **3,5 s** |
| Listas da híbrida iguais às da referência (mesmo conjunto) | = referência | 99% | 54 a 59% |
| nDCG@5 contra a referência, nas 267 consultas que mudam | = | −0,000 | **−0,004 [−0,014; +0,006]** |
| "Acharia" contra a referência | = | −0,8 pp (independentes) | **+1,1 pp [−0,7; +3,0]** |

Os intervalos são de 95%, por bootstrap pareado por consulta. A linha do fp32 sai do ONNX fp32: medida nas três primeiras linhas e na amostra de 4.000 textos, e igual à referência por construção nas outras.

**Como ler o int8:** ele troca a ordem das listas (só 23 a 25% saem idênticas), mas troca proposições de qualidade parecida. A perda de nDCG fica entre zero e 0,014, e a híbrida ganhou do BM25 sozinho por 0,095. O juiz até preferiu as listas do int8 (+11 pp), um resultado que não sei explicar e que não pesa na decisão.

**Como ler o fp16:** na CPU ele não serve. Fica igual à referência, mas usa mais RAM que o fp32 e não ganha velocidade. Processadores comuns não fazem conta em fp16, então o ONNX Runtime converte para fp32 (não conferido no código dele). Por isso o fp16 não entrou nas opções.

## Opções

| | A. BGE-M3 int8 na API | B. BGE-M3 fp32 na API | C. Embedding por API de terceiro | D. Só busca textual |
| --- | --- | --- | --- | --- |
| Acerto no conjunto de teste | o da v1 (spike) | o da v1 | não medido: outro modelo pede refazer acervo e juiz | 70,7% contra 80,7% na v1; 66% contra 89% nas coloquiais |
| RAM na API | ~0,7 GB | ~1,6 GB | quase nada | quase nada |
| Tempo por consulta | 23 ms | 90 ms (p95 349 ms) | uma ida e volta a outro serviço (não medido) | o do Postgres |
| Texto da busca | fica no servidor | fica no servidor | vai a um terceiro a cada busca | fica no servidor |
| Custo por mês | zero | zero | por uso: robô na busca vira conta | zero |

## Critérios, com peso

Nota de 1 (atende mal) a 3 (atende bem). As notas são julgamento meu sobre a tabela e o spike.

| Critério | Peso | A | B | C | D |
| --- | --- | --- | --- | --- | --- |
| 1. Acerto no conjunto de teste da busca | 3 | 3 | 3 | 1: sem número; o marco `site.busca` exige limiar | 1 |
| 2. Cabe no CX23 com folga para o Postgres e o job da madrugada | 3 | 3 | 2: cabe, mas sobra ~1,4 GB, sem swap | 3 | 3 |
| 3. Tempo de resposta em 2 núcleos | 2 | 3 | 1: p95 de 349 ms e máximo de 1,4 s | 2 | 3 |
| 4. O texto da busca não vai a outro serviço | 3 | 3 | 3 | 1 | 3 |
| 5. Custo fixo, sem conta por uso | 2 | 3 | 3 | 2 | 3 |
| 6. A busca não depende de terceiro na hora do acesso | 2 | 3 | 3 | 1: se o serviço cai, a busca cai | 3 |
| 7. Poucas peças | 1 | 2: modelo na API e passo novo na coleta | 2 | 2: chave, limite e plano B | 3 |
| **Total (máximo 48)** | | **47** | **40** | **27** | **42** |

## Decisão

**A. A busca da v2 é a híbrida da v1, com o BGE-M3 exportado para ONNX e quantizado em int8, carregado dentro da API de busca no servidor.**

1. **Por que não a D, que ficou em segundo:** a D ganha em simplicidade e perde onde o produto mais precisa. Nas consultas coloquiais do teste da v1 ("diarista direitos CLT", "jornada doméstica 44 horas"), que são a linguagem de quem não acompanha a Câmara, o BM25 sozinho acha 66% contra 89% da híbrida.
2. **Por que não a B:** o fp32 acerta igual, mas usa o dobro da RAM e é quatro vezes mais lento. Num servidor sem swap, 1,6 GB num processo só deixa pouca margem para o Postgres e para o job da madrugada, que carrega outro modelo.
3. **Por que não a C:** cada busca mandaria o texto digitado para mais um serviço, cobraria por uso (um robô vira conta) e derrubaria a busca junto com o serviço. Também exigiria refazer o acervo e o juiz com outro modelo, sem garantia de acerto.
4. **O que fica igual à v1:** os dois vetores por proposição, o vetor dos temas, os pesos (0,20; 0,10; 0,05), a rota direta por número e o corte em 128 tokens. Os vetores ficam em `halfvec(1024)` no pgvector (fp16, como na v1): ~91 MB na 57ª.
5. **O que muda:** o modelo sai do sentence-transformers e vai para o ONNX Runtime, sem PyTorch na API. O arquivo int8 (543 MB) é gerado por um script versionado a partir do BGE-M3 oficial e identificado pelo sha256. Trocar de modelo ou de precisão refaz o acervo inteiro.

### O que acontece por baixo

**A quantização.** Cada matriz de peso das 24 camadas vira inteiros de 8 bits, com uma escala por coluna (`per_channel`). A escala das ativações é calculada na hora, a cada entrada (quantização "dinâmica"), então não precisa de conjunto de calibração. O arquivo cai para um quarto, e a CPU faz as multiplicações em int8, que é onde estão os 23 ms. O preço é um vetor um pouco diferente: cosseno médio de 0,986 contra o fp32, com 0,944 no pior texto. Como acervo e consulta saem do mesmo modelo, o erro afeta os dois lados de forma parecida, e a ordem das listas muda pouco.

**A consulta.** A API tokeniza o texto e roda o modelo uma vez (23 ms). O resultado é o vetor do token inicial, normalizado. Depois ela pede ao Postgres o cosseno contra os ~46 mil vetores e soma o BM25 com os pesos. O desempate é sempre por `prop_id`: no spike, fichas de texto igual empataram exatamente, e cada sistema desempatava de um jeito.

**A madrugada.** Um passo novo em `pipeline/passos.py` calcula só os vetores que faltam: proposição nova, ou ficha com texto alterado (pelo hash do texto, como o método manda para a camada `ia`). Ele depende do passo que escreve a ficha. Num dia típico são 22 proposições, ~3,5 s com a carga do modelo; no pico de 2025, 615 proposições em um dia, ~30 s em 8 núcleos pela taxa medida (40 textos/s), e não medido em 2 núcleos.

**A conta de RAM no CX23**, com a v1 desligada:

| Peça | RAM | Fonte |
| --- | --- | --- |
| Sistema e serviços de base | ~0,3 GB | `ps` no servidor em 18/11: tudo menos a v1 soma 293 MB de RSS |
| API de busca com o modelo int8 | ~0,73 GB de pico | spike, 2 núcleos |
| FastAPI, BM25 e o resto da API | ~0,15 GB | estimado, não medido |
| Postgres | ~0,5 GB | estimado, não medido |
| Nginx | dezenas de MB | estimado |
| **Sobra** | **~2,1 GB** | 3.815 MB menos o resto |

O job da madrugada carrega outro modelo por alguns segundos (~0,7 a 1,6 GB de pico) e cabe nessa sobra.

## Consequências

- **O marco `site.busca`** constrói a API: carregar o modelo, a rota direta, os pesos e o desempate por `prop_id`. O critério de aceite é o conjunto de teste da v1. A primeira entrega reproduz as listas da referência int8 do spike; depois, o juiz confirma o acerto acima do limiar.
- **O BM25 da v1** é Python em memória sobre ~23 mil documentos. Implementar dentro do Postgres (o `ts_rank` não é BM25, porque não usa estatística do acervo; o índice do ParadeDB, `USING bm25`, é) ou manter na API se decide no `site.busca`, pelo mesmo teste. Este ADR fixa a fórmula, não o lugar.
- **pgvector com `halfvec`** e varredura exata no início: 46 mil vetores são poucos. O numpy varreu tudo em ~12 ms em 2 núcleos; no Postgres, não medido. Índice (HNSW) só se a medida pedir.
- **A busca depende da ficha**, que vem de LLM: proposição sem ficha não tem vetor. A rota já prevê isso (`site.busca` espera `taxonomia.incremental`).
- **Dependências novas na API:** `onnxruntime` e `tokenizers`. Elas entram com justificativa no PR do `site.busca`. O PyTorch fica fora do servidor; a exportação roda uma vez, fora dele.
- **Swap no servidor:** o CX23 está sem swap, e um pico de memória acionaria o OOM killer. Um arquivo de swap de 2 GB entra no `infra.deploy`.
- **O Airflow (`escala.airflow`) continua não cabendo** (4 GB no mínimo, segundo o método). Esta decisão não muda isso, e o servidor maior entra lá.

## Quando revisitar

- Se o conjunto de teste da busca, rodado a cada mudança de taxonomia ou de ficha, cair abaixo do limiar do `site.busca`.
- Se a API de busca passar de 1,2 GB de RAM ou de 200 ms de p95 no servidor.
- Se aparecer modelo de embedding multilíngue menor que, no mesmo conjunto de teste, empate com o BGE-M3: refazer este spike com ele.
- Se o Cloudflare ou a carga mostrarem robôs na busca: limite por IP antes de tudo, e só depois mudar de modelo.
