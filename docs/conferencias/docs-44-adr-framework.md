# Conferência: docs/44-adr-framework

Sessão de 16/11/2026: spike da issue #44 (branch `spike/44-build-astro`, commits `5bd1ed8` a `bf6e5a1`, enviada ao GitHub e nunca juntada ao main) e ADR 0003. A branch não mexe em `db/marts`, `pipeline` nem em dado gerado; a seção Dados não se aplica. Medições na máquina do Eduardo (WSL2, 8 núcleos, 3,8 GB).

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| Os três candidatos geram 27.242 páginas | `find <saida> -name index.html \| wc -l` = 27242 em `build-astro/dist`, `build-astro-preact/dist` e `build-next/out` (este: 644 + 26.598) | conferido |
| Build: Astro + React 41,0 s, Astro + Preact 38,9 s, Next 168,1 s | `python3 -I spike/medir.py <pasta> npx <build>`: `saida=0 tempo=41.0s`, `tempo=38.9s`, `tempo=168.1s` | conferido |
| Pico de memória ~840 MB, ~880 MB, ~2,1 GB | Mesma saída: `pico_soma=837MB`, `876MB`, `2087MB`. Amostra a cada 0,2 s perde pico curto: no Astro, o `/usr/bin/time -v` deu 986 MB num processo só, acima da soma amostrada. Ordem de grandeza | conferido |
| JS na página de proposição: Astro 0, Next 150 KB brotli | `spike/js_pagina.py` (segue `<script>` e `import` em cadeia): Astro `arquivos=0`; Next `brotli=150317` | conferido |
| JS na página de deputado: 60 KB React, 7 KB Preact, 151 KB Next | `js_pagina.py`: `brotli=59924`, `7078`, `150668`. O script acha imports em cadeia: no Astro, `react.*.js` não está no HTML e entrou na conta | conferido |
| JS com React Aria e Radix: 118 KB brotli | `js_pagina.py` em `dist/teste/index.html`: `brotli=118195` | conferido |
| React Aria e Radix funcionam na ilha React | `spike/teste_ilhas.py` no Chromium headless: 5 de 5 `ok`, `erros de console: nenhum`, `requisições depois de carregar: nenhuma`, exit 0 | conferido |
| O teste de ilhas pega ilha quebrada | Mutação: a página sem `<script>` (2 no original, 0 na cópia) deu 4 `FALHA` e exit 1; o "fecha com Esc" passa à toa | conferido |
| Com `preact/compat`, o build quebra com React Aria e com Radix | Páginas isoladas: `/so-aria` → `[object Object] is not a valid HTML tag name`; `/so-radix` → `Cannot read properties of null (reading 'useRef')`. Com `vite.ssr.noExternal` o erro continua | conferido |
| Não existe configuração que faça o Preact funcionar | Parei no prazo do spike | não conferido |
| Next repete o dado da página em script embutido | `js_pagina.py`: `script embutido no HTML=487490 bytes` na página de deputado do Next; o HTML tem 727 KB | conferido |
| Componente React sem diretiva vira só HTML | Página `/sem-diretiva` num worktree do spike: `scripts: 0, astro-island: 0` e o texto "votou 7 e 2" no HTML; com diretiva: 2 e 2 | conferido |
| Props da ilha ficam serializadas no HTML | `grep` no `dist/teste/index.html`: `props="{&quot;placar&quot;:[1,[[0,{&quot;eixo&quot;:...` | conferido |
| Placar 36 × 32 × 21, máximo 39 | Notas lidas da tabela do próprio ADR por script e ponderadas: `{'AR': 36, 'AP': 32, 'N': 21}`; máximo 3 × 13 | conferido |
| As notas de 1 a 3 | Julgamento apoiado nos números; o "3" do Next em compatibilidade com React Aria e Radix não foi testado | não conferido |
| React Aria e Radix funcionam no Next | Não testado | não conferido |
| O Astro foi comprado pela Cloudflare em janeiro de 2026 | Vem de `docs/metodo.md:265`, com fonte citada na linha 313; não abri a fonte | não conferido |
| Os 60 KB do react-dom ficam em cache entre páginas | O nome do arquivo tem hash e é o mesmo em todas as páginas do build (`client.Cd-EeyjT.js`); o cache em si depende da CDN | não conferido |
| `make rota` mostra o próximo passo novo | Saída: "próximo passo: escrever o ADR do banco; antes, avisar o Eduardo..." | conferido |

## Vazios

Não se aplica: a branch não gera nem transforma dado.

## Retrospectiva

- Disse que o primeiro build do Astro "morreu no meio"; tinha terminado. Li o log enquanto ainda era gravado, depois de uma notificação de término que chegou antes do fim. Nesta sessão, as notificações de tarefa em segundo plano chegaram antes do fim quatro vezes, e uma delas trazia números que os arquivos não tinham. Mecanismo adotado no resto do spike: o próprio comando grava `exit=` no log, e só se lê resultado depois de conferir essa linha e o horário do arquivo.
- Escrevi "1.059 a ~600 votos" sem contar; eram 3, 45 ou 1.059. Pego antes do commit.
- Usei `pgrep -f "astro build"` num laço, e ele achava o próprio comando: o laço não terminava. Trocado por `medir.py`, que segue o PID do build.
