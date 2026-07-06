---
status: "active"
inicio: "2026-07-05"
fim: "TBD"
---

# Sprint 9 — RAG Pipeline Inteligente — EPIC-004 (v2.0)

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Objetivo

Arquiteturar o RAG como grafo de inferência configurável: suporte a múltiplos modelos de embedding (MiniLM, BGE-M3, dual), pipeline de nós independentes (embed, search, rerank, format), consciência de hardware, download sob demanda com progresso, e encerramento de dívidas técnicas da v1.0.

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Fase | Status |
|----|-----------|------------|----------|------|--------|
| ID | Descrição | Estimativa | RULE-IDs | Fase | Status |
|----|-----------|------------|----------|------|--------|
| [STORY-030](stories/STORY-030-hardware-profiler-registry.md) | Hardware Profiler + Model Registry | 4h | RAG-7.1 a 8.4 | Fundação | ✅ done |
| [STORY-031](stories/STORY-031-model-router-store-refactor.md) | Model Router + VectorStore Refactor | 8h | RAG-9.1 a 10.7 | Núcleo | ✅ done |
| [STORY-032](stories/STORY-032-download-manager.md) | Download Manager | 4h | RAG-12.1 a 12.5 | Fundação | ✅ done |
| [STORY-033](stories/STORY-033-rag-pipeline-nodes.md) | RAG Pipeline Node System | 8h | RAG-11.1 a 11.6 | Pipeline | ✅ done |
| [STORY-034](stories/STORY-034-tui-rag-config.md) | TUI RAG Configuration | 4h | RAG-7.3, 9.4, 12.3 | Interface | ✅ done |
| [STORY-035](stories/STORY-035-migration-compat.md) | Migration + Backward Compatibility | 2h | RAG-10.7 | Migração | ✅ done |
| [STORY-036](stories/STORY-036-integration-tests-rag-pipeline.md) | Testes E2E Pipeline RAG | 6h | RAG-1.1 a 6.2 (herança) | Qualidade | draft |
| [STORY-037](stories/STORY-037-mcp-diagnostico-multimodelo.md) | Expandir MCP diagnóstico | 2h | RAG-10.6, 6.2 | Consolidação | draft |
| [STORY-038](stories/STORY-038-performance-benchmarking.md) | Performance Benchmarking | 3h | Métricas PRD | Qualidade | draft |
| [STORY-039](stories/STORY-039-user-documentation-rag.md) | Documentação de usuário | 2h | — | Consolidação | draft |
| [STORY-040](stories/STORY-040-config-schema-rag.md) | Schema e Config RAG | 2h | RAG-9.1, 9.4, 10.7, 11.5 | Consolidação | draft |
| [STORY-041](stories/STORY-041-debt-telemetry-nps.md) | Dívidas v1.0 + Telemetria + NPS | 6h | RAG-2.3, 2.4, 3.1 (rem.), 5.2 | Encerramento | draft |
| | **Total** | **51h** (30h done · 21h restante) | **26 RULE-IDs** (20 implementados) | | |

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

- [x] Gerar handoff ao final de cada story (6/12 — STORY-030..035 com handoff)
- [ ] Atualizar CHANGELOG.md com mudanças da sprint
- [ ] Handoff consolidado ao final da sprint

## Definição de Pronto (DoD)

- [ ] 12 stories implementadas com TDD (6/12 concluídas — STORY-030..035)
- [ ] 26 RULE-IDs cobertos (20 implementados, 6 pendentes)
- [x] Testes passando (`python -m pytest` — zero regressão nas stories concluídas)
- [ ] RULE-IDs referenciados nos commits (pendente — código não commitado)
- [x] Handoff gerado ao final (6 handoffs existentes)
- [ ] Métricas de performance validadas (STORY-038)
- [ ] NPS do módulo RAG com primeira coleta (STORY-041)
