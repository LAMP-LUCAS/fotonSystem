---
status: "draft"
sprint: "TBD"
---

# STORY-017: Integração das Entidades de Domínio no Fluxo de Produção

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.1.md`

## Descrição

Refatorar a camada de aplicação (use cases, services, repositories) para consumir as entidades `Client`, `Service` e `FinanceEntry` em vez de operar `pd.DataFrame` e `dict` crus. Esta story resolve o débito técnico deixado pela STORY-011, que modelou as entidades mas não as integrou.

## Regras

- **RULE-DOMAIN-1.1:** `Client` entity com `to_row()`, `from_row()`, `soft_delete()`, `restore()`, `is_active()` — já implementada, precisa ser usada
- **RULE-DOMAIN-1.2:** `Service` entity com `to_row()`, `from_row()`, `soft_delete()` — já implementada, precisa ser usada
- **RULE-DOMAIN-1.3:** `FinanceEntry` entity encapsulando tipo, valor, descrição, data, cliente — já implementada, precisa ser usada

## Critérios de Aceite

- [ ] `ExcelClientRepository.get_all_clients()` retorna `List[Client]` (não `pd.DataFrame`)
- [ ] `ExcelClientRepository.get_all_services()` retorna `List[Service]` (não `pd.DataFrame`)
- [ ] `CSVFinanceRepository.get_entries()` retorna `List[FinanceEntry]` (não `List[Dict]`)
- [ ] `client_crud.create_client()` recebe/retorna `Client` entity
- [ ] `FinanceService.add_entry()` recebe `FinanceEntry` entity
- [ ] Métodos `to_row()` e `from_row()` são usados na ponte repositório ↔ domínio
- [ ] Zero regressão nos 670+ testes existentes
- [ ] Backward compatibility: MCP tools mantêm assinatura atual

## Estimativa

8h

## Dependências

- STORY-011 (entidades modeladas — `partial`, pendente de integração)
- `ExcelClientRepository`, `CSVFinanceRepository`, `client_crud.py`, `FinanceService`
