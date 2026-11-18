# 0005: site, API de busca e Postgres no servidor Hetzner, atrás do Cloudflare

Status: aceito, 2026-11-17. Issue #50. Proposto pelo Claude e aceito pelo Eduardo ("Aceito o ADR").

## Contexto

Esta é a quarta decisão da lista do método. Ela diz onde ficam, na internet, as três peças que os ADRs anteriores fixaram:

- **O site é uma pasta de arquivos estáticos** ([ADR 0002](0002-forma-de-entrega-do-site.md)), refeita inteira a cada atualização e publicada de uma vez. No spike do [ADR 0003](0003-framework-do-site.md) foram 27.242 arquivos e 211 MB para a 57ª legislatura (~7,7 KB por página). A 58ª começa em 1/2/2027 e soma outras ~30 mil páginas.
- **A API de busca** (FastAPI) é a única coisa que roda na hora do acesso. Ela recebe só o texto digitado.
- **O Postgres** roda em Docker no servidor Hetzner que a v2 herda da v1 ([ADR 0004](0004-banco-de-dados.md)), e a API de busca precisa dele em toda requisição.

O ADR 0002 deixou para este a escolha entre "hospedagem estática com CDN" e "Nginx no servidor atrás de uma CDN", e pediu que a hospedagem aceite ~30 mil arquivos por publicação, com troca atômica de versão. O método acrescenta como critérios o custo, os termos de uso comercial (a camada paga é "depois do MVP, por ADR") e a integração com o build.

O servidor, conferido por SSH em 17/11/2026: CX23 `capivara-mvp`, 3,8 GB de RAM (2,6 GB disponíveis com a v1 rodando), 29 GB de disco livre de 38 GB, Nginx 1.18 ativo servindo a v1, sem Docker, `ufw` liberando só 22, 80 e 443. Segundo a nota do vault de 14/11, **não há domínio nem HTTPS**: a v1 responde por IP, em HTTP. Qualquer opção abaixo precisa de um domínio.

## Opções

| | A. Nginx no Hetzner atrás do Cloudflare grátis | B. Cloudflare Workers (arquivos estáticos), plano pago | C. GitHub Pages |
| --- | --- | --- | --- |
| Onde fica o site | numa pasta do servidor, servida pelo Nginx; o Cloudflare guarda cópia | na rede do Cloudflare | na rede do GitHub |
| Onde fica a API | no servidor, no mesmo endereço (`/api/`) | no servidor, em `api.<domínio>` | no servidor, em outro domínio |
| Limite de arquivos | o disco (29 GB livres) | 100 mil por versão (20 mil no plano grátis) | 1 GB por site |
| Custo por mês além do servidor e do domínio | zero | US$ 5 (mínimo da conta; arquivos estáticos não pagam por requisição) | zero |
| Tráfego | o Cloudflare não cobra; o servidor inclui 20 TB por mês na Europa (fonte de terceiros, não conferido na Hetzner) | requisições a arquivos estáticos "free and unlimited" | limite brando de 100 GB por mês |
| Se o servidor cair | sai do ar tudo que não estiver no cache do Cloudflare; a busca cai | o site fica no ar; a busca cai | o site fica no ar; a busca cai |
| Publicar uma versão | `rsync` para uma pasta nova e troca de um link simbólico; depois limpa o cache do Cloudflare | `wrangler deploy`: versão nova imutável | workflow do GitHub Actions |
| Termos | os do Cloudflare grátis; nada contra uso comercial encontrado | idem, plano pago | "not intended for or allowed to be used as a free web-hosting service to run your online business" |

Limites conferidos em 17/11/2026 nas páginas de limites do Cloudflare Pages, do Workers e do GitHub Pages (ver Conferência no registro). Ficaram de fora:

- **Cloudflare Pages e Workers no plano grátis:** 20 mil arquivos por site, e a 57ª sozinha já tem 27 mil.
- **Netlify grátis:** 300 créditos, e o tráfego custa 20 créditos por GB, ou seja, ~15 GB por mês. Um link que circula no WhatsApp passa disso num dia.
- **Vercel Hobby:** 100 GB de tráfego e 1 milhão de requisições à CDN por mês. A restrição de uso comercial do Hobby não estava na página aberta (não conferido); pelo modelo de servidor e cache, ele resolve um problema que o ADR 0002 decidiu não ter.
- **Nginx no Hetzner sem CDN:** o ADR 0002 pede CDN, e um pico iria inteiro para uma máquina de 2 vCPU.

