# Câmara v2 — método de construção

Nov 5, 2026 · @Edu

## O método em uma página

Você é o arquiteto e o revisor; o Claude Code digita. Nada entra no `main` sem que você consiga explicar o que mudou, por quê e com o que aquilo conversa.

**Oito regras**

1. **Documento antes de código.** Requisito, decisão de arquitetura e modelo de dados viram texto no repositório antes de virar código. O Claude lê esses textos no começo de cada sessão; você lê o código contra eles.
2. **Uma fatia por vez, completa.** Cada pergunta vai ao ar de ponta a ponta (dado → consulta → página → metodologia → texto de lançamento) antes de abrir a próxima. Várias frentes de produto abertas ao mesmo tempo foi o que virou colcha de retalhos.
3. **Simples não é improvisado.** A primeira fatia já nasce no framework definitivo e com a direção de design escolhida. Fica para depois só o que faz falta com o site crescendo: Airflow, teste de carga, testes visuais.
4. **Atualização é requisito desde o dia 1.** Toda tabela e todo derivado (ficha, tema, eixo, agregado) nasce com a resposta escrita para "como isso se atualiza amanhã?". A coleta é feita de comandos que o Airflow vai chamar depois, sem reescrever nada.
5. **O que não pode falhar vira trava automática.** O `CLAUDE.md` é conselho. Commit no `main`, segredo no repositório, teste quebrado e número errado publicado são barrados por hook, permissão, CI ou proteção de branch.
6. **Tudo no site serve a pelo menos uma das três perguntas.** O que não serve a nenhuma, sai. Uma página não precisa responder sozinha a uma pergunta; o site como um todo responde às três.
7. **Entendimento onde ele conta.** O código que gera um número publicado e as decisões de arquitetura você entende inteiros e defende em público, com metodologia assinada. Do resto (configuração, estilo, estrutura), basta saber o que cada parte faz.
8. **Construa para o tamanho que já se sabe que vem.** Decisão de fundação se toma pelo que já sabemos que o projeto vai precisar (está neste método, num ADR ou na rota), não pelo tamanho dele hoje. "Dá menos trabalho agora" não é argumento. O teste: se é só "talvez um dia", não faz; se deixar para depois obriga a refazer ou migrar, faz direito agora; se dá para acrescentar depois sem retrabalho, pode esperar. É por esse teste que o Airflow espera a Fase 5 e a coleta já nasce em `pipeline/passos.py`.

**O ciclo de cada tarefa**

1. **Issue.** A tarefa existe no GitHub, ligada a uma história de usuário com critérios de aceitação.
2. **Plano.** Em plan mode, o Claude lê os docs e propõe arquivos, alternativas, riscos e testes. Você pergunta até entender, depois aprova ou recusa.
3. **Testes primeiro no que gera ou mostra número.** Numa branch, o Claude escreve testes que falham traduzindo os critérios; depois, o código mínimo que os faz passar.
4. **Verificação.** Testes e lint rodam; se é tela, o Claude abre o build e confere o que renderizou.
5. **Walkthrough.** O PR traz o que mudou, por quê e por qual arquivo começar a ler.
6. **Teach-back, quando a mudança gera número publicado ou mexe na arquitetura.** O Claude te faz três perguntas e você responde sem olhar. Errou, estuda aquele ponto antes do merge.
7. **Merge.** CI verde, squash, docs, metodologia e ADR atualizados no mesmo PR, issue fechada e próximo passo da frente escrito no frentes.yaml.

Em configuração, estilo e estrutura, os passos 1, 2, 5 e 7 bastam. Se você usar o plugin Superpowers, ele conduz os passos 2 a 4 e o 7; o 5 e o 6 ficam com a skill /explicar (seção Claude Code).

## O que deu errado no Capivara

O Capivara não falhou por falta de capacidade técnica: faltou um processo que impedisse decisões implícitas. Cada problema abaixo vira uma regra deste método.

| Problema | Por que aconteceu | Regra que evita |
| --- | --- | --- |
| Colcha de retalhos: painel, roda temática, nuvens de palavras e de adjetivos, resumo por IA, clipping e remuneração no mesmo site | Uma feature entrava porque era possível, não porque respondia a uma pergunta | As três perguntas do vault como base e rastreabilidade: toda tela aponta para uma delas; o resto vai para os não-objetivos |
| Laboratório misturado com produto (notebooks, `exploracoes/`, `testar_*`) | Experimento e código de produção no mesmo repositório | Laboratório em repositório separado; o produto só recebe o que chega por PR, com teste. É a regra da pasta `definitivo/` aplicada ao repositório inteiro |
| Banco defasado em silêncio: deputados meses sem atualizar, discursos novos nunca coletados | Orquestração à mão e checkpoint que guardava "quem", não "até quando". Havia uma regra no CLAUDE.md para registrar cada script nos orquestradores, e etapas ficaram de fora mesmo assim | Pipeline incremental e idempotente, dependências declaradas num lugar só (que o Airflow lê depois) e um teste que falha se o dado tem mais de 2 dias |
| O mesmo erro cinco vezes: o proxy do Vite engolia rotas novas, mesmo depois de anotado | Lembrar não funciona | Checagem que importa vira script, hook ou teste: auditoria mecânica no fim, não memória no meio |
| Lacunas de compreensão | Código aceito sem revisão funda, sessões longas misturando assuntos | Walkthrough em todo PR, teach-back no código que gera número publicado e mapa do sistema atualizado quando a arquitetura muda |
| Framework virou teto de design: Streamlit, depois FastAPI + Jinja2 + Plotly; a área de membros em React nunca foi ao ar | Escolha por conveniência, sem critérios escritos nem protótipo, e deploy deixado para depois | ADR com critérios, spike descartável e a primeira fatia no ar cedo, já no framework definitivo |
| Cara de dashboard | O ponto de partida era "mostrar os dados", não "responder à pergunta" | Design content-first: a frase-resposta vem antes do gráfico; checklist de tela |
| Atalhos conscientes | Mesmo sabendo que o projeto cresceria, decisões ruins foram tomadas "porque daria menos trabalho" | Regra 8: decisão de fundação se toma pelo tamanho que já se sabe que vem |
| Dúvida se aguenta muitos usuários | Nunca foi medido nem projetado para isso | Páginas geradas depois do pipeline e servidas por CDN; teste de carga antes do lançamento |

**O que funcionou e fica.** O padrão de coleta da v1 (CSV anual mais enriquecimento por id, rede em paralelo e gravação em série, upsert por chave natural, retry em 504), a lógica de delta do `6_atualizar.py`, o trio `plano.md` / `progresso.md` / `decisoes.md` do `dag_temas`, o teto de gasto, os gabaritos com segundo passe cego, os conjuntos de teste congelados e as 58 personas (38 originais e dois conjuntos independentes de 10). As notas do vault em `Conhecimento/`, `Domínio/` e `Decisões/` são a documentação de partida; os arquivos da v1 entram como referência, não como código copiado.

## Fases e portões

O projeto anda em seis fases, e cada uma só começa quando o critério da anterior está cumprido. Depois do Produto, dados, design e infraestrutura correm lado a lado e se encontram na primeira fatia, que vai ao ar completa. Airflow, busca e teste de carga ficam para a Fase 5, quando o site já existe e precisa crescer.

&#91;embedded content: fases e portões do projeto\]

Dados e Design andam juntos porque usam modos diferentes: o pipeline se faz no Claude Code, o design em conversa e protótipo aqui no app. Não há datas, o ritmo é o seu; o único marco externo é a troca de legislatura em 1/2/2027. As fatias seguem a nota das três perguntas: primeiro a 2 (o deputado está do meu lado), que usa só dados que já existem; a 1 depende de coletar a tramitação.

**O que cada fatia publica.** As páginas de consulta, para a pessoa tirar a própria conclusão; uma página de metodologia assinada por você, com cada métrica, a fonte, as escolhas e os limites; e um texto de lançamento com um achado que a ferramenta revela. O que a pessoa conclui depende de como você mediu, e a metodologia publicada é o que mostra que essas escolhas são suas.

**Simples, mas no lugar certo.** A fatia 1 pode ser inteiramente estática: páginas geradas no build a partir dos marts, com filtros que rodam no navegador. Ela já usa o framework do ADR e os tokens da direção de design escolhida, então nada dela é jogado fora depois. A API de busca chega com o marco de busca, depois da fatia 1.

## Frentes e rota: o processo que se desenrola

A rota mora num arquivo, `docs/frentes.yaml`, que um script lê no começo de cada sessão. O Claude e você sempre começam sabendo onde trabalhar, e o arquivo muda junto com o trabalho, no mesmo PR. O diagrama de fases acima é a foto inicial desse arquivo; daqui em diante, quem manda é o `frentes.yaml`.

| Peça | O que é | Exemplo |
| --- | --- | --- |
| Frente | Linha de trabalho com objetivo próprio | `dados`: pipeline diário, incremental e idempotente |
| Marco | Resultado verificável dentro da frente, com critério de pronto; o primeiro não feito é o atual | `dados.core`: ingestão diária com o teste incremental = completo passando |
| Dependência | Marco que precisa estar feito antes de outro começar | `site.pergunta1` depende de `dados.tramitacao` |
| Contrato | Marco que fixa uma interface cedo, para outra frente andar sem esperar a implementação | `dados.contrato_marts`: schema dos marts mais uma amostra de dados, e as páginas da fatia 1 já podem começar |
| Próximo passo | A ação concreta seguinte da frente, que dá para começar sem pensar | "escrever docs/dados/atualizacao.md para as tabelas da pergunta 2" |
| Ativa | A única frente de código em andamento; as outras ficam pausadas, com o próximo passo escrito | — |

**Como uma sessão corre**

1. **A sessão abre.** O hook `SessionStart` roda `make rota`, e a saída entra no contexto do Claude: a frente ativa e o próximo passo dela, as frentes livres ordenadas pelo quanto destravam e as bloqueadas, com o que falta para cada uma. Roda também depois de `/clear` e da compactação.
2. **Você decide.** Por padrão, segue o próximo passo da frente ativa. Trocar de frente só vale para uma livre, e a que sai fica pausada com o próximo passo escrito.
3. **A tarefa roda** pelo ciclo da primeira seção: issue, plano, testes, código, walkthrough e, quando a mudança gera número publicado, teach-back.
4. **O PR fecha o laço.** No mesmo PR, o Claude propõe o novo próximo passo, ou marca o marco como feito e escreve a primeira ação do marco seguinte. Você aprova junto com o código.
5. **O CI confere.** `rota.py --check` falha se houver marco aberto sem próximo passo, dependência que não existe, ciclo, mais de uma frente ativa, frente ativa bloqueada ou marco em andamento com dependência por fazer.

Saída real do script com a rota revisada, no meio da Fase 1:

```text
ROTA (docs/frentes.yaml)

Ativa: produto, marco produto.perguntas
  próximo passo: conferir docs/produto/ contra a ordem das fatias e seguir de onde parou

Livres, da que destrava mais para a que destrava menos:
  infra.adrs (destrava 10) | próximo passo: escrever o ADR da forma de entrega do site

Bloqueadas:
  dados.modelo espera produto.perguntas
  taxonomia.incremental espera dados.core
  design.referencias espera produto.perguntas
  site.fatia1 espera infra.deploy, dados.contrato_marts, dados.core, design.tokens
  analise.metodologia1 espera produto.metricas, dados.contrato_marts
  escala.airflow espera analise.lancamento1

Concluídas: fundacao
```

