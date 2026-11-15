---
name: conferir
description: Confere as afirmações e os dados de uma mudança antes de encerrá-la - cada fato sobre a fonte, o dado ou um número com a evidência (comando e saída) ou marcado "não conferido", linhas de mart refeitas direto da Câmara, vazios explicados, e retrospectiva dos erros da sessão. Use antes de dizer que algo está certo, antes de abrir PR que mexe em db/marts, pipeline ou docs/dados, quando o hook exige-conferencia segurar a vez, e sempre que o Eduardo falar em encerrar a sessão.
---

# Conferir

A amostra dos marts de 15/11/2026 teve seis afirmações erradas, e só uma era impossível de saber sem rodar o dado. As outras vieram de três causas, e cada parte desta skill ataca uma:

1. Afirmar sem abrir a fonte, quando abrir custava segundos.
2. Tomar sinal fraco por prova.
3. Coluna que aceita vazio escondendo bug.

Análise completa: nota "Sinal fraco não é prova" no vault.

## 1. Afirmações

Liste cada afirmação factual da branch e da sessão: o que está em `docs/`, nas mensagens de commit, no PR e no que você me disse. Conta como afirmação factual:
- formato, campo, tipo ou URL da fonte;
- comportamento da API;
- contagem e "bate";
- "o teste cobre", "funciona", "corrigido".

Para cada uma, escreva em `docs/conferencias/<branch>.md`, seção Afirmações: a afirmação, a evidência e a situação (`conferido` ou `não conferido`).

**Evidência que vale:**
- **Fato da fonte:** o comando que abriu a fonte e o trecho da saída. Por exemplo, `head -1 votacoes-2025.csv` mostrando a coluna.
- **URL:** a resposta dela e a de um id inventado, lado a lado. Se as duas são iguais, a página se monta no navegador e a afirmação fica `não conferido` até alguém abrir no navegador.
- **"Bate" ou "reproduz":** contra o quê comparou, quantos casos e quais ficaram de fora.
- **"O teste cobre":** a mutação que derrubou o teste, com `assert` de que a mutação aplicou.
- **Número publicado:** recalculado à mão num caso pequeno.

**Não vale:**
- HTTP 200 sozinho;
- teste que nunca falhou;
- validador sem erro, que só diz que o formato está certo;
- "conferido na sessão anterior";
- memória.

Se a conferência mostrar que a afirmação está errada: corrija o texto, marque `conferido` com a evidência nova e anote o erro na retrospectiva.

## 2. Dados (quando a branch mexe em `db/marts`, `pipeline` ou em dado gerado)

1. **Vazios.** `make conferir` reconta os vazios de cada coluna que aceita vazio e reescreve a tabela Vazios. Para cada linha, escreva o que o vazio significa e por que aquela quantidade é plausível. Se você não consegue explicar, é bug até prova em contrário: investigue, não escreva "esperado".
2. **Linhas refeitas da fonte.** Sorteie pelo menos 5 linhas, com `random.sample` e semente anotada, misturando marts e casos difíceis: troca de partido, suplente, bloco, vazio. Refaça cada uma direto da Câmara (API ou arquivo bruto), sem passar pelo código que gerou o dado. Anote como refez e se bate. Linha que não bate é bug: corrija, e só então siga.
3. **Distribuição.** Para as colunas que entram em número publicado, olhe mínimo, máximo e os valores mais comuns. Desconfie de zero, de 100%, de valor único e de um salto em relação à versão anterior.
4. **Filtros.** Em cada filtro e junção do código, conte quantas linhas entraram, quantas saíram e por quê. Linha descartada em silêncio é o pior bug.
5. **Cruzamento entre colunas.** Vazio numa coluna que deveria andar junto com outra (rótulo sem proposição, partido sem bancada) é bug que o validador de formato não pega.

## 3. Retrospectiva (sempre que o Eduardo falar em encerrar, e no fim de cada PR)

1. Releia o que você afirmou na sessão inteira e procure o que não foi conferido ou estava errado.
2. Para cada erro achado: corrija, diga ao Eduardo e anote em `Projetos/Câmara v2/Câmara v2 - erros do Claude.md` no vault (data, o que afirmei, o que era, a causa, que regra pegaria). Use a skill `registrar`.
3. Se o erro repete uma causa já anotada, a regra atual não está segurando: proponha um mecanismo (teste, hook, checagem no `conferir.py`), não mais texto.

## 4. Feche

- Rode `make conferir` até dar `0 pendência(s)`. A marca de conferido vale para os dados como estão agora: mudou um dado, confira de novo.
- Na resposta ao Eduardo, inclua um bloco **Conferência** com as afirmações principais, a evidência e o que ficou "não conferido".
- Dispensa (`make conferir-dispensar MOTIVO="..."`) só quando o Eduardo pedir, com as palavras dele no motivo.
