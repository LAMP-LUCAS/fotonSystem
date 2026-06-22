---
type: sprint
domain: core
status: active
tags: [naming, patterns, refactor, configuration, archival]
---

# SPRINT: Sistema de Nomenclatura Configurável de Arquivos INFO

## Objetivo

Substituir o sistema rígido de nomes de arquivos INFO (`INFO-CLIENTE.md`, `INFO-SERVICO.md`) por um sistema **configurável via placeholders**, permitindo que o usuário defina o padrão de nomenclatura via `settings.json`. O padrão será `INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md`.

---

## Contexto

### Problema

O sistema atual usa nomes **fixos e hardcoded**:
- `INFO-CLIENTE.md` — Centro de Verdade do cliente
- `INFO-SERVICO.md` — Centro de Verdade do serviço
- `COD_DOC_CD_ver_rev_INFO-alias.md` — Exportação versionada

Isso gera riscos:
1. **Arquivos homônimos**: sem o código no nome, é impossível identificar a qual registro o arquivo pertence sem abri-lo
2. **Hardcodes espalhados**: 12+ pontos no código com literais `"INFO-CLIENTE.md"` e `"INFO-SERVICO.md"`
3. **Sem flexibilidade**: o usuário não pode personalizar o padrão de nomenclatura

### Solução

Criar um **`InfoPatternResolver`** — Value Object que interpreta templates com `{placeholders}` e resolve nomes de arquivo dinamicamente. Configurável via `settings.json`:

```json
"info_file_patterns": {
    "cliente": "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
    "servico": "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md"
}
```

### Documentos de referência

- Auditoria de templates: `CLIENTES/DOC/auditoria_templates_documentos.md`
- Plano de adequação: `CLIENTES/DOC/plano_adequacao_clientes.md`
- Manual de operações: `CLIENTES/README.md`

---

## Fases

| Fase | Descrição | Esforço | Depende |
|------|-----------|---------|---------|
| **0** | Config + PatternResolver + PathManager | ~4h | — |
| **1** | Criação de INFO files (substituir hardcodes) | ~3h | Fase 0 |
| **2** | Leitura e sincronização | ~3h | Fase 1 |
| **3** | Exportação versionada unificada | ~3h | Fase 2 |
| **4** | Migração retroativa (scripts) | ~2h | Fase 3 |
| **5** | Conformance checker (MCP + CLI) | ~4h | Fase 4 |
| **6** | Limpeza de dead code e documentação | ~1h | Fase 5 |

**Total estimado:** ~20h

---

## Fase 0 — Config + PatternResolver + PathManager (P0)

*Base de todo o sistema. Nada começa sem isso.*

### 0.1 Config — Adicionar `info_file_patterns` ao settings.json

**Arquivos:** `settings.json`, `config.py`

**TDD:**
- [ ] Teste: `Config().info_file_patterns` retorna dict com `cliente` e `servico`
- [ ] Teste: `Config().info_file_patterns` usa defaults se chave ausente
- [ ] Teste: schema validation aceita `info_file_patterns` como `dict`

### 0.2 Domain — Criar `InfoPatternResolver`

**Arquivo:** `foton_system/modules/shared/domain/info_pattern_resolver.py` (novo)

**Value Object puro** (sem dependências de infra):

| Método | Assinatura | Comportamento |
|--------|-----------|---------------|
| `__init__` | `(pattern: str)` | Valida e parseia placeholders com regex `\{(\w+)\}` |
| `resolve` | `(**kwargs) -> str` | Substitui placeholders pelos valores fornecidos; levanta `ValueError` se faltar placeholder obrigatório |
| `to_glob` | `() -> str` | Substitui `{placeholders}` por `*` para busca com `glob()` |
| `to_header` | `() -> str` | Retorna `## {pattern}` para usar como seção no .md |
| `extract` | `(filename: str) -> dict` | Extrai valores dos placeholders de um filename real (oposto de `resolve`) |
| `placeholders` | `(property) -> set[str]` | Retorna os placeholders encontrados no pattern |

**Placeholders suportados:**

| Placeholder | Origem | Exemplo |
|---|---|---|
| `{codCliente}` | DB / `generate_client_code` | `JOS01` |
| `{nomeCliente}` | DB / cadastro | `JOAO_SILVA` |
| `{aliasCliente}` | Nome da pasta | `JOAO_SILVA` |
| `{codServico}` | DB / `_generate_service_code` | `JOSRES01` |
| `{aliasServico}` | Nome da subpasta | `RESIDENCIA` |
| `{versao}` | Definido na exportação | `00` |
| `{revisao}` | Auto-incrementada | `00`, `01`, `02` |
| `{data}` | Sistema (date) | `2026-06-22` |
| `{dataISO}` | Sistema (ISO) | `20260622` |
| `{ano}` | Sistema | `2026` |
| `{mes}` | Sistema | `06` |
| `{timestamp}` | Sistema (datetime) | `20260622_153042` |
| `{extensao}` | Configurável | `md` |

