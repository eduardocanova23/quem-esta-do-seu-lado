# 0002: site gerado no build e servido por CDN; só a busca tem servidor

Status: aceito, 2026-11-16. Issue #42.

## Contexto

Esta é a primeira decisão da lista do método ("Arquitetura e stack"), porque restringe as seguintes: framework, banco, hospedagem e busca. A pergunta é como uma página chega ao visitante: pronta desde o build, montada pelo servidor a cada acesso ou montada no navegador.

O que já está decidido e pesa aqui:

- **Os dados mudam uma vez por dia**, depois do `make atualizar` (e, na Fase 5, da DAG de publicação).
- **A v1 não sabia se aguentava muitos usuários**, porque isso nunca foi medido nem projetado (método, tabela das lições).
- **H3.6: o lado escolhido nunca sai do navegador.** Nenhuma requisição o carrega. Como o ranking da pergunta 3 é "a pergunta 2 aplicada a todos" (perguntas.md), ele depende do lado e tem de ser calculado no navegador, a partir de dado que é o mesmo para todo mundo.
- **H7.1 e H7.2: o endereço é o mesmo para todos, e a prévia do link no WhatsApp sai no build.** O robô que monta a prévia não roda JavaScript (não conferido; o teste de H7.2 confere), então cada endereço precisa responder com HTML completo.
- **A caixa de busca acha deputado, partido, tema e proposição desde a primeira publicação** (decisão de 13/11/2026). Busca por texto livre não dá para pré-gerar.

Volumes da 57ª, contados no raw de 16/11/2026 (`dados/raw/arquivos/2026-11-16/`, anos 2023 a 2026):

| O quê | Quantos | Vira página em |
| --- | --- | --- |
| Deputados com voto registrado (titulares e suplentes) | 644 | Fatia 1 |
| Votações com voto nominal de Plenário (de 1.604 nominais; as de comissão ficam fora da fatia 1) | 1.128 | Fatia 1 (listas) |
| Proposições de PL, PLP, PEC, PDL e MPV | 26.598 | Fatia 3 |

Ou seja, da ordem de 30 mil páginas por legislatura, todas refeitas a cada atualização.

## Opções

| Opção | Como uma página chega ao visitante | O que roda na hora do acesso |
| --- | --- | --- |
| **A. Estático** | O build gera um HTML por endereço logo depois do pipeline; a CDN entrega o arquivo. Interação (lado, filtros, ranking) roda no navegador sobre JSON gerado no mesmo build | Só a API de busca |
| B. Servidor com cache | O servidor monta a página do banco no primeiro acesso; a CDN guarda a cópia até a próxima atualização, quando o cache é limpo | Servidor do site, banco e a API de busca |
| C. App no navegador | O servidor entrega uma casca vazia; o navegador pede os dados a uma API e monta a página | API para tudo e banco |

Ficou de fora um híbrido "estático por padrão, servidor em algumas rotas". Hoje nenhuma rota além da busca precisa de servidor; se uma precisar, ela entra por ADR novo, sem desfazer este.

## Critérios, com peso

Nota de 1 (atende mal) a 3 (atende bem). A nota é julgamento meu sobre o que está escrito acima, não medição; a única medida que falta é o tempo de build (ver Consequências).

| Critério | Peso | A | B | C |
| --- | --- | --- | --- | --- |
| 1. Pico de acesso não derruba nada nem muda o custo | 3 | 3: arquivo na CDN, banco fora do caminho | 2: o primeiro acesso a cada página, todo dia, vai ao banco | 1: toda visita vai à API e ao banco |
| 2. HTML completo em cada endereço (prévia de link, Google) | 3 | 3 | 3 | 1: só com pré-renderização à parte |
| 3. O lado não sai do navegador, e dá para provar | 3 | 3: o único servidor é a busca, e ela recebe só o texto digitado | 2: o dado do ranking vai inteiro para o navegador de qualquer jeito, e o servidor convida a "filtrar no servidor" | 2: idem, com a API como convite |
| 4. Site testável como função dos marts do dia, no CI, sem banco | 2 | 3: o build roda sobre a amostra (`db/marts/amostra/`) | 1: precisa de banco e servidor no teste | 2: precisa da API ou de dublês dela |
| 5. Publicação diária rápida | 2 | 1: refaz ~30 mil páginas por dia, tempo não medido | 3: não há build; limpa o cache | 3: build pequeno |
| 6. Poucas peças para operar e custo fixo baixo | 2 | 3: arquivos e uma API pequena | 1: servidor sempre ligado, banco exposto ao site, limpeza de cache | 2: API e banco atendendo todo acesso |
| 7. Todas as páginas mostram o mesmo dia | 1 | 3: a versão nova substitui a anterior inteira | 1: o cache mistura dias se a limpeza falhar pela metade | 3 |
| **Total (máximo 48)** | | **44** | **32** | **29** |

