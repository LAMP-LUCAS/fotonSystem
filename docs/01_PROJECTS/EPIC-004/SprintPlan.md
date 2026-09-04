---
type: plan
domain: core
status: draft
tags: [epic-004, sprint, planning]
---

# Sprint Plan — EPIC-004 / RAG Pipeline Inteligente

**Spec:** `specs/MOD-RAG/SPEC-RAG-v2.0.md`
**PRD:** `docs/prd/epics/EPIC-004.md`
**Estimativa total:** 51h

## Roadmap

| Fase | Stories | Esforço | Objetivo |
|------|---------|---------|----------|
| **Fase 1 — Fundação** | 030, 032 | 8h | Hardware Profiler, Model Registry, Download Manager |
| **Fase 2 — Núcleo** | 031 | 8h | Model Router, VectorStoreManager (refactor do singleton) |
| **Fase 3 — Pipeline** | 033 | 8h | Node system, EmbedNode, SearchNode, RerankNode, FormatNode |
| **Fase 4 — Interface** | 034 | 4h | TUI de configuração RAG |
| **Fase 5 — Migração** | 035 | 2h | Coleção legada → novo formato |
| **Fase 6 — Qualidade** | 036, 038 | 9h | Testes E2E + Performance Benchmarking |
| **Fase 7 — Consolidação** | 037, 039, 040 | 6h | MCP multi-modelo, documentação, schema validation |
| **Fase 8 — Encerramento** | 041 | 6h | Subprocess mode, testes faltantes, telemetria inline, NPS |

## RULE-IDs mapeados

| RULE-ID | Descrição | Story |
|---------|-----------|-------|
| RULE-RAG-7.1 a 7.4 | Hardware Profiler | 030 |
| RULE-RAG-8.1 a 8.4 | Model Registry | 030 |
| RULE-RAG-12.1 a 12.5 | Download Manager | 032 |
| RULE-RAG-9.1 a 9.5 | Model Router | 031 |
| RULE-RAG-10.1 a 10.7 | VectorStoreManager | 031 |
| RULE-RAG-11.1 a 11.6 | Pipeline Node System | 033 |
| RULE-RAG-7.3, 9.4, 12.3 | TUI Configuration | 034 |
| RULE-RAG-10.7 | Migration + Compat | 035 |
| RULE-RAG-1.1 a 6.2 | Integração E2E (herança) | 036 |
| RULE-RAG-10.6, 6.2 | MCP multi-modelo | 037 |
| Métricas PRD | Performance SLA | 038 |
| RULE-RAG-9.1, 9.4, 10.7, 11.5 | Schema Config | 040 |
| RAG-2.3, 2.4, 3.1 (remoção), 5.2 | Dívidas v1.0 + Telemetria + NPS | 041 |

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| VectorStore singleton refactor quebra testes existentes | Média | Alto | Testes de compatibilidade (STORY-035) antes do merge |
| BGE-M3 download de 2.2 GB falha por timeout | Baixa | Médio | Retry + resume parcial (huggingface_hub já suporta) |
| GPU não detectada corretamente em Windows | Média | Baixo | Fallback para CPU com warning |
| Pipeline node interface muito abstrata | Média | Médio | Começar com nós concretos, abstrair depois (YAGNI) |
| Testes E2E dependem de todas as stories anteriores | Alta | Médio | Blocker natural — executar após Fase 5 |
| Benchmark BGE-M3 sem GPU pode ser lento demais | Alta | Baixo | Mock do BGE-M3 em CI; benchmark real apenas em HW compatível |
