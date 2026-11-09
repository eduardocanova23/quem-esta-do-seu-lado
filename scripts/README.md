# scripts/

**Faz:** utilitários que não são etapa do pipeline, como o `rota.py`, que lê `docs/frentes.yaml` e mostra a frente ativa e o próximo passo, e o `instalar_gitleaks.sh`, que instala o gitleaks com versão e SHA256 conferidos. Os testes ficam em `scripts/tests/`.
**Recebe:** o que cada script documentar no próprio cabeçalho.
**Entrega:** saída no terminal ou um arquivo, sem efeito escondido.
**Quem chama:** você, o `Makefile`, os hooks do Claude Code e o CI.

Regra: só entra script reexecutável e documentado. Experimento vai para o repositório do laboratório.
