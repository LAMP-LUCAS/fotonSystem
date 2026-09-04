---
status: "done"
sprint: "2026-SPRINT-5"
completed: "2026-06-26"
---

# STORY-018: POP Audit para `atualizar_ficha_cliente`

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.1.md`

## Descrição

Implementar POP auditado para `atualizar_ficha_cliente` via `OpUpdateClientInfo(BaseOp)`. Atualmente a ferramenta MCP `atualizar_ficha_cliente` executa append/replace/remove/field sem auditoria POP. Esta story adiciona o fluxo completo: validação → execução → `AuditLogger.log_event()` obrigatório em todas as operações, inclusive falha.

## Regras

- **RULE-DOMAIN-2.8:** `atualizar_ficha_cliente` (append, replace, remove, field) deve passar por POP auditado via `OpUpdateClientInfo(BaseOp)` — validação → execução → `AuditLogger.log_event()` obrigatório em todas as operações, inclusive falha.

## Critérios de Aceite

- [ ] `OpUpdateClientInfo(BaseOp)` criado com método `execute(cliente, secao, conteudo, modo)` onde `modo ∈ {append, replace, remove, field}`
- [ ] Validação executada antes da operação: cliente existe, seção não vazia, modo válido
- [ ] `AuditLogger.log_event()` chamado em caso de sucesso (tipo, timestamp, descrição)
- [ ] `AuditLogger.log_event()` chamado em caso de falha (exceção capturada e registrada)
- [ ] `atualizar_ficha_cliente` (MCP tool) delegada para `OpUpdateClientInfo`
- [ ] Backup `.bak` mantido antes da operação (já existente, não quebrar)
- [ ] Testes: POP registrado em append com sucesso, POP registrado em replace com sucesso, POP registrado em falha (cliente inexistente), POP registrado em falha (modo inválido), backup preservado, zero regressão

## Estimativa

4h

## Dependências

- STORY-012 — implementou `BaseOp`, `AuditLogger`, padrão POP (RULE-DOMAIN-2.7)
- `atualizar_ficha_cliente` já existe como MCP tool (precisa ser refatorada)
