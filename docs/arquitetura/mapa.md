# Mapa do sistema

_Diagrama em Mermaid dos componentes e do fluxo de dados, da Câmara até a tela. Atualizado em todo PR que muda a arquitetura._

Estado: [ADR 0002](../decisoes/0002-forma-de-entrega-do-site.md) (entrega). Hospedagem, banco e modelo de busca ainda sem ADR.

```mermaid
flowchart LR
  camara[Câmara: arquivos em lote e API] --> pipeline["pipeline/ (make atualizar)"]
  pipeline --> pg[(Postgres: raw, core, marts)]
  pg --> export[marts do dia em arquivo, conferidos pelo contrato]
  export --> build["web/: build gera HTML e JSON"]
  build --> cdn[CDN]
  cdn --> nav[Navegador: lado, filtros e ranking calculados aqui]
  nav -- só o texto da busca --> api["api/: busca, papel só-leitura"]
  api --> pg
```

Na hora do acesso, só a seta da busca chega a um servidor. O resto é arquivo pronto na CDN.
