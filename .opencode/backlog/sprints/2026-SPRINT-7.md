---
status: "done"
inicio: "2026-06-30"
fim: "2026-06-30"
---

# Sprint 7 — Automação Comercial e Documentos (EPIC-003)

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Objetivo

Completar o módulo de documentos em 100% da SPEC-DOCUMENTOS-v1.1: implementar os 9 RULE-IDs restantes para automação comercial confiável — pré-validação obrigatória, engine de fórmulas robusta, histórico versionado e geração em lote.

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Status |
|----|-----------|------------|----------|--------|
| [STORY-022](stories/STORY-022-pre-validacao-placeholder-zero.md) | Pré-validação Obrigatória + Placeholder Zero | 6h | DOC-2.1↑, DOC-2.4, DOC-2.5 | ✅ done |
| [STORY-023](stories/STORY-023-engine-de-formulas.md) | Engine de Fórmulas Extraída + Hardening | 5h | DOC-4.1↑, DOC-4.2↑, DOC-4.3, DOC-4.4 | ready |
| [STORY-024](stories/STORY-024-historico-de-versoes.md) | Histórico de Versões (JSONL + MCP + TUI) | 4h | DOC-3.6 | ready |
| [STORY-025](stories/STORY-025-geracao-lote-nomenclatura.md) | Geração em Lote + Nomenclatura Padronizada | 6h | DOC-3.2↑, DOC-3.5 | ready |
| | **Total** | **21h** | **9 RULE-IDs** | |

## Dependências

```
STORY-024 ── (independente)

STORY-022 ──┬── STORY-023 (fraca)
            │
            └── STORY-025 (forte)
```

STORY-023 pode ser feita em paralelo com STORY-022, mas idealmente depois (para testar integração com pré-validação).
STORY-025 depende fortemente de STORY-022 (precisa da pré-validação obrigatória no pipeline de lote).

## Ordem Recomendada de Execução

1. **STORY-024** (independente — paralelizável)
2. **STORY-022** (base crítica para o restante)
3. **STORY-023** (engine, prefere 022 pronta)
4. **STORY-025** (depende de 022)

## Débito Técnico

- [x] Atualizar CHANGELOG.md com mudanças da sprint
- [x] Gerar handoff ao final da sprint

## Definição de Pronto (DoD)

- [x] Código implementado seguindo RULE-IDs da spec
- [x] 9 RULE-IDs cobertos por testes
- [x] Testes passando (`python -m pytest` — 792/792, zero regressão)
- [x] RULE-IDs referenciados nos commits
- [x] Handoff gerado ao final
