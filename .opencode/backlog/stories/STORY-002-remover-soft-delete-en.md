---
status: "done"
sprint: "2026-07-SPRINT-4"
estimativa: "1h"
---

# STORY-002: Corrigir "Soft Delete" para "Remover Cliente" (PT-BR)

**Spec:** [RULE-UX-4.2](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Correção (i18n)

## Descrição
A opção 9 do menu de clientes exibe `"Remover Cliente (Soft Delete)"`. O termo "Soft Delete" está em inglês — remover o parêntese, deixando apenas "Remover Cliente". O restante da interface já usa PT-BR para esta operação (cabeçalho "REMOVER CLIENTE").

## Critérios de Aceite
- [ ] Opção 9 exibe apenas "Remover Cliente"
- [ ] Nenhum termo em inglês para labels de operação no menu de clientes
- [ ] Testes de menu atualizados se necessário
- [ ] 452+ testes passando

## Arquivos
- `foton_system/interfaces/cli/menus.py` ~ linha 162
