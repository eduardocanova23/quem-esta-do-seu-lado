# Dicionário de métricas

_Todo número exibido no site: nome, definição em uma frase, fórmula, denominador, origem e ressalvas. É o texto de "como calculamos"._

Hoje cobre a pergunta 2. As histórias que usam cada métrica estão em [historias.md](historias.md). Os nomes de tabela são provisórios até o marco `dados.modelo`.

**Rascunho de 14/11/2026.** Os valores de corte vêm do protótipo da v1 (`definitivo/dag_temas/pergunta2.py`, de 03/11/2026). Os pontos marcados **Decidir** esperam o Eduardo.

## Regras que valem para todas

- **Uma legislatura e um governo por vez.** Nenhum número junta legislaturas, nem governos dentro da mesma legislatura ([diretriz](diretrizes.md#sempre-separar-legislaturas)). Na 57ª há um governo só; na 55ª, por exemplo, seriam dois (Dilma e Temer), e cada métrica seria calculada separada para cada um.
- **Partido da época.** O partido de um voto é a filiação do deputado na data daquela votação, nunca a atual.
- **A unidade é a votação.** Uma votação conta uma vez por eixo, mesmo que a proposição tenha vários temas. A v1 tinha um arquivo que contava uma vez por tema, e por isso o protótipo mudou a unidade.
- **Todo número mostra o n.** "7 de 9", nunca só "78%".
- **Nenhuma métrica vira nota.** Nada de "bom", "ruim", selo ou cor de semáforo ([não-objetivos](nao-objetivos.md)).

## Que votações entram

**Entram:** votações nominais de Plenário, de mérito, de proposições que têm eixo com direção definida (sinal `+` ou `−`).

**Ficam fora, e "como calculamos" diz isso:**

| O quê | Por quê |
| --- | --- |
| Votação simbólica | Não registra o voto de cada um |
| Urgência | Decide o rito, não o conteúdo |
| Emenda ou substitutivo do Senado | Votar Sim aceita a mudança do Senado, e a direção dela não se sabe |
| Proposição de sinal misto | Puxa o eixo para os dois lados ao mesmo tempo |
| Votação em comissão | Lá se vota o parecer, e a direção dele não se sabe |
| Destaque e emenda de Plenário (687 nominais na 57ª) | **Decidir 1** |

**Decidir 1: destaques e emendas de Plenário.**
- *Deixar fora (como na v1).* Mais simples e sem risco de errar a direção. Os eixos ralos (aborto, armas, apostas, LGBT, religião, valores na escola) continuam com 1 ou 2 votações e sem resumo.
- *Trazer para dentro.* Engrossa os eixos ralos, mas cada destaque precisa da direção do trecho destacado, não da proposição inteira. Isso é mais um passo de classificação, com gabarito próprio.
- *Recomendação:* fora na fatia 1, e um spike para medir quantos destaques ganhariam direção confiável. Volta por PR se o spike mostrar que vale.

## Métricas da pergunta 2

### Direção do voto

A base de quase tudo. Cada proposição com eixo tem sinal `s`: `+1` se puxa para um polo do eixo e `−1` se puxa para o outro (os polos estão em `eixos.yaml`). Votar **Sim** vale `s`; votar **Não** vale `−s`. Abstenção, obstrução e ausência não têm direção.

- **Origem:** votos, votações, proposição × eixo.
- **Ressalva:** o sinal vem da classificação das proposições, que tem erro medido nos gabaritos. "Como calculamos" mostra a acurácia vigente.
- **Histórias:** H2.1, H3.3.

### Contagem por polo (k de n), sem lado escolhido

"Em gasto e benefício, votou 6 vezes por ampliar e 2 por reduzir."

- **Fórmula:** por eixo, `k₊` = votos com direção `+`, `k₋` = votos com direção `−`, `n = k₊ + k₋`.
- **Denominador:** só Sim e Não. Abstenção, obstrução e ausência aparecem à parte.
- **Mostra também:** quantas dessas `n` foram quase unânimes.
- **Histórias:** H2.1, H2.3, H2.4.

### Na sua direção (k de n), com lado escolhido

"Votou na sua direção em 7 de 9 votações."

- **Fórmula:** `k` = votos cuja direção é o polo escolhido; `n` = votos Sim ou Não no eixo.
- **Calculado no navegador.** O lado escolhido nunca sai dele (H3.6).
- **Histórias:** H3.3, H3.4.

### n mínimo

Abaixo dele, o eixo não ganha número resumido, só o voto a voto.

- **Corte proposto:** `n ≥ 5` votos Sim ou Não do deputado no eixo (v1: `N_POUCO = 5`).
- **Por quê 5:** com 4 votos, um voto a mais ou a menos muda o resultado em 25 pontos. **Decidir 2** (abaixo).
- **Histórias:** H2.5, H3.4.

### Quase unânime

Votação em que quase todo o Plenário votou igual. Conta na contagem, mas aparece separada, porque diz pouco sobre a pessoa.

- **Fórmula:** `max(Sim, Não) / (Sim + Não) ≥ 0,90`.
- **Correção em relação à v1:** o protótipo media só `Sim / (Sim + Não) ≥ 0,90`. Uma votação com 95% de Não não contava como quase unânime. A fórmula acima corrige isso.
- **Origem:** os próprios votos. Na v1, os totais da tabela de votações vinham como texto e às vezes zerados.
- **Histórias:** H2.3.

### Maioria do partido

O que conta como "o partido votou assim" numa votação.

- **Fórmula:** entre os **colegas** do mesmo partido (sem o próprio deputado) que votaram Sim ou Não, o voto mais comum, se tiver `≥ 60%`. Abaixo disso, o partido "não teve maioria clara".
- **Correção em relação à v1:** o protótipo contava o próprio deputado na maioria. Num partido de 3 deputados, o voto dele decidia a maioria contra a qual ele era comparado. O ranking da v1 já tirava o próprio deputado; aqui também.
- **Partido pequeno:** com menos de 3 colegas votando Sim ou Não, não há maioria. **Decidir 2** (abaixo).
- **Histórias:** H2.2, H4.1, H4.3.

### Divergência da bancada

"Votou diferente da maioria do partido em 12 das 80 votações com eixo."

- **Fórmula:** `k` = votos Sim ou Não diferentes da maioria do partido; `n` = votos Sim ou Não em votações em que o partido teve maioria clara.
- **Ressalva:** divergir não é bom nem ruim. A página mostra cada votação, com a maioria e o tamanho dela.
- **Histórias:** H4.1 a H4.5.

### Ausência

Não votou numa votação em que estava no exercício do mandato.

- **Fórmula (aproximação da v1):** o deputado não votou, mas votou em alguma votação nominal até **15 dias** antes ou depois. A janela separa a falta de quem estava de licença ou ainda não tinha assumido.
- **Ressalva:** a Câmara não publica a presença junto com os votos. A frente de dados verifica se dá para usar o período de exercício do mandato (titular, suplente, licença), que trocaria a aproximação por um dado.
- **Abstenção e obstrução** aparecem à parte, com nome próprio. **Decidir 3** (abaixo).
- **Histórias:** H2.4.

### Autoria por tema

"Onde ele atua": em que temas ele propõe, comparado com a média.

- **Fórmula:** por tema, o número de proposições em que ele é autor principal e, separado, coautor. A comparação é com a média de proposições por deputado naquele tema, na mesma legislatura.
- **Ressalva fixa na página:** propor é barato e muita proposição é simbólica. A autoria mostra prioridade, e o voto mostra posição.
- **Nunca entra** no "na sua direção" (H5.4).
- **Histórias:** H5.1 a H5.5.

### Placar ajustado

Não aparece na pergunta 2 (H3.7). Fica registrado para a pergunta 3: `(k + m·p) / (n + m)`, com `p` = taxa dos colegas de partido no eixo e `m = 5`. Com poucos votos, o deputado fica perto do partido até a evidência dizer o contrário.

## Proposta: governo e oposição

_Não está nas histórias ainda. Se o Eduardo aprovar, vira a história H8 e entra nesta seção como as outras._

A pergunta por trás: **ele vota pelo assunto ou pela briga entre governo e oposição?** Um deputado pode votar contra algo que sempre defendeu porque a proposta é do governo, ou o contrário.

Os dados permitem medir isso. Em cada votação, a Câmara publica a orientação do Governo e a da Oposição (Sim, Não, Liberado ou sem orientação). A v1 já coletava isso para montar o gabarito.

### Alinhamento com o governo

"Votou com a orientação do Governo em 210 das 260 votações em que o Governo orientou."

- **Fórmula:** `k` = votos Sim ou Não iguais à orientação do Governo; `n` = votações em que ele votou Sim ou Não e o Governo orientou Sim ou Não. A mesma conta vale para a Oposição.
- **Entram** todas as votações nominais de Plenário com orientação, não só as que têm eixo: aqui o assunto não importa.
- **A página nomeia o governo e a legislatura.** Nunca compara com outro governo.

### Quando o assunto e o lado puxam para direções opostas

É o caso que você descreveu. Dá para medir assim:

1. Num eixo com `n ≥` mínimo, a **tendência** do deputado é o polo em que ele vota mais (por exemplo, 8 de 10 por "endurecer punição").
2. Uma votação desse eixo é **de conflito** quando a orientação do Governo (para quem é da base) ou da Oposição (para quem é da oposição) aponta contra essa tendência.
3. Nas votações de conflito, a página conta quantas vezes ele seguiu a própria tendência e quantas seguiu o lado: "Em 5 votações em que a orientação da Oposição ia contra o que ele costuma votar em punição, ele seguiu a Oposição em 4."

Cuidados:
- **A tendência vem do próprio voto, não do que ele declara.** É a melhor aproximação sem discurso, e a página diz isso.
- **"Base" e "oposição" precisam de definição.** Proposta: pelo alinhamento de cada um com o Governo em toda a legislatura, acima ou abaixo de 50%. Outra opção é a posição oficial do partido, que muda no meio do mandato e é mais difícil de datar.
- **Poucos casos.** Votação de conflito é rara por definição. Muitos deputados vão ter 0, 1 ou 2. Valem o n mínimo e o voto a voto.
- **Sem nota de "coerência".** A página mostra as votações lado a lado: a tendência, a orientação e o voto. Quem lê tira a conclusão.

### O que fica fora: ideologia

Uma escala esquerda × direita (como as que se calculam a partir dos votos) seria um rótulo político sobre o deputado e esbarra no não-objetivo de "nota ou selo". Os eixos já dizem a direção assunto por assunto, que é mais útil para quem tem um lado em cada assunto e não um lado só.

**Decidir 4:** entra o alinhamento com governo e oposição? E as votações de conflito? Na fatia 1 ou depois?

## Pontos para decidir

1. **Destaques e emendas de Plenário:** fora na fatia 1, com spike para medir (recomendado), ou dentro já.
2. **Cortes:** n mínimo 5, quase unânime 90% e maioria do partido 60% com pelo menos 3 colegas. Manter os da v1 ou mudar algum.
3. **Obstrução:** à parte, com nome próprio (recomendado); ou somada à ausência; ou contada como Não. A obstrução é uma tática para derrubar o quórum, e por isso tem efeito parecido com votar Não, mas não é um voto.
4. **Governo e oposição:** alinhamento simples; com as votações de conflito; na fatia 1 ou depois.
