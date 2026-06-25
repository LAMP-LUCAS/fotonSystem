---
status: "done"
sprint: "2026-SPRINT-5"
---

# STORY-012: CRUD — Ferramentas de Delete/Restore (MCP)

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Descrição

Criar 4 novas MCP tools para completar o CRUD: `remover_cliente`, `restaurar_cliente`, `remover_servico`, `atualizar_servico`. Todas com soft delete, backup `.bak` antes de operações destrutivas e POP auditado.

## Regras Implementadas

- **RULE-DOMAIN-2.1:** `remover_cliente` — soft delete, backup `.bak`, POP, `confirmar=False`
- **RULE-DOMAIN-2.2:** `restaurar_cliente` — lista deletados, restaura, POP
- **RULE-DOMAIN-2.3:** `remover_servico` — soft delete serviço, backup `.bak`, POP
- **RULE-DOMAIN-2.4:** `atualizar_servico` — update campo específico, POP
- **RULE-DOMAIN-2.7:** Toda operação destrutiva gera evento de auditoria POP

## Critérios de Aceite

- [ ] `remover_cliente` registrada no MCP, soft delete com backup `.bak`, POP auditado
- [ ] `restaurar_cliente` lista clientes deletados antes de restaurar, POP auditado
- [ ] `remover_servico` soft delete com backup `.bak`, POP auditado
- [ ] `atualizar_servico` permite alterar campo específico, POP auditado
- [ ] Backup `.bak` criado antes de toda operação destrutiva
- [ ] Evento POP registrado para cada operação (tipo, timestamp, usuário, descrição)
- [ ] Testes: soft delete ativo, duplo delete, restore deletado, restore ativo (no-op), serviço inexistente
- [ ] Zero regressão

## Estimativa

8h
