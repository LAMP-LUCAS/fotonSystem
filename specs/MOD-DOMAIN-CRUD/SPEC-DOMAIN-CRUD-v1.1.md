# Spec: Domain Model, CRUD & UX Evolution

**Data:** 2026-06-25
**Versão:** 1.1
**Responsável:** Time Core
**Épico:** EPIC-002

## 1. Problema

O FotonSystem atingiu v1.4 com 38 ferramentas MCP e 410+ testes, mas acumulou dívidas estruturais:

1. **Dados sem entidade de domínio** — Operações manipulam DataFrames crus. Não há garantia de que códigos, NIFs e status sigam formatos válidos.
2. **CRUD incompleto** — Create e Read existem, mas Delete é inexistente e Update é limitado. Clientes cancelados ou duplicados permanecem nas listagens para sempre.
3. **Sincronização fragmentada** — Sete ferramentas de sync com nomes confusos. O usuário não sabe qual executar.

## 2. Solução Proposta

### Camada de Domínio (nova)

Entidades `Client`, `Service`, `FinanceEntry` com regras de negócio encapsuladas — `soft_delete()`, `restore()`, `to_row()`, `from_row()` — e Value Objects (`ClientCode`, `ServiceCode`, `TaxId`) com validação nativa. Migração transparente da coluna `Status` com fallback `"ATIVO"`.

### CRUD Completo (extensão)

Soft delete e restore de clientes e serviços com backup `.bak` e POP auditado. Validação de entrada no financeiro. Melhoria do update de INFO files (substituição de seção, remoção, campo específico).

### Pipeline de Sincronização Unificado (consolidação)

Pipeline único com 3 direções (`pastas_to_db`, `db_to_pastas`, `bidir`), dry-run como default, `SyncReport` estruturado. Ferramentas legadas mantidas como aliases de backward compatibility.

> **UI/UX items transferred to EPIC-001 (SPEC-UX-v1.0).** This spec covers only domain, CRUD, and sync.

## 3. Regras de Negócio

### 3.1 Domain Model Foundation

- **RULE-DOMAIN-1.1:** `Client` entity deve implementar `to_row()` (→ dict compatível com DataFrame), `from_row()` (classmethod), `soft_delete()` (status → `"DELETADO"`), `restore()` (status → `"ATIVO"`), `is_active()` (status == `"ATIVO"`).
- **RULE-DOMAIN-1.2:** `Service` entity deve implementar `to_row()`, `from_row()`, `soft_delete()`.
- **RULE-DOMAIN-1.3:** `FinanceEntry` entity deve encapsular tipo (ENTRADA/SAIDA), valor, descrição, data, cliente vinculado.
- **RULE-DOMAIN-1.4:** Coluna `Status` no Excel deve ter fallback `"ATIVO"` se ausente (`get_clients_dataframe()` e `get_services_dataframe()`).
- **RULE-DOMAIN-1.5:** `_ensure_database_exists()` deve criar colunas `Status` e `CodCliente` na inicialização.
- **RULE-DOMAIN-1.6:** `FakeClientRepository` deve ser atualizado para suportar coluna `Status`.

### 3.2 CRUD Completo

- **RULE-DOMAIN-2.1:** `remover_cliente` — MCP tool com soft delete, backup `.bak` antes da operação, POP auditado, parâmetro `confirmar=False` para segurança adicional.
- **RULE-DOMAIN-2.2:** `restaurar_cliente` — MCP tool que lista clientes deletados e permite restaurar. POP auditado.
- **RULE-DOMAIN-2.3:** `remover_servico` — MCP tool com soft delete de serviço, backup `.bak`, POP auditado.
- **RULE-DOMAIN-2.4:** `atualizar_servico` — MCP tool para update de campo específico em serviço. POP auditado.
- **RULE-DOMAIN-2.5:** Validação de `registrar_financeiro`: tipo deve ser `"ENTRADA"` ou `"SAIDA"` (case-insensitive), cliente deve existir no DB, duplicatas (mesma descrição + valor + data) geram warning não bloqueante. `DataRegistro` é adicionada automaticamente.
- **RULE-DOMAIN-2.6:** `atualizar_ficha_cliente` deve suportar substituição de seção inteira, remoção de seção e atualização de campo via regex `@campo: valor`.
- **RULE-DOMAIN-2.7:** Toda operação destrutiva (delete, restore, overwrite) deve gerar evento de auditoria POP.
- **RULE-DOMAIN-2.8:** `atualizar_ficha_cliente` (append, replace, remove, field) deve passar por POP auditado via `OpUpdateClientInfo(BaseOp)` — validação → execução → `AuditLogger.log_event()` obrigatório em todas as operações, inclusive falha.

