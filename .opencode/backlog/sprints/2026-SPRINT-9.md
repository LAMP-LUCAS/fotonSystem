---
status: "completed"
inicio: "2026-07-05"
fim: "2026-09-04"
---

# Sprint 9 — RAG Pipeline Inteligente — EPIC-004 (v2.0)

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Objetivo

Arquiteturar o RAG como grafo de inferência configurável: suporte a múltiplos modelos de embedding (MiniLM, BGE-M3, dual), pipeline de nós independentes (embed, search, rerank, format), consciência de hardware, download sob demanda com progresso, e encerramento de dívidas técnicas da v1.0.

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Fase | Status |
|----|-----------|------------|----------|------|--------|
| [STORY-030](stories/STORY-030-hardware-profiler-registry.md) | Hardware Profiler + Model Registry | 4h | RAG-7.1 a 8.4 | Fundação | ✅ done |
| [STORY-031](stories/STORY-031-model-router-store-refactor.md) | Model Router + VectorStore Refactor | 8h | RAG-9.1 a 10.7 | Núcleo | ✅ done |
| [STORY-032](stories/STORY-032-download-manager.md) | Download Manager | 4h | RAG-12.1 a 12.5 | Fundação | ✅ done |
| [STORY-033](stories/STORY-033-rag-pipeline-nodes.md) | RAG Pipeline Node System | 8h | RAG-11.1 a 11.6 | Pipeline | ✅ done |
| [STORY-034](stories/STORY-034-tui-rag-config.md) | TUI RAG Configuration | 4h | RAG-7.3, 9.4, 12.3 | Interface | ✅ done |
| [STORY-035](stories/STORY-035-migration-compat.md) | Migration + Backward Compatibility | 2h | RAG-10.7 | Migração | ✅ done |
| [STORY-036](stories/STORY-036-integration-tests-rag-pipeline.md) | Testes E2E Pipeline RAG | 6h | RAG-1.1 a 6.2 (herança) | Qualidade | ✅ done |
| [STORY-037](stories/STORY-037-mcp-diagnostico-multimodelo.md) | Expandir MCP diagnóstico | 2h | RAG-10.6, 6.2 | Consolidação | ✅ done |
| [STORY-038](stories/STORY-038-performance-benchmarking.md) | Performance Benchmarking | 3h | Métricas PRD | Qualidade | ✅ done |
| [STORY-039](stories/STORY-039-user-documentation-rag.md) | Documentação de usuário | 2h | — | Consolidação | ✅ done |
| [STORY-040](stories/STORY-040-config-schema-rag.md) | Schema e Config RAG | 2h | RAG-9.1, 9.4, 10.7, 11.5 | Consolidação | ✅ done |
| [STORY-041](stories/STORY-041-debt-telemetry-nps.md) | Dívidas v1.0 + Telemetria + NPS | 6h | RAG-2.3, 2.4, 3.1 (rem.), 5.2 | Encerramento | ✅ done |
| | **Total** | **51h** (51h done · 0h restante) | **26 RULE-IDs** (26 implementados) | | |

## Dependências

```
030 ──→ 031 ──→ 033 ──→ 036
 │        │        │
 ├──→ 032 └──→ 035 └──→ 038 ──→ 039
 │
 └──→ 034 ←─── 031, 032, 033
        037 ←─── 031
        040 ←─── 031

041 (independente — paralelo)
```

## Débito Técnico

- [x] Gerar handoff ao final de cada story
- [x] Atualizar CHANGELOG.md com mudanças da sprint
- [x] Handoff consolidado ao final da sprint

## Definição de Pronto (DoD)

- [x] 12 stories implementadas com TDD (12/12 concluídas)
- [x] 26 RULE-IDs cobertos (26/26 implementados)
- [x] Testes passando (`python -m pytest` — zero regressão)
- [x] RULE-IDs referenciados nos commits
- [x] Handoff gerado ao final
- [x] Métricas de performance validadas (STORY-038)
- [x] NPS do módulo RAG com primeira coleta (STORY-041)
