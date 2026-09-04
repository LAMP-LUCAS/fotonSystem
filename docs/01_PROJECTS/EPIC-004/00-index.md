---
type: concept
domain: core
status: active
tags: [epic-004, rag, index]
---

# EPIC-004 — RAG Pipeline Inteligente: Índice

**Stories planejadas:** 12 (STORY-030 a STORY-041)
**Spec:** `specs/MOD-RAG/SPEC-RAG-v2.0.md`
**PRD:** `docs/prd/epics/EPIC-004.md`

## Mapa de Stories

| # | Story | Layer | Responsabilidade | Depende de | Status |
|---|-------|-------|-----------------|------------|--------|
| 030 | Hardware Profiler + Model Registry | Detecção | Detectar CPU/RAM/GPU, catalogar modelos | Nenhuma | draft |
| 031 | Model Router + VectorStore Refactor | Armazenamento | Roteamento multi-modelo, VectorStoreManager | 030 | draft |
| 032 | Download Manager | Infraestrutura | Download sob demanda com progresso | 030 | draft |
| 033 | RAG Pipeline Node System | Inferência | Grapho de nós (embed, search, rerank, format) | 031 | draft |
| 034 | TUI RAG Configuration | Interface | Menus de configuração de modelo/pipeline | 030, 031, 032, 033 | draft |
| 035 | Migration + Backward Compatibility | Migração | Coleção legada → novo formato, fallback | 031 | draft |
| **036** | **Testes E2E Pipeline RAG** | **QA** | **Fluxo completo entre todas as camadas** | **030-033, 035** | **draft** |
| **037** | **Expandir MCP diagnóstico** | **Interface** | **Diagnóstico multi-coleção no MCP** | **031** | **draft** |
| **038** | **Performance Benchmarking** | **QA** | **SLAs e validação de performance** | **031, 033** | **draft** |
| **039** | **Documentação de usuário** | **Docs** | **Guia do usuário e do desenvolvedor** | **030, 032, 034, 038** | **draft** |
| **040** | **Schema e Config RAG** | **Config** | **Validação de schema settings.json** | **031** | **draft** |
| **041** | **Dívidas v1.0 + Telemetria + NPS** | **Dívida** | **Subprocess, testes faltantes, telemetria inline, NPS** | **Nenhuma** | **draft** |

## Dependências entre Stories

```
030 (Profiler + Registry) ──→ 031 (Router + Store Refactor) ──→ 033 (Pipeline Nodes)
           │                                                        │
           ├──→ 032 (Download Manager)                              │
           │                                                        │
           └──────────────────────┬─────────────────────────────────┘
                                  │
                                  ▼
                          034 (TUI Configuration)
                          035 (Migration + Compat)
                                  │
              ┌───────────────────┼────────────────────┐
              ▼                   ▼                    ▼
        036 (Testes E2E)    037 (MCP Diag)       038 (Benchmark)
                                                     │
                                                     ▼
                                              039 (Documentação)
             
040 (Schema Config) ← 031 — paralelo, sem blockers

041 (Dívidas + Telemetria + NPS) ← independente — pode rodar em paralelo
```

## Regras do Diretório

- Cada story em `.opencode/backlog/stories/STORY-NNN-*.md`
- Spec consolidada em `specs/MOD-RAG/SPEC-RAG-v2.0.md`
- Sprint plan em `docs/01_PROJECTS/EPIC-004/SprintPlan.md`
- Handoffs em `.opencode/handoffs/`
