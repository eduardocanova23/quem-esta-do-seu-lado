# api/

**Faz:** a API de busca em FastAPI, a única parte do site que consulta o banco na hora do acesso.
**Recebe:** consultas de busca e filtros vindos do site.
**Entrega:** resultados em JSON e o schema OpenAPI, do qual saem os tipos TypeScript do `web/`.
**Quem chama:** o site, por HTTP.

Regras: rotas finas, consultas num módulo próprio, entrada validada por Pydantic, SQL sempre parametrizado, papel `app` só-leitura. Testes em `tests/`.

Vazia até o ADR de busca.
