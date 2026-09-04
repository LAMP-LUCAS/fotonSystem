# EPIC-007: Controle de Cronograma e Marcos de Obra

**Data:** 2026-06-25
**Stakeholders:** Equipe técnica, Gerentes de obra, Clientes finais (indiretos)
**Métrica de Sucesso:** Redução de 50% nos atrasos causados por falha de comunicação ou falta de acompanhamento

## Dor Atual

O Foton System não possui nenhum recurso de gestão de prazos, forçando o uso de ferramentas externas desconectadas:

- **Cronograma externo:** O planejamento de obra é feito em software separado (MS Project, Excel, Trello) sem qualquer vínculo com o cadastro de clientes ou financeiro do Foton.
- **Atrasos não notificados:** Quando uma etapa atrasa (fornecedor, aprovação, clima), ninguém é notificado automaticamente. O impacto só aparece na próxima reunião de obra.
- **Sem rastro de desvios:** Não há registro do planejado versus o executado. A mesma obra pode atrasar pelo mesmo motivo várias vezes sem que isso seja identificado.
- **Financeiro descolado:** Multas por atraso, penalidades contratuais e impacto no fluxo de caixa não são registrados nem associados ao cronograma.
- **Entrega sem checklist:** Não há um roteiro formal de conclusão de marcos. Itens importantes (limpeza, documentos, assinaturas) são esquecidos na entrega.

## Critérios de Sucesso do Negócio

- [ ] Marcos de obra configuráveis por serviço com data planejada, data real e responsável
- [ ] Notificação automática quando um marco não é concluído na data planejada
- [ ] Indicador visual de desvio (planejado vs executado) por serviço
- [ ] Checklist de conclusão por marco com itens obrigatórios e opcionais
- [ ] Histórico de alterações de cronograma com registro de justificativa e responsável
- [ ] Integração com financeiro: registro automático de multa ou penalidade ao marcar atraso
- [ ] Relatório de cumprimento de prazos por cliente para reunião de prestação de contas

## Métricas

- Zero atrasos não notificados ao responsável
- 100% dos marcos com registro de conclusão (checklist preenchido)
- Tempo médio de desvio detectado reduzido de 7 dias para 1 dia
- NPS dos gerentes de obra ≥ 7 (pesquisa pós-implementação)