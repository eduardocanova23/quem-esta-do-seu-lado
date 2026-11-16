# Spike #44: resultados do build em Astro

Máquina: WSL2, 8 núcleos, 3,8 GB de RAM, 1 GB de swap. Astro 7.4.12, @astrojs/react 7.1.9, React 19.3.1, Node 26.13.0. Medido em 16/11/2026.

Dado sintético (`gerar_dados.py`, semente 44): 644 deputados replicados dos 5 da amostra, e 26.598 proposições. Os 5 da amostra têm 1.059, 1.059, 1.059, 45 e 3 votos (soma 3.225, as linhas de `voto_deputado.csv`; nenhum voto descartado), então 3 em cada 5 páginas de deputado têm o peso máximo.

| Medida | Valor | Como |
| --- | --- | --- |
| Páginas geradas | 27.242 (644 + 26.598) | log do build e `find dist -name index.html` |
| Tempo de build | 28,8 s (30,3 s de relógio) | log do Astro e `/usr/bin/time -v` |
| Memória de pico | 986 MB | `/usr/bin/time -v`, "Maximum resident set size" |
| Tamanho do `dist` | 211 MB (299 MB em disco, blocos de 4 KB) | `du -sh --apparent-size` e `du -sh` |
| HTML de deputado com 1.059 votos | 226 KB, 24,5 KB em gzip | `stat` e `gzip -c` |
| HTML de proposição | 579 bytes, sem `<script>` | `stat` e `grep -c "<script"` |
| JS da página de deputado | 69,1 KB gzip; 59,9 KB brotli | soma dos 3 arquivos em `dist/_astro/` |
| Dos quais o react-dom (`client.*.js`) | 65,6 KB gzip; 56,8 KB brotli | idem |
| Dos quais a ilha do placar | 0,5 KB | idem |

## Leitura

- O build está bem abaixo do gatilho de 30 minutos: cerca de 60 vezes.
- O JavaScript passa do gatilho de ~50 KB, e quase todo ele é o React: a ilha em si tem meio KB.
- A página de proposição não carrega JavaScript nenhum.
- 986 MB de pico numa máquina de 3,8 GB. Com duas legislaturas, o pico deve crescer (não medido).

Observação: o primeiro build rodou com a telemetria anônima do Astro ligada; foi desligada depois (`astro telemetry disable`).
