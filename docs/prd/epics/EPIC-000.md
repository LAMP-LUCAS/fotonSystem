# EPIC-000: Jornada do Cliente AECD — Ciclo de Vida Completo

**Data:** 2026-06-25
**Stakeholders:** Todos os setores do escritório, Sócios, Time Core
**Métrica de Sucesso:** Redução de 60% no retrabalho entre etapas do ciclo de vida do cliente

## Dor Atual

O Foton System trata clientes, documentos, financeiro e cronograma como silos isolados. Não há uma visão unificada de onde cada cliente está no ciclo de vida do escritório:

- **Sem visão de funil:** O comercial não sabe quantos clientes estão em prospecção, quantos são obras em andamento e quantos estão em pós-entrega. Clientes parados ou abandonados não são identificados.
- **Transições manuais:** Quando um cliente passa de "proposta emitida" para "contrato assinado", ninguém é notificado. O financeiro só descobre que há contrato quando o primeiro pagamento entra.
- **Dados replicados:** Informações do cliente são digitadas novamente a cada etapa (proposta → contrato → obra → financeiro), gerando retrabalho e inconsistências.
- **Sem gatilhos:** A conclusão de uma etapa (ex: aprovação do projeto executivo) não dispara automaticamente a etapa seguinte (ex: início da cotação de materiais).
- **Sem métricas de ciclo:** Não é possível medir tempo médio entre proposta e assinatura, entre assinatura e início de obra, ou entre etapas — impedindo melhorias de processo.

## Critérios de Sucesso do Negócio

- [ ] Mapa visual do ciclo de vida do cliente com estágios: Prospect → Proposta → Negociação → Contrato → Serviços → Execução → Medição → Entrega → Pós-obra
- [ ] Indicador de estágio atual visível em cada ficha de cliente (INFO-*.md)
- [ ] Gatilhos automáticos entre estágios: proposta aprovada → cria serviço automaticamente; serviço concluído → notifica financeiro
- [ ] Histórico de transições de estágio com data, responsável e justificativa
- [ ] Dashboard de funil: quantos clientes em cada estágio com tempo de permanência
- [ ] Notificação de clientes parados (>30 dias sem avanço de estágio)
- [ ] Métricas de ciclo: tempo médio por estágio, taxa de conversão proposta→contrato, taxa de conversão contrato→obra

## Métricas

- Tempo médio entre proposta e contrato reduzido em 40%
- Zero clientes parados por mais de 60 dias sem notificação
- 100% dos clientes com estágio atual registrado e visível
- Dashboard de funil atualizado em tempo real na TUI

## Dependências

| Este épico depende de | Para fornecer |
|---|---|
| EPIC-002 (Domínio) | Entidades Cliente/Serviço com campos de estágio |
| EPIC-003 (Documentos) | Geração de proposta/contrato como transição de estágio |
| EPIC-006 (Financeiro) | Indicador de inadimplência como bloqueio de estágio |
| EPIC-007 (Cronograma) | Avanço de marcos como gatilho de transição |
| EPIC-001 (UX TUI) | Interface de navegação e dashboard de funil |

## Relação com Outros Épicos

O EPIC-000 é um épico **transversal** que orquestra os demais. Ele não substitui nenhum épico existente, mas define como eles se conectam na jornada do cliente. Cada épico contribui com dados e eventos para alimentar o mapa de ciclo de vida.