# Diretrizes

_Inegociáveis. Valem para qualquer decisão de dados, classificação ou produto. Contrariar uma delas pede um ADR em `docs/decisoes/`._

O que as personas perguntam está em [perguntas.md](perguntas.md). Origem: nota do vault "Câmara v2 - diretrizes" (02/11/2026). A versão viva é esta.

## Personas são o critério central

Toda decisão de classificação é julgada por uma pergunta: **alguma persona faria essa busca e ficaria satisfeita com a resposta?** Isso vale para criar, juntar ou abrir um tema, criar um eixo de direção, nomear um nó ou escolher um limiar.

- Cada mudança se justifica citando a persona e a busca que ela melhora.
- Depois de cada mudança, o teste de personas roda de novo e o placar ✅/🟡/❌ é reportado antes e depois.
- Tema ou eixo que nenhuma persona usa não entra.
- A validação usa um **conjunto independente e congelado** de personas, separado do usado para ajustar. Sem isso, vira overfitting.

**Por quê:** na v1, as métricas internas (acurácia entre irmãos, estabilidade dos macrotemas) ficaram boas, mas a árvore falhava para gente real. Não havia tema de servidor público nem de aborto, e "saidinha" caía em meio ambiente. Na v1 eram 38 personas e 161 buscas em `scripts/testar_personas_arvore.py`, com o relatório em `data/classificacao_temas/teste_personas/RELATORIO_PERSONAS.md`.

**Cuidado:** o tree testing (achar o tema clicando) mede navegação, que talvez nem seja o uso principal. O produto precisa **agregar** ("o deputado X é ativo no meu tema? votou no meu sentido?"). A métrica se escolhe pelo uso real. A generalidade está na pergunta, não no tema (decisão do vault de mesmo nome).

## Sempre incremental

A Câmara muda todo dia: proposições novas, situações que mudam, votações, discursos, posses, suplências, trocas de partido e, de tempos em tempos, uma legislatura nova. Então:

- Todo pipeline de coleta e de enriquecimento processa **só o delta** desde a última execução e é **idempotente**: rodar duas vezes não duplica nada.
- Nada é "carga única". Se uma etapa só funciona do zero, ela está errada.
- Toda estrutura derivada (temas, atribuições, casos da mídia) aceita item novo **sem ser reestruturada**. Proposição nova é atribuída aos temas que existem. Tema novo nasce de sinais: a fila de "nenhum serve", buscas sem resultado e apelidos novos da mídia. De tempos em tempos, roda a jardinagem.
- A taxonomia é versionada e descartável, não um monumento.
- Legislatura nova é um evento esperado no desenho, não uma migração.

**Por quê:** na v1, as coletas avulsas nunca revisitavam o que já tinham visto (o `10_coletar_discursos.py` não pegava discurso novo de deputado já coletado), e a atualização semanal passou meses sem atualizar deputados. O banco ficava defasado em silêncio.

## Sempre separar legislaturas

Legislaturas diferentes não se comparam. Cada métrica, ranking, perfil ou agregado é calculado **dentro de uma legislatura**, e a interface sempre deixa claro de qual se trata (a v1 tinha o seletor 56ª/57ª).

- Composição, partidos, blocos e governo mudam entre legislaturas. Juntá-las mistura contextos que não se comparam.
- Pelo mesmo motivo, **o voto se separa por governo**: "votar contra" depende de quem governa. Na v1, o PL votou contra 6% das vezes no governo Bolsonaro e 36% no governo Lula; o PT foi de 33% para 13%.
- Deputado que aparece em duas legislaturas tem dois perfis, um por legislatura. A condição de titular, suplente ou efetivado também é de cada legislatura.

## Construir para o tamanho que já se sabe que vem

Decisão de fundação se toma pelo que **já se sabe** que o projeto vai precisar, não pelo tamanho dele hoje. "Dá menos trabalho agora" não é argumento. Trabalho a mais no início é aceitável quando evita refazer depois.

O teste, nesta ordem:

1. Já se sabe que isso vai ser necessário (está no método, num ADR, na rota)? Se é só "talvez um dia", não se faz: é especulação, e trabalho desnecessário continua proibido.
2. Deixar para depois obriga a refazer ou migrar algo? Se sim, faz-se direito agora. Se dá para acrescentar depois sem retrabalho, pode esperar.

Exemplo (09/11/2026, Fase 0, passo 7): com 4 dependências, `venv` e `requirements.txt` bastavam. A opção foi recusada porque o pipeline, a API e o Airflow já estão no plano; ficou o `uv` com lockfile ([ADR 0001](../decisoes/0001-ambiente-python-com-uv.md)). Já o Prettier e o Dependabot esperaram, porque entram depois sem refazer nada.

**Por quê:** na v1, mesmo sabendo que o projeto cresceria, decisões ruins foram tomadas "porque daria menos trabalho". O exemplo registrado: um framework escolhido por conveniência virou teto de design (Streamlit, depois FastAPI, Jinja2 e Plotly).
