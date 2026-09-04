---
status: "done"
sprint: "2026-SPRINT-9"
---

# STORY-031: Model Router + VectorStore Refactor

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Refatorar o `VectorStore` singleton atual em duas classes: `VectorStoreInstance` (uma instância por modelo, com seu próprio embedder + coleção ChromaDB) e `VectorStoreManager` (facade que gerencia N instâncias). Implementar o `ModelRouter` que decide quais instâncias ativar com base na config + hardware.

## Regras

- **RULE-RAG-9.1:** `ModelRouter.resolve()` retorna lista de modelos ativos.
- **RULE-RAG-9.2:** Modo "dual" ativa dois modelos: `[primario, secundario]`.
- **RULE-RAG-9.3:** Fallback: se primário não instalado, tenta fallback configurado.
- **RULE-RAG-9.4:** `validate_pipeline_feasibility()` com warnings.
- **RULE-RAG-9.5:** Fallback automático em runtime (circuit breaker OPEN → próxima instância).
- **RULE-RAG-10.1:** `VectorStoreManager` substitui Singleton `VectorStore`.
- **RULE-RAG-10.2:** `VectorStoreInstance` = embedder + collection + breaker.
- **RULE-RAG-10.3:** Coleção nomeada `foton_{model_tag}_{dims}d` com metadata do modelo.
- **RULE-RAG-10.4:** `query()` em modo dual faz merge por score sem duplicatas.
- **RULE-RAG-10.5:** `add_documents()` indexa em todas as instâncias ativas.
- **RULE-RAG-10.6:** `diagnostic()` agrega diagnóstico multi-instância.
- **RULE-RAG-10.7:** Backward compat: config ausente → modo minilm legado.

## Critérios de Aceite

- [ ] `VectorStoreManager` é singleton (substitui o atual)
- [ ] `VectorStoreInstance` gerencia 1 embedder + 1 collection + 1 breaker
- [ ] Modo "minilm": apenas 1 instância ativa, query normal
- [ ] Modo "bgem3": apenas 1 instância ativa (com embedder BGE-M3)
- [ ] Modo "dual": 2 instâncias ativas, query paralela com merge por score
- [ ] Merge em modo dual remove duplicatas (mesmo chunk_id)
- [ ] Coleção nomeada como `foton_{tag}_{dims}d` com metadata no ChromaDB
- [ ] `ModelRouter.resolve()` aceita config + hardware e retorna lista
- [ ] Fallback: se primário não instalado → usa fallback com warning
- [ ] Fallback runtime: se instância primária falha → redireciona para secundária
- [ ] Backward compat: sem config `rag`, opera como MiniLM legado
- [ ] Testes: single, dual, fallback, merge, backward compat
- [ ] Testes existentes do VectorStore continuam passando

## Arquivos

- `foton_system/core/rag/model_router.py` (novo)
- `foton_system/core/memory/vector_store.py` (refatorado — extrair VectorStoreInstance, criar VectorStoreManager)
- `foton_system/core/ops/op_index_knowledge.py` (atualizar import para Manager)
- `foton_system/core/ops/op_query_knowledge.py` (atualizar import para Manager)

## Estimativa

8h

## Dependências

- STORY-030 (Hardware Profiler + Registry) — para `ModelRouter.resolve()` usar `validate_feasibility()`
