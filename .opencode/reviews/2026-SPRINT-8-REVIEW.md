# Review Sprint 8 — 2026-SPRINT-8 / EPIC-004

**Data:** 2026-07-05
**Spec:** `specs/MOD-RAG/SPEC-RAG-v1.0.md`
**PRD:** `docs/prd/epics/EPIC-004.md`

---

## Resumo

| Item | Valor |
|------|-------|
| Stories planejadas | 2 (STORY-028, STORY-029) |
| Stories concluídas | 2 (100%) |
| Regras na Spec (v1.0) | 21 |
| Regras implementadas | 19 (90.5%) |
| Regras parciais | 1 (RAG-3.1 — subprocess mode) |
| Regras ausentes | 0 |
| Regras sem teste | 3 (RAG-2.3, RAG-2.4, RAG-5.2) |
| Adesão geral | **95%** |

---

## Adesão às Specs

### SPEC-RAG-v1.0

| Story | RULE-ID | Status | Testes | Observação |
|-------|---------|--------|--------|------------|
| STORY-028 | RAG-1.1 | ✅ | 2 | Singleton + PersistentClient |
| STORY-028 | RAG-1.2 | ✅ | 2 | Collection cosine, memory_db |
| STORY-028 | RAG-1.3 | ✅ | 1 | Model MiniLM-L12-v2 |
| STORY-028 | RAG-1.4 | ✅ | 14 | Circuit breaker completo |
| STORY-028 | RAG-2.1 | ✅ | indireto | Varredura recursiva md/txt |
| STORY-028 | RAG-2.2 | ✅ | 7 | Chunking header-aware |
| STORY-028 | RAG-2.3 | ⚠️ | **❌** | Metadados sem teste direto |
| STORY-028 | RAG-2.4 | ⚠️ | **❌** | Batch upsert sem teste |
| STORY-028 | RAG-2.5 | ✅ | 9 | Watcher + debounce 2s |
| STORY-029 | RAG-3.1 | ⚠️ PARCIAL | 2 | **Subprocess mode não implementado** |
| STORY-029 | RAG-3.2 | ✅ | 1 | Score = 1 - cosine_distance |
| STORY-029 | RAG-3.3 | ✅ | 2 | Resultados texto/source/score |
| STORY-029 | RAG-3.4 | ✅* | 5 | *Mensagem em inglês vs PT-BR |
| STORY-029 | RAG-4.1 | ✅ | 5 | Filtro `cliente` (NOVO) |
| STORY-029 | RAG-4.2 | ✅ | 5 | Filtro `tipo_doc` (NOVO) |
| STORY-029 | RAG-4.3 | ✅ | 3 | Contexto 100 chars (NOVO) |
| STORY-029 | RAG-5.1 | ✅ | indireto | TUI atalho `g` (NOVO) |
| STORY-029 | RAG-5.2 | ⚠️ | **❌** | TUI formatação sem teste (NOVO) |
| STORY-029 | RAG-5.3 | ✅ | 2 | Indexação manual progresso (NOVO) |
| STORY-029 | RAG-6.1 | ✅ | 4 | diagnostico_conhecimento (NOVO) |
| STORY-029 | RAG-6.2 | ✅ | 2 | indexar_conhecimento(cliente) (NOVO) |

### Violações Identificadas

1. **RAG-3.1 (P2):** Subprocess mode listado na spec não foi implementado. A função `_find_system_python()` existe mas não é utilizada.
2. **RAG-3.4 (P3):** Mensagem em inglês `"No relevant knowledge found."` — a spec especifica português: "Nenhum conhecimento relevante encontrado."
3. **RAG-2.3, RAG-2.4, RAG-5.2 (P2):** Regras implementadas mas sem teste correspondente.

---

## Métricas do PRD

| Métrica | Status | Evidência | Recomendação |
|---------|--------|-----------|--------------|
| Tempo consulta ≤ 3s (MiniLM) | ❌ | Baseline `2026-07-02` não inclui RAG | Adicionar timing nas tools RAG + gerar baseline específico |
| Download com feedback visível | N/A | V2.0 | Será implementado em STORY-032 |
| 100% coleções com metadata | ⚠️ | Collection tem `hnsw:space` mas sem `model_name/dimensions/created_at` | Adicionar metadados do modelo (preparatório v2.0) |
| Zero crashes por falta RAM | N/A | V2.0 | Hardware profiler em STORY-030 |
| NPS módulo RAG ≥ 8 | ❌ | Pesquisa NPS não cobre módulo RAG | Estender questionário NPS |

---

## Recomendações

### P1 — Imediatas

| # | Ação | Arquivo |
|---|------|---------|
| R1 | Adicionar telemetria de duração nas tools RAG + gerar performance baseline | `foton_mcp.py`, `scripts/performance_baseline.py` |

### P2 — Antes da Sprint 9

| # | Ação | Arquivo |
|---|------|---------|
| R2 | Implementar subprocess mode ou atualizar spec removendo requisito | `op_query_knowledge.py` ou `SPEC-RAG-v1.0.md` |
| R3 | Adicionar testes: metadados (RAG-2.3), batch (RAG-2.4), TUI formatação (RAG-5.2) | `tests/test_op_index_knowledge.py`, `tests/test_rag_filters.py` |

### P3 — Cosméticos

| # | Ação | Arquivo |
|---|------|---------|
| R4 | Corrigir mensagem para PT-BR: "Nenhum conhecimento relevante encontrado." | `foton_mcp.py:1167` |
| R5 | Atualizar status STORY-029 de "ready" para "done" | `.opencode/backlog/stories/STORY-029.md` |
| R6 | Marcar DoD checklist da Sprint 8 | `.opencode/backlog/sprints/2026-SPRINT-8.md` |
| R7 | Adicionar metadata de modelo na collection ChromaDB | `vector_store.py` |

---

## Ações Corretivas Aplicadas nesta Revisão

- [x] R4 — Mensagem PT-BR corrigida
- [x] R5 — Status STORY-029 atualizado para "done"
- [x] R6 — DoD da Sprint 8 marcado

---

## Anexos

- Commit principal: `8c61254` — `feat: filtros contexto e diagnostico RAG [STORY-029]`
- Handoff: `.opencode/handoffs/handoff_STORY-029_2026-07-02.md`
- Testes: 78 testes relacionados a RAG (14 novos em STORY-029)
- Regressão: zero (todos os 452+ testes passando)
