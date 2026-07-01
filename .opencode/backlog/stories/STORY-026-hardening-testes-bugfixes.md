---
status: "ready"
sprint: "2026-SPRINT-7"
---

# STORY-026: Hardening de Testes, Bugfixes e Rastreabilidade

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Descrição

Corrigir bugs reais identificados na revisão `2026-SPRINT-7-REVIEW.md`, eliminar violações de Spec (RULE-IDs sem teste), adicionar testes faltantes, implementar anotações de rastreabilidade `@story:`/`@rule:`, e fortalecer segurança (path traversal) e resiliência (concorrência, NaN/Infinity). Nenhuma alteração de lógica de negócio — apenas hardening.

## Regras

- **RULE-DOC-1.2:** `.docx` e `.pptx` suportados (testar PPTX adapter)
- **RULE-DOC-1.4:** `listar_templates` com nome (descrição será tratada na STORY-027)
- **RULE-DOC-2.1:** Relatório colorido com campo `formulas` testado
- **RULE-DOC-2.2:** `dados_extras` validado com testes (max 50 keys, tipos planos)
- **RULE-DOC-2.3:** Path traversal sanitizado em todas as entradas e testado
- **RULE-DOC-3.2:** Alinhar `GERADO_` prefixo entre Spec, código e docstring
- **RULE-DOC-3.3:** `pipeline_emitir_documento` testado e com glob de duplicatas corrigido
- **RULE-DOC-3.4:** POP audit testado, com `client_id` e `threading.Lock`
- **RULE-DOC-4.3:** NaN/Infinity validado em operandos constantes e testado
- **RULE-DOC-4.4:** Relatório de fórmulas com campo `var` testado
- **RULE-DOC-5.2:** TUI commands alinhados Spec ↔ código; testes para `TUIFormView`
- **RULE-DOC-5.3:** Campos CALC não editáveis testados

## Critérios de Aceite

### Tema A — Bugfixes de Segurança (Path Traversal)
- [ ] A1: `_resolve_client_path()` em `op_doc_gen.py` usa `Path(client_name).name`
- [ ] A2: `listar_documentos_cliente` sanitiza parâmetro `servico` com `Path().name`
- [ ] A3: Helper `sanitize_path_component()` centralizado e usado em todos os pontos de entrada (cliente, serviço, template)
- [ ] Testes: path traversal com `../../etc/passwd` em cliente, serviço e template bloqueado

### Tema B — Bugfixes de Funcionalidade
- [ ] B1: Todos MCP tools com `dados_extras: dict = {}` alterados para `dados_extras: Optional[dict] = None` com `dados_extras = dados_extras or {}`
- [ ] B2: `pipeline_emitir_documento` usa glob que corresponde ao formato real do filename (não busca `GERADO_*`)
- [ ] B3: Decisão tomada e implementada: OU `build_standard_filename()` retorna com prefixo `GERADO_`, OU Spec é atualizada para remover o requisito. Docstrings atualizadas.
- [ ] B4: `OpGenerateDocument.execute()` recebe e propaga `client_id` para auditoria
- [ ] B5: `FormSession._evaluate()` propaga erro como aviso (não silencia com 0.0)
- [ ] B6: `_SafeVisitor.visit_Constant()` valida `math.isnan()` e `math.isinf()`

### Tema C — Concorrência e Resiliência
- [ ] C1: `AuditLogger.log_event()` usa `threading.Lock` para escrita segura
- [ ] C2: Payload de auditoria para `gerar_documento` trunca `extra_data` (nº de chaves em vez de valores)

### Tema D — Testes Obrigatórios (P0)
- [ ] D1: `test_validate_dados_extras` cobre: dict inválido >50 keys, valores aninhados, chave vazia, chave não-string
- [ ] D2: `test_path_traversal` cobre: cliente, serviço e template com `../../etc/passwd`
- [ ] D3: `test_pipeline_emitir_documento` cobre: pré-voo OK, variável faltante, duplicata detectada
- [ ] D4: `test_pop_audit` cobre: `OpGenerateDocument` gera entrada com timestamp, op_name, actor, client_id, status
- [ ] D5: `test_tui_form_view` cobre: navegação n/p/v/s/a/c, campos CALC não editáveis

