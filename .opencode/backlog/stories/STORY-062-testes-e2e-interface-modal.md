---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-062: Testes E2E da interface modal

**Épico:** EPIC-013 (Fase 3)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-8.11, 8.12)
**Estimativa:** 0.5h

## Descrição

Criar a suite de testes E2E para a interface modal, garantindo cobertura ≥ 80%
e zero interferência com os testes existentes (1020+).

## Regras Implementadas

- **RULE-TUI-8.11:** Testes em `tests/test_modal/`, sem interferência
- **RULE-TUI-8.12:** Cobertura ≥ 80% nas primeiras 2 semanas

## Estrutura

```
tests/test_modal/
├── __init__.py
├── test_engine.py       # ModalEngine init, fallback
├── test_normal_mode.py  # Navegação, busca, comando
├── test_splits.py       # Ctrl+w commands
├── test_insert_mode.py  # INSERT mode
├── test_visual_mode.py  # VISUAL mode
├── test_cmdline.py      # : commands
├── test_search.py       # / search
├── test_themes.py       # Temas
├── test_keybindings.py  # Keybindings configuráveis
├── test_compatibility.py# Modo de compatibilidade
└── test_help.py         # :help
```

## Cobertura Mínima

| Módulo | Testes | Cobertura alvo |
|--------|--------|----------------|
| `engine.py` | init, fallback, mode transitions | 90% |
| `modes.py` | NORMAL, INSERT, VISUAL, COMANDO | 90% |
| `buffer.py` | load, navigate, edit, save, validate | 85% |
| `splits.py` | create, navigate, resize, close | 85% |
| `cmdline.py` | parse, execute, autocomplete, error | 90% |
| `search.py` | search, highlight, navigate, empty | 90% |
| `ui.py` | status bar, message bar, rendering | 80% |
| `compatibility.py` | fallback completeness | 100% |

## Critérios de Aceite

- [ ] `tests/test_modal/` criado com todos os módulos
- [ ] Cobertura ≥ 80% nas primeiras 2 semanas
- [ ] Todos os testes E2E passam isoladamente
- [ ] Zero interferência com suite existente (`python -m pytest` total passa sem regressão)
- [ ] `python -m pytest tests/test_modal/ -v` → todos verdes
- [ ] `python -m pytest tests/ -v --ignore=tests/test_modal/` → zero regressão

## Dependências

- Todas as stories anteriores (STORY-054 a 061)

## Estimativa

0.5h
