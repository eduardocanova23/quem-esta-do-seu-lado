# 0003: Astro com ilhas em React

Status: aceito, 2026-11-16. Issue #44. Decidido pelo Claude por delegação do Eduardo ("pode decidir você, desde que anote o porquê e faça testes"), a partir do spike da issue #44.

## Contexto

O [ADR 0002](0002-forma-de-entrega-do-site.md) fixou a forma: o site é gerado no build e servido por CDN, e toda interação roda no navegador. Daí saem as exigências para o framework:

- **Gerar ~30 mil páginas por legislatura** a cada atualização, num tempo e numa memória que caibam no CI e na máquina de 3,8 GB do Eduardo.
- **Página sem interação sai sem JavaScript.** O eleitor curioso chega pelo celular, por um link no WhatsApp ([personas](../produto/personas.md)).
- **Ilha de interação onde a história pede:** o placar pelo lado (H3.6), a caixa de busca (H0) e as explicações no lugar.
- **Componentes acessíveis prontos.** O método escolheu React Aria para as peças difíceis, como a busca com sugestões, e shadcn (sobre Radix) como base. Escrever um combobox acessível à mão é caro e fácil de errar.

A lição da v1 que pesa aqui: o framework virou teto de design porque foi escolhido "por conveniência, sem critérios escritos nem protótipo". Por isso esta decisão vem de um spike medido.

## O spike

Branch `spike/44-build-astro`, que não vai para o main. Os resultados completos estão em `spike/build-astro/RESULTADOS.md` dessa branch. Mesma página, mesmo dado sintético (644 deputados e 26.598 proposições, gerados da amostra dos marts), três candidatos:

| Medida | Astro + React | Astro + Preact | Next.js 16 (`output: "export"`) |
| --- | --- | --- | --- |
| Build das 27.242 páginas | 41 s | 39 s | 168 s |
| Pico de memória (soma dos processos) | ~840 MB | ~880 MB | ~2,1 GB |
| Tamanho da saída | 211 MB | não medido | 1,4 GB |
| JS na página de proposição (sem interação), brotli | 0 | 0 | 150 KB |
| JS na página de deputado (ilha do placar), brotli | 60 KB | 7 KB | 151 KB |
| JS com ComboBox do React Aria e Dialog do Radix, brotli | 118 KB | o build quebra | não medido |
| React Aria e Radix funcionando no navegador | sim: 5 de 5 passos no Chromium, sem erro de console | não: o build quebra nos dois | não testado |

Medido em 16/11/2026 na máquina do Eduardo (WSL2, 8 núcleos, 3,8 GB). Memória amostrada a cada 0,2 s: vale como ordem de grandeza.

Ficaram fora do spike, porque o ADR 0002 já as exclui: React SPA com Vite (sem HTML por endereço) e FastAPI com Jinja2 e HTMX (renderização no servidor; e, como gerador estático, seria um gerador escrito à mão, sem componentes React).

## Critérios, com peso

Nota de 1 (atende mal) a 3 (atende bem), apoiada nos números acima.

| Critério | Peso | Astro + React | Astro + Preact | Next export |
| --- | --- | --- | --- | --- |
| 1. Página sem interação sai sem JS | 3 | 3: 0 KB | 3: 0 KB | 1: 150 KB em toda página |
| 2. React Aria e shadcn (Radix) funcionam nas ilhas | 3 | 3: testado no navegador | 1: o build quebra com os dois | 3: é o ambiente nativo deles (não testado) |
| 3. Build cabe no CI e na máquina de 3,8 GB | 2 | 3: 41 s, ~840 MB | 3: 39 s, ~880 MB | 1: 168 s, ~2,1 GB |
| 4. JS da página com ilha | 2 | 2: 60 KB, 118 KB com as bibliotecas | 3: 7 KB | 1: 151 KB |
| 5. Modelo mental pequeno: página é template do dado | 2 | 3: o `.astro` roda no build e vira HTML | 3: idem | 1: componentes de servidor e de cliente, payload de servidor repetido no HTML |
| 6. Ecossistema e risco de fornecedor | 1 | 2: menor que o do Next; o método registra a compra do Astro pela Cloudflare em janeiro de 2026 (não conferido por mim) | 2: idem | 3 |
| **Total (máximo 39)** | | **36** | **32** | **21** |