### Tema E — Cobertura Adicional (P2)
- [ ] E1: Testes para NaN (`float('nan')` como constante), Infinity (`float('inf')`), divisão 0/0
- [ ] E2: Teste para `FormulaResult.var` corresponder à chave de replacement
- [ ] E3: Teste para `PythonPPTXAdapter.validate_no_placeholders` (passa e falha)
- [ ] E4: Teste para campo `formulas` no relatório `_validate_keys`

### Tema F — Rastreabilidade
- [ ] F1: `# @story: STORY-022` a `STORY-026` e `# @rule: RULE-DOC-X.Y` adicionados em todos os arquivos de código afetados:
  - `document_service.py`, `op_doc_gen.py`, `base_op.py`, `audit_logger.py`
  - `foton_mcp.py`, `mcp_services.py`
  - `python_docx_adapter.py`, `python_pptx_adapter.py`
  - `formula_engine.py`, `safe_math.py`
  - `form_session.py`, `form_view.py`
- [ ] Commits referenciam `[STORY-026]` e `[RULE-DOC-X.Y]`

## Arquivos Afetados

### Código Fonte
- `foton_system/core/ops/op_doc_gen.py` — sanitização, client_id no audit, GERADO_ prefix
- `foton_system/core/ops/base_op.py` — truncamento de payload
- `foton_system/core/ops/audit_logger.py` — threading.Lock
- `foton_system/core/ops/formula_engine.py` — anotações
- `foton_system/modules/documents/application/use_cases/document_service.py` — build_standard_filename, GERADO_ prefix
- `foton_system/modules/documents/infrastructure/adapters/python_docx_adapter.py` — anotações
- `foton_system/modules/documents/infrastructure/adapters/python_pptx_adapter.py` — anotações
- `foton_system/modules/documents/domain/models/form_session.py` — erro de fórmula não silenciado
- `foton_system/modules/shared/domain/services/safe_math.py` — NaN/Infinity em constantes
- `foton_system/interfaces/mcp/foton_mcp.py` — mutable default, path traversal, glob duplicatas, anotações
- `foton_system/interfaces/mcp/mcp_services.py` — sanitização centralizada
- `foton_system/interfaces/cli/views/form_view.py` — comandos alinhados com Spec

### Testes
- `tests/unit/test_document_service.py` — novos testes P0 + P2
- `tests/unit/test_safe_math.py` — NaN/Infinity em constantes
- `tests/unit/test_form_view.py` (novo) — TUIFormView

## Riscos

- **Mudança de comportamento:** `GERADO_` prefixo e glob de duplicatas afetam a experiência do usuário. Comunicar mudança.
- **Mutável default:** `dados_extras: dict = {}` é code smell raro de manifestar, mas a correção é segura (muda para `None`).
- **Lock no audit:** Pode introduzir contenção se muitas ops concorrentes. Lock de curta duração (só I/O de append).

## Definição de Pronto (DoD)

- [ ] 9 bugs corrigidos (A1-A3, B1-B6)
- [ ] 2 melhorias de concorrência/resiliência (C1-C2)
- [ ] 5 suites de teste novas (D1-D5)
- [ ] 4 conjuntos de testes de cobertura adicional (E1-E4)
- [ ] Anotações `@story:` e `@rule:` em todos os arquivos fonte afetados (F1)
- [ ] `python -m pytest` — zero regressão
- [ ] Commits com `[STORY-026]`

## Dependências

- **STORY-022** a **STORY-025** (concluídas) — hardening sobre código existente
- **STORY-027** (paralelizável) — template descriptions são independentes

## Estimativa

22h
