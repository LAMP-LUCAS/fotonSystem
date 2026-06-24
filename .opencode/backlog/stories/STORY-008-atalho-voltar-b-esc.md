---
status: "ready"
sprint: "2026-07-SPRINT-4"
estimativa: "2h"
---

# STORY-008: Atalho de Teclado para Voltar (b / Esc)

**Spec:** [RULE-UX-1.2](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Melhoria (UX)

## Descrição
Atualmente apenas a opção `0` ("Voltar") retorna ao menu anterior. Não existe atalho de teclado como `b` (back) ou `Esc`. O atalho `q` no menu principal sai do sistema, mas nos submenus não há equivalente para voltar. Implementar `b` como atalho universal de "voltar" em todos os submenus.

## Critérios de Aceite
- [ ] `handle_clients`: digitar `b` volta ao menu principal
- [ ] `handle_client_servicos_menu`: digitar `b` volta ao menu de clientes
- [ ] `handle_services`: digitar `b` volta ao menu principal
- [ ] `handle_documents`: digitar `b` volta ao menu principal
- [ ] `handle_finance`: digitar `b` volta ao menu principal
- [ ] `handle_productivity`: digitar `b` volta ao menu principal
- [ ] `handle_settings`: digitar `b` volta ao menu principal
- [ ] Opção `0` continua funcionando (backward compat)
- [ ] `Esc` não é capturável via input() padrão — documentar limitação ou implementar via msvcrt/getch se viável
- [ ] Testes de atalho adicionados

## Observações
- `b` minúsculo é o padrão (case-insensitive: `choice.lower() == 'b'`)
- Não conflitar com nenhuma opção numérica existente
- Se `b` conflitar com alguma label de menu, priorizar o atalho e ajustar a label
