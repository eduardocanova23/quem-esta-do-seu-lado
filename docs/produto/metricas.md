# Dicionário de métricas

_Todo número exibido no site: nome, definição em uma frase, fórmula, denominador, origem e ressalvas. É o texto de "como calculamos"._

Hoje cobre a pergunta 2. As histórias que usam cada métrica estão em [historias.md](historias.md). Os nomes de tabela são provisórios até o marco `dados.modelo`.

**Versão de 14/11/2026, revisada pelo Eduardo.** O ponto de partida foi o protótipo da v1 (`definitivo/dag_temas/pergunta2.py`, de 03/11/2026). As decisões estão em [Decisões de 14/11/2026](#decisões-de-14112026); as definições de consenso e de divergência só valem depois dos [testes de sensibilidade](#testes-de-sensibilidade) com dado real.

## Regras que valem para todas

- **Uma legislatura e um governo por vez.** Nenhum número junta legislaturas, nem governos dentro da mesma legislatura ([diretriz](diretrizes.md#sempre-separar-legislaturas)). Na 57ª há um governo só; na 55ª, por exemplo, seriam dois (Dilma e Temer), e cada métrica seria calculada separada para cada um.
- **Partido da época.** O partido de um voto é a filiação do deputado na data daquela votação, nunca a atual.
- **A unidade é a votação.** Uma votação conta uma vez por eixo, mesmo que a proposição tenha vários temas. A v1 tinha um arquivo que contava uma vez por tema, e por isso o protótipo mudou a unidade.
- **Todo número mostra o n.** "2 de 2", "7 de 9", nunca só "100%" ou "78%". É o n à vista que deixa mostrar qualquer contagem, por menor que seja.
- **Nenhuma métrica vira nota.** Nada de "bom", "ruim", selo ou cor de semáforo ([não-objetivos](nao-objetivos.md)).
- **Nenhum corte esconde atuação.** Se o deputado votou, o voto aparece e conta, desde o primeiro dia de mandato.
- **Só conta voto dado.** Nenhum placar soma voto que o deputado não deu, seja estimado ou emprestado de partido, bancada ou outro deputado.

## Que votações entram

**Entram:** votações nominais de Plenário, de mérito, de proposições que têm eixo com direção definida (sinal `+` ou `−`). As métricas de governo e oposição usam todas as votações nominais de Plenário com orientação, com ou sem eixo.

**Ficam fora, e "como calculamos" diz isso:**

| O quê | Por quê |
| --- | --- |
| Votação simbólica | Não registra o voto de cada um |
| Urgência | Decide o rito, não o conteúdo |
| Emenda ou substitutivo do Senado | Votar Sim aceita a mudança do Senado, e a direção dela não se sabe |
| Proposição de sinal misto | Puxa o eixo para os dois lados ao mesmo tempo |
| Votação em comissão | Lá se vota o parecer, e a direção dele não se sabe |
| Destaque e emenda de Plenário (687 nominais na 57ª) | Cada destaque precisa da direção do trecho destacado, não da proposição inteira |

Destaques e emendas de Plenário ficam fora da fatia 1. O custo: os eixos ralos (aborto, armas, apostas, LGBT, religião, valores na escola) continuam com 1 ou 2 votações. Trazê-los exige classificar a direção de cada trecho destacado, com gabarito próprio. Voltam por PR se um spike mostrar que dá para fazer isso com acurácia de gabarito; o registro está em [não-objetivos](nao-objetivos.md).

## Métricas da pergunta 2

### Direção do voto

A base de quase tudo. Cada proposição com eixo tem sinal `s`: `+1` se puxa para um polo do eixo e `−1` se puxa para o outro (os polos estão em `eixos.yaml`). Votar **Sim** vale `s`; votar **Não** vale `−s`. Abstenção, obstrução e ausência não têm direção.

- **Origem:** votos, votações, proposição × eixo.
- **Ressalva:** o sinal vem da classificação das proposições, que tem erro medido nos gabaritos. "Como calculamos" mostra a acurácia vigente.
- **Histórias:** H2.1, H3.3.

### Contagem por polo, sem lado escolhido

"Em gasto e benefício, votou 6 vezes por ampliar e 2 por reduzir."

- **Fórmula:** por eixo, `k₊` = votos com direção `+`, `k₋` = votos com direção `−`, `n = k₊ + k₋`.
- **Denominador:** só Sim e Não. Abstenção, obstrução e ausência aparecem à parte.
- **Sem mínimo:** com 1 voto, a frase é "votou 1 vez, por ampliar". O n à vista é o que impede a leitura de "100%".
- **Mostra também:** quantas dessas `n` foram votações de consenso.
- **Histórias:** H2.1, H2.3, H2.4, H2.5.

### Na sua direção, com lado escolhido

"Votou na sua direção em 7 de 9 votações."

- **Fórmula:** `k` = votos cuja direção é o polo escolhido; `n` = votos Sim ou Não no eixo.
- **Sem mínimo,** pelo mesmo motivo: "votou na sua direção em 1 de 1".
- **Calculado no navegador.** O lado escolhido nunca sai dele (H3.6).
- **Histórias:** H3.3, H3.4, H3.7.

### Saldo sobre as votações do eixo, com lado escolhido

"Das 8 votações de punição em que estava no mandato: 2 na sua direção, 0 contra e 6 ausências. Saldo: +2 em 8."

- **Fórmula:** `k` = votos na direção do polo escolhido; `c = n − k` = votos na direção oposta; `T` = votações do eixo em que estava no exercício do mandato, ou seja, `n` + abstenções + obstruções + ausências. Saldo = `(k − c) / T`, de −1 a +1. A tela mostra a conta, "+2 em 8", e não o decimal.
- **Por que dois placares:** "na sua direção" responde "quando vota, vota comigo?"; o saldo responde "posso contar com ele?". Ausência, abstenção e obstrução valem 0: não somam para o seu lado nem contra. Quem falta muito fica perto de zero, longe tanto de quem vota sempre com você quanto de quem vota sempre contra.
- **Aparece sempre ao lado de "na sua direção",** nunca sozinho, com `k`, `c`, as ausências e `T` à vista.
- **Ressalva:** `T` depende da ausência, que ainda é aproximada pela janela de 15 dias ([Ausência](#ausência)). A janela entra no teste de sensibilidade também pelo saldo. Obstrução vale 0 aqui, como nos eixos; se o teste mudar isso nos eixos, muda aqui também.
- **Calculado no navegador** (H3.6).
- **Histórias:** H3.8. Também é a base do ranking da pergunta 3.

### Votação de consenso (no lugar de "quase unânime")

Votação em que os dois lados da Câmara votaram juntos. Conta na contagem do deputado, mas aparece marcada: diz pouco sobre ele e às vezes diz muito sobre o Plenário.

**Definição (confirmada em 14/11/2026, sujeita ao teste de sensibilidade):** uma votação é de consenso quando **o Governo e a Oposição orientaram o mesmo voto** (os dois Sim ou os dois Não).

Por que não um percentual fixo, como os 90% da v1:
- **O tamanho das bancadas distorce o percentual.** 90% do Plenário pode ser só o centro e o governo juntos, com a oposição inteira contra; e uma oposição pequena some num número só.
- **A orientação não depende do tamanho.** Governo e Oposição concordando é um fato publicado pela Câmara, não um corte escolhido por nós.
- **Ela pega o consenso que interessa denunciar.** Quando governo e oposição votam juntos em coisa que beneficia o próprio Congresso (fundo eleitoral, emendas, salário), a marca de consenso deixa isso visível em vez de esconder como "votação que não informa".

O teste compara essa regra com o percentual (80%, 90%, 95%), olhando quais votações mudam de lado e se a diferença é coerente.

- **Correção em relação à v1:** o protótipo media só `Sim / (Sim + Não) ≥ 0,90`, e uma votação com 95% de Não não contava como quase unânime.
- **Histórias:** H2.3.

### Divergência da bancada

"Votou diferente do que a bancada dele orientou em 12 das 80 votações em que ela orientou."

**Definição (revista em 14/11/2026, sujeita ao teste de sensibilidade):** comparar o voto com a **orientação oficial da bancada do deputado** naquela votação, publicada pela Câmara, e não com a maioria calculada dos colegas. A bancada é, nesta ordem:

1. o **partido** da época, se ele orientou em nome próprio naquela votação;
2. senão, a **federação** do partido (PT-PCdoB-PV, PSOL-REDE, PSDB-Cidadania), que funciona como um partido só;
3. senão, o **bloco parlamentar** em que o partido estava naquela votação.

- **Fórmula:** voto e orientação viram dois lados: **a favor** (Sim) e **contra** (Não ou Obstrução). `k` = votos cujo lado é diferente do lado da orientação da bancada; `n` = votos Sim, Não ou Obstrução em votações em que a bancada orientou Sim, Não ou Obstrução. "Liberado" e "sem orientação" não contam, nem abstenção e ausência. Deputado sem partido não tem bancada e fica fora.
- **Por que obstrução é contra:** obstruir é tentar derrubar a votação tirando o quórum, uma oposição mais forte que votar Não. Bancada que orienta obstrução e deputado que vota Sim divergem; bancada que orienta Sim e deputado que obstrui também. Obstruir quando a bancada orientou Não, ou votar Não quando ela orientou obstrução, é seguir a bancada. A frase da página diz qual foi o voto e qual a orientação, sem juntar os dois sob "Não".
- **Por que a bancada e não só o partido:** no Plenário da 57ª, quem orienta é quase sempre o bloco. Em 2025, de 419 votações com orientação, PP, PSD, MDB, União e Republicanos orientaram em nome próprio em 1 cada. Comparar só com o partido deixaria metade da Câmara sem divergência nenhuma, por falta de orientação e não por fidelidade.
- **Por que não a maioria dos colegas:** a maioria calculada exige um corte (a v1 usava 60%), e o resultado pode mudar muito com o corte. A orientação é um fato publicado, sem corte nenhum.
- **De onde vem o bloco de cada votação:** a Câmara não publica a composição dos blocos com data. Ela é reconstruída por regra: a sigla do bloco presente na votação diz qual composição valia, e os partidos escondidos nas reticências da sigla saem por eliminação, porque partido de bloco não orienta sozinho. A regra reproduz as composições que a API publica. Detalhe e resíduo em [`docs/dados/atualizacao.md`](../dados/atualizacao.md#em-aberto).
- **Ressalva:** divergir de um bloco grande diz menos que divergir do próprio partido, porque o bloco junta partidos que discordam entre si. A página sempre nomeia quem orientou ("o bloco de União, PP, PSD, Republicanos, MDB, PSDB-Cidadania e Podemos orientou Não"), nunca só "o partido".
- **Na lista de votações (H2.2)** a página mostra também como os colegas de partido votaram de fato ("o bloco orientou Não; 70% dos colegas do PSD votaram Não"), sem corte.
- **Correção em relação à v1:** o protótipo contava o próprio deputado na maioria. Num partido de 3, o voto dele decidia a maioria contra a qual ele era comparado.
- **Ressalva:** divergir não é bom nem ruim. A página mostra cada votação.
- **Histórias:** H4.1 a H4.5.

### Ausência

Não votou numa votação em que estava no exercício do mandato.

- **Fórmula (aproximação da v1):** o deputado não votou, mas votou em alguma votação nominal até **15 dias** antes ou depois. A janela separa a falta de quem estava de licença ou ainda não tinha assumido.
- **Ressalva:** a Câmara não publica a presença junto com os votos. A frente de dados verifica se dá para usar o período de exercício do mandato (titular, suplente, licença), que trocaria a aproximação por um dado. A janela de 15 dias entra no teste de sensibilidade enquanto for aproximação.
- **Histórias:** H2.4.

### Obstrução

Registrou "Obstrução" em vez de votar. É uma tática para impedir que a votação tenha quórum.

- **Aparece à parte, com o nome "obstrução"**, ao lado das abstenções e das ausências: "votou 6 vezes por ampliar, 2 por reduzir e obstruiu 1".
- **Não conta como Não** nem como ausência. Quem obstrui quase sempre quer derrubar a proposta, mas às vezes a obstrução é contra a pauta do dia, não contra o conteúdo (a oposição obstrui tudo para travar o Plenário). Por isso, nos eixos, ela fica à parte até o teste de sensibilidade medir quanto muda se contar como Não. Na divergência ela conta como voto contra (ver [Divergência da bancada](#divergência-da-bancada)).
- **"Como calculamos" explica a tática** no lugar em que ela aparece (H6.4).
- **Histórias:** H2.4.

### Autoria por tema

"Onde ele atua": em que temas ele propõe, comparado com a média.

- **Fórmula:** por tema, o número de proposições em que ele é autor principal e, separado, coautor. A comparação é com a média de proposições por deputado naquele tema, na mesma legislatura.
- **Ressalva fixa na página:** propor é barato e muita proposição é simbólica. A autoria mostra prioridade, e o voto mostra posição.
- **Nunca entra** no "na sua direção" (H5.4).
- **Histórias:** H5.1 a H5.5.

### Alinhamento com o governo e com a oposição

"Votou como o Governo orientou em 210 das 260 votações em que o Governo orientou Sim ou Não."

- **Fórmula:** `k` = votos Sim ou Não iguais à orientação do Governo; `n` = votações em que ele votou Sim ou Não e o Governo orientou Sim ou Não. A mesma conta vale para a Oposição.
- **Entram** todas as votações nominais de Plenário com orientação, não só as que têm eixo.
- **A página nomeia o governo e a legislatura** e nunca compara com outro governo.
- **Origem:** orientações das votações (a v1 coletava em `votacoesOrientacoes`).
- **Histórias:** H8.1, H8.2.

### Votações de conflito: o assunto contra o lado

"Em 5 votações em que a Oposição orientou o contrário do que ele costuma votar em punição, ele seguiu a Oposição em 4."

1. **Tendência do deputado num eixo:** o polo em que ele mais votou. Com empate, não há tendência e o eixo não tem votações de conflito.
2. **Lado do deputado:** base, se o alinhamento com o Governo na legislatura passa de 50%; oposição, se não passa.
3. **Votação de conflito:** uma votação do eixo em que a orientação do lado dele (Governo para a base, Oposição para a oposição) aponta contra a tendência dele.
4. **Contagem:** nas votações de conflito, quantas vezes ele seguiu a tendência e quantas seguiu o lado.

- **A tendência vem do voto, não do que ele declara.** A página diz isso.
- **A tendência inclui a própria votação de conflito.** O teste de sensibilidade compara com a tendência calculada sem ela.
- **Sem mínimo, mas com o n à vista.** Muitos deputados vão ter 0, 1 ou 2 votações de conflito. Com 0, a frase é "nenhuma votação em que o lado dele e o que ele costuma votar se opuseram".
- **Sem nota de coerência.** A página mostra cada votação: a tendência, a orientação do lado, a da bancada e o voto.
- **Histórias:** H8.3, H8.4.

### Fora: escala ideológica

Uma escala esquerda × direita calculada pelos votos seria um rótulo político sobre o deputado e esbarra no não-objetivo de "nota ou selo". Os eixos dizem a direção assunto por assunto, e as votações de conflito mostram quando o lado pesou mais que o assunto.

## Testes de sensibilidade

Regra: **um corte só vale se mudá-lo um pouco não muda muito o resultado.** Se mudar, a métrica troca de definição em vez de escolher um número.

O teste roda com dado real, antes da metodologia ser assinada (marco `analise.metodologia1`), e o resultado entra na página de metodologia:

| O quê | Variações | O que se mede |
| --- | --- | --- |
| Consenso | Governo e Oposição iguais; 80%, 90%, 95% do Plenário | Quantas votações mudam de classe e quais |
| Divergência | Orientação da bancada; só orientação própria do partido; obstrução como contra ou fora da conta; maioria dos colegas a 50%, 60%, 70%, 80% | Quantos deputados mudam de posição no total de divergências (correlação de postos) e quantos ficam sem nenhuma votação com orientação |
| Obstrução nos eixos | À parte; como Não (direção `−s`) | Quantos deputados mudam de polo dominante em algum eixo e em quantas votações a obstrução foi da bancada inteira no mesmo dia |
| Lado (base ou oposição) | 40%, 50%, 60% de alinhamento com o Governo | Quantos deputados mudam de lado |
| Tendência no eixo | Com e sem a votação de conflito | Quantas votações de conflito mudam |
| Ausência | Janela de 7, 15 e 30 dias | Quantas ausências mudam e quantos deputados mudam de saldo |

Se a variação mudar a posição de muitos deputados, a página não publica o número resumido daquela métrica, só o voto a voto, até haver outra definição.

## Decisões de 14/11/2026

1. **Destaques e emendas de Plenário:** fora da fatia 1, com volta por spike.
2. **Sem n mínimo:** todo voto aparece e conta, com o n à vista. Atuação é atuação, inclusive no começo do mandato.
3. **Consenso e divergência:** sem percentual fixo escolhido no escuro. Consenso é Governo e Oposição orientando igual; divergência é votar contra a orientação oficial da bancada (partido, federação ou bloco, nessa ordem; revisto no mesmo dia, depois de ver que os partidos de bloco quase nunca orientam sozinhos). As duas passam pelo teste de sensibilidade antes de valer.
4. **Obstrução:** à parte, com nome próprio.
5. **Governo e oposição:** alinhamento e votações de conflito entram na fatia 1 (história H8). Depois do teste com 5 pessoas, revê-se se a página ficou poluída ou se diz pouco.