**TDD (ordem de implementação):**
- [ ] RED: `test_init_com_pattern_valido` → GREEN → REFACTOR
- [ ] RED: `test_init_com_pattern_invalido_lanca` → GREEN → REFACTOR
- [ ] RED: `test_placeholders_property` → GREEN → REFACTOR
- [ ] RED: `test_resolve_substitui_todos_placeholders` → GREEN → REFACTOR
- [ ] RED: `test_resolve_com_placeholders_parciais` → GREEN → REFACTOR
- [ ] RED: `test_resolve_placeholder_extra_e_ignorado` → GREEN → REFACTOR
- [ ] RED: `test_resolve_placeholder_faltante_lanca` → GREEN → REFACTOR
- [ ] RED: `test_to_glob_substitui_por_asterisco` → GREEN → REFACTOR
- [ ] RED: `test_to_header_prefixo_com_cerquilha` → GREEN → REFACTOR
- [ ] RED: `test_extract_extrai_valores_do_filename` → GREEN → REFACTOR
- [ ] RED: `test_extract_filename_nao_correspondente_retorna_vazio` → GREEN → REFACTOR
- [ ] RED: `test_resolve_com_placeholder_extensao` → GREEN → REFACTOR

### 0.3 PathManager — Factory methods

**Arquivo:** `path_manager.py`

**Novos métodos:**
```python
@staticmethod
def get_info_pattern(tipo: str) -> "InfoPatternResolver":
    """Retorna o resolver para o tipo ('cliente'|'servico')."""

@staticmethod
def get_info_header(tipo: str) -> str:
    """Retorna o header ## para templates markdown."""

@staticmethod
def get_info_glob(tipo: str) -> str:
    """Retorna o glob pattern para buscar arquivos INFO existentes."""
```

**TDD:**
- [ ] RED: `get_info_pattern_cliente` → GREEN
- [ ] RED: `get_info_header_cliente` → GREEN
- [ ] RED: `get_info_glob_cliente` → GREEN
- [ ] RED: `get_info_pattern_tipo_invalido_lanca` → GREEN

### Riscos da Fase 0

- `extract()` depende de regex inversa — pode falhar se o pattern tiver placeholders adjacentes sem separadores. Solução: usar named groups com `(?P<nome>...)` e garantir separadores não ambíguos.
- Placeholder `{extensao}` precisa de tratamento especial no `to_glob()` para não virar `*.md` → `*.*md`.

### Critério de aceitação da Fase 0

- `pytest tests/unit/test_info_pattern_resolver.py -v` → 12+ testes verdes
- `pytest tests/unit/test_path_manager.py -v -- conhecidos` → 4+ testes verdes
- Nenhum teste existente quebrado

---

## Fase 1 — Criação de INFO files (P0)

*Substituir hardcodes de criação para usar o pattern configurado.*

### 1.1 `foton_mcp.py:criar_estrutura_servico` (linha 440-445)

**Problema:** `shutil.copy(template_path, service_path / "INFO-SERVICO.md")` — nome hardcoded.

**Solução:** Usar `PathManager.get_info_pattern("servico").resolve(...)` para gerar o nome.

### 1.2 `foton_mcp.py:pipeline_novo_cliente` (linha 1083)

**Problema:** `base / c['name'] / "INFO-CLIENTE.md"` — busca por nome exato.

**Solução:** Usar `PathManager.get_info_glob("cliente")` para busca.

### 1.3 `client_crud.py:get_template_sections` (linha 153-177)

**Problema:** Headers fixos `## INFO-CLIENTE.md` e `## INFO-SERVICO.md` nas templates.

**Solução:** Substituir headers pelos do `PathManager.get_info_header()`.

### 1.4 `assets/info-Template.md` (linhas 3, 23)

**Problema:** Headers fixos no template asset.

**Solução:** Alterar para `## INFO-CLIENTE` e `## INFO-SERVICO` (sem `.md`, genéricos).

### TDD (transversal para Fase 1)
- [ ] Teste: criar_estrutura_servico gera INFO file com nome do pattern
- [ ] Teste: criar_estrutura_servico escreve header configurado no .md
- [ ] Teste: pipeline_novo_cliente encontra INFO file com pattern ao buscar NIF
- [ ] Teste: get_template_sections retorna headers do pattern

