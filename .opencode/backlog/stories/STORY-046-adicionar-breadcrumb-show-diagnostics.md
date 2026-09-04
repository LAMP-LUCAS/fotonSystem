---
status: "completed"
sprint: "2026-SPRINT-6"
---

# STORY-046: Adicionar breadcrumb em `show_diagnostics` e telas de diagnóstico

**Épico:** EPIC-001 (Fase 0)
**Spec:** `MOD-UX/SPEC-UX-v1.0.md` (RULE-UX-1.1, RULE-UX-8.12)
**Regressão:** R7 (complemento)

## Descrição

A função `show_diagnostics` (em `menus_rag.py`) e outras telas de diagnóstico/informação do sistema
não exibem breadcrumb, violando RULE-UX-1.1 que determina que TODO submenu deve exibir breadcrumb.

Embora a correção principal de R7 esteja na STORY-044, esta story garante que:
1. `show_diagnostics` tem breadcrumb (já coberto na STORY-044)
2. Todas as outras telas de diagnóstico no sistema também têm breadcrumb
3. Uma busca exaustiva é feita para identificar telas sem breadcrumb

## Busca Exaustiva

Script de verificação:
```python
# Buscar funções que printam headers/titles mas não chamam print_breadcrumb
# Padrão: função que contém "def .*_ui" ou "def .*diagnostic" ou "def show_"
# e NÃO contém "print_breadcrumb" no mesmo arquivo
```

Arquivos a verificar:
- `foton_system/interfaces/cli/menus.py`
- `foton_system/interfaces/cli/menus_clients.py`
- `foton_system/interfaces/cli/menus_finance.py`
- `foton_system/interfaces/cli/menus_docs.py`
- `foton_system/interfaces/cli/menus_config.py`
- `foton_system/interfaces/cli/menus_rag.py`

## Regras Implementadas

- **RULE-UX-1.1:** Todo submenu com breadcrumb
- **RULE-UX-8.12:** Telas de diagnóstico obrigatoriamente com breadcrumb

## Critérios de Aceite

- [ ] `show_diagnostics` exibe breadcrumb (ex: "Sistema > Diagnóstico")
- [ ] Busca exaustiva identifica zero telas de diagnóstico sem breadcrumb
- [ ] Toda tela de diagnóstico identificada recebe breadcrumb
- [ ] Testes: `test_all_ui_functions_have_breadcrumb` (verificação automatizada)
- [ ] Zero regressão na suite existente

## Arquivos Afetados

- `foton_system/interfaces/cli/menus_rag.py` — `show_diagnostics`
- Potencialmente outros arquivos de menu (depende da busca exaustiva)

## Dependências

- STORY-044 (já cobre o breadcrumb de `show_diagnostics` em `menus_rag.py`)
- Esta story cobre o restante do sistema

## Estimativa

1h
