---
status: "ready"
sprint: "2026-07-SPRINT-4"
estimativa: "4h"
---

# STORY-001: Listar Todos os Clientes na TUI

**PRD:** [Melhoria de UX — Navegabilidade](docs/01_PROJECTS/AgenticSprintPlan.md)
**Spec:** [RULE-CLIENTES-2.2](specs/MOD-CLIENTES/SPEC-CLIENTES-v1.0.md)
**Tipo:** Melhoria (UX)

## Descrição
Atualmente não existe uma opção "Listar Todos os Clientes" na TUI. O usuário precisa saber o nome ou alias para buscar. Adicionar uma opção no menu de clientes que exiba todos os clientes cadastrados em formato de lista navegável.

## Critérios de Aceite
- [ ] Opção "Listar Todos os Clientes" visível no menu de clientes
- [ ] Exibe código, nome, alias e status de cada cliente
- [ ] Lista paginada (10 itens por vez) com "Pressione Enter para continuar"
- [ ] Clientes deletados aparecem com marcador visual (ex: `[DELETADO]`)
- [ ] Opção funciona com 0 clientes (mensagem amigável)
- [ ] Testes unitários para o novo método

## Tarefas Técnicas
1. Adicionar método `list_all_clients_ui()` em `menus.py`
2. Adicionar opção no menu de clientes (próximo número disponível)
3. Implementar paginação com `input("Pressione Enter...")`
4. Integrar com `client_service.list_all()` ou similar
5. Escrever testes unitários