**O que continua com você.** O processo se desenrola sozinho, mas três coisas são suas:

- **Qual frente livre pegar.** O script ordena pelo caminho crítico (quantos marcos cada uma destrava); a prioridade da pergunta, a incerteza e o seu cansaço desempatam.
- **Replanejar.** Marco novo, dependência que mudou ou frente que surgiu entram num PR só disso.
- **A qualidade do próximo passo.** "Melhorar o pipeline" não passa; "escrever o teste de idempotência das votações" passa.

O `frentes.yaml` guarda para onde ir. O `docs/estado.md` vira só a anotação de passagem quando uma tarefa para no meio, e o que já foi feito fica no histórico de PRs. O arquivo revisado e o script estão nos anexos D e E.

## Requisitos: da pergunta à tela

O MVP é o menor conjunto de telas que responde bem às quatro perguntas centrais. Tudo sai de um banco de perguntas escrito antes de qualquer tela, e cada elo da cadeia aponta para o anterior: pergunta → história → critério de aceitação → teste → tela.

**1. Perfis de uso.** As 58 personas e as lentes do `dag_temas` continuam como critério de classificação, que é diretriz inegociável do vault. Para o app, bastam quatro ou cinco perfis definidos por como a pessoa chega e do que precisa:

| Perfil | Como chega | Quer saber | Precisa de |
| --- | --- | --- | --- |
| Eleitor curioso | Google ou link no WhatsApp, pelo celular | O que o deputado X fez e defende | Resposta em uma frase, sem jargão, fácil de compartilhar |
| Quem acompanha uma causa | Busca por tema ("saidinha", "agrotóxico") | O que tramita sobre aquilo e quem é a favor ou contra | Busca boa, proposições do tema, placar por eixo |
| Jornalista ou pesquisador | Volta sempre, busca direta | Números confiáveis e comparáveis | Metodologia, data de atualização, o n de cada número, exportação |
| Estudante ou professor | Link de aula ou de trabalho | Como a Câmara funciona | Glossário embutido, o processo explicado |

**2. Banco de perguntas.** A base já existe na nota "As três perguntas que o produto responde", e as quatro perguntas desta conversa cabem nela:

1. **Quais assuntos a Câmara prioriza e quais abandona?** Inclui "o que a Câmara fez" e "quais temas demoram".
2. **Este deputado está do meu lado?** Inclui "o que o deputado X faz e defende".
3. **Quem é o mais aliado e o mais inimigo?** Inclui "e o partido", vista por bancada.

Pergunta nova entra no arquivo com o perfil que a faz, a prioridade e o dado que a responde.

**3. Histórias com critérios testáveis.** Cada pergunta prioritária vira uma ou mais histórias, e cada critério vira um teste end-to-end. Exemplo:

> *Como eleitor que acompanha um deputado, quero saber se ele vota na minha direção num eixo que me importa.*
>
> - Dado um eixo com votos suficientes, a página diz "votou na sua direção em 7 de 9 votações" e lista as votações ao lado.
> - Abaixo do n mínimo, mostra só as votações, sem percentual.
> - Destaca as votações em que ele divergiu da bancada.
> - Ausências e obstruções aparecem à parte, fora do placar.
> - A direção escolhida pelo usuário não é gravada em lugar nenhum.

**4. MVP e não-objetivos.** O MVP começa pela pergunta 2 nos cinco eixos com volume de votos (gasto e benefício, carga tributária, punição, ambiente, trabalho), como a nota recomenda. Ela usa só dados que já existem, e o protótipo em Streamlit (`app_deputado.py`) serve de especificação de comportamento. Candidatos a ficar fora do MVP, numa lista que o Claude lê em toda sessão: nuvens de palavras e de adjetivos, resumo por IA, login e camada paga, Senado e o clipping do DO, que já virou projeto próprio.

**5. Dicionário de métricas.** Todo número exibido tem nome, definição em uma frase, fórmula, denominador, tabelas de origem e ressalvas, e a tela mostra essa definição em "como calculamos". É o que separa o app dos painéis confusos. Dois casos difíceis já foram analisados no vault:

- **Quais temas andam e quais param.** A média de tempo engana: as paradas não têm tempo final, e ela subestima justamente os temas abandonados. Use volume por tema, taxa de avanço (parecer aprovado, urgência, votação, sanção) e a curva de Kaplan–Meier por tema, com as paradas como censuradas. "Abandonado" é relativo a uma taxa base baixíssima: 1.148 de 26.512 proposições (≈4%) foram deliberadas no Plenário.
- **Ranking de aliados.** Deputado com 2 votos, ambos a favor, vira "100%" e sobe para o topo. O placar é encolhido para a média do partido quando há poucos votos, exige n mínimo e aparece como "partidos mais alinhados com você e, dentro de cada um, quem foge da linha".

**6. Requisitos não funcionais.** Cada um com número, para virar teste:

| Requisito | Meta inicial |
| --- | --- |
| Atualidade | Dados com no máximo 24 h; "atualizado em" visível em toda página |
| Desempenho | LCP abaixo de 2,5 s no celular em 4G |
| Acessibilidade | WCAG 2.2 AA |
| Legislaturas e governos | Toda métrica calculada dentro de uma legislatura e de um governo; deputado em duas legislaturas tem dois perfis (diretriz do vault) |
| Privacidade | Perfil do usuário opcional; o sentido político dele nunca é guardado (decisão do vault) |
| Neutralidade | Mesmo tratamento para todo partido; nenhuma nota de "bom" ou "ruim" |
| Transparência de IA | Todo rótulo gerado por modelo é marcado e explicado na página de metodologia |
| Custo | Teto mensal de infraestrutura e de LLM definido por você |

**7. Decisões que vêm do `dag_temas`.** A busca é a porta de entrada e a árvore é vitrine. A generalidade está na pergunta, não no tema: porta, lente, caso da mídia e consulta são todos conjuntos de temas.

**Onde fazer.** Esta fase é conversa, não código: faça aqui no app, onde estão os plugins Intent (estratégia, arquitetura de informação, texto de interface) e Engineering. O resultado vai para `docs/produto/` no repositório.

## Banco de dados e pipeline: a atualização vem primeiro

O banco é o produto, e ele é desenhado de trás para frente: para cada tabela, primeiro a regra de atualização, depois o schema, por último o código. A regra geral é incremental onde custa (API e LLM) e recálculo total onde é barato (agregados).

**As fontes e o ritmo delas**

- Os arquivos em lote da Câmara têm atualização diária. Proposições, autores, temas, votações, votos e orientações (só de Plenário) vêm por ano; deputados, órgãos, frentes e legislaturas, sem divisão por ano.
- O arquivo de proposições é organizado por ano de apresentação. Uma proposição de 2019 que andou ontem muda no arquivo de 2019, então o pipeline relê todos os anos do seu universo, não só o corrente.
- A API (`https://dadosabertos.camara.leg.br/api/v2`) dá o detalhe por id: temas, autores, votos, orientações, discursos. Tramitações (`/proposicoes/{id}/tramitacoes`) não têm arquivo em lote, a v1 nunca as coletou e a pergunta 1 depende delas. Compare o hash de cada linha do arquivo do dia com o de ontem e busque na API só as que mudaram.
- A mídia é a terceira fonte: o pipeline de `definitivo/midia_proposicoes/` (WordPress e Google News, regex de citação formal, Jev) passa a rodar numa janela diária e alimenta os casos da mídia.
- O padrão da nota "Coleta incremental de API com checkpoint" vale como está: rede em paralelo, gravação em série, upsert por chave natural, checkpoint que guarda "até quando" e não só "quem", retry em 504.

**Quatro camadas**

| Camada | Guarda | Como atualiza |
| --- | --- | --- |
| `raw` | Cópia exata do que veio (arquivo, resposta da API, matéria), com data de coleta, URL e hash, em JSON e parquet fora do Postgres, como a v1 já fazia | Só acrescenta. Permite reprocessar sem baixar de novo e saber o que a Câmara dizia em tal dia, sem gastar o espaço do banco |
| `core` | Entidades limpas com as chaves da Câmara: deputado, filiação, legislatura, proposição, autoria, tramitação, votação, voto, orientação, órgão | Upsert idempotente: rodar duas vezes dá o mesmo resultado |
| `ia` | Ficha, embedding, temas, eixo e sinal | Calcula só o que falta. Cada linha guarda versão da taxonomia, modelo, versão do prompt e hash do texto de entrada |
| `marts` | Tabelas prontas para as telas: placar por deputado e eixo, partido × tema, atividade por semana, curvas de sobrevivência | Recálculo total a cada execução, publicado de uma vez |

**A tabela de atualização.** Antes do primeiro `CREATE TABLE`, `docs/dados/atualizacao.md` tem uma linha por tabela: fonte, frequência, chave natural, estratégia, janela de reprocessamento e o que dispara. A janela existe porque a Câmara corrige dados antigos: uma vez por semana, releia um período maior.

**Armadilhas do domínio que o modelo tem de absorver**

- **Troca de partido.** "O que o partido fez" atribui cada ato ao partido da época. Filiação é uma tabela com início e fim, nunca uma coluna no deputado.
- **Legislaturas e governos separados.** A 57ª acaba em 31/1/2027 e a 58ª começa em 1/2/2027, daqui a menos de três meses. Legislatura é dimensão desde o dia 1, e a diretriz do vault proíbe comparar legislaturas ou governos: deputado em duas legislaturas tem dois perfis, e titular, suplente ou efetivado é condição de cada legislatura.
- **Arquivamento no fim da legislatura.** Desde a Resolução 33/2022, o art. 105 do Regimento poupa as proposições do art. 59 da Constituição que ainda não atravessaram três legislaturas completas, entre outras exceções. Uma leva de proposições antigas vai ser arquivada; o pipeline registra isso como evento, não como dado que sumiu.
- **Apensadas.** A votação de uma apensada fica registrada sob a principal. A v1 decidiu manter uma linha por proposição real, cada uma com seu status; o avanço de uma apensada se mede pela principal.
- **Pegadinhas da API** (nota do vault): discurso sem id estável (a chave é deputado mais data e hora de início), `codTema` que a v1 nunca guardou, votação secreta sem votos.

**A árvore de temas como algo que se atualiza.** A taxonomia muda devagar e com revisão humana; a classificação roda todo dia sozinha.

1. A taxonomia vive no git como arquivo legível (`taxonomia/temas.yaml`): id, nome, definição, pais, sinônimos, eixos. Mudar a taxonomia é um PR com diff legível, e o mesmo vale para o `apelidos_manuais.csv`; os apelidos automáticos vêm do pipeline de mídia, com a probabilidade guardada.
2. Ids nunca são renumerados nem reaproveitados. Renomear mantém o id, fundir deixa o id antigo apontando para o novo e dividir aposenta o antigo. Links e URLs não quebram.
3. Todo dia, proposições novas ou com texto alterado ganham ficha, embedding e temas na versão vigente, sem reestruturar nada. As de baixa confiança vão para a fila de "nenhum serve".
4. Tema novo nasce de sinais, como manda a diretriz do vault: a fila de "nenhum serve", buscas sem resultado (guardadas sem identificar quem buscou) e apelidos novos da mídia. Quando os sinais se acumulam, roda a jardinagem: agrupa, propõe temas e abre o PR da taxonomia.
5. Todo PR de taxonomia traz o placar das personas (✅/🟡/❌) antes e depois, medido no conjunto independente congelado. Tema que nenhuma persona usa não entra.
6. Taxonomia nova reclassifica só o afetado (temas fundidos ou divididos, mais a fila). Reclassificação total só em versão maior, comparando métricas com a anterior.
7. Os gabaritos ouro A e B viram teste de regressão: se a acurácia cair abaixo do limiar, a execução não publica.
8. O site nunca chama LLM na hora do acesso; tudo que vem de modelo é pré-calculado, com teto de gasto por execução.

