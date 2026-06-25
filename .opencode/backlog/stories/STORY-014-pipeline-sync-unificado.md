---
status: "ready"
sprint: "2026-SPRINT-5"
---

# STORY-014: Pipeline de Sincronização Unificado

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Descrição

Consolidar as 7 ferramentas de sincronização fragmentadas em um pipeline único com 3 direções, dry-run como default, SyncReport estruturado e backward compatibility via aliases.

## Regras Implementadas

- **RULE-DOMAIN-3.1:** `pipeline_sincronizacao()` com 3 direções + `dry_run=True`
- **RULE-DOMAIN-3.2:** Pipeline com 5 passos: snapshot, diff, validate, apply, report
- **RULE-DOMAIN-3.3:** `SyncReport` com `to_dict()` e `resumo()`(serialização)
- **RULE-DOMAIN-3.4:** Ferramentas existentes delegam internamente para o pipeline
- **RULE-DOMAIN-3.5:** Sync nunca remove dados; filesystem prevalece em conflitos

## Critérios de Aceite

- [ ] `pipeline_sincronizacao()` aceita `pastas_to_db`, `db_to_pastas`, `bidir`
- [ ] `dry_run=True` como default (executa diff + validate mas não apply)
- [ ] 5 passos executados em sequência
- [ ] `SyncReport` com: direção, dry_run, listas de novos/atualizados/deletados, conflitos, erros, duração, timestamp
- [ ] `SyncReport.to_dict()` para serialização MCP
- [ ] `SyncReport.resumo()` texto para TUI
- [ ] `sincronizar_clientes`, `sincronizar_pastas_clientes`, `sincronizar_base` delegam para pipeline
- [ ] Nenhum dado removido durante sync (apenas adiciona/atualiza)
- [ ] Conflito: filesystem prevalece como Centro de Verdade
- [ ] Testes: 3 direções, dry-run vs apply, conflitos, SyncReport serialização
- [ ] Zero regressão

## Estimativa

8h
