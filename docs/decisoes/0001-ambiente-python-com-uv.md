# 0001: ambiente Python com uv e lockfile, em Python 3.13

Status: aceito, 2026-11-09. Issue #6.

## Contexto

O repositório só tem um script Python hoje, mas o método já prevê pipeline, API de busca em FastAPI, Alembic e DAGs do Airflow. Pela regra 7 do método, a decisão se toma por esse tamanho, não pelas 4 ferramentas de desenvolvimento do momento.

Sem arquivo de trava, cada instalação resolve as dependências indiretas de novo, e o CI e as máquinas locais podem divergir sem aviso. A versão do Python também precisa sair do 3.10 que o sistema e o CI usam: `pre-commit` 4.7.0 e `apache-airflow` 3.4.0 exigem 3.11 ou mais novo.

## Opções

| Opção | Trava indiretas | Gerencia a versão do Python | Monorepo Python (`pipeline/`, `api/`) | Ferramenta nova |
| --- | --- | --- | --- | --- |
| `venv` + `requirements-dev.txt` | Não | Não | À mão | Nenhuma |
| `pip-tools` | Sim | Não | À mão, um arquivo por grupo | Uma, sobre o pip |
| Poetry | Sim | Não | Sem workspaces nativos | Uma |
| **uv** | Sim, com hashes, num `uv.lock` | Sim | Workspaces nativos, um lock só | Um binário |

## Critérios, com peso

1. Builds reproduzíveis no CI e localmente (peso 3).
2. Aguentar os vários pacotes Python já previstos sem migrar de ferramenta (peso 3).
3. Fixar a versão do Python no repositório, sem depender do sistema (peso 2).
4. Poucas peças para entender (peso 1).

## Decisão

`uv` para ambiente e dependências, com `pyproject.toml` e `uv.lock` versionados, e Python 3.13, fixado em `.python-version`.

O 3.13 está na faixa aceita pelo Airflow 3.4.0 (3.11 a 3.14). Fica um degrau atrás do topo dessa faixa para dar folga às bibliotecas de embeddings, ainda não escolhidas.

### O que acontece por baixo

`uv sync` lê o `pyproject.toml`, resolve as versões, grava todas no `uv.lock` com os hashes dos arquivos e cria o `.venv`, um ambiente virtual comum. `uv sync --locked` falha se o lock não bate com o `pyproject.toml`. `uv run <comando>` executa dentro desse ambiente. Ou seja, o resultado é o mesmo ambiente que `python -m venv` e `pip install` criariam; o uv decide as versões e faz a instalação.

## Consequências

- `make setup` e o CI dependem do binário do `uv`, com versão fixada.
- Dependência nova entra por `uv add`, e o diff do `uv.lock` vem no PR.
- O Python do sistema deixa de importar. `make rota` e o hook de início de sessão passam a rodar pelo `uv`.
- `pipeline/` e `api/` poderão virar membros de um workspace sem trocar de ferramenta.

## Quando revisitar

- Se o `uv` deixar de ser mantido ou mudar de licença.
- Se uma dependência obrigatória não suportar Python 3.13.
