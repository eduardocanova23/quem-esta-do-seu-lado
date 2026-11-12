# Perfis de uso

_Os quatro perfis de quem usa o site: como chegam, o que perguntam e do que precisam para confiar na resposta. Eles decidem telas, histórias e critérios de aceitação._

Origem: tabela de perfis de [docs/metodo.md](../metodo.md#requisitos-da-pergunta-à-tela). As perguntas centrais estão em [perguntas.md](perguntas.md).

## Perfil de uso não é persona de classificação

São duas coisas com nomes parecidos e papéis opostos:

| | Perfis de uso (este arquivo) | Personas de classificação |
| --- | --- | --- |
| Descrevem | como a pessoa chega e do que precisa | quem a pessoa é e o que ela busca |
| Quantos | 4 | 58: 38 originais e dois conjuntos independentes de 10 |
| Decidem | telas, histórias, critérios de aceitação | temas, eixos, nomes de nó, limiares ([diretrizes](diretrizes.md#personas-são-o-critério-central)) |
| Mudam | por PR de produto | as 38, só por PR de taxonomia com placar; as 20 independentes nunca: estão congeladas com SHA256 |

Os dois eixos se cruzam. A Mãe de autista (persona de classificação) pode chegar como eleitora curiosa, por um link no WhatsApp com o nome de um deputado, ou como quem acompanha uma causa, buscando "terapia ABA plano de saúde". Os exemplos abaixo usam personas de classificação para mostrar esse cruzamento.

As 58 ainda estão no repositório da v1 (`CAPIVARA`) e vão para `avaliacao/` na frente taxonomia:

- 38 originais, com 161 buscas: `scripts/testar_personas_arvore.py` (lista `PERSONAS`); polos por eixo em `definitivo/dag_temas/out/lentes.yaml`.
- Independente 1, com 150 interesses: `definitivo/dag_temas/eval/independente/personas.json` e `SHA256` (commit `af56a5a`).
- Independente 2: `definitivo/dag_temas/eval/independente2/personas.json` e `SHA256`.

## Resumo

| Perfil | Como chega | Quer saber | Precisa de | Perguntas |
| --- | --- | --- | --- | --- |
| Eleitor curioso | Google ou link no WhatsApp, pelo celular | O que o deputado X fez e defende | Resposta em uma frase, sem jargão, fácil de compartilhar | **2**, 3 |
| Quem acompanha uma causa | Busca por tema ("saidinha", "agrotóxico") | O que tramita sobre aquilo e quem é a favor ou contra | Busca boa, proposições do tema, placar por eixo | **2**, **3**, **1** |
| Jornalista ou pesquisador | Volta sempre, busca direta | Números confiáveis e comparáveis | Metodologia, data de atualização, o n de cada número, exportação | 2, **3**, **1** |
| Estudante ou professor | Link de aula ou de trabalho | Como a Câmara funciona | Glossário embutido, o processo explicado | 2, 3, **1** |

Em negrito, as perguntas em que o perfil é público principal. A matriz completa está [no fim](#matriz-perfil--pergunta).

## Eleitor curioso

- **Contexto:** celular, visita única de poucos minutos. Chega com o nome de um deputado, por link ou pelo Google. Não conhece o regimento nem a sigla de tipo de proposição.
- **Pergunta:**
  - "O deputado em quem eu votei faz o quê?" → 2
  - "Ele é a favor ou contra [assunto]?" → 2
  - "Ele está entre os que mais concordam comigo?" → 3
- **Confia quando:**
  - a resposta vem em uma frase antes de qualquer gráfico;
  - o n aparece em palavras: "em punição, votou na sua direção em 7 de 9 votações";
  - a legislatura e o partido da época ficam claros;
  - escolhe o lado na hora, sem cadastro, e esse lado nunca é guardado.
- **Desiste quando:** encontra jargão (PL, PEC, destaque, requerimento), quando o site pede para escolher muitos eixos antes de mostrar qualquer coisa ou quando vê um número sem explicação.
- **Exemplo:** a Usuária de ônibus recebe no grupo da família o link de um deputado e quer saber se ele "presta".

## Quem acompanha uma causa

- **Contexto:** chega por busca de tema, quase sempre pelo nome popular. Volta quando o assunto esquenta. Usa celular ou computador.
- **Pergunta:**
  - "O que tramita sobre [tema]?" → 1
  - "Esse assunto anda ou está parado?" → 1
  - "Quem é a favor e quem é contra [tema]?" → 3
  - "O meu deputado votou como eu queria em [tema]?" → 2
- **Buscas do teste de personas:**
  - Trabalhador 6x1: "fim da escala 6x1", "redução da jornada de trabalho";
  - Punitivista: "fim da saidinha", "redução da maioridade penal";
  - Preocupado com bets: "apostas online bets", "jogo do tigrinho";
  - Cabeleireira MEI: "MEI limite de faturamento".
- **Confia quando:**
  - a busca entende o nome popular;
  - as votações concretas aparecem ao lado de qualquer placar;
  - o eixo com poucas votações mostra o voto a voto em vez de um placar.
- **Desiste quando:**
  - um apelido não traz nada na busca;
  - o site mostra "vota contra o tema X" sem as votações;
  - o site chama um tema de "abandonado" sem dizer que só cerca de 4% das proposições chegam ao Plenário.

## Jornalista ou pesquisador

- **Contexto:** computador. Volta sempre e busca direto um deputado, um partido ou uma proposição. Vai citar o número numa matéria ou num artigo.
- **Pergunta:**
  - "Quantas vezes X votou diferente da bancada?" → 2
  - "Quais partidos votam mais juntos em [eixo]?" → 3
  - "Quais temas têm a menor taxa de avanço nesta legislatura?" → 1
  - "Como esse número foi calculado e de quando é o dado?" → todas
- **Confia quando:**
  - todo número tem "como calculamos" ([metricas.md](metricas.md));
  - aparecem a data de atualização, o n, a legislatura e o link para a fonte na Câmara;
  - o endereço é estável e dá para citar.
- **Desiste quando:** um número muda sem aviso, quando o ranking não tem n mínimo ou quando vê uma comparação entre legislaturas, que é proibida.
- **Exemplo:** o caso de 03/11 em [perguntas.md](perguntas.md): "Kim Kataguiri divergiu do partido 30 vezes" é o tipo de frase que vira manchete e por isso precisa de fonte e n.

## Estudante ou professor

- **Contexto:** chega por link de aula ou de trabalho, no computador da escola ou no celular. Quer entender o processo antes do resultado.
- **Pergunta:**
  - "Por que tanto projeto fica parado?" → 1
  - "Como um projeto vira lei?" → 1, como contexto
  - "O que é orientação de bancada, e por que o voto segue o partido?" → 2 e 3
- **Confia quando:** o termo é explicado no lugar em que aparece e o processo é mostrado com um caso real.
- **Desiste quando:** o glossário fica numa página separada, longe do texto, ou quando o tom é de militância.
- **Exemplo:** a Professora da rede pública prepara uma aula sobre o Fundeb e usa a página da proposição para mostrar a tramitação.
- **Atenção:** "como a Câmara funciona" não é uma das três perguntas. Este perfil é atendido dentro delas, com glossário e explicações no lugar. Uma página própria sobre o processo legislativo é candidata a [não-objetivo](nao-objetivos.md).

## Matriz perfil × pergunta

● público principal · ○ também usa

| Perfil | 2. Deputado do meu lado (MVP) | 3. Aliado × inimigo | 1. Priorizados × abandonados |
| --- | --- | --- | --- |
| Eleitor curioso | ● | ○ | |
| Quem acompanha uma causa | ● | ● | ● |
| Jornalista ou pesquisador | ○ | ● | ● |
| Estudante ou professor | ○ | ○ | ● |

Consequência para o MVP: a pergunta 2 é desenhada primeiro para o eleitor curioso e para quem acompanha uma causa. Isso quer dizer celular primeiro, uma frase antes do número e o lado escolhido na hora. O que o jornalista precisa e o eleitor não vê (exportação, por exemplo) é registrado aqui, mas a entrada no MVP é decidida em [historias.md](historias.md) e [nao-objetivos.md](nao-objetivos.md).

## Limites deste arquivo

- As perguntas entre aspas na voz de cada perfil são hipóteses escritas em 12/11/2026, sem pesquisa com usuário. Elas são validadas com as 5 pessoas do marco `design.tokens`.
- As buscas citadas vêm do teste de personas. Também não foram feitas por gente real: as originais foram escritas numa sessão com o Claude, e as dos conjuntos independentes, pelo Haiku.
