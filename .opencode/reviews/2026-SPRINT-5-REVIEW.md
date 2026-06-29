# Relatório de Revisão — 2026-SPRINT-5

**Data:** 2026-06-28
**Specs de referência:** `SPEC-DOMAIN-CRUD-v1.1.md`, `SPEC-UX-v1.0.md` (de fato v1.1), `SPEC-SYNC-v1.0.md`
**Testes atuais:** 690 passando, 0 falhas (handoff 2026-06-28)

---

## Resumo

| Métrica | Valor |
|---------|-------|
| Stories planejadas | 7 (STORY-010 a 015, 018) |
| Stories concluídas (done) | 6 |
| Stories parciais | 1 (STORY-011) |
| Stories não-listadas na sprint mas executadas | 2 (STORY-016, STORY-017) |
| RULE-IDs na Spec | 22 |
| RULE-IDs implementados | 22 |
| RULE-IDs com teste | 22 |
| Cobertura de testes | 121+ testes novos |

---

## Adesão às Specs

### RULE-DOMAIN (SPEC-DOMAIN-CRUD-v1.1)

| Story | RULE | Status | Observação |
|-------|------|--------|------------|
| STORY-010 | **RULE-DOMAIN-1.4** — Status fallback "ATIVO" | ✅ OK | `get_clients_dataframe()` L282, `get_services_dataframe()` L312 |
| STORY-010 | **RULE-DOMAIN-1.5** — `_ensure_database_exists()` colunas Status+CodCliente | ✅ OK | L100-104 na `excel_client_repository.py` |
| STORY-010 | **RULE-DOMAIN-1.6** — `FakeClientRepository` suporta Status | ⚠️ Gap | `test_client_service.py:53-57` não filtra DELETADO nos services |
| STORY-011 | **RULE-DOMAIN-1.1** — `Client` entity com 5 métodos | ✅ OK | `client.py` completo |
| STORY-011 | **RULE-DOMAIN-1.2** — `Service` entity com 3 métodos | ✅ OK | `service.py` completo (+ bônus restore/is_active) |
| STORY-011 | **RULE-DOMAIN-1.3** — `FinanceEntry` encapsula dados | ✅ OK | `finance_entry.py` com validação em `__post_init__` |
| STORY-012 | **RULE-DOMAIN-2.1** — `remover_cliente` | ✅ OK | Soft delete + `.bak` + `confirmar=False` + POP |
| STORY-012 | **RULE-DOMAIN-2.2** — `restaurar_cliente` | ✅ OK | Lista deletados + restaura + POP |
| STORY-012 | **RULE-DOMAIN-2.3** — `remover_servico` | ✅ OK | Soft delete + `.bak` + POP |
| STORY-012 | **RULE-DOMAIN-2.4** — `atualizar_servico` | ✅ OK | 11 campos válidos + POP |
| STORY-012 | **RULE-DOMAIN-2.7** — POP em operações destrutivas | ✅ OK | `BaseOp.finally` sempre loga |
| STORY-013 | **RULE-DOMAIN-2.5** — Validação `registrar_financeiro` | ✅ OK | Tipo, cliente, duplicata, DataRegistro |
| STORY-013 | **RULE-DOMAIN-2.6** — `atualizar_ficha_cliente` multi-operação | ✅ OK | Replace, remove, field via regex, append |
| STORY-018 | **RULE-DOMAIN-2.8** — POP auditado em `atualizar_ficha_cliente` | ✅ OK | `OpUpdateClientInfo(BaseOp)` — validate→execute→log |
| STORY-014 | **RULE-DOMAIN-3.1** — `pipeline_sincronizacao()` 3 direções + `dry_run=True` | ✅ OK | `pipeline_sync.py` L81 |
| STORY-014 | **RULE-DOMAIN-3.2** — 5 passos sequenciais | ✅ OK | snapshot→diff→validate→apply→report |
| STORY-014 | **RULE-DOMAIN-3.3** — `SyncReport` com `to_dict()` e `resumo()` | ✅ OK | `pipeline_sync.py` L17-78 |
| STORY-014 | **RULE-DOMAIN-3.4** — Ferramentas legadas delegam ao pipeline | ⚠️ **Violação** | MCP tools delegam, mas `client_crud.py` L859-965 e TUI menu usam implementações paralelas independentes |
| STORY-014 | **RULE-DOMAIN-3.5** — Sync nunca remove dados, filesystem prevalece | ✅ OK | Testado e verificado |

### RULE-UX (SPEC-UX-v1.1)

| Story | RULE | Status | Observação |
|-------|------|--------|------------|
| STORY-015 | **RULE-UX-8.1** — menus.py dividido em submódulos | ✅ OK | 4 handlers + dispatch principal |
| STORY-015 | **RULE-UX-8.2** — `ProgressTracker` | ⚠️ **Não integrado** | Classe existe e testada, mas **zero consumidores** no código de produção |
| STORY-015 | **RULE-UX-8.3** — Erros com sugestões | ⚠️ **Não integrado** | `error_suggestions` existe e testado, mas **nunca chamado** no tratamento de exceções |
| STORY-016 | **RULE-UX-8.4** — Subgrupos visuais no menu | ✅ OK | `--- Cadastro ---`, `--- Perigo ---`, etc. |
| STORY-016 | **RULE-UX-8.5** — Atalho `g` busca global | ✅ OK | `parse_command()` |
| STORY-016 | **RULE-UX-8.6** — `parse_command()` interpreta atalhos | ✅ OK | |
| STORY-016 | **RULE-UX-8.7** — `listar_clientes` com paginação MCP | ✅ OK | |
| STORY-016 | **RULE-UX-8.8** — `confirm_action()` padronizado | ✅ OK | |

