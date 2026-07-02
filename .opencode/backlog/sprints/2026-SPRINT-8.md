---
status: "active"
inicio: "2026-07-02"
fim: "TBD"
---

# Sprint 8 — Recuperação Inteligente (RAG) — EPIC-004

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v1.0.md`

## Objetivo

Evoluir o RAG de MVP técnico para ferramenta de uso diário: criar SPEC formal, implementar filtros de busca por cliente/tipo de documento, contexto enriquecido nos resultados, diagnóstico de integridade e indexação seletiva.

## Stories

| ID | Descrição | Estimativa | RULE-IDs | Status |
|----|-----------|------------|----------|--------|
| [STORY-028](stories/STORY-028-spec-rag-v1.md) | SPEC-RAG-v1.0 — Formalização | 1h | RAG-1.1 a 6.2 | done |
| [STORY-029](stories/STORY-029-filtros-contexto-diagnostico-rag.md) | Filtros + Contexto + Diagnóstico | 6h | RAG-4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2 | ready |
| | **Total** | **7h** | **7 RULE-IDs** | |

## Dependências

```
STORY-028 (SPEC) ──→ STORY-029 (features)
```

STORY-028 já concluída. STORY-029 pronta para execução.

## Débito Técnico

- [ ] Atualizar CHANGELOG.md com mudanças da sprint
- [ ] Gerar handoff ao final da sprint

## Definição de Pronto (DoD)

- [ ] Código implementado seguindo RULE-IDs da spec
- [ ] 7 RULE-IDs cobertos por testes
- [ ] Testes passando (`python -m pytest` — zero regressão)
- [ ] RULE-IDs referenciados nos commits
- [ ] Handoff gerado ao final
