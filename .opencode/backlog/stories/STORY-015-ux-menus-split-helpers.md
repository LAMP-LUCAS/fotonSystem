---
status: "ready"
sprint: "2026-SPRINT-5"
---

# STORY-015: UX — Split do menus.py + Helpers de TUI

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Descrição

Dividir o `menus.py` monolítico (54KB) em submódulos. Criar helpers de TUI: `ProgressTracker` para feedback de progresso em operações batch e sistema de erro com sugestões contextuais.

## Regras Implementadas

- **RULE-DOMAIN-4.1:** `menus.py` dividido em `menus_clients.py`, `menus_finance.py`, `menus_docs.py`, `menus_config.py`
- **RULE-DOMAIN-4.2:** `ProgressTracker` com `advance(item)` e `finish()`
- **RULE-DOMAIN-4.3:** Erros TUI com sugestões contextualizadas por tipo

## Critérios de Aceite

- [ ] `menus.py` mantém apenas dispatch principal (entry point)
- [ ] `menus_clients.py`: menu de clientes e serviços
- [ ] `menus_finance.py`: menu financeiro
- [ ] `menus_docs.py`: menu de documentos
- [ ] `menus_config.py`: menu de configuração
- [ ] `ProgressTracker` exibe `"[3/10] Processando CLIENTE..."`
- [ ] `ProgressTracker.advance(item)` incrementa contador
- [ ] `ProgressTracker.finish()` finaliza com resumo
- [ ] Erros exibem sugestão: `FileNotFoundError` → "Verifique settings.json"
- [ ] Erros exibem sugestão: `PermissionError` → "Feche o Excel e tente novamente"
- [ ] Erros exibem sugestão: bloqueio de DB → "Base aberta em outro programa"
- [ ] Testes para ProgressTracker, breadcrumbs, error suggestions
- [ ] Zero regressão

## Estimativa

6h
