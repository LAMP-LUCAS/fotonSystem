---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-044: Corrigir conformidade UX de `menus_rag.py`

**Épico:** EPIC-001 (Fase 0)
**Spec:** `MOD-UX/SPEC-UX-v1.0.md` (RULE-UX-8.3, RULE-UX-4.1, RULE-UX-8.13, RULE-UX-1.1)
**Regressões:** R4, R5, R6, R7

## Descrição

`menus_rag.py` possui 4 violações de conformidade com a SPEC-UX:

1. **R4 (RULE-UX-8.3):** 3 `except:` genéricos sem `format_error_with_suggestion()`
   - `except Exception as e: print(f"Erro: {e}")` (∼linha 45)
   - `except Exception as e: print(f"Erro ao indexar: {e}")` (∼linha 78)
   - `except Exception as e: print(f"Erro na consulta: {e}")` (∼linha 120)

2. **R5 (RULE-UX-4.1):** "Opcao invalida." sem acento — deve ser "Opção inválida."
   - Verificar outras strings para garantir PT-BR completo

3. **R6 (RULE-UX-8.13):** Uso de `.format()` em vez de f-strings
   - Ex: `"Processando {}...".format(nome)` → `f"Processando {nome}..."`

4. **R7 (RULE-UX-1.1):** `show_diagnostics` sem breadcrumb
   - Toda tela deve exibir `print_breadcrumb()` (ver SPEC-UI-COMPONENTS.md §3.2)

## Regras Implementadas

- **RULE-UX-8.3:** Error handling com sugestão contextualizada
- **RULE-UX-4.1:** PT-BR consistente
- **RULE-UX-8.13:** f-strings obrigatórias
- **RULE-UX-1.1:** Breadcrumb obrigatório

## Critérios de Aceite

- [ ] Todos os `except:` em `menus_rag.py` usam `format_error_with_suggestion()`
- [ ] Nenhum `except:` genérico sem formatação permanece
- [ ] "Opcao invalida." substituído por "Opção inválida." (com acentos)
- [ ] Revisão completa de PT-BR em todas as strings de `menus_rag.py`
- [ ] Zero usos de `.format()` — 100% f-strings
- [ ] `show_diagnostics` exibe breadcrumb (ex: "Sistema > Diagnóstico")
- [ ] Testes: `test_menus_rag_error_suggestions`, `test_menus_rag_ptbr`, `test_menus_rag_fstrings`, `test_show_diagnostics_breadcrumb`
- [ ] Zero regressão na suite existente

## Arquivos Afetados

- `foton_system/interfaces/cli/menus_rag.py` — 4 correções de conformidade

## Estimativa

1h
