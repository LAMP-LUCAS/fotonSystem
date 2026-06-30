# EPIC-012: Observabilidade e Telemetria de Uso

**Data:** 2026-06-28
**Stakeholders:** Time Core (desenvolvimento), Equipe do escritório (beneficiários indiretos)
**Métrica de Sucesso:** Capacidade de medir e acompanhar a evolução da performance, uso e satisfação do sistema com dados reais e históricos

## Dor Atual

O Foton System não possui visibilidade sobre como está sendo utilizado:

- **Zero dados de uso real:** Não é possível saber quais funcionalidades são mais acionadas, com que frequência, ou se estão sendo usadas como projetado. Decisões de priorização são tomadas sem evidência.
- **Performance cega:** Operações como sincronização podem estar lentas, mas não há série histórica para confirmar tendências. A meta de 40% de redução no tempo de sincronização (EPIC-002) não pode ser validada sem baseline e medição contínua.
- **Satisfação descontextualizada:** A pesquisa NPS existe, mas a nota não carrega informações sobre o contexto de uso — quantas sessões o usuário teve, quantas operações realizou, qual o padrão de utilização. Uma nota 8 de um usuário novo tem significado diferente de uma nota 8 de um usuário experiente.
- **Gargalos invisíveis:** Sem métricas por operação, não é possível identificar quais funcionalidades são lentas, quais falham mais, ou quais dominam o tempo de uso.
- **Feedback isolado:** O usuário não tem um canal estruturado para fornecer contexto junto com sua avaliação — comentários e dados de uso não viajam juntos.

## Critérios de Sucesso do Negócio

- [ ] **Cobertura total de telemetria:** 100% das operações de feature registram automaticamente: timestamp, duração, sucesso/falha e contexto (quantos clientes/serviços envolvidos)
- [ ] **Rastreamento de sessão:** Cada execução do sistema é registrada como uma sessão distinta, com interface de origem (TUI vs MCP), duração e quantidade de operações
- [ ] **Série histórica de performance:** Operações como sincronização acumulam registros que permitem calcular tendências (está melhorando ou piorando?)
- [ ] **Satisfação com contexto:** Toda resposta NPS carrega automaticamente o contexto de uso do usuário (sessões, operações, tempo de uso) — permitindo correlacionar satisfação com padrão de uso
- [ ] **Exportação sob demanda:** O usuário pode optar por compartilhar seus dados de telemetria e NPS com o time de desenvolvimento em um formato autocontido, sem necessidade de infraestrutura de recebimento no lado do escritório
- [ ] **Dados 100% locais por padrão:** Nenhum dado sai da máquina do usuário sem ação explícita dele. Conformidade com LGPD (art. 7º) por design

## Métricas

| Métrica | Meta | Como medir |
|---------|------|-----------|
| Operações instrumentadas | 100% das features | Auditoria de código vs lista de operações |
| Dados de performance disponíveis | ≥ 90% das execuções registradas | Contagem de operation_log vs execuções esperadas |
| NPS com contexto | 100% das respostas com session_count + operation_count | Campo session_count ausente = inconformidade |
| Exportação | Zero dependência de servidor externo | A exportação gera arquivo sem chamada de rede |
| LGPD | Zero dado enviado sem consentimento explícito | Auditoria de código: nenhuma requisição HTTP nas rotas de telemetria/NPS |

## Histórico

| Data | Evento |
|------|--------|
| 2026-06-28 | EPIC-012 criado a partir da análise dos gaps de métricas do EPIC-002 (Review Sprint 5) |

## Especificações Técnicas

- SPEC-TELEMETRY-v1.0 (prevista — RULE-TELEMETRY-1.1 a 1.5)
- SPEC-UX-v1.2 (prevista — RULE-UX-9.1 expandida + RULE-UX-9.2)