## Decisão

**A. O site é gerado no build e servido por CDN. Só a API de busca roda na hora do acesso.**

1. **O build lê os marts do dia em arquivo, não no banco.** O último passo do pipeline exporta os marts no formato da amostra (um arquivo por mart, conferido por `db/marts/contrato.yaml`), e o build lê esses arquivos. Assim o CI gera o site sobre `db/marts/amostra/` sem Postgres, e o `web/` nunca importa o `pipeline/`. O formato do arquivo (CSV, como a amostra hoje, ou outro) se fixa no ADR de framework.
2. **Toda interação roda no navegador, sobre JSON gerado no build.** Escolha de lado, filtros e o ranking da pergunta 3 leem arquivos que são os mesmos para todo mundo. O ranking de uma legislatura cabe num arquivo só: 644 deputados por 5 eixos com volume, alguns números cada (tamanho não medido; estimativa de dezenas de KB).
3. **A API de busca recebe só o texto digitado.** Nenhum parâmetro de lado, filtro de lado ou placar passa por ela. Ela consulta o Postgres com um papel que não consegue escrever.
4. **Cada atualização refaz o site inteiro e publica de uma vez.** A versão nova substitui a anterior inteira; voltar atrás é republicar o build anterior. Build incremental (refazer só as páginas cujo dado mudou) fica para quando o tempo de build pedir, porque dá para acrescentar depois sem refazer nada (regra 8 do método).

### O que acontece por baixo

O build é um programa que roda depois do pipeline: lê os marts, chama um template por endereço e grava um arquivo HTML por página (`/deputado/<id>/<legislatura>/index.html`, por exemplo), mais os JSON da interação e os arquivos de CSS e JS. A pasta resultante sobe para a hospedagem. A CDN é uma rede de servidores que guarda cópias desses arquivos perto de quem acessa: quando alguém abre o link, recebe o arquivo pronto do servidor mais próximo, sem programa nenhum rodando e sem tocar no banco. Mil acessos ou um milhão custam a mesma coisa para o banco: zero.

O navegador recebe o HTML já com o conteúdo neutro (H2.1: a página abre neutra). O JavaScript da página só entra para o que é interativo: quando a pessoa escolhe um lado, ele recalcula o placar com o JSON que já baixou, sem fazer requisição nenhuma.

## Consequências

- **O ADR de framework passa a exigir:** geração estática de milhares de páginas, ilhas de interação sem carregar JavaScript na página inteira, e um build de ~30 mil páginas em tempo aceitável. O spike do framework mede esse tempo com volume sintético da 57ª; é o maior risco desta decisão.
- **O ADR de banco fica mais simples:** o banco não atende o site, só o pipeline, o build (por arquivo exportado) e a API de busca.
- **O ADR de hospedagem escolhe entre hospedagem estática com CDN e Nginx atrás de CDN**, e precisa aceitar ~30 mil arquivos por publicação, com troca atômica de versão.
- **O que não dá para fazer sem um ADR novo:** página que depende de quem está acessando (login, camada paga), dado novo entre duas atualizações diárias, filtro cujo dado não cabe no navegador.
- `web/README.md` e `api/README.md` dizem que a API atende "busca e filtros". Com esta decisão, os filtros rodam no navegador e a API atende só a busca; os dois READMEs se ajustam no mesmo PR.
- O teste de H3.6 fica simples: no e2e, escolher um lado e conferir que nenhuma requisição saiu (a busca só sai quando a pessoa digita na caixa).
- Cada legislatura nova soma outras ~30 mil páginas. As de legislaturas encerradas não mudam mais, e são as primeiras candidatas ao build incremental.

## Quando revisitar

- Se o build completo passar de 30 minutos, ou a hospedagem limitar o número de arquivos por publicação: primeiro build incremental, depois um ADR novo se não bastar.
- Se vier a camada paga com login e estado por usuário (não-objetivos: "depois do MVP, por ADR").
- Se uma pergunta nova pedir dado mais fresco que uma atualização por dia.
- Se algum JSON de interação passar de 1 MB comprimido numa página aberta pelo celular.
