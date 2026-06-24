---
status: "ready"
sprint: "2026-07-SPRINT-4"
estimativa: "1h"
---

# STORY-006: Padronizar Diálogos de Confirmação (S/N)

**Spec:** [RULE-UX-5.1](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-5.2](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-5.3](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Correção (consistência)

## Descrição
O sistema possui dois padrões de confirmação conflitantes:
1. `menus.py`: usa `.upper() != 'S'` na maioria dos lugares (correto)
2. `form_view.py`: usa `.lower() == 's'` (divergente)
3. `handle_installation`: usa `.upper() == 'S'` (funcional mas padrão diferente)

Padronizar tudo para `.upper() != 'S'` — que é mais seguro (qualquer tecla diferente de S cancela).

## Critérios de Aceite
- [ ] `form_view.py` linha 26: `input(...).lower() == 's'` → `input(...).upper() != 'S'`
- [ ] `form_view.py` linha 30: `input(...).lower() == 's'` → `input(...).upper() != 'S'`
- [ ] `handle_installation` linha 393: `== 'S'` mantido (semanticamente é "prosseguir APENAS se S")
- [ ] Todos os demais confirmations já usam `!= 'S'` — verificar
- [ ] Testes de confirmação passando

## Arquivos
- `foton_system/interfaces/cli/views/form_view.py`
- `foton_system/interfaces/cli/menus.py` (handle_installation — verificar)
