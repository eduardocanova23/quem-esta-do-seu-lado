# Conferência: docs/50-adr-hospedagem

Sessão de 17/11/2026: ADR 0005 (hospedagem), proposto. A branch não mexe em `db/marts`, `pipeline` nem em dado gerado; a seção Dados não se aplica.

## Afirmações

| Afirmação | Evidência | Situação |
| --- | --- | --- |
| Servidor: `capivara-mvp`, 3.815 MB de RAM (2.604 disponíveis), 29 GB livres de 38 GB, Nginx 1.18 e `capivara` ativos, sem Docker | `ssh hetzner 'hostname; free -m; df -h /; systemctl is-active capivara nginx; command -v docker; nginx -v'` em 17/11/2026 | conferido |
| `ufw` ativo, só 22, 80 e 443 de qualquer origem | `ssh hetzner 'ufw status'` em 17/11/2026 | conferido |
| Sem domínio nem HTTPS | Nota do vault `Eu/Servidor Hetzner - acesso e configuração` (14/11) | não conferido hoje |
| 27.242 arquivos, 211 MB no spike; ~7,7 KB por página | ADR 0003; 211e3/27242 = 7,75 por script | conferido (a conta) |
| Cloudflare Pages: 20 mil arquivos no grátis, 100 mil nos pagos, 25 MiB por arquivo | WebFetch developers.cloudflare.com/pages/platform/limits/ | conferido (por resumo) |
| Workers: 20 mil arquivos por versão no grátis, 100 mil no pago; requisições a arquivos estáticos "free and unlimited"; mínimo de US$ 5 por mês | WebFetch em workers/platform/limits/, workers/static-assets/billing-and-limitations/ e workers/platform/pricing/ | conferido (por resumo) |
| Cloudflare não guarda HTML nem JSON por padrão; plano grátis tem 10 regras de cache | WebFetch cache/concepts/default-cache-behavior/ e cache/how-to/cache-rules/ | conferido (por resumo) |
| "Guardar tudo" e limpeza completa disponíveis no plano grátis | As páginas não dizem por plano | não conferido |
| GitHub Pages: 1 GB, 100 GB por mês (brando), proibido para "online business" | WebFetch docs.github.com/.../github-pages-limits | conferido (por resumo) |
| Netlify grátis: 300 créditos, 20 por GB (~15 GB) | WebFetch netlify.com/pricing; se renova por mês não estava na página | conferido (por resumo) |
| Vercel Hobby: 100 GB e 1 milhão de requisições à CDN | WebFetch vercel.com/docs/plans/hobby | conferido (por resumo) |
| Vercel Hobby proíbe uso comercial | Não estava nas páginas abertas | não conferido |
| CX23 a € 5,99, 20 TB de tráfego na Europa | Página da Hetzner: "starting from € 5.99", "currently not available"; os 20 TB só em fontes de terceiros | não conferido |
| `.com.br` a R$ 40 por ano | Fontes secundárias (Teletime, NIC.br citado); registro.br não abriu pelo WebFetch | não conferido |
| US$ 5 ~ R$ 30 | Câmbio não aberto | não conferido |
| Placar 45 × 42 × 36, máximo 51 | Script: `{'A': 45, 'B': 42, 'C': 36} max 51` | conferido |
| As notas de 1 a 3 | Julgamento sobre a tabela de opções | não conferido |
| Troca de link simbólico é atômica | Propriedade do `rename(2)` em POSIX quando feita com `ln -s` num nome temporário e `mv -T`; não testei | não conferido |

## Vazios

Não se aplica: a branch não gera nem transforma dado.

## Retrospectiva

- Primeira versão do texto dizia que a 59ª legislatura alcança o teto de 100 mil arquivos do Workers; com ~30 mil por legislatura, quem passa é a 60ª. Corrigido antes do commit.
- O Eduardo estranhou "60ª legislatura" no resumo: o teto só pesa em 2035, e eu tinha apresentado como argumento forte. O ADR aceito diz que o custo é o que decide e que o teto pesa pouco.
- O mapa dizia "só a seta da busca chega a um servidor"; com o Nginx de origem, página fora do cache também chega. Corrigido para "só a busca chega ao banco".
