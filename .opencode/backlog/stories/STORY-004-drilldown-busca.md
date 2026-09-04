---
status: "done"
sprint: "2026-07-SPRINT-4"
estimativa: "4h"
---

# STORY-004: Drill-down nos Resultados de Busca

**Spec:** [RULE-UX-3.1](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-3.2](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-3.3](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Melhoria (UX)

## Descrição
Atualmente `search_client_ui` (opção 4) e `global_search_ui` (atalho `g`) exibem resultados como texto plano — o usuário vê os nomes mas não pode interagir com eles. Implementar numeração dos resultados com opção de selecionar um para navegar até a ficha do cliente (`read_client_info_ui`).

## Critérios de Aceite
- [ ] `search_client_ui` numera resultados (1, 2, 3...) e pergunta "Digite o número para abrir a ficha (ENTER para voltar)"
- [ ] Ao selecionar um resultado, abre `read_client_info_ui` para o cliente escolhido
- [ ] `global_search_ui` também permite selecionar um resultado de cliente para navegar
- [ ] Resultados de serviço na busca global mostram o cliente pai (já implementado)
- [ ] Termo de busca vazio em `search_client_ui` lista todos os clientes (atalho listagem)
- [ ] Testes unitários para o fluxo de drill-down

## Arquivos
- `foton_system/interfaces/cli/menus.py` (search_client_ui, global_search_ui)
