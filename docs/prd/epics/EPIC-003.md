# EPIC-003: Automação Comercial e Geração de Documentos

**Data:** 2026-06-25
**Stakeholders:** Setor comercial do escritório, Time Core (manutenção)
**Métrica de Sucesso:** Redução de 80% no tempo de geração de propostas e contratos

## Dor Atual

A engine de documentos do Foton System já existe e é funcional, mas o usuário não confia nela para uso diário:

- **Placeholders incompreensíveis:** Variáveis ausentes nos dados geram "---" ou "None" no documento final, forçando revisão manual linha a linha.
- **Falhas silenciosas:** Fórmulas de cálculo (`[calculo: @areaTotal * @execcub]`) quebram sem alerta ao usuário — o documento é gerado, mas o valor fica incorreto.
- **Sem pré-visualização:** Não há como validar as variáveis antes de gerar o documento. O erro só aparece no PDF final.
- **Sem histórico:** Documentos gerados não ficam registrados na ficha do cliente. O comercial não sabe o que já foi emitido.
- **Geração individual:** Cada documento exige uma operação separada. Proposta, contrato e anexo demandam três fluxos distintos.

## Critérios de Sucesso do Negócio

- [ ] Validação prévia de variáveis antes da geração, com relatório de variáveis resolvidas, não encontradas e fórmulas aplicadas
- [ ] Geração em lote: um único comando gera proposta + contrato + anexo simultaneamente
- [ ] Templates padronizados de proposta, contrato e anexo acessíveis por atalho no menu principal
- [ ] Histórico de documentos gerados disponível na ficha do cliente com data, tipo e status
- [ ] Zero placeholders não resolvidos em documentos finais — variável ausente gera erro visível antes da geração
- [ ] Regeneração de documento com dados atualizados sem perder o histórico da versão anterior
- [ ] Documentos gerados nomeados com padrão legível (`CLIENTE_SERVICO_TIPO_DATA.pptx`)

## Métricas

- 80% menos retrabalho manual em documentos
- 100% dos documentos com variáveis resolvidas (zero placeholders)
- Tempo médio para emitir proposta + contrato reduzido de 40 min para 8 min
- NPS do setor comercial ≥ 8 (pesquisa pós-implementação)
