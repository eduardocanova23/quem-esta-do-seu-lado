# Histórias de usuário

_Uma história por necessidade de um perfil, ligada a uma pergunta, com critérios de aceitação testáveis. Cada critério diz a camada de teste que o cobre._

Cadeia: [pergunta](perguntas.md) → história → critério → teste → tela. Os perfis estão em [personas.md](personas.md). Os números de corte (n mínimo, quase unânime, maioria do partido, janela de ausência) ficam em [metricas.md](metricas.md); aqui eles aparecem só pelo nome.

As histórias seguem a ordem das fatias. Hoje só a pergunta 2 tem histórias, porque é a fatia 1. As perguntas 3 e 1 ganham histórias quando a fatia delas abrir.

## Camadas de teste

Cada critério leva uma etiqueta com a camada que o testa e quando esse teste entra ([método, Testes por camada](../metodo.md#testes-por-camada)):

| Etiqueta | O que testa | Quando entra |
| --- | --- | --- |
| `métrica` | O número, recalculado à mão num caso pequeno (pytest) | Agora |
| `build` | O que o gerador de páginas produz a partir dos marts: rotas, listas, links (pytest ou Vitest) | Agora |
| `site` | Lógica no navegador: frases, filtros, placar do lado escolhido (Vitest) | Agora |
| `fumaça` | As páginas da fatia abrem no build com dado real (Playwright, um teste) | Agora |
| `e2e` | O fluxo num navegador de verdade (Playwright) | Fase 5 |

O que só o `e2e` cobre é conferido à mão antes do lançamento da fatia 1 e vira teste automático na Fase 5.

## Decisões da pergunta 2

Tomadas em 12/11/2026, na escrita destas histórias:

1. **A página abre neutra e o lado vem depois, opcional.** O eleitor curioso desiste quando o site pede escolhas antes de mostrar algo. O protótipo da v1 pedia o lado primeiro.
2. **O lado é escolhido eixo a eixo, sem perfil pronto.** As lentes da v1 são personas de classificação, e publicá-las como produto misturaria as duas camadas, além de soar como rótulo político.
3. **A autoria é neutra: "onde ele atua".** Sem persona, não existem "os seus temas" para personalizar.
4. **O link compartilhado nunca leva o lado.** O sentido político não é guardado em lugar nenhum, nem num link que circula.

## Página inicial e busca

Serve às três perguntas: é por onde a pessoa chega a um deputado (pergunta 2), a um partido (pergunta 3) ou a um tema (pergunta 1).

### H0. Achar qualquer coisa numa caixa só

> *Como qualquer pessoa que chega ao site, quero digitar o que tenho na cabeça (um nome, um partido, um assunto, um apelido de lei) e cair na página certa.*

Perfis: todos. Quem acompanha uma causa ● (chega pelo assunto), eleitor curioso ● (chega pelo nome).

- **H0.1** A página inicial tem quase nada além de uma caixa de texto grande no centro, com o convite "Digite um deputado, um partido ou um assunto". Em cima, quatro abas: Principal, Temas, Deputados, Partidos. `fumaça`
- **H0.2** A caixa acha deputado pelo nome civil ou parlamentar, sem diferenciar acento nem maiúscula e tolerando erro de digitação. `site`
- **H0.3** A caixa acha partido pela sigla e pelo nome. `site`
- **H0.4** A caixa acha tema por busca híbrida (significado + palavra exata), a que venceu o teste de busca de 03/11/2026, incluindo apelidos populares: "saidinha", "6x1", "bets", "jogo do tigrinho". `e2e` e o conjunto de teste de busca da v1 acima do limiar
- **H0.5** A caixa acha proposição pela sigla e número ("PL 1234/2023") e pelo apelido ("marco temporal"). `site` para a sigla; apelido junto com H0.4
- **H0.6** Os resultados vêm agrupados por tipo (deputados, partidos, temas, proposições). Deputado aparece com partido da época e UF. Clicar leva à página daquele resultado. `site`
- **H0.7** A busca nunca termina vazia: sem resultado, a página diz o que a caixa procura, mostra exemplos clicáveis e oferece a lista de deputados. `site`
- **H0.8** Busca sem resultado é guardada sem identificar quem buscou (sem IP, sem cookie), para virar apelido novo ou tema que falta. `e2e`
- **H0.9** No celular, a caixa ocupa a largura da tela e abre o teclado com um toque. `e2e`

**Ordem de entrada.** A caixa acha tudo desde a primeira publicação (decisão de 13/11/2026): H0.1 a H0.9 entram juntas. Por isso o marco `site.busca` vem antes de `site.fatia1`, com um servidor de busca e a taxonomia que se atualiza sozinha já prontos. As abas Temas e Partidos levam a páginas que chegam com as perguntas 1 e 3; até lá, o que a primeira publicação mostra ao clicar num tema ou num partido é decidido nos wireframes.

## Pergunta 2: este deputado está do meu lado?

### H1. Achar o deputado

> *Como eleitor curioso que recebeu um nome, quero chegar à página do deputado sem saber o nome completo nem o partido.*

Perfis: eleitor curioso ●, jornalista ○.

- **H1.1** Cada deputado tem uma página por legislatura, num endereço estável que inclui a legislatura. Quem exerceu mandato em duas legislaturas tem duas páginas, ligadas entre si e sem número que compare uma com a outra. `build`
- **H1.2** A lista de deputados filtra por nome civil ou parlamentar, sem diferenciar acento nem maiúscula, e por partido e UF. `site`
- **H1.3** O partido mostrado é o da época. O cabeçalho mostra a filiação na legislatura e, se ela mudou, cada troca com a data. `métrica`
- **H1.4** A condição na legislatura (titular, suplente ou efetivado) aparece no cabeçalho. `build`
- **H1.5** Um endereço de deputado que não existe responde 404, com link para a lista. `e2e`

### H2. Ver como ele vota, sem escolher nada antes

> *Como eleitor que chegou pelo link de um deputado, quero ver como ele vota nos grandes assuntos antes de precisar escolher qualquer coisa.*

Perfis: eleitor curioso ●, quem acompanha uma causa ●.

- **H2.1** A página abre sem pedir escolha. Para cada um dos cinco eixos com volume (gasto e benefício, carga tributária, punição, ambiente, trabalho), mostra quantas vezes ele votou em cada polo, com os polos em linguagem comum: "em gasto e benefício, votou 6 vezes por ampliar e 2 por reduzir". `métrica`
- **H2.2** Cada contagem abre a lista das votações, com data, o que a proposição faz em linguagem comum, o voto dele, a maioria do partido dele e o link para a votação no site da Câmara. `build`
- **H2.3** Votações quase unânimes entram na contagem, mas aparecem separadas: "2 delas quase unânimes". `métrica`
- **H2.4** Abstenção, obstrução e ausência ficam fora das contagens e aparecem à parte, com a definição de ausência ao lado. `métrica`
- **H2.5** Num eixo com menos votações que o mínimo, não há contagem resumida. Aparece a frase "só 2 votações neste eixo: não dá para dizer como ele vota" e a lista das votações. `site`
- **H2.6** Entram só votações nominais de mérito no Plenário, de proposições com eixo. O que fica de fora (urgência, emenda do Senado, proposição de sinal misto) está escrito em "como calculamos". `métrica`
- **H2.7** Nenhuma frase avalia o deputado ("bom", "ruim", nota). O mesmo modelo de frase vale para todo partido. `site`

### H3. Comparar com o que eu quero

> *Como quem já viu como o deputado vota, quero dizer o que eu quero em cada eixo e saber se ele vota na minha direção.*

Perfis: eleitor curioso ●, quem acompanha uma causa ●.

- **H3.1** "Compare com o que você quer" vem depois do resumo neutro. Abrir a comparação não esconde o resumo. `e2e`
- **H3.2** Cada eixo oferece os dois polos em linguagem comum e "não me importa", que é a opção inicial. `site`
- **H3.3** Com um polo escolhido e o n do eixo no mínimo ou acima, a página diz "votou na sua direção em 7 de 9 votações" e marca cada votação da lista como na sua direção ou contra. `métrica` para o k e o n, `site` para a frase.
- **H3.4** Abaixo do mínimo, só as votações marcadas aparecem, sem número resumido. `site`
- **H3.5** Sem nenhum eixo escolhido, não aparece placar. `site`
- **H3.6** O lado escolhido nunca sai do navegador: nenhuma requisição o carrega, e ele não vai para cookie, `localStorage`, endereço da página nem métrica de acesso. Fechar a página apaga a escolha. `site` e `e2e`
- **H3.7** A pergunta 2 mostra o placar cru (k de n) com o n à vista. O placar ajustado, puxado para o partido, é ferramenta de ranking da pergunta 3 e não aparece aqui. `site`

### H4. Ver quando ele foge da bancada

> *Como jornalista, quero ver as votações em que o deputado votou diferente do partido, porque é isso que fala dele e não do partido.*

Perfis: jornalista ●, quem acompanha uma causa ○.

- **H4.1** A página lista as votações com eixo em que o voto dele foi diferente da maioria do partido, mostrando a maioria e o tamanho dela. `métrica`
- **H4.2** O partido de cada votação é a filiação dele na data daquela votação. `métrica`
- **H4.3** Votação em que o partido não teve maioria clara não conta como divergência. `métrica`
- **H4.4** O total de divergências aparece perto do topo da página, ao lado do total de votações com eixo. `site`
- **H4.5** Sem nenhuma divergência, a frase é "votou com a maioria do partido em todas as N votações com eixo". `site`

### H5. Ver onde ele atua

> *Como eleitor curioso, quero saber em que assuntos o deputado mais propõe, sem confundir proposta com posição.*

Perfis: eleitor curioso ○, jornalista ○, estudante ○.

- **H5.1** A página mostra os temas em que ele é autor ou coautor, com a contagem de cada um e a comparação com a média dos deputados da mesma legislatura. `métrica`
- **H5.2** Autor principal e coautor aparecem separados. `métrica`
- **H5.3** Um aviso fixo diz que propor é barato e que muita proposição é simbólica: a autoria mostra prioridade, e o voto mostra posição. `site`
- **H5.4** A autoria nunca entra no "votou na sua direção". `métrica`
- **H5.5** Os temas usam os nomes da taxonomia vigente, ligados por id estável. `build`

### H6. Confiar no número

> *Como jornalista que vai citar o número, quero saber como ele foi calculado, de quando é o dado e onde está a fonte.*

Perfis: jornalista ●, estudante ○.

- **H6.1** Todo número da página tem um "como calculamos" que leva à seção daquela métrica na página de metodologia. O build falha se uma métrica exibida não tem seção. `build`
- **H6.2** Toda página mostra a legislatura e "dados até DD/MM/AAAA". `fumaça`
- **H6.3** Toda votação e toda proposição listadas têm link para a página oficial na Câmara. `build`
- **H6.4** Votação nominal, orientação de bancada, obstrução e votação de mérito são explicadas no primeiro lugar em que aparecem na página, sem mandar para outra página. `e2e`

### H7. Compartilhar

> *Como eleitor curioso, quero mandar a página do deputado para o grupo da família.*

Perfis: eleitor curioso ●.

- **H7.1** O endereço da página é o mesmo para todo mundo e não muda quando a pessoa escolhe um lado. `e2e`
- **H7.2** A prévia do link no WhatsApp traz o nome, o partido da época, a legislatura e uma frase neutra. Ela é gerada no build. `build`
- **H7.3** O botão de compartilhar usa o compartilhamento do celular, e o texto enviado não leva o lado. `site`
