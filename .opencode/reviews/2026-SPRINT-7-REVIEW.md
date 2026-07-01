# Revisão — 2026-SPRINT-7 / EPIC-003

**Data:** 2026-07-01
**Spec:** `specs/MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`
**PRD:** `docs/prd/epics/EPIC-003.md`

---

## 1. Resumo

| Item | Valor |
|---|---|
| Sprint | 2026-SPRINT-7 |
| Stories planejadas | 4 |
| Stories concluídas (status done) | 4 |
| RULE-IDs na SPEC v1.1 | 22 |
| RULE-IDs cobertos pela sprint | 9 (DOC-2.1↑, 2.4, 2.5, 3.2↑, 3.5, 3.6, 4.1↑, 4.2↑, 4.3, 4.4) |
| RULE-IDs implementados 100% | 14 de 22 |
| RULE-IDs implementados parcialmente | 3 (1.4, 3.2, 5.2) |
| RULE-IDs sem teste (violação) | 4 completos (2.2, 2.3, 3.3, 3.4) + 6 parciais |
| Anotações `@story:`/`@rule:` no código | **Ausentes** |
| Testes passando | 792/792 |

---

## 2. Adesão às Specs

### 2.1 Stories da Sprint

| Story | RULE-ID | Status | Observação |
|---|---|---|---|
| **STORY-022** | DOC-2.1↑ | ⚠️ Parcial | Relatório colorido implementado; campo `formulas` sem teste |
| | DOC-2.4 | ✅ Completo | Pré-validação bloqueante dentro de `generate_document()` |
| | DOC-2.5 | ✅ Completo | Placeholder zero em 2 camadas (pré e pós replace) |
| **STORY-023** | DOC-4.1↑ | ✅ Completo | `FormulaEngine` extraída, formato `[calculo: ...]` |
| | DOC-4.2↑ | ✅ Completo | `safe_eval()` com AST, `_parse_value_for_eval()`, BR format |
| | DOC-4.3 | ⚠️ Parcial | NaN/Infinity trata como erro, mas **sem teste explícito** |
| | DOC-4.4 | ⚠️ Parcial | Report implementado (`FormulaResult`), campo `var` não testado |
| **STORY-024** | DOC-3.6 | ✅ Completo | JSONL com versionamento, 15 testes |
| **STORY-025** | DOC-3.2↑ | ⚠️ Parcial | Padrão `CLIENTE_SERVICO_TIPO_DATA` OK; **GERADO_ prefixo ausente** (spec discrepante) |
| | DOC-3.5 | ✅ Completo | Lote com 2 fases (pré-voo unificado → geração), 5 testes |

### 2.2 Regras Pré-existentes (v1.0)

| RULE-ID | Implementado | Testado | Observação |
|---|---|---|---|
| DOC-1.1 | ✅ | ✅ | Templates em `templates/` |
| DOC-1.2 | ✅ | ⚠️ Parcial | PPTX adapter sem teste direto |
| DOC-1.3 | ✅ | ✅ | Case-insensitive |
| DOC-1.4 | ⚠️ Parcial | ✅ (parcial) | **Sem descrição de templates** — Spec vs código |
| DOC-2.2 | ✅ | ❌ **Violação** | `_validate_dados_extras` zero testes |
| DOC-2.3 | ✅ | ❌ **Violação** | Path traversal sem teste |
| DOC-3.1 | ✅ | ✅ | Merge template + INFO + dados_extras |
| DOC-3.3 | ✅ | ❌ **Violação** | `pipeline_emitir_documento` zero testes |
| DOC-3.4 | ✅ | ❌ **Violação** | POP audit não testado |
| DOC-5.1 | ✅ | ✅ | `criar_arquivo_dados` |
| DOC-5.2 | ⚠️ Parcial | ❌ **Violação** | Comandos `/n` vs `n` (divergência Spec); zero testes |
| DOC-5.3 | ✅ | ❌ **Violação** | CALC fields não testados |

---

## 3. Métricas do PRD

