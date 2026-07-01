---
status: "ready"
sprint: "2026-SPRINT-7"
---

# STORY-025: Geração em Lote + Nomenclatura Padronizada

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Descrição

Implementar geração em lote de documentos (proposta + contrato + anexo em um comando). Padronizar nomenclatura dos arquivos gerados para `CLIENTE_SERVICO_TIPO_DATA.ext` com fallback para o formato legado.

## Regras

- **RULE-DOC-3.2 (upgrade):** Documento gerado segue padrão `CLIENTE_SERVICO_TIPO_DATA.ext`. Fallback para nome atual se campos não disponíveis.
- **RULE-DOC-3.5 (nova):** `gerar_documentos_lote` aceita lista de pares (template, dados_extras). Pré-voo executado para cada item antes de gerar qualquer um. Se 1 falhar → lote todo bloqueado.

## Critérios de Aceite

- [ ] Nomenclatura `CLIENTE_SERVICO_TIPO_DATA.ext` implementada em `DocumentService.generate_document()`
- [ ] Fallback mantém nome atual quando campos não disponíveis (mudança não quebradora)
- [ ] MCP tool `gerar_documentos_lote(cliente, documentos: list[dict])` — cada dict com `{template, dados_extras, tipo}`
- [ ] Pipeline: Fase 1 — valida todos (pré-voo), Fase 2 — gera todos (só se todos OK)
- [ ] Relatório consolidado: lista cada documento com status (OK/ERROR)
- [ ] TUI: opção "Gerar Lote (Proposta + Contrato + Anexo)" no menu Documentos
- [ ] Testes: lote todo válido, lote bloqueado se 1 falha, relatório de lote, nomenclatura padronizada, fallback legado

## Arquivos Afetados

- `foton_system/modules/documents/application/use_cases/document_service.py` — nomenclatura, batch generation
- `foton_system/core/ops/op_doc_gen.py` — suporte a lote
- `foton_system/interfaces/mcp/foton_mcp.py` — nova tool `gerar_documentos_lote`
- `foton_system/interfaces/tui/menus/menus_docs.py` — opção "Gerar Lote"

## Estimativa

6h

## Dependências

- **STORY-022** (forte — precisa da pré-validação obrigatória para o pipeline de lote funcionar corretamente)
