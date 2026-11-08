# Câmara v2

Site que responde, em linguagem comum, as três perguntas de docs/produto/perguntas.md: o que a Câmara prioriza e abandona, se um deputado está do lado de quem pergunta e quem é mais aliado ou inimigo.
Método: docs/metodo.md. Rota: docs/frentes.yaml (make rota). Tarefa parada no meio: docs/estado.md.

## Onde está cada coisa
- docs/produto/: perguntas, personas, histórias e não-objetivos. Leia antes de mexer em qualquer tela.
- docs/decisoes/: ADRs. Não contrarie um ADR sem propor outro.
- docs/dados/atualizacao.md: toda tabela nova ganha uma linha aqui antes do schema.
- Notebook e experimento não entram aqui: vão para o repositório do laboratório.

## Comandos
- Rota: make rota
- Testes rápidos: make test
- Tudo, como no CI: make ci
- Ambiente local: docker compose -f infra/compose.yml up -d

## Git
- Commit local a cada mudança coesa, sem perguntar. git push e gh pr create só quando eu pedir.
- Nunca commit nem push no main. Uma branch por issue: feat/<n>-<slug>, fix/, data/, docs/, spike/.
- Conventional Commits; a mensagem explica o porquê.
- Confira git status e adicione arquivo por arquivo; nada de git add -A às cegas.
- Todo PR que fecha um passo atualiza o próximo passo da frente em docs/frentes.yaml.

## Como trabalhar
- Trabalhe na frente ativa da rota; trocar de frente só com o meu ok.
- Explique o que cada parte faz e por quê; mostre opções e trade-offs antes de decisões de arquitetura.
- Plano antes de mexer em mais de um arquivo, com alternativas e riscos.
- Teste primeiro: mostre a saída falhando e depois passando.
- Escrever não é rodar: coleta, notebook e chamada paga só quando eu pedir, com estimativa de custo e --max-custo.
- Depois de implementar, diga o que testar: URLs (caminho feliz e um erro), consultas SQL, arquivos esperados.
- Nenhuma dependência nova sem justificativa no PR e sem explicar a camada de baixo.
- Sem filtros manuais sobre método estatístico: explique o mecanismo em vez de esconder o resultado.
- Nenhuma chamada de LLM no caminho de uma requisição do site; saída de LLM sempre validada por schema.
- Mudança de schema só pela skill /migracao.
- Se a tarefa parar no meio, anote em docs/estado.md onde parou.

## Pegadinhas do domínio
- Nunca compare legislaturas nem governos; deputado em duas legislaturas tem dois perfis.
- Partido é o da época do ato (tabela de filiação), nunca o atual.
- Ids de tema são estáveis: nunca renumere nem reaproveite.
- Personas são o critério de classificação: toda mudança de tema reporta o placar antes e depois.