---

## Métricas do PRD

O PRD do **EPIC-002** define métricas de sucesso. Nenhuma delas tem logs de performance ou testes automatizados:

| Métrica | Status | Evidência |
|---------|--------|-----------|
| Redução de 50% em interações de suporte | ❌ **Sem métrica** | Nenhum log de suporte ou baseline |
| Tempo médio para localizar cliente reduzido 30% | ❌ **Sem métrica** | Nenhum performance log |
| Zero consultas "qual sincronização executar" | ✅ **Indireto** | Pipeline unificado elimina escolha, mas sem medição |
| 100% clientes/serviços com código válido | ✅ **Parcial** | `fill_missing_codes()` + `ClientCode` VO, mas sem validação em lote |
| Tempo de sincronização completo reduzido 40% | ❌ **Sem métrica** | `SyncReport` tem duração, mas sem baseline/log histórico |

---

## Vaporware, Mocks e Incompletudes

### 🔴 ALTO — Vaporware confirmado

**`MCPDocumentService.generate()` — stub que retorna sucesso falso**
`foton_system/interfaces/mcp/mcp_services.py:444-456`

```python
def generate(self, ...) -> DocumentResult:
    return DocumentResult(success=True, message="Documento gerado",
                          output_path=f"/output/{client_name}/{template_name}")
```

O método ignora `path_resolver`, não executa merge, e retorna caminho fabricado. A rota principal via `OpGenerateDocument` em `foton_mcp.py` é funcional, mas este stub na camada de serviço intermediária é um falso positivo.

### 🟡 MÉDIO — Incompletudes de integração

| Item | Detalhe |
|------|---------|
| **Domain entities ~60% integradas** | `get_deleted_clients()`, `soft_delete_client()`, `restore_client()` em `client_crud.py` ainda manipulam DataFrames crus |
| **delete/restore não usa entidades** | `client_crud.py:460-529` opera `pd.DataFrame` diretamente |
| **Sincronização paralela** | TUI menu (opções 5/6) usa `client_crud.sync_*` em vez do pipeline |
| **ProgressTracker sem consumidor** | Nenhuma operação batch usa feedback de progresso |
| **error_suggestions sem integração** | Erros exibem `print_error` genérico |

### 🟢 BAIXO — TODOs e código morto

| Item | Local |
|------|-------|
| `TODO` em `op_doc_gen.py:83` | Refatorar Service para aceitar Dict |
| `TODO` em `op_index_knowledge.py:42` | Header-aware splitting no Markdown |
| `import os` não usado | `document_service.py:1` |
| `ClientServiceProtocol` não usado | `mcp_services.py:58-84` |
| `SyncServiceProtocol` não usado | `mcp_services.py:87-89` |
| `except Exception: pass` | `audit_logger.py:64-65` — engole erros |
| `FakeClientRepository` não filtra DELETADO | `test_client_service.py:57` |

---

## Recomendações (priorizadas)

### P0 — Correção obrigatória antes de encerrar a sprint

1. **Corrigir `MCPDocumentService.generate()`** stub em `mcp_services.py:444` — ou delega para `OpGenerateDocument` ou levanta `NotImplementedError`
2. **Atualizar `2026-SPRINT-5.md`** — incluir STORY-016 e STORY-017 (já concluídas na sprint)
3. **Corrigir `FakeClientRepository.get_services_dataframe()`** em `test_client_service.py:57` — aplicar filtro `Status != 'DELETADO'`

### P1 — Débito técnico que afeta confiabilidade

4. **Refatorar `client_crud.py:460-529`** (delete/restore) para usar `Client.soft_delete()`/`Service.soft_delete()` em vez de manipular DataFrames
5. **Redirecionar TUI menu opções 5/6** para o pipeline unificado (`pipeline_sincronizacao`) em vez de `client_crud.sync_*`
6. **Remover `except Exception: pass`** em `audit_logger.py:64-65` — no mínimo logar o erro

### P2 — Melhorias de UX que não foram conectadas

7. **Integrar `ProgressTracker`** nas operações batch da TUI (sync, listagens longas)
8. **Integrar `error_suggestions`** no `try/except` dos handlers TUI

### P3 — Housekeeping

9. **Remover imports não utilizados** (`os` em `document_service.py`, `Any`/Protocols em `mcp_services.py`)
10. **Criar baseline de performance** para as métricas do EPIC-002 (tempo de sincronização, tempo de navegação) — essencial antes de medir melhoria
11. **Atualizar versão da SPEC-UX** referenciada em STORY-015 de `v1.0` para `v1.1`

---

## Conclusão

A Sprint 5 entregou **22 de 22 RULE-IDs** com implementação funcional, 121+ testes novos e zero regressão. No entanto:

- **3 violações de spec** identificadas (RULE-DOMAIN-3.4 parcial, RULE-UX-8.2 e 8.3 sem integração)
- **1 vaporware** ativo (`MCPDocumentService.generate()`)
- **Débito técnico de integração**: entidades de domínio (~60% integradas), pipeline de sync (~80% integrado na TUI)
- **Sprint file desatualizado** em relação ao que foi realmente executado

A sprint merece **status `done` condicional** — sujeito à correção dos **P0** e **P1** acima. Os gaps de integração de UI helpers (P2) podem ficar para a próxima sprint.
