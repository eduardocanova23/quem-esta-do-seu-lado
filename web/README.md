# web/

**Faz:** o site. As páginas são geradas depois do pipeline e servidas por CDN.
**Recebe:** os marts do dia, em arquivo, no build; e a `api/`, por HTTP, só para a busca. Filtros, lado e ranking rodam no navegador sobre JSON gerado no build ([ADR 0002](../docs/decisoes/0002-forma-de-entrega-do-site.md)).
**Entrega:** HTML estático por página, com ilhas interativas só onde há interação.
**Quem chama:** o visitante, pela CDN; a DAG `publicacao` dispara o build.

Regras: nunca importa o `pipeline/`; formatação de números e modelos de frase em `src/lib/`, testados; testes em `tests/` e `e2e/`.

Framework: Astro com ilhas em React ([ADR 0003](../docs/decisoes/0003-framework-do-site.md)). Vazia até o marco `site.esqueleto`.
