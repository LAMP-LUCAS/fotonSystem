---
status: "ready"
sprint: "2026-07-SPRINT-4"
estimativa: "0.5h"
---

# STORY-009: Remover Atalho `00` (No-Op) do Menu Principal

**Spec:** [RULE-UX-1.4](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Limpeza

## Descrição
O menu principal trata `choice == '00'` com `continue` (no-op). O usuário que digita `00` acidentalmente (talvez tentando `0` para sair) não recebe feedback visual algum. Remover o tratamento especial ou substituir por atalho útil (ex: recarregar menu).

## Critérios de Aceite
- [ ] `00` não é mais tratado como caso especial
- [ ] `00` cai no fluxo normal (opção inválida ou comportamento default)
- [ ] Nenhuma funcionalidade existente é afetada
- [ ] Testes de menu principal atualizados

## Arquivos
- `foton_system/interfaces/cli/menus.py` ~ linha 284