## Decisão

**Astro com ilhas em React, em TypeScript.** Versões do spike: Astro 7.4.12, @astrojs/react 7.1.9, React 19.3.1. As versões exatas se fixam no `package-lock` do marco `site.esqueleto`.

1. **Por que não o Next:** ele resolve um problema que o ADR 0002 decidiu não ter (renderizar no servidor). Em modo estático, ainda manda o runtime do React e o dado da página repetido em script para toda página, inclusive as que não têm interação, e gasta 4 vezes o tempo e 2,5 vezes a memória do build.
2. **Por que React e não Preact nas ilhas,** apesar de pesar 8 vezes mais: o Preact só vale se rodar as peças escolhidas para a interface, e com `preact/compat` o build quebra tanto com React Aria quanto com Radix. Pode existir configuração que resolva (não conferido; o spike parou no prazo). Um ganho de ~50 KB na primeira visita não paga escrever à mão um combobox e um diálogo acessíveis. Os 60 KB do react-dom ficam em cache entre páginas, porque o arquivo tem nome com hash e é o mesmo em todas.
3. **Tailwind, tokens e quais componentes do shadcn** são decisão da frente de design (`design.tokens`), não deste ADR.

### O que acontece por baixo

No build, o Astro executa cada página `.astro` em Node: o trecho entre `---` lê o dado (aqui, os marts em arquivo, como manda o ADR 0002) e o resto é um template que vira HTML puro. Componente React usado sem diretiva também vira só HTML: o React roda no build e some.

Componente marcado com uma diretiva `client:` (por exemplo, `<Placar client:visible placar={...} />`) vira uma **ilha**. O Astro grava o HTML inicial do componente dentro de um elemento `<astro-island>`, junto com as props serializadas em JSON e o endereço do script. No navegador, um script pequeno espera a condição da diretiva (`visible`: quando a ilha entra na tela), baixa o React e o componente e "hidrata" só aquele trecho: liga os eventos ao HTML que já está lá. O resto da página nunca vira React.

Duas consequências disso para o código: tudo que vai como prop de ilha fica escrito no HTML (então props de ilha são pequenas, e o dado grande fica no HTML ou num JSON à parte); e o estado da ilha, como o lado escolhido, existe só na memória da página.

## Consequências

- **Regra de código:** interação só onde há história pedindo. Lista de votos, placares neutros e textos são HTML do build; ilha é exceção, revisada no PR.
- **Prop de ilha nunca carrega o lado nem dado grande.** O lado nasce e morre no estado da ilha (H3.6). O teste de fumaça confere, como no spike, que nenhuma requisição sai depois de carregar a página.
- **Custo conhecido de JavaScript:** ~60 KB brotli na primeira página com ilha, ~118 KB quando a página usa React Aria e Radix (a página inicial, com a busca). O Lighthouse da Fase 5 (`escala.carga`) mede o efeito no celular.
- **CI:** Node e npm entram no CI do site; o Playwright precisa de `install --with-deps` para o Chromium (a máquina local não tem as bibliotecas do sistema); telemetria desligada com `ASTRO_TELEMETRY_DISABLED=1`.
- **Dependências novas no marco `site.esqueleto`:** `astro`, `@astrojs/react`, `react`, `react-dom` e TypeScript, justificadas por este ADR.
- **O ADR de hospedagem** recebe uma pasta de arquivos estáticos (211 MB e 27 mil arquivos por legislatura no spike).

## Quando revisitar

- Se o Lighthouse no celular mostrar que o JavaScript das ilhas pesa no carregamento: primeiro tentar o Preact com a configuração certa, depois bibliotecas mais leves.
- Se o build de todas as legislaturas passar de 30 minutos ou não couber na memória do CI (gatilho herdado do ADR 0002).
- Se vier a camada paga com login e estado por usuário (já pede ADR novo pelo ADR 0002).
- Se o Astro mudar de licença ou deixar de ser mantido.
