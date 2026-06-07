---
type: sprint
domain: core
status: active
tags: [clients, structure, tdd, refactor]
---

# SPRINT: Reestruturação da Pasta de Clientes

## Objetivo

Implementar a convenção de pastas descrita no PRD, tornando a árvore `CLIENTES/` resiliente, robusta, coesa, coerente e segura — com suporte a sub-serviços horizontais (`__`), pastas funcionais configuráveis (`{DOC}`, `{ADM}`, `{OP}`), e busca regressa de contexto.

## Fases

### Fase 0: Documentação e Baseline
- [x] PRD criado
- [x] Sprint Plan criado
- [ ] Rodar suite completa para confirmar baseline (203 testes)

### Fase 1: ConfigProvider — folder_conventions (TDD)

**Vermelho:** Criar testes para:
- `Config.folder_doc` retorna `'00_DOC'` (default)
- `Config.folder_adm` retorna `'01_ADM'` (default)
- `Config.folder_op` retorna `'02_OPERACAO'` (default)
- `Config.folder_op_phases` retorna lista default
- `Config.ignored_folders` inclui as pastas funcionais

**Verde:** Adicionar properties em `Config` e schema opcional.

### Fase 2: ClientService — normalização + detecção (TDD)

**Vermelho:** Criar testes para:
- `normalize_client_name`:
  - Remove acentos: `"João"` → `"JOAO"`
  - Substitui espaços por `_`: `"João Silva"` → `"JOAO_SILVA"`
  - Remove hífens: `"ANTONIO-FERREIRA"` → `"ANTONIO_FERREIRA"`
  - Não permite `__` duplo
  - `None` ou vazio retorna string vazia
- `list_service_nodes`:
  - Lista apenas pastas que não começam com `_`
  - Lista apenas pastas que não são funcionais ({DOC}, {ADM}, {OP})
  - Decodifica `__` corretamente (raiz vs sub-serviço vs sub-sub)
  - Retorna `depth` e `parent` corretos
  - Cliente sem serviços retorna lista vazia

**Verde:** Adicionar métodos em `ClientService`.

### Fase 3: DocumentService — contexto regressivo (TDD)

**Vermelho:** Criar testes para:
- `_load_context_data` encontra `INFO-CLIENTE.md` na raiz
- `_load_context_data` encontra `INFO-CLIENTE.md` em subpasta `{DOC}/`
- `_load_context_data` carrega `INFO-SERVICO.md` do serviço correto
- `_load_context_data` mergeia dados (serviço sobrescreve cliente)
- `_load_context_data` com dados aninhados (cliente → serviço → sub-serviço)

**Verde:** Refatorar `_load_context_data` no `DocumentService`.

### Fase 4: CSVFinanceRepository — ledger com fallback (TDD)

**Vermelho:** Criar testes para:
- `_get_ledger_path` retorna `{ADM}/FINANCEIRO.csv` quando existe
- `_get_ledger_path` retorna `FINANCEIRO.csv` (raiz) quando `{ADM}` não existe
- `_get_ledger_path` cria em `{ADM}/FINANCEIRO.csv` quando nenhum existe

**Verde:** Adicionar fallback em `CSVFinanceRepository`.

### Fase 5: MCP — normalização e novas tools (TDD)

**Vermelho:** Criar testes para:
- `cadastrar_cliente` normaliza nome
- `pipeline_novo_cliente` normaliza nome
- `listar_servicos_cliente` retorna hierarquia `__`
- Nova tool `criar_estrutura_servico` cria pastas {DOC}+{ADM}+{OP}+fases

**Verde:** Atualizar `foton_mcp.py` e `mcp_services.py`.

### Fase 6: Script de Migração

- [ ] Implementar `scripts/migrate_client_structure.py`:
  - Backup completo de CLIENTES/
  - Dry-run com relatório
  - Mesclagem de duplicatas
  - Renomeação para UPPER_SNAKE_CASE
  - Criação de pastas funcionais
  - Movimento de FINANCEIRO.csv
  - Achatamento de sub-serviços com __
  - Rollback via backup

### Fase 7: Integração e Deploy

- [ ] Full test suite
- [ ] Build com PyInstaller
- [ ] Deploy para AppData
- [ ] Restart opencode para validação final

## Critérios de Aceitação

- [ ] 100% dos testes (novos + existentes) verdes
- [ ] Nenhum teste existente quebrado (regressão zero)
- [ ] Novo cliente criado já nasce com estrutura normalizada
- [ ] Serviços com `__` são detectados e listados corretamente
- [ ] Contexto carrega INFO-CLIENTE.md de qualquer subpasta
- [ ] Financeiro opera em modo híbrido (novo + legado)
- [ ] Documentos gerados vão para `{DOC}/GERADOS/{tipo}/`
- [ ] Script de migração executa sem erros em dry-run
