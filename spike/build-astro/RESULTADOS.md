# Spike #44: resultados do build

Máquina: WSL2, 8 núcleos, 3,8 GB de RAM, 1 GB de swap. Node 26.13.0. Medido em 16/11/2026.

Dado sintético (`gerar_dados.py`, semente 44): 644 deputados replicados dos 5 da amostra, e 26.598 proposições. Os 5 da amostra têm 1.059, 1.059, 1.059, 45 e 3 votos (soma 3.225, as linhas de `voto_deputado.csv`; nenhum voto descartado), então 3 em cada 5 páginas de deputado têm o peso máximo. A página de deputado tem a ilha do placar por lado (H3.6) e a tabela de votos; a de proposição não tem interação.

Candidatos, com a mesma página e o mesmo dado:
- `build-astro/`: Astro 7.4.12 com ilha React (@astrojs/react 7.1.9, React 19.3.1).
- `build-astro-preact/`: Astro 7.4.12 com ilha Preact (@astrojs/preact 6.1.6, Preact 11.2.0).
- `build-next/`: Next.js 16.4.6 com `output: "export"` (Turbopack), React 19.3.1.

## Números

| Medida | Astro + React | Astro + Preact | Next.js export |
| --- | --- | --- | --- |
| Páginas | 27.242 | 27.242 | 27.242 |
| Tempo de build (`medir.py`, relógio) | 41,0 s | 38,9 s | 168,1 s |
| Pico de memória somada da árvore (`medir.py`) | 837 MB | 876 MB | 2.087 MB |
| Pico do maior processo (`/usr/bin/time -v`) | 986 MB | 984 MB | 800 MB |
| Tamanho da saída | 211 MB | não medido | 1,4 GB |
| HTML da página de deputado (1.059 votos), gzip | 24,5 KB | não medido | 58,3 KB (727 KB bruto, 487 KB dele em script embutido) |
| JS baixado na página de deputado, brotli | 59,9 KB | 7,1 KB | 150,7 KB |
| JS baixado na página de proposição, brotli | 0 | 0 | 150,3 KB |

Como cada número saiu:
- Tempo e memória somada: `python3 -I medir.py <pasta> npx <build>`, que soma o `VmRSS` de toda a árvore de processos a cada 0,2 s. Amostra a cada 0,2 s perde pico curto: no Astro, o pico de um processo só (986 MB) passou da soma amostrada (837 MB). Leia a memória como ordem de grandeza.
- O primeiro build do Astro, medido só com `/usr/bin/time -v`, deu 30,3 s; a diferença para 41 s é a partida do `npx` e a amostragem.
- JS baixado: `js_pagina.py` lê os `<script>` do HTML e segue os `import` estáticos em cadeia; comprimido com brotli 11 e gzip 9. Não inclui o script embutido no HTML (5,3 KB bruto no Astro).
- Páginas: `find <saida> -name index.html | wc -l`.

## Leitura

- O Next não cabe no ADR 0002: manda 150 KB de JS para toda página, inclusive a de proposição, que não tem interação; repete o dado da página como script embutido; e gasta 4 vezes o tempo e 2,5 vezes a memória do Astro. Na máquina de 3,8 GB, os 2,1 GB de pico já pesam.
- No Astro, o JS da página de deputado é quase todo o runtime da ilha: 57 KB do react-dom contra 4 KB do Preact. A escolha de runtime da ilha é independente da escolha do framework.
- Tempo de build está longe do gatilho de 30 min em qualquer candidato.

Telemetria: o primeiro build do Astro rodou com a telemetria anônima ligada; foi desligada (`astro telemetry disable`). O Next rodou com `NEXT_TELEMETRY_DISABLED=1`.
