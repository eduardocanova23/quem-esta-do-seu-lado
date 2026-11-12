# Perguntas que o produto responde

_O banco de perguntas: as três perguntas centrais e as que entrarem depois, cada uma com o perfil que a faz, a prioridade e o dado que a responde._

Estas três perguntas são a base do produto. Toda feature, dado coletado ou métrica serve a pelo menos uma delas; o que não serve vai para [nao-objetivos.md](nao-objetivos.md). As [diretrizes](diretrizes.md) dizem como decidir; este arquivo diz o que se pergunta. Toda pergunta parte de uma persona.

Origem: nota do vault "As três perguntas que o produto responde" (03/11/2026). A versão viva é esta.

| # | Pergunta | Inclui | Perfis | Prioridade | Dado que responde |
| --- | --- | --- | --- | --- | --- |
| 2 | Este deputado está do meu lado? | O que o deputado X faz e defende: como vota, o que propõe e se isso interessa | **Eleitor curioso, quem acompanha uma causa**; jornalista, estudante | 1ª (MVP) | Votos nominais de mérito com eixo, orientação de bancada, autoria e temas |
| 3 | Quem é o mais aliado e o mais inimigo? | "E o partido?", vista por bancada | **Quem acompanha uma causa, jornalista**; eleitor curioso, estudante | 2ª | O mesmo da pergunta 2, aplicado a todos os deputados |
| 1 | Quais assuntos a Câmara prioriza e quais abandona? | O que a Câmara fez; quais temas demoram | **Quem acompanha uma causa, jornalista, estudante** | 3ª | Proposições por tema e eventos de tramitação (ainda não coletados) |

Os perfis estão em [personas.md](personas.md); em negrito, o público principal de cada pergunta.

## Viabilidade

_Análise de 03/11/2026 com os dados do DAG de temas v1.1 (57ª legislatura). É uma foto: os números mudam com a coleta nova e a legislatura nova._

**A área de atuação está bem coberta; a direção pelo voto é fina.** Autoria e coautoria existem para quase todas as 23 mil proposições. Já a direção depende de voto nominal de mérito:

- Só **156 das 334** proposições votadas no Plenário na 57ª têm eixo com sinal + ou −.
- Elas se concentram em poucos eixos: gasto e benefício 43, carga tributária 36, punição 25, ambiente 15, trabalho 10, Estado na economia 10, terra 9, segurança × privacidade 6, controle de autoridades 5.
- **Aborto, LGBT, armas, apostas, valores na escola e religião têm 1 ou 2 votações cada.** Nesses eixos não dá para dizer "como o deputado vota"; só dá para mostrar o voto naquela votação.
- Por deputado e eixo, a mediana é de cerca de 6 votos, e o número está inflado, porque a mesma proposição conta em mais de um tema.
- Fonte na v1: `definitivo/dag_temas/out/prop_eixo.parquet` e `out/deputado_tema_eixo.parquet`. Ver também a nota do vault "Direção e voto dos deputados".

### 1. Assuntos priorizados × abandonados: dá, mas não com tempo médio

- **O tempo médio de tramitação engana (censura).** Proposição parada não tem tempo final; a média só vê as que andaram e subestima justamente os temas abandonados.
- Usar:
  - **volume** por tema, que mede a oferta (o interesse dos deputados, não o da instituição);
  - **taxa de avanço**: a fração que deu um passo real em X meses (parecer aprovado em comissão, urgência, votação, sanção). Melhor ainda: a **curva de sobrevivência de Kaplan–Meier por tema**, que trata as paradas como censuradas.
