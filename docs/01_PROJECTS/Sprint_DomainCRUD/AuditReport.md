---
type: audit
domain: core
version: 1.5.0
sprint: Sprint_DomainCRUD
status: aprovado-com-ressalvas
data: 2026-06-23
tags: [auditoria, domain-model, crud, sync, ui, roadmap]
---

# Auditoria do Plano de Implementação v1.5.0

> Relatório técnico de viabilidade, aderência ao repositório e riscos identificados.

## 1. Contexto

| Item | Valor |
|------|-------|
| Versão atual | 1.4.0 (conforme `version.txt`) |
| Versão alvo | 1.5.0 |
| Testes existentes | 410 (verificado via `pytest --co -q`) |
| Testes projetados | ~61 novos → ~471 total |
| Novos arquivos | ~11 |
| Novas MCP tools | 5 |
| Fases | 3 (Domain Model → CRUD → Pipeline Sync) |

## 2. Análise de Aderência ao Repositório

### 2.1 Arquitetura Existente ✅

O plano **é coerente** com a arquitetura Ports & Adapters (Hexagonal) já implantada:

```
modules/clients/
├── application/
│   ├── ports/              ← Interfaces (ClientRepositoryPort)
│   └── use_cases/          ← Lógica de domínio (client_crud, client_service, etc.)
└── infrastructure/
    └── repositories/       ← Implementações (ExcelClientRepository)
```

**Observações:**
- O plano propõe `clients/domain/` como **novo diretório**. Isso é compatível — a camada `domain` ficaria ao lado de `application/` e `infrastructure/`, seguindo DDD.
- Value Objects já existem no projeto: `InfoPatternResolver` em `shared/domain/` é um precedente sólido para os novos `ClientCode`, `ServiceCode`, `TaxId`.

### 2.2 Port Interface (ClientRepositoryPort) ⚠️

**Arquivo atual:** `client_repository_port.py` — 7 métodos abstratos:
- `get_clients_dataframe()`, `get_services_dataframe()`
- `save_clients()`, `save_services()`
- `list_client_folders()`, `list_service_folders()`, `create_folder()`

**O plano propõe 3 novos métodos:**
- `soft_delete_client()`, `soft_delete_service()`, `restore_client()`

**Risco:** Adicionar métodos na port **quebra o FakeClientRepository** usado nos testes (`conftest.py`). É necessário atualizar **tanto a port quanto o fake** simultaneamente.

> [!WARNING]
> O `FakeClientRepository` em `tests/conftest.py` precisa ser atualizado junto com a port, senão **todos os testes existentes falham por ABC violation**.

**Recomendação:** Implementar soft delete **sem alterar a port** inicialmente. Os métodos `soft_delete_client()` e `restore_client()` podem ser implementados como operações compostas sobre `get_clients_dataframe()` + `save_clients()` (lê → modifica → salva). Isso mantém backward compatibility e não exige alteração do FakeClientRepository. A port pode ser estendida em uma segunda iteração se necessário.

### 2.3 Schema do Excel (DataFrame) ⚠️

**Colunas atuais de `baseClientes`:**
```
ID, NomeCliente, Alias, TelefoneCliente, Email, CPF_CNPJ, Endereco,
CidadeProposta, EstadoCivil, Profissao
```

**O plano requer:** Nova coluna `Status` com default `"ATIVO"`.

**Riscos identificados:**

1. **Migração retroativa**: DataFrames existentes **não têm** coluna `Status`. A leitura precisa de fallback.
2. **CodCliente**: A coluna já existe no DB real (usada por `fill_missing_codes()`), mas **não está** no schema de criação de `_ensure_database_exists()`. O plano não menciona essa inconsistência.
3. **CPF_CNPJ vs NIF**: O plano usa `nif` na entidade Client, mas o Excel usa `CPF_CNPJ`. O mapeamento `to_row()`/`from_row()` precisa ser explícito.

> [!IMPORTANT]
> A migração da coluna `Status` precisa ser **transparente**: se a coluna não existir, assumir `"ATIVO"` para todos os registros existentes. Mesma abordagem usada na v1.4.0 para `CodCliente`.

### 2.4 Padrões de Código ✅

O plano respeita os padrões encontrados no código:

| Padrão | Status | Evidência |
|--------|--------|-----------|
| Docstrings PT-BR | ✅ | Todo código usa PT-BR |
| Logger via `setup_logger()` | ✅ | Padrão em todos os módulos |
| Exceções em `shared/domain/exceptions.py` | ✅ | Hierarquia `FotonError` |
| POP Auditado | ✅ | Para operações críticas |
| Path sanitization | ✅ | `validate_filename()` |
| Tipo hints | ✅ | Parcial mas consistente |
| Testes com `FakeClientRepository` | ✅ | Fixture centralizada |

### 2.5 MCP Interface ⚠️

**Arquivo:** `foton_mcp.py` (59 KB, já grande).

O plano adiciona **6 novas tools**. O arquivo já tem 38 tools.

**Recomendação:** Antes de adicionar tools, considerar se `foton_mcp.py` deveria ser refatorado em submódulos (`mcp_clients.py`, `mcp_finance.py`, etc.). Mas essa refatoração **não é pré-requisito** — pode ser tratada como melhoria futura.

