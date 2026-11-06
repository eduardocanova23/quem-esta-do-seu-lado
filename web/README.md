# web/

**Faz:** o site. As páginas são geradas depois do pipeline e servidas por CDN.
**Recebe:** os marts do dia (no build) e a `api/` (por HTTP, para busca e filtros).
**Entrega:** HTML estático por página, com ilhas interativas só onde há interação.
**Quem chama:** o visitante, pela CDN; a DAG `publicacao` dispara o build.

Regras: nunca importa o `pipeline/`; formatação de números e modelos de frase em `src/lib/`, testados; testes em `tests/` e `e2e/`.

Vazia até o ADR de framework e o marco `site.esqueleto`.
