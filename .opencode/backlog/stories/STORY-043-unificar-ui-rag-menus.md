---
status: "done"
sprint: "2026-SPRINT-6"
---

# STORY-043: Unificar UI de indexação e consulta RAG em `menus_rag.py`

**Épico:** EPIC-001 (Fase 0)
**Spec:** `MOD-UX/SPEC-UX-v1.0.md` (RULE-UX-8.1, RULE-UX-8.9)
**Regressões:** R2, R3

## Descrição

Duas regressões interligadas:

1. **R2 — Duplicação de UI:** `menus_config.py` contém funções de UI para indexação (`_index_knowledge_ui`) e consulta (`_query_knowledge_ui`) que DUPLICAM as mesmas funções em `menus_rag.py`. Isso viola RULE-UX-8.1 (menus modulares).

2. **R3 — Handler errado:** `_query_knowledge_ui` está registrado em `MenuConfigHandler` em vez de `MenuRagHandler`. A indexação e consulta RAG devem pertencer exclusivamente ao `MenuRagHandler`.

## Solução

- Remover `_index_knowledge_ui` e `_query_knowledge_ui` de `menus_config.py`
- Garantir que `menus_rag.py` tenha ambas as funções (ou criar se ausentes)
- Registrar ambas no `MenuRagHandler`
- Atualizar o dispatch em `menus.py` se necessário

## Regras Implementadas

- **RULE-UX-8.1:** Menus modulares respeitados (RAG isolado em `menus_rag.py`)

## Critérios de Aceite

- [ ] `menus_config.py` não contém mais `_index_knowledge_ui` ou `_query_knowledge_ui`
- [ ] `menus_rag.py` contém `_index_knowledge_ui` (existente ou movida)
- [ ] `menus_rag.py` contém `_query_knowledge_ui` (existente ou movida)
- [ ] `MenuRagHandler` expõe ambas as funções como métodos
- [ ] Menu de Configurações não mostra mais opções de indexação/consulta RAG
- [ ] Menu de RAG mostra opções de indexação e consulta
- [ ] A navegação para RAG a partir do menu principal funciona corretamente
- [ ] Indexação e consulta RAG funcionam dos dois lugares (se houver entry points)
- [ ] Testes: `test_rag_ui_in_menus_rag`, `test_rag_ui_not_in_menus_config`
- [ ] Zero regressão na suite existente

## Arquivos Afetados

- `foton_system/interfaces/cli/menus_config.py` — remover `_index_knowledge_ui`, `_query_knowledge_ui`
- `foton_system/interfaces/cli/menus_rag.py` — garantir presença de ambas
- `foton_system/interfaces/cli/menus.py` — verificar dispatch do MenuRagHandler

## Estimativa

1h
