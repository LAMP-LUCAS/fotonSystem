---
type: epic
domain: documents
status: active
tags: [epic-003, roadmap, documents, automation, sprint-7]
---

# EPIC-003 — Automação Comercial e Documentos (v1.1)

## Resumo

Evoluir o módulo de documentos de **50% → 100%** da SPEC-DOCUMENTOS-v1.1, implementando os 9 RULE-IDs restantes para completar o ciclo de automação comercial: pré-validação obrigatória, engine de fórmulas robusta, histórico versionado e geração em lote.

## Status Atual — Auditoria de RULE-IDs

| Status | Contagem | RULE-IDs |
|--------|----------|----------|
| ✅ Já implementados (v1.0) | 7 | 1.1, 1.2, 1.3, 1.4, 2.2, 2.3, 3.1 |
| ✅ Já implementados (v1.1 básico) | 2 | 4.1, 4.2 |
| ⚠️ Existem mas precisam de upgrade | 3 | **2.1** (relatório colorido), **3.2** (nomenclatura), **4.3** (NaN/Infinity hardening) |
| ❌ Não implementados | 6 | **2.4** (pré-validação obrigatória), **2.5** (placeholder zero), **3.5** (geração lote), **3.6** (histórico), **4.4** (relatório fórmulas), **5.1-5.3** (TUIFormView — já estão) |

**Total: 18 RULE-IDs → 9 OK / 3 upgrade / 6 novos = 50% completo**

## Mapa de Implementação

### Dependências

```
STORY-022 ──┬── STORY-023 (fraca)
            │
            └── STORY-025 (forte)
            
STORY-024 (independente)
```

---

## Story 022 — Pré-validação Obrigatória + Placeholder Zero

**Esforço:** ~6h | **Dependências:** Nenhuma

### O que fazer

| RULE-ID | Ação | Descrição | Arquivos |
|---------|------|-----------|----------|
| 2.4 | **Nova** | `gerar_documento()` executa `validar_template` internamente antes de gerar. Se houver variáveis faltando → bloqueia com relatório de erro | `document_service.py:132` (generate_document), `op_doc_gen.py:execute_logic` |
| 2.5 | **Nova** | Após merge, verificar se `@VAR` sobreviveu como `"None"`/`"---"`/vazio no documento final. Se sim → erro antes de salvar | `document_service.py`, `python_docx_adapter.py`, `python_pptx_adapter.py` |
| 2.1 | **Upgrade** | `validar_template` retorna relatório colorido com categorias: ✅ resolvidas / ⚠️ fórmulas validadas / ❌ faltantes | `foton_mcp.py:894`, `menus_docs.py:160` |

### Testes

- `test_rule_2_4_pre_validation_blocks_generation_with_missing_vars`
- `test_rule_2_5_placeholder_zero_blocks_generation`
- `test_rule_2_5_clean_generation_passes`
- `test_rule_2_1_colored_report_format`

---

## Story 023 — Engine de Fórmulas Extraída + Hardening

**Esforço:** ~5h | **Dependências:** STORY-022 (fraca — pode rodar depois)

### O que fazer

| RULE-ID | Ação | Descrição | Arquivos |
|---------|------|-----------|----------|
| 4.1-4.2 | **Extrair** | Mover `_resolve_operations` de `DocumentService` para módulo dedicado `core/ops/formula_engine.py` | `formula_engine.py` (novo), `document_service.py` |
| 4.3 | **Upgrade** | NaN/Infinity: `safe_eval` hoje retorna 0.0 silenciosamente em div/0. Mudar para erro explícito com status FAIL. Adicionar `NaN` e `inf` detection pós-eval | `safe_math.py`, `formula_engine.py` |
| 4.4 | **Nova** | `FormulaEngine.report()` retorna lista de fórmulas com: `{var, expressao, resultado, status}` | `formula_engine.py` |
| — | **Harmonizar** | Unificar `DocumentService._resolve_operations` e `FormSession._evaluate` que hoje têm parsing divergente | `form_session.py`, `document_service.py` |

### Arquitetura do `FormulaEngine`

```
FormulaEngine
├── resolve(replacements: dict) → dict (valores resolvidos)
├── report() → list[FormulaResult] (relatório)
└── safe_eval(expr) → float (delega safe_math)
```

### Testes

- `test_formula_engine_extraction_keeps_behavior`
- `test_nan_infinity_explicit_error`
- `test_formula_engine_report_structure`
- `test_formula_circular_dependency_error`
- `test_formula_engine_brazilian_number_format`

---

## Story 024 — Histórico de Versões

**Esforço:** ~4h | **Dependências:** Nenhuma

### O que fazer