| Métrica | Status | Evidência |
|---|---|---|
| 80% menos retrabalho manual | 🔶 Não mensurável | Sem benchmark baseline ou telemetria de retrabalho |
| 100% variáveis resolvidas | ✅ Garantido tecnicamente | Pré-validação 2.4 + Placeholder zero 2.5 bloqueiam geração com erro |
| Tempo 40min → 8min | 🔶 Não mensurável | `BaseOp` grava `duracao_ms` mas não há baseline nem dashboard |
| NPS ≥ 8 | ⏳ Futuro | Pesquisa pós-implantação com setor comercial |
| Zero placeholders não resolvidos | ✅ Garantido | Dupla camada: pré-validate + pós-replace scan |
| Histórico na ficha do cliente | ✅ | JSONL versionado + MCP `historico_documentos` |
| Regeneração com versionamento | ✅ | `_resolve_version_and_archive()` preserva versão anterior |
| Nomenclatura legível | ⚠️ Parcial | `CLIENTE_SERVICO_TIPO_DATA` OK; falta prefixo `GERADO_` |

---

## 4. Recomendações

### P0 — Violações sem teste (bloqueiam done da sprint)

| # | Ação | RULE-ID | Arquivos alvo |
|---|---|---|---|
| 1 | Criar testes para `_validate_dados_extras` (max 50 keys, tipos, flat) | DOC-2.2 | `test_document_service.py` |
| 2 | Criar teste de path traversal (`../../etc/passwd`) | DOC-2.3 | `test_document_service.py` |
| 3 | Criar testes para `pipeline_emitir_documento` (pré-voo completo) | DOC-3.3 | `test_document_service.py` |
| 4 | Criar teste que verifica `OpGenerateDocument` gera entrada de auditoria | DOC-3.4 | `test_document_service.py` |
| 5 | Criar testes para `TUIFormView`, `FormSession`, campos CALC | DOC-5.2, 5.3 | `test_form_view.py` |

### P1 — Implementação incompleta vs Spec

| # | Ação | RULE-ID |
|---|---|---|
| 6 | Implementar descrição de templates **ou** atualizar Spec removendo "descricao" | DOC-1.4 |
| 7 | Decidir: Spec diz `GERADO_` prefixo vs código não aplica. Alinhar (corrigir Spec ou código) | DOC-3.2 |
| 8 | Alinhar comandos TUI: Spec `n/p/v/s/a/c` vs código `/n /p /v /s /a /c`. Atualizar Spec | DOC-5.2 |

### P2 — Cobertura parcial

| # | Ação | RULE-ID |
|---|---|---|
| 9 | Adicionar testes para NaN (`0/0`) e Infinity | DOC-4.3 |
| 10 | Adicionar teste para campo `var` no `FormulaResult` | DOC-4.4 |
| 11 | Adicionar teste para `PythonPPTXAdapter.validate_no_placeholders` | DOC-1.2 |
| 12 | Adicionar teste para campo `formulas` no relatório de validação | DOC-2.1 |

### P3 — Rastreabilidade

| # | Ação |
|---|---|
| 13 | Adicionar `# @story: STORY-XXX` e `# @rule: RULE-X.Y.Z` nos arquivos modificados |

### P4 — Métricas

| # | Ação |
|---|---|
| 14 | Adicionar timer interno em `DocumentService.generate_document()` (granularidade: data load vs formula vs replace) |
| 15 | Criar issue para dashboard de tempo de geração usando dados já capturados por `BaseOp` |

---

## 5. Conclusão

| Item | Status |
|---|---|
| 4 stories concluídas | ✅ |
| 6 RULE-IDs sem teste | ⛔ **Violação de Spec** |
| 3 RULE-IDs com implementação parcial | ⛔ |
| Anotações `@story:`/`@rule:` ausentes | ⛔ |

**A sprint NÃO pode ser considerada fully done.** Recomendo criar `STORY-026` (hardening de testes) para cobrir as 6 violações P0 sem alterar lógica de negócio, seguida de `STORY-027` para alinhamento Spec vs código (P1).

Após correções, rodar `/review 2026-SPRINT-7` novamente para validação final.