**Airflow depois, sem retrabalho.** Até a Fase 5, a atualização roda à mão com `make atualizar`. Quatro regras fazem o Airflow entrar depois sem reescrever nada:

- **Cada passo é um comando Python com testes** (`python -m pipeline.ingestao --data 2026-11-05`), que recebe a data lógica e é idempotente: rodar de novo para o mesmo dia dá o mesmo estado. É o que o Airflow faz em cada tarefa, e é o que permite reprocessar o passado.
- **A lista de passos mora num arquivo só**, `pipeline/passos.py`: nome, comando e de quais passos cada um depende. O `make atualizar` roda essa lista na ordem. Na Fase 5, as DAGs leem a mesma lista e criam uma tarefa por passo. Passo novo nunca nasce fora dela.
- **Cada passo guarda até que data processou**, não quem processou. Foi o checkpoint por "quem" que deixou o banco da v1 defasado em silêncio.
- **Os passos já se agrupam como as DAGs da tabela abaixo**, então a fronteira entre elas não muda quando o Airflow chega.

Quando ele entrar, o trabalho é escrever DAGs finas, subir o Airflow no servidor e ligar os alertas. Os passos e os testes ficam como estão. As DAGs previstas:

| DAG | Quando | Faz |
| --- | --- | --- |
| `ingestao_diaria` | Toda madrugada | Arquivos do dia para `raw`, detecta o que mudou, busca tramitações, atualiza `core` |
| `midia_diaria` | Toda madrugada | Coleta a janela do dia nos veículos, extrai citações e apelidos, atualiza os casos da mídia |
| `enriquecimento` | Quando `core` atualiza | Calcula o que falta em `ia`. A parte paga fica em disparo manual até o custo medido te convencer; depois roda sozinha, com teto por execução e por mês |
| `publicacao` | Quando `ia` termina | Monta os marts num schema de rascunho, roda os testes de dados, troca pelo publicado de uma vez, manda o site regenerar as páginas |
| `manutencao_taxonomia` | Manual ou mensal | Junta os sinais, propõe temas e abre o PR da taxonomia |
| `backfill` | Manual | Carrega legislaturas passadas |

Conceitos de Airflow para estudar nesta ordem: DAG e task; agendamento e data lógica, que é o que permite reprocessar o passado; idempotência e retries; assets, para uma DAG disparar quando o dado de outra fica pronto; pools, para limitar chamadas à API da Câmara; conexões e variáveis para segredos.

A versão atual do Airflow é a 3.3.2. No Windows ele roda via WSL2 ou contêineres Linux, e o docker compose oficial pede pelo menos 4 GB de memória para o Docker (8 GB é o ideal) e avisa que não serve para produção. Na sua máquina (8 GB, muitas vezes com menos de 1 GB livre) e no CX23 de 4 GB da v1, isso não cabe junto com o resto, como a sua nota do Airflow já previa.

Por isso a lógica fica em Python comum: você desenvolve e testa os passos sem Airflow e sobe o Airflow só para estudar ou testar uma DAG. O pipeline de produção roda num servidor, nunca no seu PC, onde processo longo em segundo plano morre. Onde o Airflow roda (servidor com 8 GB ou mais, serviço gerenciado, ou Dagster e Prefect, que a nota lista como alternativas) é decisão de ADR.

**Postgres e as regras dele**

- Postgres com pgvector para os embeddings.
- Migrations versionadas desde o dia 1 (Alembic, já que o pipeline é Python). A v1 aprendeu que `create_all()` nunca adiciona coluna a tabela existente. Toda mudança de schema é um arquivo com ida e volta, revisado no PR pela skill `/migracao`.
- Três papéis: `pipeline` escreve, `app` só lê, `migrador` muda o schema. O site não consegue escrever nada.
- Backup diário e teste de restauração uma vez por mês, com runbook. Como `raw` guarda tudo, o banco inteiro pode ser reconstruído.
- TLS das chamadas à Câmara com `truststore`, nunca `verify=False`, como diz a nota de SSL no Windows.

