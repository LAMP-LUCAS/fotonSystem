# Spec: Módulo Financeiro — v2.0

**Data:** 2026-06-25
**Versão:** 2.0
**Responsável:** Time Core
**Alterações:** Adicionadas regras de lucro por obra, projeção de fluxo de caixa, alerta de estouro, categorização de despesas, conciliação bancária, e dashboard geral avançado.

## 1. Problema (v2.0)

O módulo financeiro atual registra entradas e saídas, consulta saldos e gera resumo geral. Porém não oferece visão estratégica: o usuário não consegue ver lucro por obra, não há projeção de fluxo de caixa, custos podem ultrapassar o contrato sem alerta, despesas não são categorizadas, e o fechamento mensal requer exportação manual para Excel.

## 2. Solução Proposta (v2.0)

Evolução do módulo financeiro com inteligência analítica:

1. **Lucro por obra:** Cálculo automático de receitas - despesas por serviço, com indicadores de margem.
2. **Fluxo de caixa projetado:** Projeção para 30, 60 e 90 dias com base em recebíveis registrados e despesas recorrentes.
3. **Alerta de estouro:** Notificação automática quando custos acumulados atingem 80%, 90% e 100% do valor do contrato.
4. **Categorização de despesas:** Cada saída é categorizada por tipo (mão de obra, material, taxa, imposto, outros) para análise de composição de custos.
5. **Conciliação bancária:** Importação de extrato CSV para conciliação automática com lançamentos registrados.
6. **Dashboard geral avançado:** Faturamento mensal, lucro consolidado, inadimplência, top 5 clientes por receita.

## 3. Regras de Negócio

### 3.1 Lançamentos (mantido da v1.0 + expandido)
- **RULE-FINANCEIRO-1.1:** `tipo` deve ser `ENTRADA` (crédito) ou `SAIDA` (débito). Qualquer outro valor é rejeitado.
- **RULE-FINANCEIRO-1.2:** `valor` deve ser float positivo. Valores negativos ou zero são rejeitados.
- **RULE-FINANCEIRO-1.3:** `descricao` é string obrigatória (não vazia).
- **RULE-FINANCEIRO-1.4:** Ao registrar um lançamento, o POP de auditoria é acionado (evento auditado).
- **RULE-FINANCEIRO-1.5 (NOVA):** `categoria` é campo obrigatório para SAIDA. Valores válidos: `MAO_DE_OBRA`, `MATERIAL`, `TAXA`, `IMPOSTO`, `OUTROS`.
- **RULE-FINANCEIRO-1.6 (NOVA):** `data_vencimento` é campo opcional para ENTRADA. Quando preenchido, o valor é considerado um "recebível" para projeção de fluxo de caixa.
- **RULE-FINANCEIRO-1.7 (NOVA):** `servico_cod` é campo opcional que vincula o lançamento a um serviço específico do cliente. Permite cálculo de lucro por serviço.

### 3.2 Consultas (expandido v2.0)
- **RULE-FINANCEIRO-2.1:** `consultar_financeiro`: retorna saldo (entradas - saídas) e extrato completo de um cliente.
- **RULE-FINANCEIRO-2.2:** `resumo_financeiro_geral`: retorna dashboard com saldo de todos os clientes.
- **RULE-FINANCEIRO-2.3:** Clientes sem movimentação financeira não aparecem no extrato.
- **RULE-FINANCEIRO-2.4 (NOVA):** `lucro_por_servico`: calcula e retorna lucro líquido por serviço (entradas - saídas vinculadas ao serviço), margem percentual, e total de receitas/despesas.
- **RULE-FINANCEIRO-2.5 (NOVA):** `fluxo_caixa_projetado`: projeta saldo futuro para 30, 60 e 90 dias. Cálculo: saldo atual + entradas previstas (recebíveis com `data_vencimento` no período) - despesas recorrentes estimadas.
- **RULE-FINANCEIRO-2.6 (NOVA):** `painel_financeiro_cliente`: dashboard por cliente com lucro, faturamento, despesas por categoria (gráfico de pizza textual), indicador de estouro de orçamento, e inadimplência.

### 3.3 Alertas (NOVO v2.0)
- **RULE-FINANCEIRO-3.1 (NOVA):** Alerta de estouro: ao registrar uma SAIDA, sistema verifica se o total de saídas do serviço ultrapassou 80%, 90% ou 100% do valor total de entradas vinculadas ao mesmo serviço. Se sim, evento POP é gerado e notificação é exibida.
- **RULE-FINANCEIRO-3.2 (NOVA):** Alerta de inadimplência: entradas com `data_vencimento` passada e sem recebimento correspondente são listadas no dashboard como "em aberto".
- **RULE-FINANCEIRO-3.3 (NOVA):** Alerta de fluxo de caixa: se a projeção para 30 dias indicar saldo negativo, notificação é gerada.

### 3.4 Conciliação Bancária (NOVO v2.0)
- **RULE-FINANCEIRO-4.1 (NOVA):** `importar_extrato_csv`: importa arquivo CSV de extrato bancário com colunas `data, descricao, valor, tipo`. Cada linha é comparada com lançamentos existentes por valor aproximado (tolerância de R$0,01) e data (±3 dias).
- **RULE-FINANCEIRO-4.2 (NOVA):** Lançamentos conciliados recebem flag `conciliado: True`. Lançamentos do extrato sem correspondente são sugeridos como novos lançamentos.
- **RULE-FINANCEIRO-4.3 (NOVA):** Relatório de conciliação: lista lançamentos conciliados, não conciliados (no sistema mas não no extrato) e não identificados (no extrato mas não no sistema).

### 3.5 Dashboard Geral Avançado (NOVO v2.0)
- **RULE-FINANCEIRO-5.1 (NOVA):** `resumo_financeiro_geral` expandido para incluir: faturamento mensal (últimos 12 meses), lucro consolidado (entradas - saídas de todos os clientes), inadimplência total, top 5 clientes por receita, despesas por categoria (consolidado).
- **RULE-FINANCEIRO-5.2 (NOVA):** Exportação de relatório financeiro padronizado para contabilidade: CSV com colunas `cliente, servico, tipo, categoria, valor, data, descricao`, filtrado por período.

### 3.6 Persistência (mantido da v1.0)
- **RULE-FINANCEIRO-6.1:** Cada cliente tem seu próprio arquivo CSV de financeiro na pasta do cliente.
- **RULE-FINANCEIRO-6.2:** O dashboard geral é consolidado em `baseDados.xlsx`.

## 4. Relações
- Port: `finance_repository_port.py`
- MCP tools (existentes): `registrar_financeiro`, `consultar_financeiro`, `resumo_financeiro_geral`
- MCP tools (propostas): `lucro_por_servico`, `fluxo_caixa_projetado`, `painel_financeiro_cliente`, `importar_extrato_csv`, `relatorio_conciliacao`

## 5. Changelog

| Versão | Data | Mudanças |
|---|---|---|
| v1.0 | 2026-06-24 | Versão inicial |
| v2.0 | 2026-06-25 | Adicionado RULE-FINANCEIRO-1.5 a 1.7, 2.4 a 2.6, 3.1 a 3.3, 4.1 a 4.3, 5.1 a 5.2. Seções 1-2 reescritas. |