---
status: "done"
inicio: "2026-06-28"
fim: "2026-06-29"
---

# Sprint 6 — Telemetria, Observabilidade e NPS Evolutivo

**Épico:** EPIC-012, EPIC-001
**Spec:** `MOD-TELEMETRY/SPEC-TELEMETRY-v1.0.md`, `MOD-UX/SPEC-UX-v1.2.md`

## Objetivo

Implementar telemetria de uso (session + operation tracking) com exportação local, e expandir a pesquisa NPS com contexto de uso e evolução temporal. Fechar os gaps de métricas identificados no Review da Sprint 5 para o EPIC-002.

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Status |
|----|-----------|------------|----------|--------|
| [STORY-020](stories/STORY-020-telemetria-session-operation-tracking.md) | Telemetria — Session + Operation Tracking | 5h | TELEMETRY-1.1, 1.2, 1.3, 1.4 | done |
| [STORY-021](stories/STORY-021-nps-evolutivo-export-unificado.md) | NPS Evolutivo + Export Unificado | 4h | UX-9.1, UX-9.2, TELEMETRY-1.5 | done |
| | **Total** | **9h** | **7 RULE-IDs** | |

## Dependências

```
STORY-020 ──→ STORY-021
```

STORY-021 depende de STORY-020 (session_tracker + operation_log necessários para o contexto do NPS e export unificado).

## Débito Técnico

- [x] Atualizar CHANGELOG.md com mudanças da sprint
- [x] Atualizar AGENTS.md com EPIC-012 e SPEC-UX-v1.2
- [ ] Handoff gerado ao final da sprint

## Definição de Pronto (DoD)

- [x] Código implementado seguindo RULE-IDs da spec
- [x] 7 RULE-IDs cobertos por testes
- [x] Testes passando (`python -m pytest` — zero regressão)
- [x] RULE-IDs referenciados nos commits
- [ ] Handoff gerado ao final