---

## Fase 2 — Leitura e sincronização (P0)

*Substituir hardcodes de busca de INFO files.*

### 2.1 `sync_service.py:sync_dashboard` (linha 31)

**Problema:** `glob("INFO-CLIENTE.md")` — busca exata.

**Solução:** `glob(PathManager.get_info_glob("cliente"))`.

### 2.2 `document_service.py:_load_context_data` (linha 218)

**Problema:** `f.name.upper() in ('INFO-CLIENTE.MD', 'INFO-SERVICO.MD')` — tupla fixa.

**Solução:** `fnmatch.fnmatch(f.name, PathManager.get_info_glob("cliente"))` ou similar.

### 2.3 `client_crud.py:read_client_info_file` / `update_client_info_file`

**Opcional:** refinar glob de `*INFO*.md` para `to_glob()`.

### TDD
- [ ] Teste: sync_dashboard encontra INFO files com pattern configurado
- [ ] Teste: _load_context_data prefere arquivos do pattern sobre genéricos
- [ ] Teste: read_client_info_file encontra arquivo com pattern

---

## Fase 3 — Exportação versionada unificada (P1)

*Unificar o sistema dual (canônico + exportação) num único sistema de pattern.*

### 3.1 `client_crud.py` — Substituir:
- `_generate_filename()` → `_resolve_info_filename()`
- `_parse_filename()` → `_parse_revision_from_filename()`
- `_get_latest_file()` → usar `to_glob()` do resolver

### 3.2 `client_crud.py:export_client_data` / `export_service_data`

Refatorar para usar os novos métodos.

### TDD
- [ ] Teste: export_client_data cria arquivo com pattern configurado
- [ ] Teste: export_client_data incrementa revisão corretamente
- [ ] Teste: _parse_revision_from_filename extrai dados
- [ ] Teste: _get_latest_file ordena por revisão

---

## Fase 4 — Migração retroativa (P1)

*Script para renomear INFO files existentes.*

### 4.1 `scripts/migrate_info_to_pattern.py` (novo)

```bash
python scripts/migrate_info_to_pattern.py          # dry-run
python scripts/migrate_info_to_pattern.py --apply   # executa
python scripts/migrate_info_to_pattern.py --rollback # restaura .bak
```

### 4.2 Atualizar `migrate_client_structure.py:normalize_info_files`

### TDD
- [ ] Teste: migrate renomeia INFO files para pattern
- [ ] Teste: migrate dry-run não altera arquivos
- [ ] Teste: migrate rollback restaura originais

---

## Fase 5 — Conformance checker (P1)

*Auditoria interativa via MCP + CLI.*

### 5.1 `modules/clients/application/use_cases/client_conformance.py` (novo)

- `ClientConformanceChecker.check()` → relatório de conformidade
- `auto_fix(item)` → renomeia pasta/arquivo
- `accept_state(item)` → persiste decisão

### 5.2 MCP Tools em `foton_mcp.py`

- `verificar_conformidade_clientes(modo)` 
- `corrigir_conformidade(item_id)`

### 5.3 CLI/TUI via entry point

- `foton --conformance` → mesmo motor, interface diferente

### TDD
- [ ] Teste: check identifica pasta com espaço
- [ ] Teste: check identifica INFO file ausente
- [ ] Teste: check identifica INFO file com nome fora do pattern
- [ ] Teste: auto_fix renomeia corretamente
- [ ] Teste: accept_state persiste decisão

---

## Fase 6 — Limpeza e documentação (P2)

### 6.1 Dead code removal

- `_generate_filename()` (client_crud.py:180)
- `_parse_filename()` (client_crud.py:184)
- `get_latest_info_file()` (fix_info_files.py:61)
- `normalize_info_files()` (migrate_client_structure.py:247) — substituída

### 6.2 Documentação

- Atualizar `CLIENTES/README.md` com seção de patterns configuráveis
- Atualizar `CLIENTES/.gitignore` se necessário

---

## Riscos gerais

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Regex do `extract()` não cobrir todos os patterns | Média | Alto | Testar com 10+ patterns diferentes, incluindo borda |
| Script de migração corromper INFO files existentes | Baixa | Crítico | Sempre criar .bak antes; modo dry-run obrigatório |
| Quebra de compatibilidade com versões anteriores | Média | Alto | Fases 0-3 não quebram nada (só adicionam); Fase 4 é opcional |
| Testes existentes hardcoded com `INFO-CLIENTE.md` | Alta | Médio | Atualizar fixtures dos testes conforme cada fase |
