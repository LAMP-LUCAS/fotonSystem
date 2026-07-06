---
status: "done"
sprint: "2026-SPRINT-9"
---

# STORY-033: RAG Pipeline Node System

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Implementar o sistema de nós de pipeline (PipelineNode graph) que permite compor o fluxo de inferência do RAG de forma configurável. Criar os 4 nós padrão (EmbedNode, SearchNode, RerankNode, FormatNode) e o orquestrador RagPipeline. O pipeline "simple" (embed → search → format) substitui o fluxo hardcoded atual. O pipeline "rerank" adiciona o nó de rerank com cross-encoder.

## Regras

- **RULE-RAG-11.1:** `PipelineNode(ABC)` — interface com `name`, `input_keys`, `output_keys`, `execute(context)`.
- **RULE-RAG-11.2:** `ProcessContext` — dict progressivo enriquecido a cada nó.
- **RULE-RAG-11.3:** `RagPipeline.run(context)` — executa nós sequencialmente.
- **RULE-RAG-11.4:** Nós padrão: EmbedNode, SearchNode, RerankNode, FormatNode.
- **RULE-RAG-11.5:** Pipeline configurável via settings.json (`rag.pipeline.type` e `rag.pipeline.nodes`).
- **RULE-RAG-11.6:** (Futuro) Pipeline customizado via JSON array.

## Critérios de Aceite

- [ ] `PipelineNode` ABC definida com `execute(context)` abstrato
- [ ] `ProcessContext` é um MutableMapping com chaves padronizadas
- [ ] `EmbedNode` gera embedding da query usando o embedder do modelo ativo
- [ ] `SearchNode` busca na(s) coleção(ões) via VectorStoreManager
- [ ] `RerankNode` reordena top-K usando cross-encoder (ex: `BAAI/bge-reranker-v2-m3`)
- [ ] RerankNode é opcional — pipeline "simple" não o inclui
- [ ] `FormatNode` monta saída com score, fonte, contexto e marcadores `>>>...<<<`
- [ ] `RagPipeline.run()` em modo "simple" executa: Embed → Search → Format
- [ ] `RagPipeline.run()` em modo "rerank" executa: Embed → Search → Rerank → Format
- [ ] Pipeline lê configuração de `settings.json` (`rag.pipeline.type`)
- [ ] Fallback: se rerank não instalado, pipeline "rerank" cai para "simple" com warning
- [ ] Testes: pipeline simple, pipeline rerank (mockado), nó individual, contexto progressivo

## Arquivos

- `foton_system/core/rag/pipeline.py` (novo) — RagPipeline orquestrador
- `foton_system/core/rag/nodes/__init__.py` (novo)
- `foton_system/core/rag/nodes/embed_node.py` (novo)
- `foton_system/core/rag/nodes/search_node.py` (novo)
- `foton_system/core/rag/nodes/rerank_node.py` (novo)
- `foton_system/core/rag/nodes/format_node.py` (novo)

## Estimativa

8h

## Dependências

- STORY-031 (VectorStoreManager) — SearchNode usa Manager
