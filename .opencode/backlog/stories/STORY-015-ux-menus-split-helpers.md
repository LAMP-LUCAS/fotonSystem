---
status: "done"
sprint: "2026-SPRINT-5"
---

# STORY-015: UX — Split do menus.py + Helpers de TUI

**Épico:** EPIC-001
**Spec:** `MOD-UX/SPEC-UX-v1.0.md`

## Descrição

Dividir o `menus.py` monolítico (54KB) em submódulos. Criar helpers de TUI: `ProgressTracker` para feedback de progresso em operações batch e sistema de erro com sugestões contextuais.

## Regras Implementadas

- **RULE-UX-8.1:** `menus.py` dividido em `menus_clients.py`, `menus_finance.py`, `menus_docs.py`, `menus_config.py`
- **RULE-UX-8.2:** `ProgressTracker` com `advance(item)` e `finish()`
- **RULE-UX-8.3:** Erros TUI com sugestões contextualizadas por tipo

## Critérios de Aceite

- [x] `menus.py` mantém apenas dispatch principal (entry point)
- [x] `menus_clients.py`: menu de clientes e serviços
- [x] `menus_finance.py`: menu financeiro
- [x] `menus_docs.py`: menu de documentos
- [x] `menus_config.py`: menu de configuração
- [x] `ProgressTracker` exibe `"[3/10] Processando CLIENTE..."`
- [x] `ProgressTracker.advance(item)` incrementa contador
- [x] `ProgressTracker.finish()` finaliza com resumo
- [x] Erros exibem sugestão: `FileNotFoundError` → "Verifique settings.json"
- [x] Erros exibem sugestão: `PermissionError` → "Feche o Excel e tente novamente"
- [x] Erros exibem sugestão: bloqueio de DB → "Base aberta em outro programa"
- [x] Testes para ProgressTracker, breadcrumbs, error suggestions
- [x] Zero regressão

## Estimativa

6h
