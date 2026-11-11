# Travas: quem barra o quê, e onde

Cada trava só enxerga um caminho. O Claude Code só vê o que o Claude faz; o git só vê a sua máquina (e `--no-verify` o desliga); o GitHub vale para todo mundo. O que não tem trava fica no `CLAUDE.md` como conselho.

## O caminho de uma mudança

| Etapa | Peça | Barra |
|---|---|---|
| Editar | Regras `deny` em `.claude/settings.json` | O Claude ler `.env` e `secrets/` pela ferramenta Read (um `cat` pelo Bash passa) |
| | Hook `PostToolUse` (`.claude/hooks/formata.sh`) | Nada: formata o `.py` editado e devolve ao Claude o lint que não corrige sozinho |
| Commitar | pre-commit (`.pre-commit-config.yaml`), também nos commits do Claude | Lint, tipos e segredos nos arquivos em staging |
| | Hook `PreToolUse` (`.claude/hooks/protege-main.sh`), só para o Claude | Commit e push no `main`; `push --force` em qualquer branch |
| Encerrar a vez | Hook `Stop` (`.claude/hooks/testes.sh`), só para o Claude | O Claude parar com `make test` falhando |
| Push e PR | Regras `ask`, só para o Claude | `git push`, `gh pr create`, `git add -A` e coleta (`python -m pipeline`) sem a sua licença |
| | Ruleset `proteger-main` no GitHub | Push direto no `main`, force push e apagar o `main`, para qualquer pessoa |
| CI | `.github/workflows/ci.yml`: jobs `rota` e `qualidade` (`make ci`) | Rota inconsistente, lint, tipos, testes e segredos no histórico inteiro |
| Merge | Ruleset `proteger-main` | Merge sem os checks `rota` e `qualidade` verdes; outro método que não squash |

## O ruleset `proteger-main`

Não é arquivo do repositório: vive no GitHub (*Settings → Rules*). Vale para o branch padrão, sem exceções (nem o dono). Exige PR, só squash, os checks `rota` e `qualidade`, e proíbe force push e apagar o branch. Exige **zero** aprovações: a revisão é o teach-back, por disciplina, não por trava. Renomear um job do CI sem atualizar o ruleset prende todo merge em "aguardando".

Conferir o que está valendo: `gh api repos/eduardocanova23/quem-esta-do-seu-lado/rulesets`.

## Quando uma regra vira trava

Quando a violação é silenciosa, cara de desfazer e dá para checar mecanicamente. Quando depende de julgamento, o conselho basta: uma trava ali só seria cumprida no formato. Próxima candidata: ids de tema estáveis, como teste sobre `taxonomia/temas.yaml` quando ele existir.
