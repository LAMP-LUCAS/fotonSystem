# Relatório de Handoff — Sprint 7 (EPIC-003)

**Data:** 2026-06-30
**Sprint:** 2026-SPRINT-7
**Épico:** EPIC-003 — Automação Comercial e Documentos
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`
**Status:** ✅ COMPLETA (4/4 stories, 9 RULE-IDs)

---

## 1. Resumo

A Sprint 7 implementou os 9 RULE-IDs restantes da SPEC-DOCUMENTOS-v1.1, elevando o módulo de documentos de **50% → 100%**. Foram 4 stories executadas em sequência, totalizando **~21h de esforço**.

| Story | RULE-IDs | h | Commits |
|-------|----------|---|---------|
| STORY-022 — Pré-validação Obrigatória + Placeholder Zero | DOC-2.1↑, 2.4, 2.5 | 6h | `b0e777e` |
| STORY-023 — Engine de Fórmulas Extraída + Hardening | DOC-4.1↑, 4.2↑, 4.3, 4.4 | 5h | `ebf315a` |
| STORY-024 — Histórico de Versões | DOC-3.6 | 4h | `b8154fa` |
| STORY-025 — Geração em Lote + Nomenclatura Padronizada | DOC-3.2↑, 3.5 | 6h | `fc45f55` |

---

## 2. O que foi entregue

### Pré-validação Obrigatória (STORY-022)
- `generate_document()` executa `validar_template` internamente e bloqueia se houver variáveis não resolvidas
- Adapters DOCX/PPTX validam pós-replace se `@VAR` sobreviveu como `"None"`/`"---"` — erro explícito
- `validar_template` relatório colorido categorizado (✅ resolvidas / ❌ faltantes / ⚠️ valores inválidos)

### Engine de Fórmulas Extraída (STORY-023)
- `core/ops/formula_engine.py` — `FormulaEngine` com `resolve()` e `report()`
- Div/0, NaN, Infinity → erro explícito (status FAIL) em vez de 0.0 silencioso
- `safe_math.py` atualizado para levantar erro em vez de retornar 0.0
- `FormSession._evaluate` harmonizada com `FormulaEngine` (parser único)

### Histórico de Versões (STORY-024)
- `historico_documentos.jsonl` por cliente com campos completos
- Regeneração preserva versão anterior (`_v1` → `_v2`)
- Nova MCP tool `historico_documentos(cliente, limite=10)`
- Opção TUI "Histórico de Documentos"

### Geração em Lote + Nomenclatura (STORY-025)
- `gerar_documentos_lote(cliente, documentos)` — MCP tool com 2 fases
- `OpGenerateBatchDocuments(BaseOp)` — POP auditado
- Padrão `CLIENTE_SERVICO_TIPO_DATA.ext` com fallback legado

---

## 3. Estado do Código

| Métrica | Valor |
|---------|-------|
| Testes totais | **792** (98 novos desde o 1.4.0) |
| Commits na sprint | 4 |
| Arquivos novos | `formula_engine.py` |
| Arquivos modificados | `document_service.py`, `op_doc_gen.py`, `foton_mcp.py`, `menus_docs.py`, `python_docx_adapter.py`, `python_pptx_adapter.py`, `safe_math.py`, `mcp_services.py`, `form_session.py` |

---

## 4. Decisões de Arquitetura

1. **Pré-validação bloqueante:** `_validate_keys()` retorna `dict` categorizado (não mais `list[str]`). `clean_missing_variables` removido — substituído por `ValueError` bloqueante.
2. **FormulaEngine modular:** Extraído para `core/ops/` seguindo o padrão de componentes reutilizáveis. `DocumentService` e `FormSession` agora delegam para a mesma engine.
3. **JSONL em vez de SQLite:** `historico_documentos.jsonl` (append-only) — sem dependência extra de DB, fácil de ler/auditar manualmente.
4. **Batch como POP separado:** `OpGenerateBatchDocuments` segue `BaseOp` — auditoria + telemetria automáticas, mesmo padrão dos demais POPs.
5. **Nomenclatura com fallback:** `CLIENTE_SERVICO_TIPO_DATA.ext` com sanitização (acentos mantidos, símbolos removidos). Fallback para `GERADO_{template_name}` se `client_name` vazio.

---

## 5. Pendências para Próximas Sprints

- **Nenhuma pendência técnica na EPIC-003** — 18/18 RULE-IDs implementados
- Próximo épico a ser definido (candidatos: EPIC-006 Financeiro, EPIC-004 RAG, EPIC-007 Cronograma)

---

## 6. Artefatos Atualizados

| Artefato | Mudança |
|----------|---------|
| `CHANGELOG.md` | Adicionada seção Sprint 7 no `[Unreleased]` |
| `AGENTS.md` | EPIC-003: `completed`; MCP tools: 43; Documentos: 8 ferramentas |
| `2026-SPRINT-7.md` | `planning` → `done` |
| `STORY-022/023/024/025` | `ready` → `done` |
