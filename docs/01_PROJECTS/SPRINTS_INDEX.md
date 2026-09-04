---
type: index
domain: core
status: active
tags: [roadmap, sprints, tracking]
---

# Índice de Sprints — Foton System

## Mapa Estratégico

```
[2025]                         [2026]
  |                              |
  v                              v
SystemAudit ──> DualInterface ──> Resiliência ──> InfoNaming ──> DomainCRUD
(Arquitetura)    (TUI + MCP)      (Segurança +     (Nomenclatura   (Domain Model
                                    Robustez)        Configurável)   CRUD + UX)
```

## Sprints Concluídas

| Sprint | Data | Commits | Objetivo | Resultado |
|--------|------|---------|----------|-----------|
| **SystemAudit** | Mai/2026 | `650e964` `4bc8b15` ... | Auditoria arquitetural, segurança, resiliência, documentação | ✅ Cobertura de path traversal, circuit breaker, tip service, documentação |
| **DualInterface** | Jun/2026 | `69a9edb` `ae8a4d2` `1aa4682` `fe11bae` | TUI bugs, dedup MCP↔domain, documentação dual-paradigma, flag `--tui` | ✅ 4 commits, 264 testes, zero regressão |

## Sprints Concluídas (novo formato)

| Sprint | Épico | Stories | Esforço | RULE-IDs |
|--------|-------|---------|---------|----------|
| **2026-SPRINT-7** | EPIC-003 — Documentos v1.1 | 4 | ~21h | 9 |

## Sprints Ativas

| Sprint | Foco | Stories | Esforço | Spec |
|--------|------|---------|---------|------|
| **2026-SPRINT-8** | EPIC-004 — RAG (Filtros + Contexto + Diagnóstico) | 2 | ~7h | `SPEC-RAG-v1.0` |
| **Resiliência** | Segurança (`eval`→parser), bare excepts, bugs, vapor, arquitetura, testes | 8 fases | ~21h | — |
| **InfoNaming** | Sistema de nomenclatura configurável de arquivos INFO com placeholders | 7 fases | ~20h | — |
| **DomainCRUD** | Domain Model (entidades, VOs), CRUD completo (soft delete), Pipeline sync | 3 fases | ~20-26h | — |
| **2026-07-SPRINT-4** | Consolidação UX + rastreabilidade | 4 stories | ~11h | — |

## Próximas Candidatas

| Sprint | Foco | Esforço | Status | Doc |
|--------|------|---------|--------|-----|
| **UX Agêntica** | JSON estruturado nas tools MCP, rate limiting, observabilidade | — | 🗓️ candidata | — |
| **i18n** | Internacionalização das strings de interface | — | 🗓️ candidata | — |
| **WebView Revival** | Feature parity TUI↔WebView, autosave, segurança | — | 🗓️ candidata | — |

---

## Convenção

### Formato Legado (sprints em `docs/01_PROJECTS/`)
Cada sprint vive em `docs/01_PROJECTS/Sprint_<Nome>/` com:
- `SprintPlan.md` — planejamento detalhado (fases, TDD, riscos)
- `Log.md` — registro diário de progresso

### Novo Formato (a partir de 2026-07)
Sprints e stories migram para `.opencode/backlog/`:
- `.opencode/backlog/sprints/YYYY-MM-SPRINT-N.md`
- `.opencode/backlog/stories/STORY-NNN-descricao.md`
- Commits referenciam `[STORY-XXX] [RULE-X.Y.Z]`
