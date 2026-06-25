# Spec: Módulo Financeiro

**Data:** 2026-06-24
**Versão:** 1.0
**Responsável:** Time Core
**Status:** OBSOLETA — Substituída por SPEC-FINANCEIRO-v2.0 (2026-06-25)

## 1. Problema
O escritório precisa registrar entradas e saídas financeiras por cliente, consultar saldos individuais e ter um dashboard geral do escritório.

## 2. Solução Proposta
Módulo financeiro com persistência por cliente (CSV na pasta do cliente) e dashboard consolidado em Excel.
- Registro de entradas (crédito) e saídas (débito)
- Consulta de saldo por cliente
- Resumo financeiro geral (todos os clientes)
- Operações auditadas via sistema POP

## 3. Regras de Negócio

### 3.1 Lançamentos
- **RULE-FINANCEIRO-1.1:** `tipo` deve ser `ENTRADA` (crédito) ou `SAIDA` (débito). Qualquer outro valor é rejeitado.
- **RULE-FINANCEIRO-1.2:** `valor` deve ser float positivo. Valores negativos ou zero são rejeitados.
- **RULE-FINANCEIRO-1.3:** `descricao` é string obrigatória (não vazia).
- **RULE-FINANCEIRO-1.4:** Ao registrar um lançamento, o POP de auditoria é acionado (evento auditado).

### 3.2 Consultas
- **RULE-FINANCEIRO-2.1:** `consultar_financeiro`: retorna saldo (entradas - saídas) e extrato completo de um cliente.
- **RULE-FINANCEIRO-2.2:** `resumo_financeiro_geral`: retorna dashboard com saldo de todos os clientes.
- **RULE-FINANCEIRO-2.3:** Clientes sem movimentação financeira não aparecem no extrato.

### 3.3 Persistência
- **RULE-FINANCEIRO-3.1:** Cada cliente tem seu próprio arquivo CSV de financeiro na pasta do cliente.
- **RULE-FINANCEIRO-3.2:** O dashboard geral é consolidado em `baseDados.xlsx`.

## 4. Relações
- Port: `finance_repository_port.py`
- MCP tools: `registrar_financeiro`, `consultar_financeiro`, `resumo_financeiro_geral`