## Critérios, com peso

Nota de 1 (atende mal) a 3 (atende bem). As notas são julgamento meu sobre a tabela acima, não medição.

| Critério | Peso | A | B | C |
| --- | --- | --- | --- | --- |
| 1. Pico de acesso não derruba nada nem muda o custo | 3 | 3: o Cloudflare guarda as páginas; o que escapa do cache é arquivo servido pelo Nginx, sem banco | 3 | 2: limite brando de 100 GB por mês; num pico o GitHub pode reclamar |
| 2. Cresce com as legislaturas sem trocar de hospedagem | 3 | 3: limitado pelo disco | 2: 100 mil arquivos dão ~3 legislaturas; depois, dividir o site ou trocar | 2: 1 GB dá ~4 legislaturas de 211 MB |
| 3. Custo dentro do que já se paga | 3 | 3: zero além do domínio | 2: US$ 5 por mês (~R$ 30, câmbio não conferido), mais que o orçamento inteiro do banco | 3: zero |
| 4. Troca atômica e volta rápida | 2 | 2: o link simbólico troca de uma vez, mas o cache do Cloudflare guarda a versão anterior até a limpeza, segundos depois | 3: versão imutável, volta pelo painel ou pela linha de comando | 2: atômica; voltar é rodar de novo o workflow da versão anterior |
| 5. O site fica no ar se o servidor cair | 2 | 1: só o que estiver no cache, e página pouco acessada sai do cache | 3 | 3 |
| 6. Poucas peças e um endereço só para site e API | 2 | 3: um domínio, um certificado de origem, a API em `/api/` sem CORS, um lugar para olhar logs | 2: dois destinos de publicação; a API em subdomínio pede CORS | 1: dois fornecedores, a API em outro domínio, sem cabeçalhos HTTP próprios (cache, CSP) |
| 7. Termos compatíveis com a camada paga, se vier | 1 | 3 | 3 | 1: proibido para "online business" |
| 8. Fácil de sair do fornecedor | 1 | 3: o Cloudflare é só DNS e cache; tirá-lo deixa o Nginx servindo | 2: a configuração é do Workers; os arquivos são os mesmos | 2 |
| **Total (máximo 51)** | | **45** | **42** | **36** |

## Decisão

**A. O site, a API de busca e o Postgres ficam no servidor Hetzner. O Nginx serve o site e encaminha `/api/` para a API, e o Cloudflare, no plano grátis, fica na frente como DNS, HTTPS e CDN.**

1. **Por que não o Workers (B), que ficou perto:** ele ganha em dois critérios, a volta de versão e o site no ar com o servidor caído. O segundo vale menos do que parece: com o servidor caído, a busca cai junto em qualquer opção, e a caixa de busca é a primeira coisa da página inicial. Em troca, B custa US$ 5 por mês para sempre, e esse é o argumento que decide. O teto de 100 mil arquivos pesa pouco: com ~30 mil páginas por legislatura, só a 60ª (2035 a 2039) passaria dele, se o site guardar todas as legislaturas desde a 57ª.
2. **Por que não o GitHub Pages (C):** os termos proíbem o uso para negócio online, o que fecha a porta da camada paga, e ele não deixa definir cabeçalhos HTTP.
3. **O preço da escolha é a disponibilidade:** o site depende de um servidor só. O Cloudflare amortece (as páginas mais acessadas ficam no cache), mas não substitui. Se o servidor cair muitas vezes, B passa a valer a diferença (ver Quando revisitar). Mudar para B depois não refaz nada: a pasta do build é a mesma, muda só o destino do `rsync`.
4. **O domínio é decisão do Eduardo** e entra no marco `infra.deploy`. Um `.com.br` custa R$ 40 por ano no Registro.br (fonte secundária, não conferido no Registro.br). Os servidores de nome do domínio passam a ser os do Cloudflare.

### O que acontece por baixo