Fontes: [arquivos de dados abertos da Câmara](https://dadosabertos.camara.leg.br/swagger/arquivos.html), [Resolução 33/2022](https://www2.camara.leg.br/legin/int/rescad/2022/resolucaodacamaradosdeputados-33-4-agosto-2022-793091-publicacaooriginal-165882-pl.html), [Airflow no Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html), [pré-requisitos do Airflow](https://airflow.apache.org/docs/apache-airflow/3.1.6/installation/prerequisites.html), [anúncios do Airflow](https://airflow.apache.org/announcements/).

## Arquitetura e stack: decisões por ADR

Toda escolha cara de reverter vira um ADR com alternativas, critérios e consequências, e as mais incertas passam antes por um spike descartável de um dia. Abaixo, a ordem das decisões e o ponto de partida que eu recomendo.

**Como decidir**

1. ADR em `docs/decisoes/NNNN-titulo.md`: contexto, opções, critérios com peso, decisão, consequências e quando revisitar. A skill `architecture` do plugin Engineering faz o rascunho; a decisão você reescreve com as suas palavras.
2. Spike: protótipo descartável numa branch `spike/...`, com prazo de um dia e uma pergunta só ("consigo fazer a página do deputado com X?"). O código vai fora; o aprendizado vai para o ADR.
3. Os ADRs saem nesta ordem, porque cada um restringe o seguinte: forma de entrega do site, framework, banco e hospedagem do site antes da fatia 1; busca e Airflow em produção na Fase 5; depois disso, autenticação e camada paga.

**A decisão que resolve a dúvida de carga.** Os dados mudam uma vez por dia, então quase todo o site pode ser gerado logo depois do pipeline e servido por CDN. Uma página pronta na CDN não consulta o banco no acesso, e um pico de visitas não derruba nada. Só a busca e os filtros que não dá para pré-gerar precisam de servidor.

&#91;embedded content: arquitetura · fluxo noturno e acesso\]

O diagrama mostra o sistema da Fase 5. Até lá, o mesmo fluxo roda com `make atualizar` no lugar do Airflow, e a API de busca ainda não existe: a fatia 1 é só página gerada e servida pela CDN.

A CDN entrega as páginas sem tocar no banco. Só a API de busca consulta o Postgres, com um papel que não consegue escrever. Isso encolhe a superfície de ataque; as lições de segurança da v1 (path traversal, XSS, JWT em cookie HttpOnly) voltam a valer quando vier a camada paga.

**Framework de frontend**

| Opção | Modelo mental | Componentes prontos | Risco |
| --- | --- | --- | --- |
| Astro com ilhas React | Página é um template renderizado no build; interatividade só onde você marca uma ilha | Usa componentes React, shadcn inclusive, dentro das ilhas | Ecossistema menor que o do Next; comprado pela Cloudflare em janeiro de 2026 |
| Next.js | Componentes de servidor e de cliente, várias camadas de cache | O maior: quase toda biblioteca de componentes nasce para React e Next | Superfície conceitual grande, e o modelo de cache mudou entre versões |
| React SPA com Vite, como a área de membros da v1 | Tudo roda no navegador; o servidor entrega uma casca vazia | Os mesmos do React, shadcn inclusive | Sem HTML por página, a prévia de link no WhatsApp e o Google dependem de pré-renderização; o proxy de dev da v1 engoliu rotas cinco vezes |
| FastAPI + Jinja2 + HTMX | HTML renderizado pelo servidor, que você já conhece | Nenhum componente React; tudo em CSS e JS próprios | Design polido custa mais; foi o caminho do Capivara, e a nota de visão já fixou React |

Minha recomendação é **Astro com ilhas React**, TypeScript, Tailwind e componentes shadcn onde houver interação, mais uma **API de busca em FastAPI**. É o menor modelo mental entre as opções com acesso ao ecossistema React, e o site vira uma função dos marts do dia, fácil de entender e de testar. O Next.js passa a valer mais se a camada paga virar um app com login e muito estado por usuário.

**As outras decisões e o que decide cada uma**

| ADR | Opções | Critério |
| --- | --- | --- |
| Banco | Postgres no seu servidor (Docker) ou gerenciado (Supabase, Neon) | Custo, backup pronto e espaço. Na v1, o Neon free de 512 MB ficou em 128 MB com Câmara e votos, e a sua nota já previa que a tramitação completa estouraria. Só os embeddings de 26,5 mil proposições em 1.024 dimensões somam \~110 MB, fora o índice |
| Busca | BGE-M3 no servidor, embedding por API (re-embedando o acervo) ou só busca textual do Postgres no MVP | O seu conjunto de teste de busca (a híbrida achava em 80,7%), mais latência e RAM medidas no spike. O BGE-M3 ocupa \~2,5 GB de RAM e não cabe num servidor de 4 GB junto com Postgres e Airflow |
| Airflow em produção | Mesmo servidor, servidor separado, serviço gerenciado, Dagster ou Prefect, ou as funções agendadas sem orquestrador até ele se pagar | RAM (4 GB no mínimo só para o Airflow), custo, o que você quer aprender |
| Site | Hospedagem estática com CDN ou Nginx no servidor atrás de uma CDN | Custo, termos de uso comercial, integração com o build |

**Um repositório só.** Uma mudança que atravessa banco, pipeline e site cabe num PR, e o Claude enxerga tudo:

```
camara/
├── CLAUDE.md
├── Makefile           make setup, make test, make ci, make rota, make atualizar
├── pyproject.toml     dependências Python e configuração das ferramentas (uv.lock ao lado)
├── docs/
│   ├── metodo.md      este doc
│   ├── frentes.yaml   a rota: frentes, marcos, dependências, próximos passos
│   ├── estado.md      passagem de sessão quando uma tarefa para no meio
│   ├── produto/       perguntas, personas, histórias, métricas, não-objetivos
│   ├── decisoes/      ADRs numerados
│   ├── dados/         modelo, dicionário, atualização, taxonomia
│   ├── design/        princípios, referências, tokens, componentes
│   ├── arquitetura/   mapa do sistema
│   └── runbooks/
├── pipeline/          Python: coleta, transformação, IA, qualidade, publicação, testes
├── dags/              DAGs do Airflow, finas
├── db/                migrations/ e marts/
├── taxonomia/         temas.yaml, apelidos_manuais.csv, changelog
├── avaliacao/         gabaritos e conjunto de personas congelado
├── api/               FastAPI da busca, testes
├── web/               site, testes, e2e/
├── scripts/           rota.py e utilitários reexecutáveis
├── infra/             docker compose, deploy
├── .claude/           settings.json, hooks/, skills/, agents/
└── .github/           workflows/, templates de PR e de issue
```

O trio do `dag_temas` continua: o plano vira o frentes.yaml e as issues, o progresso vira `docs/estado.md` e as decisões viram ADRs. O laboratório (notebooks, explorações) fica num repositório à parte; o produto só recebe o que chega por PR, com teste.

Fontes: [Cloudflare compra o Astro](https://www.businesswire.com/news/home/20260116386991/en/Cloudflare-Acquires-Astro-to-Accelerate-the-Future-of-High-Performance-Web-Development), [shadcn no Astro](https://v3.shadcn.com/docs/installation/astro), [pré-requisitos do Airflow](https://airflow.apache.org/docs/apache-airflow/3.1.6/installation/prerequisites.html).

## Organização do código e dos documentos

Cada tipo de arquivo tem um lugar só, e a direção das dependências é fixa: quem está mais perto do usuário depende de quem está mais perto do dado, nunca o contrário.

| Tipo | Onde mora | Regra |
| --- | --- | --- |
| Código do pipeline | `pipeline/`, um módulo por etapa: `coleta/`, `transformacao/`, `ia/`, `qualidade/`, `publicacao/` | Transformação em funções puras, entrada e saída nas bordas; cada etapa tem CLI própria |
| DAGs | `dags/` | Só chamam funções do `pipeline/`, sem lógica |
| Schema | `db/migrations/` | Uma migration por mudança, com volta |
| SQL dos marts | `db/marts/`, um arquivo por mart | O schema de cada mart é o contrato com o site, documentado em `docs/dados/` |
| API de busca | `api/` | Rotas finas, consultas num módulo próprio, entrada validada por Pydantic |
| Site | `web/src/pages/`, `web/src/components/`, `web/src/lib/` | Formatação de número e modelos de frase em `lib/`, testados; ilhas React só onde há interação |
| Taxonomia e apelidos | `taxonomia/` | YAML e CSV legíveis; mudam só por PR, com placar de personas |
| Testes | `pipeline/tests/`, `api/tests/`, `web/tests/` e `web/e2e/` | Ao lado do que testam; respostas reais e pequenas da Câmara como fixtures em `pipeline/tests/fixtures/` |
| Gabaritos e conjunto congelado | `avaliacao/` | Não se editam à mão depois de congelados; o SHA256 fica registrado |
| Notebooks e experimentos | Repositório do laboratório, fora do produto | O que vira produto entra por PR, reescrito como módulo com teste |
| Scripts avulsos | `scripts/` | Só se forem reexecutáveis e documentados, como o `rota.py` |
| Dados | Fora do git: `raw` no disco do servidor ou num storage | O `.gitignore` cobre `dados/`, `.env` e arquivos grandes; só fixtures pequenas entram |
| Segredos | `.env` local, secrets do GitHub Actions, variáveis de ambiente no servidor | `.env.example` versionado com os nomes, sem valores |
| Configuração do Claude | `.claude/` versionado; `.claude/settings.local.json` fora do git | Hooks, skills, agentes e permissões passam por PR como código |

**Documentos**

| Documento | Onde | Quando muda |
| --- | --- | --- |
| Método | `docs/metodo.md`, este doc exportado | Na retrospectiva, se uma regra mudar |
| Rota | `docs/frentes.yaml` | Em todo PR que fecha um passo |
| Passagem de sessão | `docs/estado.md` | Quando uma tarefa para no meio |
| Produto | `docs/produto/`: perguntas, personas, histórias, métricas, não-objetivos | Antes de qualquer tela nova |
| Decisões | `docs/decisoes/NNNN-titulo.md` (ADR) | A cada decisão cara de reverter; ADR antigo não se edita, é substituído por um novo |
| Dados | `docs/dados/`: modelo, dicionário, atualização, taxonomia | No mesmo PR da migration |
| Design | `docs/design/`: princípios, referências, tokens, componentes | A cada componente ou token novo |
| Arquitetura | `docs/arquitetura/mapa.md` | No PR que muda a arquitetura |
| Runbooks | `docs/runbooks/`: restaurar backup, reprocessar um dia, trocar de legislatura, trocar uma chave vazada | Quando o procedimento muda; cada um testado uma vez |
| README | Um por pasta | Quando a pasta muda de papel |

**Direção das dependências.** `dags` chama `pipeline`, que escreve no banco. O `web` lê os marts no build e chama a `api` por HTTP; nada importa de `dags`, e o `web` nunca importa o `pipeline`. Entre site e API, o contrato é o schema OpenAPI que o FastAPI gera, e os tipos TypeScript saem dele por geração (openapi-typescript), nunca copiados à mão.

**Nomes.** Termos do domínio em português sem acento (`proposicao`, `tramitacao`, `votacao`), como na v1: traduzir "proposição" para "bill" cria uma segunda língua dentro do projeto.

## Design e frontend: sem cara de painel feito por IA

Cada página abre com uma frase que responde à pergunta, não com uma grade de cartões. O processo vai do conteúdo para a estrutura e da estrutura para o estilo, e a direção visual você escolhe comparando opções concretas lado a lado.

**O que denuncia o painel feito por IA.** Saber reconhecer é metade do trabalho de evitar:

- Grade de cartões de indicador com ícone, número grande e variação sem contexto.
- Gradiente roxo e azul, vidro fosco, sombra pesada, emoji em título.
- O tema padrão do shadcn sem ajuste (cinza neutro, fonte Inter, ícone em tudo), que virou a assinatura dos apps gerados.
- Vários gráficos por tela, pizza com muitas fatias, nuvem de palavras.
- Uma fileira de filtros antes de qualquer resposta.
- Número sem período, sem n e sem comparação.

**Princípios deste app**

1. **Resposta primeiro.** A frase de abertura sai de um modelo de texto preenchido com os dados ("Fulano apresentou 42 proposições desde fevereiro de 2023, a maioria sobre segurança pública"). Os modelos de frase são texto do produto, revisados por você, não LLM em tempo real.
2. **Uma visualização principal por tela**, escolhida pela pergunta; o resto é detalhe que se abre.
3. **Todo número com período, n e comparação** (com a Câmara, com o partido), sempre dentro da mesma legislatura.
4. **Linguagem de leigo**, com glossário embutido em termos como "apensada" e "regime de urgência".
5. **Celular primeiro.** Muita gente vai chegar por link no WhatsApp; cada página tem uma imagem de prévia que se explica sozinha.
6. **Cor neutra para direção de voto.** Vermelho, azul, verde e amarelo têm leitura partidária no Brasil. "A favor" e "contra" usam um par neutro, distinguível por daltônicos e sempre com rótulo.
7. **Incerteza à vista.** Todo rótulo de IA aparece como tal, com link para "como classificamos".
8. **Voto mostrado sem enganar**, pelas regras da nota de voto do vault: nunca "vota contra o tema X" sem as votações concretas ao lado; placar por partido em cada votação; divergência da bancada em destaque, porque o voto mostra mais o partido que a pessoa; ausência e obstrução contadas à parte, fora do placar.

**O processo em cinco passos**

1. **Conteúdo antes de pixel.** Para cada tela do MVP, escreva em texto puro a frase-resposta, o número, a visualização e o que dá para aprofundar. Use dados reais: nomes longos, deputado sem proposição, tema com uma proposição só.
2. **Wireframe em cinza.** Estrutura e hierarquia, sem cor nem fonte. Aqui no app, o plugin Intent e o canvas de Design servem para isso.
3. **Caça de referências com anotação.** Junte 15 a 20 capturas de sites que você acha bonitos e claros e anote o que pega e o que larga em cada uma: tipografia, densidade, cor, navegação.
   - Dados explicados para leigo: Our World in Data, The Pudding.
   - Parlamento: os [resumos de votação do TheyWorkForYou](https://www.theyworkforyou.com/mp/25813/fleur_anderson/putney/votes), que dizem em frase como o deputado votou em cada tema, são o modelo mais próximo de "o que ele defende"; GovTrack também.
   - Clareza de serviço público: GOV.UK Design System.
   - Telas de produtos reais: Mobbin e Refero.
   - O que o público já encontra aqui: o portal da Câmara e o [Radar do Congresso](https://www.congressoemfoco.com.br/tema/radar-do-congresso), do Congresso em Foco.
4. **Três direções lado a lado.** Com as anotações e os wireframes, eu monto aqui no app três versões da mesma página de deputado (por exemplo: editorial com serifa, institucional sóbria, técnica densa, a estética "panóptico" que o seu colega queria na v1). Você escolhe ou mistura (o tweakcn e a página de temas do shadcn, que você já tinha anotado, ajudam a testar tokens), e a vencedora vira tokens (fontes, escala tipográfica, cores, espaçamentos) em `docs/design/` e no código.
5. **Teste com gente.** Cinco pessoas, uma tarefa cada ("descubra o que o deputado do seu estado defende sobre segurança pública"), pensando em voz alta. É a mesma disciplina do tree testing que você já fez.

**Componentes: onde garimpar**

| Fonte | O que é | Use para |
| --- | --- | --- |
| shadcn/ui | Componentes copiados para dentro do seu código, sobre primitivas acessíveis; o código passa a ser seu | A base: diálogo, abas, dica, combobox. Troque os tokens para fugir da cara padrão |
| Registries de terceiros, via shadcn MCP | Coleções no mesmo formato, que o MCP busca e instala | Garimpar blocos prontos |
| React Aria Components | Componentes sem estilo da Adobe, com acessibilidade muito cuidada | As peças difíceis, como a busca com sugestões |
| Observable Plot e visx | Gráficos: o primeiro com bons padrões editoriais, o segundo com controle total | Gráfico com cara de reportagem, não de painel |

Nada entra no projeto sem uma linha em `docs/design/componentes.md` dizendo o que é e por que entrou.

**Checklist de tela** (vira a skill `/revisar-tela`):

- [ ] A tela responde à pergunta dela nos primeiros 5 segundos, no celular.
- [ ] Cada elemento aponta para uma pergunta da lista.
- [ ] Todo número tem período, n e comparação.
- [ ] No máximo uma visualização principal.
- [ ] Contraste AA, foco visível, funciona só com teclado.
- [ ] Estados de carregando, vazio, erro e dado parcial desenhados.
- [ ] Texto revisado por você, sem jargão.

## Claude Code no dia a dia

Uma sessão por tarefa, plano antes de código, travas automáticas no lugar de pedidos e agentes extras só para pesquisar e revisar.

**Sessão**

- Uma issue por sessão e `/clear` entre tarefas. Corrigiu o Claude duas vezes na mesma coisa sem resolver: `/clear` e um prompt melhor. Dê nome com `/rename` e retome com `claude --resume`.
- Plan mode (Shift+Tab até aparecer "plan mode on") para tudo que mexe em mais de um arquivo. `Ctrl+G` abre o plano no editor para você corrigir antes de aprovar. Se o diff cabe em uma frase, pule o plano.
- Feature grande: peça "me entreviste com AskUserQuestion e escreva SPEC.md" e implemente numa sessão nova, só com a spec.
- `/rewind` desfaz conversa e código, mas só o que o Claude editou pelas ferramentas dele. Não substitui git.
- Estilo de saída **Explanatory** (`/output-style explanatory`): cada mudança vem com blocos "Insight" explicando as escolhas. É o modo do seu objetivo. O **Learning** deixa trechos `TODO(human)` para você escrever, como a sua nota "Como trabalhar comigo" pedia; com a cabeça cansada, use só quando quiser praticar um conceito.

**CLAUDE.md curto.** Comandos, convenções que fogem do padrão, regras de git e onde ficam os docs. A documentação avisa que um CLAUDE.md inchado faz o Claude ignorar metade dele. Teste de cada linha: tirar isso faria o Claude errar? Um na raiz, um em `pipeline/` e um em `web/`; rascunho no anexo.

**Plugins que você já tem.** Os plugins ligados na sua conta do claude.ai sincronizam com o Claude Code do terminal quando você está logado e aparecem como `<nome>@synced` no `/plugin`. Antes de usar um, leia os `SKILL.md` dele: são markdown curtos, e é o seu método que eles vão executar.

| Plugin | Use para | Cuidado |
| --- | --- | --- |
| Superpowers | O ciclo inteiro: brainstorming, plano escrito, TDD, verificação antes de dizer "pronto", fechamento da branch | O modo com um subagente por tarefa é o mais caro e te deixa revisar menos; prefira `executing-plans` enquanto aprende |
| Engineering | ADR (`architecture`), `system-design`, `testing-strategy`, `deploy-checklist` | — |
| Frontend design | Direção estética e tipografia sem cara de template | É ponto de partida; o checklist de tela é seu |
| Intent | Estratégia, arquitetura de informação, texto de interface, acessibilidade, avaliação heurística | Rende mais aqui no app, nas fases de requisitos e design |
| Supabase | `supabase-postgres-best-practices` vale para qualquer Postgres, não só Supabase | — |

Escolha uma metodologia de base. Se for o Superpowers, não crie uma skill sua que repita os mesmos passos: as duas disparam juntas.

**Skills suas**, para o que nenhum plugin cobre. Ficam em `.claude/skills/<nome>/SKILL.md`, com `disable-model-invocation: true` para só rodarem quando você chamar:

| Skill | O que faz |
| --- | --- |
| `/explicar` | Walkthrough do diff atual e as três perguntas de teach-back |
| `/migracao` | Mudança de schema: migração com volta, teste de dados, dicionário e estratégia de atualização revisados |
| `/revisar-tela` | Checklist de design numa tela, com screenshot no celular e no desktop |

**CLI antes de MCP.** A documentação recomenda CLIs como o jeito mais econômico em contexto, e você consegue ver e repetir cada comando: `gh` para o GitHub, `psql` com usuário só-leitura para o banco, `docker compose` para o ambiente. MCP só onde não há CLI equivalente:

- **Claude in Chrome** (`claude --chrome`): o Claude abre o app local, lê o console e tira screenshot da tela que fez. Não funciona de dentro do WSL, e na sua máquina já teve timeouts e quedas (nota do vault): conte com screenshots do Playwright e, para diagnóstico, com o console do seu navegador colado na conversa.
- **shadcn MCP** (`pnpm dlx shadcn@latest mcp init --client claude`): busca e instala componentes de registries, inclusive de terceiros.
- **Supabase MCP**, se o ADR de hospedagem escolher Supabase.
- O vault do Obsidian não precisa de conector: abra o Claude com `--add-dir` apontando para o vault; o como e o quando estão na seção do Obsidian, logo abaixo.

**Travas em `.claude/settings.json`** (versionado):

- Hook `PreToolUse` no Bash que bloqueia `git commit` e `git push` quando a branch é `main`, e `git push --force` sempre. Um hook que nega vale até no modo que pula permissões.
- Hook `PostToolUse` em edições que roda o formatador (ruff, prettier).
- Hook `Stop` que roda os testes rápidos e não deixa o Claude encerrar a vez enquanto falham.
- Regras `deny`, que vencem qualquer `allow`: `Read(./.env)`, `Read(./secrets/**)`.
- Regras `ask`, que perguntam até no auto mode: `git push`, `gh pr create`, scripts de coleta e qualquer chamada paga. São as suas regras do vault ("commit sem perguntar, push só quando eu pedir" e "não executar sem eu pedir") virando trava em vez de lembrete.
- Testes e lint em `allow`: rodam sem perguntar, porque o ciclo de TDD depende deles.
- Modo de permissão: auto mode (o padrão das versões recentes) com essas travas. Aprovar comando por comando cansa e vira clique automático; a revisão que importa é a do PR.

**Múltiplos agentes**

- **Não** para escrever código em paralelo enquanto você aprende: cada agente a mais é mais diff para revisar, e foi assim que o Capivara virou colcha.
- **Sim** para três coisas:
  1. Pesquisa: "use um subagente para investigar X" lê dezenas de arquivos num contexto separado e devolve só o resumo.
  2. Revisão independente: `/code-review` revisa o diff num subagente que não viu o raciocínio de quem escreveu. Peça só o que afeta correção ou requisito, porque um revisor mandado achar problema sempre acha algum.
  3. Frentes independentes, mais tarde: duas sessões em worktrees separadas (pipeline e design, por exemplo) quando a fatia 1 estiver no ar e você der conta de revisar as duas.
- Agent teams são experimentais, vêm desligados e custam bem mais tokens. Dispensáveis aqui.

Fontes: [boas práticas](https://code.claude.com/docs/en/best-practices.md), [skills](https://code.claude.com/docs/en/skills.md), [hooks](https://code.claude.com/docs/en/hooks-guide.md), [permissões](https://code.claude.com/docs/en/permissions.md), [output styles](https://code.claude.com/docs/en/output-styles.md), [plugins](https://code.claude.com/docs/en/plugins/install.md), [Chrome](https://code.claude.com/docs/en/chrome.md), [agent teams](https://code.claude.com/docs/en/agent-teams.md), [shadcn MCP](https://ui.shadcn.com/docs/mcp), [guia do Superpowers](https://www.developersdigest.tech/blog/claude-code-superpowers-plugin-guide).

## Obsidian: o vault e o repositório

O repositório guarda a especificação do projeto: o que o sistema é agora. O vault guarda a memória, deste projeto e dos outros: o que aconteceu e o que se aprendeu. Se muda junto com o código, mora no repositório; se conta uma história ou uma lição, mora no vault, que aponta para o repositório e nunca copia.

| Informação | Onde mora | Por quê |
| --- | --- | --- |
| Especificação do Câmara v2: requisitos, ADRs, modelo de dados, rota, estado da sessão | Repositório, `docs/` | Muda junto com o código que explica, no mesmo PR |
| Memória do Câmara v2: visão, estado datado no fim de cada fase, retrospectivas, pesquisa | Vault, `Projetos/Câmara v2/` | Conta o que aconteceu e o que se aprendeu; qualquer sessão, aqui ou no Claude Code, sabe onde o projeto está sem abrir o código |
| As três perguntas e as diretrizes | Repositório, `docs/produto/perguntas.md` e `diretrizes.md` (migradas na Fase 1, passo 1) | A nota do vault fica como origem, com uma linha apontando para o repositório, e não é mais editada |
| Decisão que vale para mais de um projeto | Vault, `Decisões/` | Como "Onde guardar cada dado", que já está lá |
| Lição técnica e nota de estudo | Vault, `Conhecimento/` | Valem para o Clipping e para o próximo projeto, e estão nas suas palavras |
| APIs e dados públicos | Vault, `Domínio/` | Servem a mais de um projeto |
| Como você trabalha, sua máquina | Vault, `Eu/` | É sobre você, não sobre o projeto |

A pasta `Projetos/Câmara v2/` fica assim: a visão e as notas de pesquisa que já existem (voto, mídia, classificação de temas), mais três notas novas. "Câmara v2 - método" aponta para este doc e, depois da Fase 0, para o repositório. "Câmara v2 - estado" ganha uma entrada datada no fim de cada fase. "Câmara v2 - retrospectivas" guarda o que fugiu do controle e a regra que nasceu disso.

**Como o Claude Code enxerga o vault**

- `--add-dir` dá acesso aos arquivos do vault, mas não carrega o CLAUDE.md dele; para isso, a sessão precisa da variável `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`. Uma pasta listada em `additionalDirectories` no settings só dá acesso aos arquivos e nunca carrega o CLAUDE.md.
- No WSL, o vault fica em `/mnt/c/Users/Utilisateur/Documents/Obsidian Vault`. Um alias no `~/.bashrc` junta as duas coisas:

```bash
alias claude-vault='CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir "/mnt/c/Users/Utilisateur/Documents/Obsidian Vault"'
```

- **Velocidade:** ler pelo `/mnt/c` é mais lento que ler do lado Linux. Para notas não faz diferença; o projeto em si fica em `~/projetos/camara`, como a Microsoft recomenda.
- **Quebra de linha no git do vault:** o git do Windows converte CRLF em LF ao gravar e o do Ubuntu não, então um commit feito pelo WSL gravaria as notas no formato errado (já aconteceu uma vez, num commit feito por um git Linux). Uma vez só: `git -C "/mnt/c/Users/Utilisateur/Documents/Obsidian Vault" config core.autocrlf true`. A regra fica gravada dentro do vault e vale para qualquer git.

* Desligue a memória automática do Claude Code neste projeto com `"autoMemoryEnabled": false` no `.claude/settings.json`. Ela grava notas próprias em `~/.claude/projects/<projeto>/memory/` que entram em toda sessão sem passar por você: um terceiro lugar de memória. O vault já cumpre esse papel, e as memórias antigas do Claude Code já foram destiladas nele (estão em `Arquivo/`).
* Aqui no app eu leio o vault pela pasta conectada, como hoje. As notas que saírem das fases de requisitos e de design seguem as mesmas regras.

**Quando o Claude escreve no vault**

- Nunca no meio de uma tarefa: a sessão de feature mexe só no repositório.
- Na retrospectiva quinzenal: o registro vai para "Câmara v2 - retrospectivas", lições que servem fora do projeto viram notas em `Conhecimento/`, e decisões que valem para outros projetos vão para `Decisões/`.
- No estudo dirigido: a nota com as suas palavras.
- No fim de cada fase: "Câmara v2 - estado" ganha uma entrada datada com a fase, a frente ativa, os números-chave e o link para o repositório.

Tudo passa pela skill pessoal `/registrar` (`~/.claude/skills/registrar/SKILL.md`, que vale em todos os seus projetos). Ela lê o CLAUDE.md do vault, escreve a nota no formato dele (frontmatter, `resumo:`, linha no índice) e faz o commit com `git -C` no repositório do vault. O hook do anexo C só protege o repositório do projeto, então esse commit passa mesmo com o projeto no `main`.

Fontes: [memória e CLAUDE.md](https://code.claude.com/docs/en/memory.md), [diretórios adicionais](https://code.claude.com/docs/en/permissions.md), [skills pessoais](https://code.claude.com/docs/en/skills.md).

## Git e GitHub: três camadas de proteção

O `main` é protegido no GitHub e toda mudança entra por PR com CI verde. As regras de git ficam em três camadas: o CLAUDE.md pede, o hook bloqueia na sua máquina e o GitHub recusa para qualquer um, inclusive você com pressa.

| Camada | O que faz | Garantia |
| --- | --- | --- |
| CLAUDE.md | Escreve as regras de git | Conselho: o Claude costuma seguir, mas pode esquecer |
| Hooks e permissões do Claude Code | Bloqueiam commit e push no `main`, `push --force` e leitura de `.env` | Determinístico na sua máquina, mas casa texto de comando, então tem brecha |
| Proteção de branch no GitHub | `main` só recebe PR, com checks obrigatórios e sem force push | Sem brecha: vale para qualquer cliente git |

**O fluxo**

- `main` sempre implantável. Uma branch por issue: `feat/12-perfil-deputado`, `fix/...`, `data/...`, `docs/...`, `spike/...`.
- Commits pequenos no padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`). A mensagem diz o porquê, não só o quê.
- O Claude commita sozinho a cada mudança coesa; push e abertura de PR só quando você pede, como diz a sua nota "Como trabalhar comigo" (regra `ask` no anexo C).
- PR com um assunto só, idealmente até umas 400 linhas fora testes e arquivos gerados. Maior que isso, divide.
- Squash merge: o histórico do `main` fica com um commit por PR, cada um fechando uma issue (`Closes #12`).
- O backlog são as issues do GitHub num quadro do GitHub Projects; cada história de `docs/produto/` vira uma issue. O Claude lê e cria issues com `gh`.
- Toda biblioteca nova tem uma linha no PR dizendo o que faz, por que não dá sem ela e o que ela faz por baixo (a sua regra contra biblioteca mágica). O Dependabot abre os PRs de atualização.

**CI no GitHub Actions, a cada PR:** lint, testes do pipeline e das métricas (com Postgres num serviço do próprio Actions), build do site, um teste de fumaça contra o build, `rota.py --check` e varredura de segredos (gitleaks). O mesmo gitleaks roda no pre-commit, junto dos formatadores. Testes end-to-end completos, de acessibilidade, visuais e de carga entram na Fase 5.

O template de PR e o script do hook estão nos anexos.

## Testes por camada

Cada camada tem o seu tipo de teste, e o mais importante deste projeto não é de código: é o que impede dado ruim de chegar ao site. Os marts são montados num schema de rascunho, testados e só então trocados pelo publicado; se um teste falha, o site continua com os dados de ontem e você recebe um alerta.

O critério para um teste entrar agora é um só: ele protege um número publicado? Os que protegem o site crescendo esperam a Fase 5.

| Camada | O que testar | Ferramenta | Quando entra |
| --- | --- | --- | --- |
| Funções do pipeline | Parsers e transformações, com arquivos reais da Câmara salvos como fixtures | pytest | Agora, a cada commit |
| Pipeline integrado | Idempotência (rodar duas vezes dá o mesmo estado) e incremental igual a completo (carregar o dia 1 e depois o dia 2 dá o mesmo que carregar os dois de uma vez) | pytest com Postgres em contêiner | Agora, no CI |
| Qualidade de dados | Chaves únicas, integridade referencial, nulos proibidos, contagens na faixa esperada, dado com no máximo 2 dias, distribuição de temas sem salto | Consultas SQL de asserção | Agora, dentro do `make atualizar`, antes de publicar |
| Métricas publicadas | Cada número da metodologia recalculado num caso pequeno feito à mão (um deputado, poucas votações) | pytest | Agora, no CI |
| Classificador | Gabaritos ouro A e B com limiar de acurácia, mais o placar de personas no conjunto independente congelado (commit + SHA256) | Script de avaliação do `dag_temas` | A cada mudança de taxonomia, prompt ou modelo |
| Lógica do site | Formatação de números e datas, modelos de frase | Vitest | Agora, a cada commit |
| Fumaça do site | As páginas da fatia abrem no build com dado real | Playwright, um teste por fatia | Agora, no CI |
| API de busca | Consultas do seu conjunto de teste ("saidinha", "jogo do tigrinho") achando o tema certo | pytest com cliente HTTP | Com o marco de busca |
| Fluxos do site | Os critérios de aceitação das histórias, num navegador de verdade | Playwright | Fase 5 |
| Acessibilidade | Violações automáticas de WCAG | axe-core dentro do Playwright | Fase 5 |
| Visual | Screenshot de cada página-chave comparado com o último aprovado | Comparação de screenshot do Playwright | Fase 5 |
| Desempenho e carga | LCP e peso das páginas; carga na API de busca | Lighthouse CI; k6 | Fase 5, antes do lançamento grande |

**TDD com o Claude.** No pipeline e nas métricas, o teste vem antes do código, e o Claude mostra a saída do teste falhando antes de implementar e passando depois. A documentação do Claude Code insiste nisso: peça evidência, não afirmação de que funcionou. A skill de TDD do Superpowers impõe a ordem, e o hook `Stop` impede o Claude de encerrar a vez com teste rápido quebrado.

**Dentro do WSL**, o Claude confere telas com screenshots do Playwright salvos em arquivo, já que a integração com o Chrome não funciona ali.

## Segurança

O maior risco deste projeto não é invasão, é publicar dado errado sobre um deputado; depois vêm segredo vazado e abuso da busca. Cada risco tem uma defesa automática, não um lembrete.

| Risco | Defesa |
| --- | --- |
| Dado errado publicado | Marts montados em rascunho, testados e só então publicados; dicionário de métricas; rótulo de IA sempre marcado |
| Segredo vazado: chave do OpenRouter, senha do banco, SSH | `.env` fora do git e negado ao Claude; gitleaks no pre-commit e no CI; secrets do GitHub Actions; runbook de troca de chave |
| Injeção de SQL e banco exposto | SQL sempre parametrizado; papel `app` só-leitura; Postgres sem porta aberta para a internet |
| Abuso da busca: robô, custo, queda | Limite de requisições por IP, tamanho máximo da consulta, cache e CDN na frente |
| Injeção de prompt pelos dados | Matérias, ementas e discursos são texto de terceiros. O LLM do pipeline roda sem ferramentas, devolve saída estruturada validada por schema e só pode escolher ids que existem na taxonomia; a saída nunca vira HTML sem escape |
| XSS no site | Astro e React escapam texto por padrão; `set:html` e `dangerouslySetInnerHTML` ficam proibidos para dado; cabeçalhos CSP e HSTS |
| Dependência comprometida | Lockfiles, Dependabot, `pip-audit` e `npm audit` no CI; plugin do Claude Code só depois de ler o que ele instala |
| Servidor invadido | SSH só com chave e sem root, firewall só com 80 e 443, atualização automática de segurança, interface do Airflow só por túnel SSH, backup criptografado fora do servidor |
| Dado pessoal de quem usa (LGPD) | Perfil opcional, sentido político nunca guardado, métrica de acesso sem cookie, busca sem resultado guardada sem identificar quem buscou, política de privacidade |

**Revisão de segurança com o Claude**

- **Plugin `security-guidance`** (`/plugin install security-guidance@claude-plugins-official`). Procura padrões perigosos a cada edição, sem custo, e revisa o diff no fim de cada vez e a cada commit com um Claude separado. Não bloqueia nada, e as revisões com modelo gastam uso; cada camada pode ser desligada por variável.
- **`.claude/claude-security-guidance.md`**: a tabela acima em forma de checklist (SQL parametrizado, nada de `set:html` com dado, nada de `verify=False`, saída de LLM validada). O revisor do plugin lê esse arquivo.
- **`/security-review`** antes de cada release, numa passada pelo branch inteiro.
- **Camada paga, quando vier:** as lições da nota "Segurança web - lições da v1" (JWT em cookie HttpOnly e SameSite, path traversal, XSS em atributo) entram no mesmo checklist.

Fontes: [plugin security-guidance](https://code.claude.com/docs/en/security-guidance.md), [diretivas do Astro](https://docs.astro.build/en/reference/directives-reference).

## Rotina anti-caixa-preta

Entender o projeto vira algo que se verifica, não uma sensação, mas só onde conta: no código que gera número publicado e nas decisões de arquitetura. Ali, qualquer linha que você não saiba justificar é tratada como bug e vira uma issue com o rótulo `entender`. No resto, basta saber o que cada parte faz.

| Ritual | Quando | Como |
| --- | --- | --- |
| Teach-back | PR que gera número publicado ou muda a arquitetura | `/explicar` gera o walkthrough e três perguntas; você responde sem olhar. Errou, estuda antes do merge |
| Metodologia | PR que muda uma métrica | A página de metodologia é atualizada no mesmo PR, com a fórmula, a fonte e os limites em linguagem comum. Se você não consegue escrever, ainda não entendeu |
| Mapa do sistema | PR que muda a arquitetura | `docs/arquitetura/mapa.md` com o diagrama dos componentes e do fluxo de dados em Mermaid, atualizado no mesmo PR |
| README por pasta | Toda pasta nova | Cinco a dez linhas: o que faz, o que recebe, o que entrega, quem chama |
| Retrospectiva | No fim de cada fatia | O que fugiu do controle? A regra que evita isso vira hook, skill ou linha no CLAUDE.md; a lição que serve fora do projeto vira nota no vault |

**Estudo dirigido.** Antes de usar um conceito novo (data lógica do Airflow, componente de servidor, índice no Postgres), leia a página de conceitos da documentação oficial e escreva uma nota no vault com as suas palavras. Depois peça ao Claude que te argua sobre a nota. É o mesmo teach-back, aplicado ao conceito em vez do código.

## Primeiros passos, decisões em aberto e anexos

A Fase 0 deixou o repositório pronto e travado antes da primeira linha de produto, e a lista abaixo fica como registro. A referência que o Claude lê é o `docs/metodo.md` do repositório, exportado deste doc, e as perguntas que mexem no projeto vão para a sessão do Claude Code aberta na pasta dele.

**Fase 0, passo a passo**

1. **Ambiente no WSL2**, o Linux (Ubuntu) que roda dentro do Windows: `wsl --install` num PowerShell aberto como administrador, depois reinicie. Se já houver um Ubuntu no WSL, use esse mesmo, desde que esteja no WSL 2, seja 22.04 ou mais novo (o Docker não aceita versões anteriores) e tenha o systemd ligado. Se houver só outra distribuição, instale o Ubuntu com wsl --install -d Ubuntu. Dentro do Ubuntu entram Docker Engine direto no Ubuntu, sem o Docker Desktop (roda Postgres e Airflow isolados), Python (pipeline e API), Node (build do site), `gh` (GitHub pela linha de comando), `jq` (lê JSON; o hook do anexo C usa) e o próprio Claude Code. Por quê: o Airflow não roda direto no Windows, o servidor de produção é Linux, e somem as armadilhas do Windows que o vault já registra (encoding, SSL, Playwright com uvicorn).
2. Repositório no GitHub com o `main` protegido: só PR, checks obrigatórios, sem force push.
3. Esqueleto de pastas, `docs/` com os arquivos vazios e seus títulos, um README por pasta.
4. `CLAUDE.md` (anexo A), template de PR (anexo B) e `.claude/settings.json` com hooks e permissões (anexo C).
5. Rota: `docs/frentes.yaml` (anexo D), `scripts/rota.py` (anexo E) e o `--check` no CI.
6. Vault ligado: o alias `claude-vault`, o ajuste de quebra de linha no git do vault, a memória automática desligada e a skill pessoal `/registrar` (seção do Obsidian).
7. CI mínimo com lint, tipos e um teste de exemplo, sobre um ambiente `uv` com lockfile (ADR 0001); pre-commit com formatadores e gitleaks.
8. `/output-style explanatory`, e `/plugin` para conferir os plugins sincronizados e instalar o `security-guidance`.
9. Portão: você explica, sem olhar, cada arquivo de configuração criado.

**Para levar uma revisão do método ao repositório.** Exporte este doc como Markdown e, numa sessão nova do Claude Code, em plan mode:

> Substitua docs/metodo.md pelo Markdown que eu exportei (está em /mnt/c/Users/Utilisateur/Downloads). Reestruture docs/frentes.yaml como o anexo D do novo método, mantendo os status e os próximos passos que já estão no arquivo. Ajuste o CLAUDE.md e o template de PR aos anexos A e B. Rode make rota e rota.py --check, me mostre o diff de cada arquivo e só abra o PR quando eu pedir.

**Onde perguntar**

- Decisão de produto, design, método e pesquisa: aqui no app, onde estão o doc e o vault.
- O que roda comando ou mexe em arquivo do projeto: o Claude Code, dentro da pasta do projeto.
- Decisão técnica que vale lembrar, como onde instalar o Docker: vira ADR no repositório, seja onde for que ela foi discutida.

**Decisões em aberto que só você toma**

- A camada paga continua no plano? Muda autenticação e talvez o framework.
- Onde fica o laboratório: repositório separado, que é o que eu recomendo, ou uma pasta que o CI ignora.
- Teto mensal para infraestrutura e para LLM.
- Lançar a fatia 1 antes ou depois de 1/2/2027? Com a 57ª legislatura fechada, a pergunta 2 tem um conjunto completo de votações, um bom gancho para o texto de lançamento.
- Onde o texto de lançamento sai além do site: blog próprio, LinkedIn ou proposta a uma redação.
- Nome e domínio: "Quem está do seu lado" é provisório, e o domínio não foi conferido.

Já decidido: repositório público, com o `main` protegido (nota em `Decisões/` no vault).

**Anexo A — CLAUDE.md**

```markdown
# Câmara v2

Site que responde, em linguagem comum, as três perguntas de docs/produto/perguntas.md: o que a Câmara prioriza e abandona, se um deputado está do lado de quem pergunta e quem é mais aliado ou inimigo.
Método: docs/metodo.md. Rota: docs/frentes.yaml (make rota). Tarefa parada no meio: docs/estado.md.

## Onde está cada coisa
- docs/produto/: perguntas, diretrizes, personas, histórias e não-objetivos. Leia antes de mexer em qualquer tela.
- docs/decisoes/: ADRs. Não contrarie um ADR sem propor outro.
- docs/dados/atualizacao.md: toda tabela nova ganha uma linha aqui antes do schema.
- pipeline/passos.py: a lista de passos da coleta e de quem depende de quem (nasce com o marco dados.core).
- Notebook e experimento não entram aqui: vão para o repositório do laboratório.

## Comandos
- Preparar a máquina: make setup
- Rota: make rota
- Testes rápidos: make test
- Tudo, como no CI: make ci
- Atualizar os dados: make atualizar (nasce com o marco dados.core)
- Ambiente local: docker compose -f infra/compose.yml up -d

## Git
- Commit local a cada mudança coesa, sem perguntar. git push e gh pr create só quando eu pedir.
- Nunca commit nem push no main. Uma branch por issue: feat/<n>-<slug>, fix/, data/, docs/, spike/.
- Conventional Commits; a mensagem explica o porquê.
- Confira git status e adicione arquivo por arquivo; nada de git add -A às cegas.
- Todo PR que fecha um passo atualiza o próximo passo da frente em docs/frentes.yaml.

## Como trabalhar
- Trabalhe na frente ativa da rota; trocar de frente só com o meu ok.
- Explique em detalhe o código que gera número publicado e as decisões de arquitetura, com opções e trade-offs. No resto, diga em uma linha o que cada parte faz.
- Plano antes de mexer em mais de um arquivo, com alternativas e riscos.
- Decida pelo tamanho que já se sabe que vem, não pelo de hoje: "dá menos trabalho agora" não é argumento. Se é só "talvez um dia", não faça; se adiar obriga a refazer, faça direito agora.
- No pipeline e nas métricas, teste primeiro: mostre a saída falhando e depois passando.
- Passo novo da coleta entra em pipeline/passos.py, como comando idempotente que recebe a data lógica; nunca num script solto.
- Mudou uma métrica, atualize a página de metodologia no mesmo PR.
- Escrever não é rodar: coleta, notebook e chamada paga só quando eu pedir, com estimativa de custo e --max-custo.
- Depois de implementar, diga o que testar: URLs (caminho feliz e um erro), consultas SQL, arquivos esperados.
- Nenhuma dependência nova sem justificativa no PR e sem explicar a camada de baixo.
- Sem filtros manuais sobre método estatístico: explique o mecanismo em vez de esconder o resultado.
- Nenhuma chamada de LLM no caminho de uma requisição do site; saída de LLM sempre validada por schema.
- Mudança de schema só pela skill /migracao.
- Se a tarefa parar no meio, anote em docs/estado.md onde parou.
- Sugira /registrar no fim da tarefa quando ela fechar uma fase ou render lição ou decisão útil fora do projeto; só grave no vault se eu confirmar.

## Pegadinhas do domínio
Resumo; a fonte é docs/produto/diretrizes.md.
- Nunca compare legislaturas nem governos; deputado em duas legislaturas tem dois perfis.
- Partido é o da época do ato (tabela de filiação), nunca o atual.
- Ids de tema são estáveis: nunca renumere nem reaproveite.
- Personas são o critério de classificação: toda mudança de tema reporta o placar antes e depois.
```

**Anexo B — template de PR** (`.github/pull_request_template.md`)

```markdown
## O que muda e por quê

## Issue
Closes #

## Por onde começar a ler
1.

## Como testar

## Checklist
- [ ] Consigo explicar sem ajuda o que gera número publicado; do resto, sei o que cada arquivo faz
- [ ] Os testes cobrem os critérios de aceitação da issue
- [ ] Próximo passo da frente atualizado em docs/frentes.yaml
- [ ] Metodologia atualizada, se mudou uma métrica
- [ ] Docs, ADR e mapa do sistema atualizados, se for o caso
- [ ] Migração tem volta e linha em docs/dados/atualizacao.md, se for o caso
- [ ] Screenshots no celular e no desktop, se mexe em tela
- [ ] Nenhuma dependência nova sem justificativa
```

**Anexo C — permissões e hook que protege o `main`**

`.claude/hooks/protege-main.sh` (torne executável com `chmod +x`; precisa do `jq`):

```bash
#!/bin/bash
# Bloqueia commit e push no main do projeto, e push --force em qualquer lugar.
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
DIR=$(echo "$INPUT" | jq -r '.cwd // empty')

RE_FORCE='git.*push.*(--force|-f([[:space:]]|$))'
RE_ESCRITA='git.*(commit|push)'
RE_C='git[[:space:]]+-C[[:space:]]+("([^"]+)"|([^[:space:]]+))'

if [[ "$CMD" =~ $RE_FORCE ]]; then
  echo "Bloqueado: push --force não é permitido neste projeto." >&2
  exit 2
fi

# Com git -C <pasta>, vale a pasta do comando, não a da sessão
if [[ "$CMD" =~ $RE_C ]]; then
  DIR="${BASH_REMATCH[2]:-${BASH_REMATCH[3]}}"
fi

# Só o repositório do projeto é protegido; o vault e outros repositórios passam
ALVO=$(git -C "$DIR" rev-parse --show-toplevel 2>/dev/null)
PROJETO=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null)
[[ "$ALVO" != "$PROJETO" ]] && exit 0

BRANCH=$(git -C "$DIR" rev-parse --abbrev-ref HEAD 2>/dev/null)
if [[ "$BRANCH" == "main" && "$CMD" =~ $RE_ESCRITA ]]; then
  echo "Bloqueado: você está no main. Crie uma branch: git switch -c feat/<issue>-<slug>" >&2
  exit 2
fi

exit 0
```

`.claude/settings.json`:

```json
{
  "autoMemoryEnabled": false,
  "permissions": {
    "allow": ["Bash(make test)", "Bash(make ci)", "Bash(make rota)", "Bash(git status *)", "Bash(git diff *)", "Bash(git add *)", "Bash(git commit *)"],
    "ask": ["Bash(git push *)", "Bash(gh pr create *)", "Bash(git add -A*)", "Bash(git add .)", "Bash(python -m pipeline*)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  },
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          { "type": "command", "command": "cd \"$CLAUDE_PROJECT_DIR\" && uv run --locked --quiet python scripts/rota.py" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/protege-main.sh" }
        ]
      }
    ]
  }
}
```

A ordem de avaliação é deny, depois ask, depois allow, e a primeira que casa decide. Por isso `git add -A` pergunta mesmo com `git add *` liberado, e o `ask` do push vale até no auto mode.

O hook `Stop` dos testes rápidos e o `PostToolUse` do formatador seguem o mesmo formato. Peça ao Claude para escrevê-los a partir da [documentação de hooks](https://code.claude.com/docs/en/hooks-guide.md) e confira que o `Stop` respeita o campo `stop_hook_active`, senão ele entra em laço.

**Anexo D — `docs/frentes.yaml` revisado**

Ao trocar o arquivo no repositório, mantenha os status e os próximos passos que já estão no seu: o que muda é a estrutura (fatias, frente de análise e frente de escala). O `rota.py` do anexo E não muda.

```yaml
# Rota do projeto. `make rota` lê este arquivo, valida e mostra onde trabalhar em seguida.
#
# frente         linha de trabalho com objetivo próprio
# marcos         resultados verificáveis, em ordem; o primeiro não feito é o atual
# criterio       como saber que o marco está feito
# depende_de     marcos que precisam estar feitos antes ("frente.marco")
# status         pendente | andamento | feito
# ativa          no máximo uma frente de código ativa por vez
# proximo_passo  a próxima ação concreta da frente, que dá para começar sem pensar

frentes:
  fundacao:
    objetivo: repositório pronto e travado antes da primeira linha de produto
    marcos:
      - id: repo
        criterio: main protegido, CI verde, CLAUDE.md, hooks e rota funcionando; você explica cada arquivo de configuração
        status: feito

  produto:
    objetivo: as três perguntas viram histórias testáveis
    ativa: true
    proximo_passo: conferir docs/produto/ contra a ordem das fatias e seguir de onde parou
    marcos:
      - id: perguntas
        criterio: perguntas, personas, histórias e não-objetivos em docs/produto/
        depende_de: [fundacao.repo]
        status: andamento
      - id: metricas
        criterio: dicionário de métricas da pergunta 2 revisado por você
        depende_de: [produto.perguntas]

  dados:
    objetivo: coleta incremental e idempotente, pronta para o Airflow sem reescrever nada
    proximo_passo: escrever docs/dados/atualizacao.md para as tabelas da pergunta 2
    marcos:
      - id: modelo
        criterio: modelo de dados e tabela de atualização revisados
        depende_de: [produto.perguntas]
      - id: contrato_marts
        criterio: schema dos marts da pergunta 2 fixado, com amostra de dados para o site
        depende_de: [dados.modelo, produto.metricas]
      - id: core
        criterio: proposições, votos e orientações atualizados com make atualizar, a partir de pipeline/passos.py; teste incremental = completo passa
        depende_de: [dados.modelo]
      - id: tramitacao
        criterio: tramitações coletadas por delta
        depende_de: [dados.core]

  taxonomia:
    objetivo: temas que se atualizam sem reestruturar nada
    proximo_passo: levar temas.yaml e os gabaritos do dag_temas para taxonomia/
    marcos:
      - id: incremental
        criterio: proposição nova ganha ficha e temas na versão vigente; gabaritos rodam como teste
        depende_de: [dados.core]
      - id: jardinagem
        criterio: fila de "nenhum serve" e PR de taxonomia com placar de personas
        depende_de: [taxonomia.incremental]

  design:
    objetivo: direção visual própria, sem cara de painel feito por IA, antes da primeira página
    proximo_passo: juntar 15 referências anotadas em docs/design/referencias.md
    marcos:
      - id: referencias
        criterio: 15 a 20 referências com o que pega e o que larga
        depende_de: [produto.perguntas]
      - id: wireframes
        criterio: wireframes das telas da pergunta 2, com dados reais
        depende_de: [design.referencias]
      - id: tokens
        criterio: direção escolhida, tokens e componentes de base no repositório, 5 pessoas testaram
        depende_de: [design.wireframes]

  infra:
    objetivo: um merge no main publica o site sozinho
    proximo_passo: escrever o ADR da forma de entrega do site
    marcos:
      - id: adrs
        criterio: ADRs de entrega, framework, banco e hospedagem escritos
        depende_de: [fundacao.repo]
      - id: deploy
        criterio: merge no main publica o site; backup restaurado uma vez
        depende_de: [infra.adrs]

  site:
    objetivo: as três perguntas no ar, uma fatia por vez
    proximo_passo: página de um deputado gerada pelo build a partir da amostra do contrato
    marcos:
      - id: fatia1
        criterio: páginas de consulta da pergunta 2 geradas pelo build a partir dos marts; teste de fumaça passa
        depende_de: [infra.deploy, dados.contrato_marts, dados.core, design.tokens]
      - id: fatia2
        criterio: páginas de consulta da pergunta 3 no ar
        depende_de: [analise.lancamento1]
      - id: fatia3
        criterio: páginas de consulta da pergunta 1 no ar
        depende_de: [analise.lancamento2, dados.tramitacao]
      - id: busca
        criterio: conjunto de teste de busca acima do limiar
        depende_de: [site.fatia1, taxonomia.incremental]

  analise:
    objetivo: cada fatia sai com metodologia assinada e um achado
    proximo_passo: rascunhar a metodologia da pergunta 2 a partir do dicionário de métricas
    marcos:
      - id: metodologia1
        criterio: página de metodologia da pergunta 2 assinada; cada número sai de um comando que você roda e explica
        depende_de: [produto.metricas, dados.contrato_marts]
      - id: lancamento1
        criterio: fatia 1 publicada com a metodologia e o texto de lançamento
        depende_de: [analise.metodologia1, site.fatia1]
      - id: lancamento2
        criterio: fatia 2 publicada com metodologia e texto
        depende_de: [site.fatia2]
      - id: lancamento3
        criterio: fatia 3 publicada com metodologia e texto
        depende_de: [site.fatia3]

  escala:
    objetivo: o site se atualiza sozinho e aguenta pico de acesso
    proximo_passo: escrever o ADR de onde o Airflow roda em produção
    marcos:
      - id: airflow
        criterio: DAGs geradas a partir de pipeline/passos.py rodando no servidor, com alerta de falha
        depende_de: [analise.lancamento1]
      - id: carga
        criterio: teste de carga, Lighthouse e testes de acessibilidade e visuais no CI
        depende_de: [analise.lancamento1]
```

**Anexo E — `scripts/rota.py`**

`make rota` roda o script pelo `uv`, e o CI roda `make rota-check`. O PyYAML vem do `uv.lock`. O hook que mostra a rota no começo da sessão está no `settings.json` do anexo C.

```python
#!/usr/bin/env python3
"""Lê docs/frentes.yaml, valida a rota e mostra onde trabalhar em seguida.

    python3 scripts/rota.py           mostra a rota; sai sempre com 0 (é o que o hook usa)
    python3 scripts/rota.py --check   só valida; sai com 1 se houver erro (é o que o CI usa)
"""
import sys
from pathlib import Path

import yaml

ARQUIVO = Path(__file__).resolve().parent.parent / "docs" / "frentes.yaml"
STATUS = {"pendente", "andamento", "feito"}


def carregar(caminho):
    frentes = yaml.safe_load(caminho.read_text(encoding="utf-8"))["frentes"]
    marcos = {}  # "frente.marco" -> marco
    for nome, frente in frentes.items():
        for m in frente.get("marcos", []):
            m.setdefault("status", "pendente")
            m.setdefault("depende_de", [])
            marcos[f"{nome}.{m['id']}"] = m
    return frentes, marcos


def marco_atual(frente):
    """O primeiro marco que ainda não foi feito, ou None se a frente acabou."""
    return next((m for m in frente.get("marcos", []) if m["status"] != "feito"), None)


def faltando(m, marcos):
    return [d for d in m["depende_de"] if marcos.get(d, {}).get("status") != "feito"]


def ciclos(marcos):
    cor, erros = {}, []

    def visita(k, caminho):
        cor[k] = "visitando"
        for dep in marcos[k]["depende_de"]:
            if dep not in marcos:
                continue
            if cor.get(dep) == "visitando":
                erros.append("ciclo: " + " -> ".join(caminho + [dep]))
            elif dep not in cor:
                visita(dep, caminho + [dep])
        cor[k] = "visto"

    for k in marcos:
        if k not in cor:
            visita(k, [k])
    return erros


def validar(frentes, marcos):
    erros = []
    for chave, m in marcos.items():
        if m["status"] not in STATUS:
            erros.append(f"{chave}: status '{m['status']}' não existe")
        for dep in m["depende_de"]:
            if dep not in marcos:
                erros.append(f"{chave}: depende de '{dep}', que não existe")
        if m["status"] != "pendente" and faltando(m, marcos):
            erros.append(f"{chave}: está '{m['status']}', mas espera {', '.join(faltando(m, marcos))}")
    ativas = [n for n, f in frentes.items() if f.get("ativa")]
    if len(ativas) > 1:
        erros.append(f"mais de uma frente ativa: {', '.join(ativas)}")
    for nome, f in frentes.items():
        atual = marco_atual(f)
        if atual and not str(f.get("proximo_passo") or "").strip():
            erros.append(f"{nome}: tem marco aberto e nenhum próximo passo")
        if f.get("ativa") and atual and faltando(atual, marcos):
            erros.append(f"{nome}: está ativa, mas o marco atual espera {', '.join(faltando(atual, marcos))}")
    return erros + ciclos(marcos)


def destrava(marcos):
    """Quantos marcos dependem, direta ou indiretamente, de cada marco."""
    dependentes = {k: set() for k in marcos}
    for k, m in marcos.items():
        for dep in m["depende_de"]:
            if dep in dependentes:
                dependentes[dep].add(k)

    def alcance(k, vistos):
        for d in dependentes[k] - vistos:
            vistos.add(d)
            alcance(d, vistos)
        return vistos

    return {k: len(alcance(k, set())) for k in marcos}


def main():
    frentes, marcos = carregar(ARQUIVO)
    erros = validar(frentes, marcos)
    if "--check" in sys.argv:
        for e in erros:
            print("ERRO:", e)
        sys.exit(1 if erros else 0)

    peso = destrava(marcos)
    ativa, livres, bloqueadas, concluidas = None, [], [], []
    for nome, f in frentes.items():
        m = marco_atual(f)
        if m is None:
            concluidas.append(nome)
            continue
        chave = f"{nome}.{m['id']}"
        item = (nome, chave, f.get("proximo_passo"), faltando(m, marcos), peso[chave])
        if f.get("ativa"):
            ativa = item
        elif item[3]:
            bloqueadas.append(item)
        else:
            livres.append(item)

    print("ROTA (docs/frentes.yaml)")
    if ativa:
        print(f"\nAtiva: {ativa[0]}, marco {ativa[1]}\n  próximo passo: {ativa[2]}")
    else:
        print("\nNenhuma frente ativa: escolha uma das livres e marque ativa: true.")
    if livres:
        print("\nLivres, da que destrava mais para a que destrava menos:")
        for nome, chave, passo, _, n in sorted(livres, key=lambda i: -i[4]):
            print(f"  {chave} (destrava {n}) | próximo passo: {passo}")
    if bloqueadas:
        print("\nBloqueadas:")
        for nome, chave, _, falta, _ in bloqueadas:
            print(f"  {chave} espera {', '.join(falta)}")
    if concluidas:
        print(f"\nConcluídas: {', '.join(concluidas)}")
    for e in erros:
        print("ERRO:", e)


if __name__ == "__main__":
    main()
```

## Glossário

Os termos técnicos deste doc, em uma linha cada. Se faltar algum, comente nele que eu acrescento.

| Termo | O que é |
| --- | --- |
| ADR | Registro curto de uma decisão de arquitetura: contexto, opções, escolha e consequências |
| Alembic | Ferramenta de migrations para Python: cada mudança de schema vira um arquivo com ida e volta |
| Backfill | Rodar o pipeline para datas passadas, para preencher o histórico |
| CDN | Rede de servidores que guarda cópias das páginas e entrega do mais próximo, sem tocar no banco |
| CI | Integração contínua: o GitHub roda testes e checagens sozinho a cada PR |
| Contrato | Interface combinada entre duas partes, como as colunas de um mart, que deixa cada lado andar sem esperar o outro |
| Conventional Commits | Padrão de mensagem de commit com prefixo: `feat:`, `fix:`, `docs:` |
| Docker, contêiner | Empacota um programa com tudo de que ele precisa e o roda isolado; sobe Postgres ou Airflow com um comando |
| e2e | Teste de ponta a ponta: abre o site num navegador de verdade e faz o que o usuário faria |
| Fixture | Dado de exemplo guardado para os testes, como uma resposta real da API da Câmara |
| `gh` | A linha de comando do GitHub: criar issue, abrir PR |
| Hook | Comando que o Claude Code roda sozinho em certos momentos, como antes de um comando ou ao abrir a sessão; pode bloquear |
| Idempotente | Rodar duas vezes dá o mesmo resultado que rodar uma |
| Ilha (Astro) | Pedaço interativo, em React, numa página que no resto é HTML pronto |
| `jq` | Programa de linha de comando que lê e filtra JSON |
| Kaplan–Meier | Curva que estima quanto tempo algo leva para acontecer, contando também quem ainda não chegou lá (censura) |
| LCP | Tempo até o maior elemento da página aparecer; mede se ela parece rápida |
| Lint | Checagem automática de estilo e de erros comuns no código, sem executá-lo |
| Mart | Tabela pronta para uma tela, montada a partir das tabelas limpas |
| MCP | Protocolo que liga o Claude a ferramentas externas, como GitHub, navegador ou banco |
| Migration | Arquivo versionado que muda o schema do banco, com o caminho de volta |
| MoSCoW | Priorização em Must, Should, Could e Won't: deve, deveria, poderia, não vai |
| Plan mode | Modo do Claude Code em que ele só pesquisa e propõe um plano, sem mudar nada |
| Pre-commit | Checagens que rodam na sua máquina antes de cada commit, como formatador e gitleaks |
| PR | Pull request: pedido para juntar uma branch ao `main`, onde se revisa o diff |
| Skill | Arquivo de instruções que ensina um procedimento ao Claude, chamado com `/nome` |
| Spike | Protótipo descartável, com prazo curto, para responder uma pergunta antes de decidir |
| Squash merge | Junta todos os commits de um PR num só quando ele entra no `main` |
| Subagente | Outra instância do Claude, com contexto próprio, para pesquisar ou revisar |
| Teach-back | Explicar de volta, com as suas palavras, para provar que entendeu |
| Token de design | Valor nomeado do visual (cor, fonte, espaçamento) usado no site inteiro |
| Upsert | Insere a linha se ela não existe e atualiza se existe |
| Walkthrough | Roteiro de leitura de uma mudança: o que mudou, por quê e por onde começar |
| Worktree | Segunda cópia de trabalho do mesmo repositório, para duas sessões não se atrapalharem |
| WSL2 | O Linux (Ubuntu) que roda dentro do Windows |
| XSS | Ataque em que um texto malicioso vira código rodando na página de outra pessoa |

Fonte da instalação do WSL: [Microsoft Learn](https://learn.microsoft.com/en-us/windows/wsl/install).
