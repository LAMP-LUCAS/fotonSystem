---
status: "active"
inicio: "2026-06-25"
fim: "TBD"
---

# Sprint 5 — Domain Model, CRUD & Pipeline Sync

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.1.md`
**Dependência externa:** UI/UX items now in EPIC-001 (SPEC-UX-v1.0 — RULE-UX-8.1 to 8.8)

## Objetivo

Implementar camada de domínio com entidades ricas, CRUD completo (soft delete/restore) e pipeline de sincronização unificado. UI/UX foi realocado para EPIC-001 (ver SPEC-UX-v1.0).

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Status |
|----|-----------|------------|----------|--------|
| [STORY-010](stories/STORY-010-domain-model-status-migration.md) | Domain Model — Migração da Coluna Status | 3h | DOMAIN-1.4, 1.5, 1.6 | done |
| [STORY-011](stories/STORY-011-domain-model-entities.md) | Domain Model — Entidades de Domínio | 5h | DOMAIN-1.1, 1.2, 1.3 | partial |
| [STORY-012](stories/STORY-012-crud-delete-restore-mcp.md) | CRUD — Ferramentas de Delete/Restore (MCP) | 8h | DOMAIN-2.1, 2.2, 2.3, 2.4, 2.7 | done |
| [STORY-013](stories/STORY-013-crud-financeiro-info-files.md) | CRUD — Validação Financeiro + INFO Files | 4h | DOMAIN-2.5, 2.6 | done |
| [STORY-014](stories/STORY-014-pipeline-sync-unificado.md) | Pipeline de Sincronização Unificado | 8h | DOMAIN-3.1, 3.2, 3.3, 3.4, 3.5 | done |
| [STORY-015](stories/STORY-015-ux-menus-split-helpers.md) | UX — Split menus.py + Helpers TUI | 6h | UX-8.1, 8.2, 8.3 | done |
| [STORY-016](stories/STORY-016-ux-menu-restructuring-navigation.md) | UX — Reestruturação Menu + Navegação | 4h | UX-8.4, 8.5, 8.6, 8.7, 8.8 | done |
| [STORY-017](stories/STORY-017-integracao-entidades-dominio.md) | Integração das Entidades de Domínio | 3h | DOMAIN-1.1, 1.2, 1.3 (integração) | done |
| [STORY-018](stories/STORY-018-pop-audit-atualizar-ficha.md) | POP Audit para `atualizar_ficha_cliente` | 4h | DOMAIN-2.8 | done |
| | **Total** | **45h** | **27 RULE-IDs** | |

## Dependências

```
STORY-010 ──→ STORY-011 ──→ STORY-012
                               │
                               ├──→ STORY-013
                               │
                               └──→ STORY-014

STORY-015      STORY-016  (UX — EPIC-001, independentes entre si)

STORY-017 (integração — depende de STORY-011, adicionado durante sprint)
```

- STORY-012 depende de STORY-011 (entidades de domínio)
- STORY-013 depende de STORY-011 (usa entidades)
- STORY-014 depende de STORY-012 (usa soft delete no relatório)
- STORY-017 depende de STORY-011 (integra entidades no fluxo de produção)
- UI/UX items (STORY-015, STORY-016) movidos para EPIC-001 — ver SPEC-UX-v1.0 e v1.1 (RULE-UX-8.1 a 8.8)

## Débito Técnico

- [ ] Atualizar CHANGELOG.md com todas as mudanças
- [ ] Atualizar AGENTS.md com novas MCP tools
- [ ] version.txt → `1.5.0`
- [x] Handoff gerado ao final da sprint

## Definição de Pronto (DoD)

- [ ] Código implementado seguindo RULE-IDs da spec
- [ ] 27 RULE-IDs cobertos por testes
- [ ] Testes passando (`python -m pytest` — zero regressão)
- [ ] RULE-IDs referenciados nos commits
- [ ] Handoff gerado ao final
- [ ] version.txt atualizado