**O caminho de uma visita.** O navegador pergunta ao DNS onde fica `<domínio>`; como o domínio aponta para o Cloudflare, a resposta é um endereço do Cloudflare, não o do servidor. A conexão HTTPS termina num servidor do Cloudflare perto de quem acessa (no Brasil, se houver um lá; não conferido). Se a página está no cache dele, ela volta dali, e o Hetzner nem fica sabendo. Se não está, o Cloudflare pede ao Nginx do servidor, por HTTPS, guarda a cópia e entrega.

**O Cloudflare não guarda HTML nem JSON por padrão** (só CSS, JS e imagens). Uma regra de cache ("Cache Rule": o plano grátis tem 10) manda guardar tudo que não for `/api/`. Como o site só muda na publicação, a cópia vale até a próxima limpeza.

**A publicação.** O build vai para uma pasta nova, `/srv/site/versoes/<data-e-hora>/`. Quando ela chega inteira, um link simbólico `/srv/site/atual` passa a apontar para ela; o Nginx serve sempre `atual`. Trocar um link simbólico é uma operação só do sistema de arquivos (`rename`), então nenhuma visita vê meia versão. Depois, uma chamada à API do Cloudflare limpa o cache, e as visitas seguintes buscam a versão nova. Voltar atrás é apontar o link para a pasta anterior e limpar o cache de novo. As últimas versões ficam no disco (211 MB cada).

**A API e o banco.** O mesmo `infra/compose.yml` do ADR 0004 sobe o Postgres e a API em contêineres. O Nginx recebe `/api/` e repassa para a API, que escuta só dentro do servidor. Como site e API estão no mesmo endereço, o navegador não precisa de CORS (a regra que barra uma página de chamar outro domínio sem permissão).

**HTTPS nas duas pontas.** Entre o visitante e o Cloudflare, o certificado é do Cloudflare. Entre o Cloudflare e o servidor, um certificado de origem emitido pelo Cloudflare, no modo "Full (strict)", que confere esse certificado. O `ufw` passa a aceitar 80 e 443 só das faixas de IP do Cloudflare: sem isso, quem descobrisse o IP chegaria ao Nginx por fora da CDN.

## Consequências

- **O marco `infra.deploy`** faz: compra do domínio, zona no Cloudflare, regra de cache, certificado de origem, `ufw` restrito ao Cloudflare, Docker no servidor, `infra/compose.yml` (Postgres e API), configuração do Nginx versionada em `infra/`, script de publicação com troca de link e limpeza de cache, e a retirada da v1 (serviço `capivara` e o site dela no Nginx).
- **Quem faz o build** fica para o `infra.deploy`. Hoje o pipeline roda na máquina do Eduardo e o critério da frente é "um merge no main publica o site sozinho". O caminho mais curto é o GitHub Actions gerar o site e mandar por `rsync` com uma chave SSH só de publicação; os marts do dia precisam chegar ao build, e isso se resolve lá. Quando o pipeline for para o servidor (`escala.airflow`), o build pode rodar no próprio servidor (~840 MB de pico no spike).
- **Segredos novos** (chave SSH de publicação, token do Cloudflare só com permissão de limpar cache) ficam nos secrets do GitHub e nunca no repositório (`infra/README.md`).
- **O Cloudflare vê toda requisição**, inclusive o texto da busca, como qualquer CDN. O lado escolhido continua sem sair do navegador (H3.6). Nenhum produto de análise do Cloudflare se liga sem decisão própria.
- **RAM:** Nginx e arquivos estáticos quase não somam aos ~3,8 GB. O que aperta continua sendo a busca (BGE-M3) e o Airflow, como o ADR 0004 já registrou; se o ADR da busca pedir um servidor maior, o site vai junto sem mudar nada aqui.
- **Não conferido e a medir no `infra.deploy`:** que a regra "guardar tudo" e a limpeza completa do cache funcionam no plano grátis (a página de regras de cache lista as 10 regras e a limpeza completa, mas não diz por plano), e o preço atual do CX23 (a página da Hetzner mostra "a partir de € 5,99" para a linha e "currently not available" para pedidos novos).

## Quando revisitar

- Se o servidor ficar fora do ar mais de uma vez num trimestre, ou mais de uma hora seguida: B (Workers) ou outra hospedagem estática separada do servidor.
- Se o disco passar de 70% (gatilho que o ADR 0004 já usa para o banco).
- Se o Cloudflare mudar os termos ou os limites do plano grátis para cache de HTML.
- Se vier a camada paga com login (o ADR 0002 já pede ADR novo).
