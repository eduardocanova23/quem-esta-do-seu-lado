# Não-objetivos

_O que fica fora do MVP e por quê. O Claude lê esta lista em toda sessão._

Um item sai desta lista só por PR, dizendo que pergunta ele passa a responder. "Fora da fatia 1" quer dizer que pode voltar numa fatia seguinte; "fora do produto" quer dizer que não volta.

## Fora do produto

| O quê | Por quê |
| --- | --- |
| Nuvens de palavras e de adjetivos, resumo por IA de deputado ou proposição | Não respondem a nenhuma das três perguntas. Foram a colcha de retalhos da v1 |
| Clipping do Diário Oficial | Virou projeto próprio (Clipping DO-Rio) |
| Nota, selo ou "bom × ruim" para deputado ou partido | O requisito de neutralidade pede o mesmo tratamento para todo partido. A conclusão é de quem lê |
| Guardar o lado político de quem usa, mesmo com consentimento | Decisão do vault: o sentido político é dado sensível (LGPD, art. 5º, II, e art. 11) e nunca é guardado |
| Comparar legislaturas ou governos | [Diretriz](diretrizes.md#sempre-separar-legislaturas) |

## Fora da fatia 1 (pergunta 2)

| O quê | Por quê | Volta quando |
| --- | --- | --- |
| Perfis prontos que preenchem o lado ("trabalhador CLT", "agro") | As lentes são personas de classificação, o `lentes.yaml` tem erro conhecido e um perfil pronto soa como rótulo político ([histórias, decisão 2](historias.md#decisões-da-pergunta-2)) | Se o teste com 5 pessoas mostrar que escolher eixo a eixo trava |
| Autoria personalizada por temas escolhidos | Precisa de seletor de temas, que depende da busca e da taxonomia incremental | Marco `site.busca` |
| Lado no link compartilhado | [Histórias, decisão 4](historias.md#decisões-da-pergunta-2) | Não volta sem nova decisão |
| Placar ajustado (puxado para o partido) na página do deputado | É ferramenta de ranking. Para um deputado só, o k de n com o n à vista é mais honesto | Fatia 2 (pergunta 3), no ranking |
| Placar resumido nos eixos ralos (aborto, armas, apostas, LGBT, religião, valores na escola) | Têm 1 ou 2 votações cada na 57ª. A página mostra o voto a voto, sem número | Quando um eixo passar do n mínimo |
| Votações de destaque, de emenda e de comissão | Na comissão, a direção do parecer não se sabe. Destaques e emendas estão em aberto em [perguntas.md](perguntas.md#em-aberto) | Decisão em `metricas.md` |
| Página própria sobre "como a Câmara funciona" | Não responde a nenhuma das três perguntas. O estudante é atendido com explicação no lugar ([personas](personas.md#estudante-ou-professor)) | Se virar pergunta no banco |
| Login, conta e camada paga | Não respondem a nenhuma pergunta do MVP | Depois do MVP, por ADR |
| Senado | As três perguntas são sobre a Câmara | Pergunta nova no banco |
| Tema e proposição na caixa de busca da página inicial (H0.4, H0.5) | Precisam da taxonomia que se atualiza sozinha e de um servidor de busca; na primeira publicação a caixa acha deputado e partido | Marco `site.busca` |
| Exportação de dados para jornalista | Necessidade registrada em [personas](personas.md#jornalista-ou-pesquisador), sem história ainda | História própria |
