---
status: "done"
sprint: "2026-SPRINT-5"
---

# STORY-019: Correção dos Débitos Técnicos P1 (Review Sprint 5)

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.1.md`, `MOD-SYNC/SPEC-SYNC-v1.0.md`

## Descrição

Corrigir os 3 itens P1 identificados no relatório `2026-SPRINT-5-REVIEW.md`:

1. Refatorar delete/restore em `excel_client_repository.py` para usar `Client.soft_delete()`/`Service.soft_delete()` em vez de manipular `pd.DataFrame` diretamente
2. Redirecionar TUI menu (opções 5/6) para `pipeline_sincronizacao` em vez de `client_crud.sync_*`
3. Remover `except Exception: pass` em `audit_logger.py:64-65`

## Regras Implementadas

- **RULE-DOMAIN-1.1:** `Client.soft_delete()`/`restore()` usado no repositório real e fake
- **RULE-DOMAIN-1.2:** `Service.soft_delete()` usado no repositório real e fake
- **RULE-DOMAIN-3.4:** Ferramentas legadas delegam ao pipeline (TUI)
- **RULE-DOMAIN-2.7:** POP auditado sem `except: pass`

## Critérios de Aceite

- [x] `excel_client_repository.soft_delete_client()` usa `Client.soft_delete()`
- [x] `excel_client_repository.restore_client()` usa `Client.restore()`
- [x] `excel_client_repository.soft_delete_service()` usa `Service.soft_delete()`
- [x] `excel_client_repository.restore_service()` usa `Service.restore()`
- [x] FakeClientRepository (conftest.py) alinhado com mesmo padrão
- [x] TUI opções de sync redirecionam para `pipeline_sincronizacao`
- [x] `audit_logger.py` sem `except: pass`
- [x] Zero regressão nos testes — **694/694 passando**

## Estimativa

3h

## Débito Técnico

N/A
