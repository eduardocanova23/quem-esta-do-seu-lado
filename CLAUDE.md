# Câmara v2

Site que responde, em linguagem comum, as três perguntas de docs/produto/perguntas.md: o que a Câmara prioriza e abandona, se um deputado está do lado de quem pergunta e quem é mais aliado ou inimigo.
Método: docs/metodo.md. Rota: docs/frentes.yaml (make rota). Tarefa parada no meio: docs/estado.md.

## Onde está cada coisa
- docs/produto/: perguntas, diretrizes, personas, histórias e não-objetivos. Leia antes de mexer em qualquer tela.
- docs/decisoes/: ADRs. Não contrarie um ADR sem propor outro.
- docs/dados/atualizacao.md: toda tabela nova ganha uma linha aqui antes do schema.
- pipeline/passos.py: a lista de passos da coleta e de quem depende de quem (nasce com o marco dados.core).
- Notebook e experimento não entram aqui: vão para o repositório do laboratório.

## Comandos
- Preparar a máquina: make setup
- Rota: make rota
- Testes rápidos: make test
- Tudo, como no CI: make ci
- Atualizar os dados: make atualizar (nasce com o marco dados.core)
- Ambiente local: docker compose -f infra/compose.yml up -d

## Git
- Commit local a cada mudança coesa, sem perguntar. git push e gh pr create só quando eu pedir.
- Nunca commit nem push no main. Uma branch por issue: feat/<n>-<slug>, fix/, data/, docs/, spike/.
- Conventional Commits; a mensagem explica o porquê.
- Confira git status e adicione arquivo por arquivo; nada de git add -A às cegas.
- Todo PR que fecha um passo atualiza o próximo passo da frente em docs/frentes.yaml.

## Como trabalhar
- Trabalhe na frente ativa da rota; trocar de frente só com o meu ok.
- Explique em detalhe o código que gera número publicado e as decisões de arquitetura, com opções e trade-offs. No resto, diga em uma linha o que cada parte faz.
- Plano antes de mexer em mais de um arquivo, com alternativas e riscos.
- Decida pelo tamanho que já se sabe que vem, não pelo de hoje: "dá menos trabalho agora" não é argumento. Se é só "talvez um dia", não faça; se adiar obriga a refazer, faça direito agora.
- No pipeline e nas métricas, teste primeiro: mostre a saída falhando e depois passando.
- Passo novo da coleta entra em pipeline/passos.py, como comando idempotente que recebe a data lógica; nunca num script solto.
- Mudou uma métrica, atualize a página de metodologia no mesmo PR.
- Escrever não é rodar: coleta, notebook e chamada paga só quando eu pedir, com estimativa de custo e --max-custo.
- Depois de implementar, diga o que testar: URLs (caminho feliz e um erro), consultas SQL, arquivos esperados.
- Nenhuma dependência nova sem justificativa no PR e sem explicar a camada de baixo.
- Sem filtros manuais sobre método estatístico: explique o mecanismo em vez de esconder o resultado.
- Nenhuma chamada de LLM no caminho de uma requisição do site; saída de LLM sempre validada por schema.
- Mudança de schema só pela skill /migracao.
- Se a tarefa parar no meio, anote em docs/estado.md onde parou.
- Sugira /registrar no fim da tarefa quando ela fechar uma fase ou render lição ou decisão útil fora do projeto; só grave no vault se eu confirmar.

## Pegadinhas do domínio
Resumo; a fonte é docs/produto/diretrizes.md.
- Nunca compare legislaturas nem governos; deputado em duas legislaturas tem dois perfis.
- Partido é o da época do ato (tabela de filiação), nunca o atual.
- Ids de tema são estáveis: nunca renumere nem reaproveite.
- Personas são o critério de classificação: toda mudança de tema reporta o placar antes e depois.