- **"Abandonado" é relativo a uma taxa base baixíssima:** só cerca de 1.148 de 26.512 proposições (≈4%) foram deliberadas no Plenário. Abandonado quer dizer muita oferta e muita demanda das personas, com avanço bem abaixo da base.
- **Proposições antigas:** o universo do DAG já exclui as de legislaturas anteriores que só tramitam sem votação na 57ª (ver [Sempre separar legislaturas](diretrizes.md#sempre-separar-legislaturas)). Cuidados que restam:
  - **apensadas** andam junto com a principal. Medir o avanço por proposição faz parecer abandonado um tema que andou pela principal. Abandonar o agrupamento de apensadas (nota do vault) não resolve isso: é preciso olhar a principal;
  - **o arquivamento de fim de legislatura** (RICD, art. 105) só acontece no início de 2027. Até lá, "parada" não é "arquivada".
- **Falta dado:** o DAG só sabe se a proposição foi votada ou deliberada, sem o histórico de tramitação. Os eventos de tramitação vêm da API de Dados Abertos da Câmara (grátis, coleta incremental com checkpoint; notas do vault em `Domínio/` e `Conhecimento/`).

### 2. Este deputado está do meu lado: dá, nos eixos com volume, sempre com o n

- A persona tem um polo preferido por eixo (`out/lentes.yaml` na v1). O placar é a concordância do voto com esse polo: "em punição, votou na sua direção em 7 de 9 votações".
- O sentido que o usuário quer é escolhido na hora e nunca é salvo (decisão do vault "Perfil do usuário é opcional e o sentido político nunca é guardado").
- **Disciplina partidária:** o voto mostra sobretudo a orientação do partido. O que fala da pessoa é quando ela **diverge da bancada**. Isso vai em destaque, não só o placar bruto.
- **Ausência e obstrução** ficam fora do placar, porque quem falta muito parece neutro quando está ausente. Elas aparecem à parte.
- **Dois sinais separados:**
  - "como vota": poucos votos, mas que pesam;
  - "o que propõe": autoria com sinal, muito volume, mas propor é barato e há muita proposição simbólica.
- **"Isso me interessa?"** é a parte fácil: a sobreposição entre os temas em que o deputado atua e os temas da lente. Não depende de eixo.

### 3. Aliado × inimigo: dá, mas o ranking cru engana

- Deputado com 2 votos, ambos do seu lado, vira "100%" e vai para o topo. Por isso:
  - o placar é **encolhido para uma referência** (a média do partido dele) quando há poucos votos: pouca evidência fica perto do partido até provar o contrário;
  - há um **n mínimo**, e a soma usa só os eixos da lente, com o peso que a persona der.
- **Empates por partido:** as bancadas votam juntas, então o ranking vira blocos partidários, e dentro deles a diferença vem das faltas e das poucas dissidências. A apresentação mais honesta: **"partidos mais alinhados com você" e, dentro de cada um, quem foge da linha.**
- Nenhum eixo tem correlação |r| ≥ 0,9 com o governismo, então os eixos não se reduzem a governo × oposição. Mesmo assim, uma persona que se importa com muitos eixos tende a ter um ranking parecido com o de governismo.

### Resumo

| Pergunta | Viável? | Principal limite |
| --- | --- | --- |
| 1. Priorizados × abandonados | Sim | Coletar a tramitação; usar avanço e sobrevivência, não média; apensadas |
| 2. Deputado do meu lado | Sim, nos eixos com volume (gasto, tributo, punição, ambiente, trabalho) | Poucos votos por eixo; o voto mostra o partido mais que a pessoa |
| 3. Aliado × inimigo | Sim, com n mínimo e encolhimento | Vira blocos partidários |

## Por onde começar

**A pergunta 2, restrita aos cinco eixos com volume**, sempre com o n à vista. Ela usa só o que já existe (`deputado_tema_eixo.parquet` e `lentes.yaml`), sem LLM e sem coleta nova. Também é a base da pergunta 3: o ranking é a pergunta 2 aplicada a todos, mais o encolhimento. A pergunta 1 depende de coletar a tramitação antes.

O protótipo em Streamlit da v1 (`definitivo/dag_temas/pergunta2.py` e `app_deputado.py`) serve de especificação de comportamento. O estado dele e os exemplos de 03/11 ficam na nota do vault.

## Em aberto

- As votações de destaque e de emenda de Plenário (687 nominais) estão fora do placar. Podem engrossar os eixos ralos.
- Votações em comissão: lá se vota o parecer, e a direção dele não se sabe.
- O peso da autoria × voto quando os dois discordam (o deputado propõe uma coisa e vota outra).
- `lentes.yaml` precisa de revisão: "Direitos humanos" pede "amplia vigilância", provavelmente invertido.
