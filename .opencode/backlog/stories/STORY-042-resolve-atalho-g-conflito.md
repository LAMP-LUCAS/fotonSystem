---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-042: Resolver conflito de atalho `g` entre SPEC-UX e SPEC-RAG

**Épico:** EPIC-001 (Fase 0)
**Spec:** `MOD-UX/SPEC-UX-v1.0.md` (RULE-UX-8.9)
**Regressão:** R1

## Descrição

O atalho `g` no menu principal está mapeado para duas funções conflitantes:
- SPEC-UX (RULE-UX-1.3 / 8.5): `g` → `global_search` (busca global por clientes)
- SPEC-RAG (RULE-RAG-8.4): `g` → `rag_query` (consulta na base de conhecimento RAG)

Como o menu principal é controlado pelo EPIC-001 (SPEC-UX), o atalho `g` DEVE disparar exclusivamente `global_search`.
A função RAG deve ser acessada via submenu de RAG ou via atalho alternativo no contexto RAG (ex: submenu de Configurações > RAG).

## Regras Implementadas

- **RULE-UX-8.9:** Atalho `g` no menu principal dispara exclusivamente `global_search`
- **RULE-RAG-8.4** (atualizada): Remover mapeamento conflitante; RAG acessível via submenu

## Critérios de Aceite

- [ ] `g` no menu principal chama `global_search()` — inalterado
- [ ] `g` em submenus NÃO-RAG não conflita (comportamento inalterado)
- [ ] RAG `_query_knowledge_ui` não é mais acionável via `g` no menu principal
- [ ] RAG permanece acessível via seu submenu (Configurações > RAG > Consultar Conhecimento)
- [ ] `global_search` continua funcionando: busca por alias, nome, código ou NIF
- [ ] Resultados numerados com drill-down para ficha do cliente
- [ ] SPEC-RAG-v1.0 atualizada (RULE-RAG-8.4 revisada)
- [ ] Testes: `test_menu_g_shortcut` + `test_rag_g_shortcut_removed`
- [ ] Zero regressão na suite existente

## Arquivos Afetados

- `foton_system/interfaces/cli/menus.py` — verificar `parse_command()` e dispatch de `g`
- `foton_system/interfaces/cli/menus_config.py` — verificar se `g` está sendo capturado
- `specs/MOD-RAG/SPEC-RAG-v1.0.md` — atualizar RULE-RAG-8.4

## Estimativa

1h
