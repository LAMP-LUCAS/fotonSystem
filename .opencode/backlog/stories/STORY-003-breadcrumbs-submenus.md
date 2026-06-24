---
status: "done"
sprint: "2026-07-SPRINT-4"
estimativa: "2h"
---

# STORY-003: Adicionar Breadcrumbs em Todos os Submenus

**Spec:** [RULE-UX-1.1](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Melhoria (UX)

## Descrição
Atualmente apenas o submenu de serviços (`handle_client_servicos_menu`) exibe breadcrumb via `self.print_breadcrumb(["Clientes", "Serviços"])`. Os demais submenus (clientes, financeiro, documentos, configurações, produtividade) não têm breadcrumb, obrigando o usuário a memorizar onde está na hierarquia.

## Critérios de Aceite
- [x] `display_clients_menu` exibe breadcrumb "Clientes"
- [x] `display_finance_menu` exibe breadcrumb "Financeiro"
- [x] `display_documents_menu` exibe breadcrumb "Documentos"
- [x] `display_settings_menu` exibe breadcrumb "Configurações"
- [x] `display_productivity_menu` exibe breadcrumb "Produtividade"
- [x] `handle_client_servicos_menu` mantém breadcrumb existente "Clientes > Serviços"
- [x] Breadcrumbs são chamados antes das opções de menu, depois do header
- [x] Testes atualizados se necessário

## Arquivos
- `foton_system/interfaces/cli/menus.py` (display_*_menu methods)
