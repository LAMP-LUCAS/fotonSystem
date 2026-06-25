---
status: "active"
inicio: "2026-06-25"
fim: "TBD"
---

# Sprint 5 — Domain Model, CRUD & UX Evolution

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Objetivo

Implementar camada de domínio com entidades ricas, CRUD completo (soft delete/restore), pipeline de sincronização unificado e UX modernizada com busca global, subgrupos e feedback de progresso.

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Status |
|----|-----------|------------|----------|--------|
| [STORY-010](stories/STORY-010-domain-model-status-migration.md) | Domain Model — Migração da Coluna Status | 3h | DOMAIN-1.4, 1.5, 1.6 | ready |
| [STORY-011](stories/STORY-011-domain-model-entities.md) | Domain Model — Entidades de Domínio | 5h | DOMAIN-1.1, 1.2, 1.3 | ready |
| [STORY-012](stories/STORY-012-crud-delete-restore-mcp.md) | CRUD — Ferramentas de Delete/Restore (MCP) | 8h | DOMAIN-2.1, 2.2, 2.3, 2.4, 2.7 | ready |
| [STORY-013](stories/STORY-013-crud-financeiro-info-files.md) | CRUD — Validação Financeiro + INFO Files | 4h | DOMAIN-2.5, 2.6 | ready |
| [STORY-014](stories/STORY-014-pipeline-sync-unificado.md) | Pipeline de Sincronização Unificado | 8h | DOMAIN-3.1, 3.2, 3.3, 3.4, 3.5 | ready |
| [STORY-015](stories/STORY-015-ux-menus-split-helpers.md) | UX — Split menus.py + Helpers TUI | 6h | DOMAIN-4.1, 4.2, 4.3 | ready |
| [STORY-016](stories/STORY-016-ux-menu-restructuring-navigation.md) | UX — Reestruturação Menu + Navegação | 8h | DOMAIN-4.4, 4.5, 4.6, 4.7, 4.8 | ready |
| | **Total** | **42h** | **23 RULE-IDs** | |

## Dependências

```
STORY-010 ──→ STORY-011 ──→ STORY-012
                               │
                               ├──→ STORY-013
                               │
                               └──→ STORY-014 ──→ (independe)
               
STORY-015 ──→ STORY-016
```

- STORY-012 depende de STORY-011 (entidades de domínio)
- STORY-013 depende de STORY-011 (usa entidades)
- STORY-014 depende de STORY-012 (usa soft delete no relatório)
- STORY-015 e STORY-016 são independentes entre si
- STORY-015 depende de STORY-011 (entities disponíveis para helpers)

## Débito Técnico

- [ ] Atualizar CHANGELOG.md com todas as mudanças
- [ ] Atualizar AGENTS.md com novas MCP tools
- [ ] version.txt → `1.5.0`
- [ ] Handoff gerado ao final da sprint

## Definição de Pronto (DoD)

- [ ] Código implementado seguindo RULE-IDs da spec
- [ ] 23 RULE-IDs cobertos por testes
- [ ] Testes passando (`python -m pytest` — zero regressão)
- [ ] RULE-IDs referenciados nos commits
- [ ] Handoff gerado ao final
- [ ] version.txt atualizado
