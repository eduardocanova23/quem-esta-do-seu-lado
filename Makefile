.PHONY: setup rota rota-check lint tipos test segredos ci atualizar conferir conferir-status conferir-dispensar

# Prepara a máquina: ambiente do uv.lock, gitleaks e hook do pre-commit
setup:
	@command -v uv >/dev/null || { echo "uv não encontrado: instale a versão de required-version do pyproject.toml (https://docs.astral.sh/uv/getting-started/installation/)." >&2; exit 1; }
	uv sync --locked
	scripts/instalar_gitleaks.sh
	uv run --locked pre-commit install

# Mostra a frente ativa e o próximo passo (docs/frentes.yaml)
rota:
	uv run --locked python scripts/rota.py

# Só valida a rota; sai com erro se ela estiver inconsistente
rota-check:
	uv run --locked python scripts/rota.py --check

lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check .

tipos:
	uv run --locked mypy

test:
	uv run --locked pytest

# Roda os passos de pipeline/passos.py para DATA (AAAA-MM-DD); sem DATA, hoje em Brasília
atualizar:
	uv run --locked python -m pipeline.passos --data $(or $(DATA),$(shell TZ=America/Sao_Paulo date +%F))

# Varre o histórico inteiro do git, não só o que está em staging
segredos:
	scripts/instalar_gitleaks.sh
	.venv/bin/gitleaks git --redact --verbose --no-banner

# Tudo, como no CI: o job qualidade roda exatamente este alvo
ci: rota-check lint tipos test segredos

# Confere o registro em docs/conferencias/<branch>.md e marca os dados atuais como conferidos (skill /conferir)
conferir:
	uv run --locked python scripts/conferir.py

# Sai com erro se a branch mudou dados que não foram conferidos (usado pelo hook Stop)
conferir-status:
	@uv run --locked --quiet python scripts/conferir.py --status

# Só com o ok do Eduardo: make conferir-dispensar MOTIVO="..."
conferir-dispensar:
	uv run --locked python scripts/conferir.py --dispensar "$(MOTIVO)"
