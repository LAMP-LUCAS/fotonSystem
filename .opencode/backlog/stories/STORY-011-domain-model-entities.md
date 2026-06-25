---
status: "ready"
sprint: "2026-SPRINT-5"
---

# STORY-011: Domain Model — Entidades de Domínio

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Descrição

Criar as entidades de domínio `Client`, `Service` e `FinanceEntry` com métodos `to_row()`, `from_row()`, `soft_delete()`, `restore()` e `is_active()`. Encapsular regras de negócio nas entidades em vez de operar DataFrames crus.

## Regras Implementadas

- **RULE-DOMAIN-1.1:** `Client` entity com `to_row()`, `from_row()`, `soft_delete()`, `restore()`, `is_active()`
- **RULE-DOMAIN-1.2:** `Service` entity com `to_row()`, `from_row()`, `soft_delete()`
- **RULE-DOMAIN-1.3:** `FinanceEntry` entity encapsulando tipo, valor, descrição, data, cliente

## Critérios de Aceite

- [ ] `Client` entity criada em `modules/clients/domain/models/client.py`
- [ ] `Service` entity criada em `modules/clients/domain/models/service.py`
- [ ] `FinanceEntry` entity criada em `modules/clients/domain/models/finance_entry.py`
- [ ] `to_row()` retorna dict compatível com DataFrame do Excel
- [ ] `from_row()` é classmethod que cria entidade a partir de row do Excel
- [ ] `soft_delete()` altera status para `"DELETADO"`
- [ ] `restore()` altera status para `"ATIVO"`
- [ ] `is_active()` retorna `True` apenas se `status == "ATIVO"`
- [ ] Testes unitários para todas as entidades (mín. 6 cenários por entidade)
- [ ] Zero regressão nos 410+ testes existentes

## Estimativa

5h
