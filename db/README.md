# db/

**Faz:** guarda o schema do Postgres e o SQL que monta as tabelas do site.
**Recebe:** mudanças de schema revisadas em PR.
**Entrega:** `migrations/` (Alembic, uma por mudança, sempre com volta) e `marts/` (um arquivo SQL por mart).
**Quem chama:** o papel `migrador` aplica as migrations; o `pipeline/` roda os marts na publicação.

O schema de cada mart é o contrato com o site e fica documentado em `docs/dados/`, no mesmo PR.

Vazia até o marco `dados.modelo`.