| RULE-ID | Ação | Descrição | Arquivos |
|---------|------|-----------|----------|
| 3.6 | **Nova** | Substituir `history.log` textual por `historico_documentos.jsonl` na pasta do cliente. Campos obrigatórios: `data_hora`, `tipo_template`, `nome_arquivo`, `status`, `versao` | `document_service.py:_log_generation` |
| 3.6 MCP | **Nova** | MCP tool `historico_documentos(cliente, limite=10)` — retorna lista JSON de documentos gerados | `foton_mcp.py` |
| 3.6 TUI | **Nova** | Opção "Histórico de Documentos" no menu Documentos, exibe tabela com data/tipo/status | `menus_docs.py` |
| 3.6 | **Regeneração** | Ao regenerar documento existente: versão anterior vira `_v1`, nova é `_v2`, registro no JSONL com `versao_anterior` | `document_service.py:generate_document` |

### Formato JSONL

```jsonl
{"data_hora":"2026-07-01T14:30:00","tipo_template":"CONTRATO_HONORARIOS","nome_arquivo":"GERADO_CONTRATO_HONORARIOS_MATRIZ.docx","status":"SUCCESS","versao":1,"cliente":"Cliente A"}
{"data_hora":"2026-07-15T10:00:00","tipo_template":"PROPOSTA_COMERCIAL","nome_arquivo":"GERADO_PROPOSTA_v2.pptx","status":"SUCCESS","versao":2,"versao_anterior":"GERADO_PROPOSTA_v1.pptx","cliente":"Cliente A"}
```

### Testes

- `test_document_history_jsonl_created_on_generation`
- `test_document_history_append_on_multiple_generations`
- `test_document_history_regeneration_versioning`
- `test_mcp_tool_document_history_returns_entries`
- `test_document_history_error_on_missing_file`

---

## Story 025 — Geração em Lote + Nomenclatura Padronizada

**Esforço:** ~6h | **Dependências:** STORY-022

### O que fazer

| RULE-ID | Ação | Descrição | Arquivos |
|---------|------|-----------|----------|
| 3.5 MCP | **Nova** | `gerar_documentos_lote(cliente, documentos: list[dict])` — valida todos via pré-voo antes de gerar qualquer um. Se 1 falhar → lote todo bloqueado | `foton_mcp.py`, `op_doc_gen.py` |
| 3.5 TUI | **Nova** | Opção "Gerar Lote (Proposta + Contrato + Anexo)" no menu | `menus_docs.py` |
| 3.2 | **Upgrade** | Padrão de nomenclatura: `CLIENTE_SERVICO_TIPO_DATA.ext`. Fallback para nome legado se campos indisponíveis. Ex: `MATRIZ_REFORMA_PROPOSA_20260701.docx` | `document_service.py`, `op_doc_gen.py` |

### Pipeline de Lote

```
gerar_documentos_lote(documentos: [doc1, doc2, ...])
  │
  ├─ Fase 1: Pré-voo (valida todos)
  │   ├─ doc1 → validar_template → OK
  │   ├─ doc2 → validar_template → FALHA ❌
  │   └─ Lote bloqueado, relatório de erros por documento
  │
  └─ Fase 2: Geração (todos OK)
      ├─ doc1 → gerar_documento → OK
      ├─ doc2 → gerar_documento → OK
      └─ Relatório final consolidado
```

### Testes

- `test_batch_generation_all_valid`
- `test_batch_generation_blocked_if_one_fails`
- `test_batch_generation_report_format`
- `test_naming_convention_cliente_servico_tipo_data`
- `test_naming_convention_fallback_legacy`
- `test_mcp_tool_batch_generation_end_to_end`

---

## Resumo do Esforço

| Story | RULE-IDs | h | Tipo | Prioridade |
|-------|----------|---|------|------------|
| STORY-022 | 2.4, 2.5, 2.1↑ | ~6h | 🔵 Funcionalidade crítica | P0 |
| STORY-023 | 4.1-4.4 | ~5h | 🟢 Qualidade/Engine | P1 |
| STORY-024 | 3.6 | ~4h | 🟡 Observabilidade | P1 |
| STORY-025 | 3.5, 3.2↑ | ~6h | 🔵 Funcionalidade avançada | P0 |
| **Total** | **9 RULE-IDs** | **~21h** | | |

## Ordem Recomendada

1. **STORY-022** (pré-validação + placeholder) — base para tudo
2. **STORY-024** (histórico) — independente, pode rodar em paralelo com 022
3. **STORY-023** (engine de fórmulas) — após 022, extração segura
4. **STORY-025** (lote + nomenclatura) — depende de 022, coroa o módulo

## Riscos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Engine de fórmulas duplicada (DocumentService vs FormSession) | Bugs por parsing divergente | STORY-023 já prevê harmonização |
| safe_math retorna 0.0 em div/0 silenciosamente | Perda de dados financeiros | STORY-023: erro explícito + status FAIL |
| Geração em lote sem pré-validação | Lote gera documentos quebrados | STORY-025 depende de STORY-022 |
| Histórico JSONL sem migração de history.log legado | Perda de registros antigos | Aceitar como quebra controlada — history.log é local por cliente |
