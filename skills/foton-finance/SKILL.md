---
name: foton-finance
description: Gestão financeira do escritório de arquitetura — entradas, saídas, saldos por cliente e dashboard geral
---

# Foton Skill: Financeiro

Skill especializada em **gestão financeira** do Foton System.
Carregue esta skill quando a tarefa envolver registrar movimentações ou consultar saldos.

## Skills relacionadas

Este skill faz parte do ecossistema Foton. Consulte as demais conforme necessário:

| Skill | Quando usar |
|---|---|
| `foton-architecture` | Visão geral do sistema, primeiros passos |
| `foton-clients` | Cadastro e fichas de clientes (contexto financeiro) |
| `foton-documents` | Gerar contratos, propostas (valores financeiros) |
| `foton-rag` | Buscar conhecimento em projetos passados |

## Ferramentas

| Ferramenta | Descrição |
|---|---|
| `registrar_financeiro` | Entrada (ENTRADA) ou saída (SAIDA) no CSV do cliente |
| `consultar_financeiro` | Saldo e extrato de um cliente específico |
| `resumo_financeiro_geral` | Dashboard financeiro de todo o escritório |

## Workflows

### Registrar movimentação
1. `consultar_financeiro(cliente)` — ver saldo atual
2. `registrar_financeiro(cliente, descricao, valor, "ENTRADA"|"SAIDA")`
3. `consultar_financeiro(cliente)` — confirmar atualização

### Dashboard executivo
1. `resumo_financeiro_geral()` — visão geral do escritório
2. `consultar_financeiro(cliente)` — detalhar cliente específico

### Sincronização periódica
1. `sincronizar_base()` — alinhar Excel mestre com filesystem

## Convenções

- **Valores**: sempre passar como float (ex: `1500.50`), nunca como string formatada
- **Tipos**: `'ENTRADA'` para crédito, `'SAIDA'` para débito
- **POP Auditado**: toda movimentação passa pelo sistema de auditoria
- **Sincronização**: rodar `sincronizar_base` após lotes de registros
