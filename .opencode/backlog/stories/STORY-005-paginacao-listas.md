---
status: "ready"
sprint: "2026-07-SPRINT-4"
estimativa: "3h"
---

# STORY-005: Paginação em Listas de Clientes e Serviços

**Spec:** [RULE-UX-2.2](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-2.3](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Melhoria (UX)

## Descrição
Listas com muitos itens são exibidas de uma só vez, sem paginação. Isso afeta: `restore_client_ui` (clientes deletados), `list_client_servicos_ui` (serviços) e `resumo_financeiro_ui`. Implementar paginação com page size de 10 itens e "Pressione Enter para continuar..." entre páginas.

## Critérios de Aceite
- [ ] `restore_client_ui`: clientes deletados paginados (10/page)
- [ ] `list_client_servicos_ui`: serviços paginados (10/page)
- [ ] `resumo_financeiro_ui`: clientes no resumo paginados (10/page)
- [ ] Indicador "Página X de Y" visível em cada página
- [ ] Funciona corretamente com 0 itens (mensagem amigável)
- [ ] Funciona corretamente com menos de 10 itens (uma página só)
- [ ] Testes unitários para a lógica de paginação

## Observações
- Considere extrair lógica de paginação para um helper reutilizável em `tui_layout.py`
- A paginação de `restore_client_ui` é crítica pois a lista de deletados pode crescer com o tempo
