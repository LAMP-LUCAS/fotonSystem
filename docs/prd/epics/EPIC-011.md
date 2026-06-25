# EPIC-011: Controle de Qualidade e Inspeção

**Data:** 2026-06-25
**Stakeholders:** Equipe técnica, Gerentes de obra, Clientes finais, Fiscal
**Métrica de Sucesso:** Redução de 50% em não-conformidades recorrentes e 100% dos marcos com checklist preenchido

## Dor Atual

O escritório não possui controles formais de qualidade, expondo o negócio a retrabalho, insatisfação de clientes e riscos legais:

- **Sem checklist de entrega:** Não há um roteiro formal de verificação antes da entrega de cada etapa. Itens críticos (limpeza, documentos, funcionamento de instalações) são esquecidos regularmente.
- **Não-conformidades não rastreadas:** Quando um problema é identificado (material fora do especificado, serviço mal executado), não há registro formal. O mesmo problema se repete em obras diferentes sem que a gerência perceba.
- **Sem inspeção programada:** Não há agenda de inspeções obrigatórias (fundações, estrutura, instalações, acabamento). Inspeções são feitas "quando sobra tempo" ou após o problema aparecer.
- **Aprovação de terceiros sem rastro:** Aprovações do cliente ou da fiscalização não são registradas formalmente. Em caso de discordância posterior, não há evidência de aprovação.
- **Sem métricas de qualidade:** O escritório não sabe quantas não-conformidades foram abertas, quantas foram fechadas ou qual o tempo médio de correção. Melhorias contínuas são impossíveis sem dados.

## Critérios de Sucesso do Negócio

- [ ] Checklists configuráveis por tipo de serviço (fundação, estrutura, alvenaria, instalações, acabamento) com itens obrigatórios e opcionais
- [ ] Registro de não-conformidade com: descrição, data, responsável, severidade (crítica/maior/menor), plano de ação e data de fechamento
- [ ] Agenda de inspeções com notificação automática ao responsável na data programada
- [ ] Relatório de inspeção exportável em PDF com foto e assinatura digital do inspetor
- [ ] Dashboard de qualidade: NCs abertas por severidade, tempo médio de correção, NCs recorrentes por tipo
- [ ] Registro de aprovação formal (cliente ou fiscalização) com data, responsável e anexo de documento
- [ ] Bloqueio de avanço de cronograma: marcos críticos não podem ser concluídos sem checklist aprovado e sem NCs críticas em aberto
- [ ] Histórico de qualidade por serviço com gráfico de evolução de conformidade ao longo do tempo

## Métricas

- Zero entregas sem checklist preenchido e aprovado
- 100% das não-conformidades críticas com plano de ação em até 48h
- Tempo médio de correção de NC reduzido em 40%
- Dashboard de qualidade com dados dos últimos 12 meses

## Dependências

| Este épico depende de | Para fornecer |
|---|---|
| EPIC-002 (Domínio) | Entidades Serviço e Cliente |
| EPIC-007 (Cronograma) | Marcos para bloqueio/liberação por checklist |
| EPIC-010 (Diário de Obra) | Registro diário alimenta checklists |
| EPIC-001 (UX TUI) | Formulários e dashboards |