### 3.3 Pipeline de Sincronização

- **RULE-DOMAIN-3.1:** `pipeline_sincronizacao()` deve suportar 3 direções: `pastas_to_db`, `db_to_pastas`, `bidir`. Parâmetro `dry_run=True` como default (segurança).
- **RULE-DOMAIN-3.2:** Pipeline deve executar 5 passos sequenciais: `snapshot()`, `diff()`, `validate()`, `apply()`, `report()`.
- **RULE-DOMAIN-3.3:** `SyncReport` deve conter: direção, dry_run, listas de clientes/serviços novos/atualizados/deletados, conflitos, erros, duração, timestamp. Métodos `to_dict()` (serialização MCP) e `resumo()` (texto para TUI).
- **RULE-DOMAIN-3.4:** Ferramentas de sync existentes (`sincronizar_clientes`, `sincronizar_pastas_clientes`, `sincronizar_base`, etc.) são mantidas como aliases de backward compatibility, delegando internamente para o pipeline.
- **RULE-DOMAIN-3.5:** Sincronização nunca remove dados — apenas adiciona ou atualiza. Em caso de conflito, o filesystem (INFO-*.md) prevalece como Centro de Verdade.

### 3.4 (Reservado — UI/UX movido para EPIC-001 / SPEC-UX-v1.0)

## 4. Critérios de Aceite Técnicos

- [ ] RULE-DOMAIN-1.1 a 1.6: Value Objects e entidades criados, testes passando, zero regressão nos 410+ testes existentes
- [ ] RULE-DOMAIN-2.1 a 2.8: 4 novas MCP tools registradas, backup `.bak` antes de delete, POP auditado em todas as operações destrutivas e de INFO file
- [ ] RULE-DOMAIN-3.1 a 3.5: Pipeline unificado com dry-run, SyncReport JSON, aliases legados funcionando
- [ ] UI/UX complete — see EPIC-001 / SPEC-UX-v1.0 (RULE-UX-8.1 to 8.8)
- [ ] CHANGELOG.md atualizado com todas as mudanças
- [ ] AGENTS.md atualizado com as novas MCP tools
- [ ] version.txt → `1.5.0`

## 5. Restrições e Limitações

- **Port do repositório não será alterada** nesta versão para evitar quebra do `FakeClientRepository` e dos 410+ testes existentes.
- **Soft delete não remove pastas ou arquivos** do filesystem — apenas marca `Status = "DELETADO"` no Excel.
- **Menus legados mantidos** durante transição — a divisão de `menus.py` é feita em etapas para evitar quebra (ver EPIC-001 / SPEC-UX-v1.0).
- **Backward compatibility obrigatória** — parâmetros opcionais em MCP tools existentes não podem quebrar chamadas sem os novos parâmetros.
- **ChromaDB isolado** — RAG não é indexado automaticamente após operações de delete/restore (decisão consciente para evitar lentidão).

## 6. Relações

- Specs base: `SPEC-CLIENTES-v1.0` (Value Objects, CRUD base), `SPEC-SYNC-v1.0` (direções de sync)
- UI/UX: See `SPEC-UX-v1.0` (EPIC-001) — breadcrumbs, paginação, confirmações, menus, busca global
- Código: `modules/clients/domain/`, `modules/sync/application/pipeline_sync.py`, `interfaces/cli/helpers/`
- MCP tools novas: `remover_cliente`, `restaurar_cliente`, `remover_servico`, `atualizar_servico`, `pipeline_sincronizacao`
- ADRs relacionados: `ADR001_ParaZettelkastenDoc` (estrutura de docs), `ADR002_PascalCaseNaming` (nomes de serviço), `ADR003_SandboxTestIsolation` (testes)
