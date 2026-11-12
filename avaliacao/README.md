# avaliacao/

**Faz:** guarda o que mede a qualidade do classificador de temas.
**Recebe:** gabaritos ouro A e B e as 38 personas originais e os dois conjuntos independentes congelados (10 + 10, cada um com SHA256).
**Entrega:** os limiares de acurácia e o placar das personas usados como teste de regressão.
**Quem chama:** o script de avaliação, a cada mudança de taxonomia, prompt ou modelo.

Regra: depois de congelado, nada aqui se edita à mão. O commit e o SHA256 de cada conjunto ficam registrados.

Vazia até o marco da frente `taxonomia`.
