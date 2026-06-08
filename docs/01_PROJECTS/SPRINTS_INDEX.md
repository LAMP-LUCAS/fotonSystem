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
SystemAudit ──> DualInterface ──> Resiliência ──> [Próximo]
(Arquitetura)    (TUI + MCP)      (Segurança +     (UX Agêntica?)
                                   Robustez)
```

## Sprints Concluídas

| Sprint | Data | Commits | Objetivo | Resultado |
|--------|------|---------|----------|-----------|
| **SystemAudit** | Mai/2026 | `650e964` `4bc8b15` ... | Auditoria arquitetural, segurança, resiliência, documentação | ✅ Cobertura de path traversal, circuit breaker, tip service, documentação |
| **DualInterface** | Jun/2026 | `69a9edb` `ae8a4d2` `1aa4682` `fe11bae` | TUI bugs, dedup MCP↔domain, documentação dual-paradigma, flag `--tui` | ✅ 4 commits, 264 testes, zero regressão |

## Sprint Ativa

| Sprint | Foco | Fases | Esforço |
|--------|------|-------|---------|
| **Resiliência** | Segurança (`eval`→parser), bare excepts, bugs, vapor, arquitetura, testes | 8 fases | ~21h |

## Próximas Candidatas (não planejadas)

- **UX Agêntica**: JSON estruturado nas tools MCP, rate limiting, observabilidade
- **i18n**: Internacionalização das strings de interface
- **WebView Revival**: Feature parity TUI↔WebView, autosave, segurança

---

## Convenção

Cada sprint vive em `docs/01_PROJECTS/Sprint_<Nome>/` com:
- `SprintPlan.md` — planejamento detalhado (fases, TDD, riscos)
- `Log.md` — registro diário de progresso