### 2.6 Finance Module ⚠️

O plano propõe validações em `registrar_financeiro`:
- Tipo contra `["ENTRADA", "SAIDA"]`
- Verificar se cliente existe
- Verificar duplicatas
- Coluna `DataRegistro`

**Observação:** O módulo finance (`modules/finance/`) possui sua própria estrutura com `application/` e `infrastructure/`. As validações propostas são sensatas, mas é necessário examinar o schema CSV atual do financeiro para confirmar compatibilidade.

### 2.7 TUI (CLI) ⚠️

**Arquivo:** `menus.py` (54 KB) — menu monolítico.

O plano original propunha reestruturação do menu e split do `menus.py`. Conforme decisão de alinhamento EPIC-001/EPIC-002, estes itens foram migrados para EPIC-001 (SPEC-UX-v1.0, RULE-UX-8.1 a 8.8). O escopo do EPIC-002 foca exclusivamente em domínio, CRUD e sincronização.

### 2.8 Validação de Value Objects ✅

Os patterns de validação propostos são coerentes:

| Value Object | Regex | Observação |
|---|---|---|
| `ClientCode` | `^[A-Z]{3}\d{2}$` | Consistente com `generate_client_code()` existente |
| `ServiceCode` | `^[A-Z]{6}\d{2}$` | Consistente com `generate_service_code()` existente |
| `TaxId` | 8-14 dígitos | Amplo o suficiente para NIF/CPF/CNPJ |

## 3. Riscos Identificados

| # | Risco | Severidade | Mitigação |
|---|-------|------------|-----------|
| R1 | Quebra do FakeClientRepository ao alterar port | 🔴 Alto | Não alterar port; usar operações compostas |
| R2 | Migração da coluna `Status` em bases existentes | 🟡 Médio | Fallback transparente no `get_clients_dataframe()` |
| R3 | `menus.py` já tem 54KB — adicionar mais funcionalidades degrada manutenibilidade | 🟡 Médio | Migrado para EPIC-001 (SPEC-UX-v1.0, RULE-UX-8.x) — escopo fora deste épico |
| R4 | `foton_mcp.py` com 59KB + 6 novas tools | 🟡 Médio | Registrar tools mas delegar lógica para services |
| R5 | Inconsistência `CPF_CNPJ` (Excel) vs `nif` (entidade) | 🟡 Médio | Mapeamento explícito em `to_row()`/`from_row()` |
| R6 | Pipeline sync bidirecional — conflitos não resolvidos podem corromper dados | 🔴 Alto | Modo dry-run obrigatório antes de apply; conflict resolution explícita |
| R7 | `CodCliente` não está no schema `_ensure_database_exists()` | 🟡 Médio | Adicionar coluna no schema de criação |

## 4. Gaps no Plano

### 4.1 Gaps Funcionais

1. **Sem menção a auditoria POP** para as novas operações de delete/restore — devem ser POP-auditadas.
2. **Sem menção a backup `.bak`** antes de soft delete — padrão existente no projeto.
3. **`update_service_info`** (Fase 2.4) precisa definir quais campos são editáveis e quais são readonly.
4. **Paginação MCP** (Fase 5.3) — alterar assinatura de `listar_clientes` pode quebrar clientes MCP existentes. Usar parâmetros opcionais.

### 4.2 Gaps Técnicos

1. **Sem plano de migração de dados** — bases Excel existentes precisam receber coluna `Status`.
2. **Sem critérios de aceitação** por fase (DoD — Definition of Done).
3. **Sem estimativa de esforço** por fase.
4. **Sem plano de rollback** caso uma fase introduza regressão.

## 5. Recomendações de Ajuste

1. **Fase 1 — Não alterar `ClientRepositoryPort`** inicialmente. Soft delete via operações compostas.
2. **Fase 2 — Adicionar migração transparente** da coluna `Status` no `get_clients_dataframe()`.
3. **Fase 3 — Pipeline sync** deve ter modo `dry_run=True` como default.
4. **Fase 4 (UI/UX) — Migrada para EPIC-001.** O split do `menus.py` e as melhorias de TUI passam a ser responsabilidade do EPIC-001 (SPEC-UX-v1.0, RULE-UX-8.1 a 8.8).
5. **Todas as fases — POP Auditado** para operações destrutivas (delete, restore, sync apply).
6. **Testes — Atualizar `conftest.py`** com suporte a coluna `Status` no `FakeClientRepository`.

## 6. Parecer Final

| Aspecto | Parecer |
|---------|---------|
| Viabilidade técnica | ✅ **Viável** — arquitetura atual suporta as extensões |
| Coerência arquitetural | ✅ **Coerente** — segue DDD, Hexagonal, Port & Adapters existente |
| Riscos | ⚠️ **Gerenciáveis** — mitigações identificadas para cada risco |
| Esforço | ⚠️ **Adequado** — 20-26h sem UI/UX (migrado para EPIC-001) |
| Recomendação | ✅ **Aprovado com ressalvas** — seguir com ajustes nas Fases 1 e 4 |

---

*Auditoria conduzida em 2026-06-23 por análise automatizada do código-fonte.*
*Base: 410 testes passando, versão 1.4.0.*
