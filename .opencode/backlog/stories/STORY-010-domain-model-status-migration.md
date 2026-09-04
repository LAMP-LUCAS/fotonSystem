---
status: "done"
sprint: "2026-SPRINT-5"
---

# STORY-010: Domain Model — Migração da Coluna Status

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.1.md`

## Descrição

Implementar a migração transparente da coluna `Status` no Excel para suportar soft delete. Garantir fallback `"ATIVO"` para bases existentes sem a coluna, atualizar `_ensure_database_exists()` e adaptar `FakeClientRepository` para os testes.

## Regras Implementadas

- **RULE-DOMAIN-1.4:** Coluna `Status` com fallback `"ATIVO"` se ausente
- **RULE-DOMAIN-1.5:** `_ensure_database_exists()` criar colunas `Status` + `CodCliente`
- **RULE-DOMAIN-1.6:** `FakeClientRepository` atualizado para coluna `Status`

## Critérios de Aceite

- [ ] `get_clients_dataframe()` retorna `Status="ATIVO"` para bases sem a coluna
- [ ] `get_services_dataframe()` retorna `Status="ATIVO"` para bases sem a coluna
- [ ] `_ensure_database_exists()` cria colunas `Status` e `CodCliente` em bases novas
- [ ] `FakeClientRepository` suporta coluna `Status` em todos os métodos
- [ ] 410+ testes existentes continuam passando (zero regressão)

## Estimativa

3h
