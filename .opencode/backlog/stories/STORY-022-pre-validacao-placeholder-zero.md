---
status: "done"
sprint: "2026-SPRINT-7"
---

# STORY-022: Pré-validação Obrigatória + Placeholder Zero

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Descrição

Implementar camada de confiança na engine de documentos: `gerar_documento` deve executar `validar_template` internamente e **bloquear** a geração se houver variáveis não resolvidas ou placeholders inválidos. Upgrade do relatório `validar_template` para formato colorido com categorias.

## Regras

- **RULE-DOC-2.1 (upgrade):** `validar_template` gera relatório completo com variáveis resolvidas (verde), não encontradas (vermelho), fórmulas validadas, e alerta se valor for `None` ou `"---"`.
- **RULE-DOC-2.4 (nova):** `gerar_documento` executa `validar_template` internamente. Se houver variáveis não resolvidas ou fórmulas com erro, a geração é **bloqueada** e o relatório de erros é exibido.
- **RULE-DOC-2.5 (nova):** Nenhum `@VAR` pode chegar ao documento final como `"None"`, `"---"` ou string vazia. Toda variável não resolvida gera erro explícito antes da geração.

## Critérios de Aceite

- [ ] `generate_document()` no `DocumentService` chama `_validate_keys` antes de gerar e bloqueia se houver faltantes
- [ ] Após merge, pós-processamento verifica se `@VAR` sobreviveu como `"None"`/`"---"`/vazio — erro antes de salvar
- [ ] `validar_template` retorna relatório categorizado (resolvidas OK ✅ / não encontradas ❌ / fórmulas ⚠️)
- [ ] `op_doc_gen.py` integra a pré-validação no `execute_logic()`
- [ ] Testes: pré-validação bloqueia geração com vars faltando; placeholder zero bloqueia com None no documento; relatório colorido com formato correto

## Arquivos Afetados

- `foton_system/modules/documents/application/use_cases/document_service.py` — `generate_document()`, `_validate_keys()`
- `foton_system/modules/documents/infrastructure/adapters/python_docx_adapter.py` — pós-processamento placeholder
- `foton_system/modules/documents/infrastructure/adapters/python_pptx_adapter.py` — pós-processamento placeholder
- `foton_system/core/ops/op_doc_gen.py` — integrar pré-validação
- `foton_system/interfaces/mcp/foton_mcp.py` — `validar_template` relatório colorido

## Estimativa

6h

## Dependências

Nenhuma
