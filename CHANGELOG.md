# Changelog

Todas as mudanças notáveis no Foton System são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o versionamento segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (EPIC-004 — Sprint 8: Recuperação Inteligente RAG)
- **SPEC-RAG-v1.0** (STORY-028) — formalização do módulo RAG com 18 RULE-IDs
- **Filtros + Contexto + Diagnóstico** (STORY-029, RULE-RAG-4.1/4.2/4.3/5.1/5.2/5.3/6.1/6.2)
  - `consultar_conhecimento` agora aceita filtro `cliente` e `tipo_doc`
  - Resultados incluem trecho de contexto (100 chars antes/depois)
  - Nova MCP tool `diagnostico_conhecimento` — total chunks, status CB, última indexação
  - Indexação seletiva por cliente (`indexar_conhecimento(cliente="X")`)
  - TUI: atalho `g` para busca semântica global
  - TUI: resultados formatados com score, fonte e contexto

### Added (EPIC-003 — Sprint 7: Automação Comercial e Documentos)
- **Pré-validação Obrigatória + Placeholder Zero** (STORY-022, RULE-DOC-2.1/2.4/2.5)
  - `gerar_documento()` executa `validar_template` internamente e bloqueia geração se houver variáveis não resolvidas
  - Pós-processamento nos adapters DOCX/PPTX detecta `@VAR` sobreviventes como `"None"`/`"---"` — erro explícito
  - `validar_template` relatório colorido com categorias ✅ Resolvidas / ❌ Não encontradas / ⚠️ Valores inválidos
- **Engine de Fórmulas Extraída + Hardening** (STORY-023, RULE-DOC-4.1-4.4)
  - `FormulaEngine` em `core/ops/formula_engine.py` — extraído de `DocumentService._resolve_operations`
  - Div/0, NaN, Infinity → erro explícito (status FAIL) em vez de 0.0 silencioso
  - `FormulaEngine.report()` — relatório de fórmulas com expressão, resultado e status (OK/ERRO)
  - Harmonização do parser com `FormSession._evaluate` (mesma engine, comportamento unificado)
- **Histórico de Versões** (STORY-024, RULE-DOC-3.6)
  - `historico_documentos.jsonl` por cliente com campos: data_hora, tipo_template, nome_arquivo, status, versao, cliente
  - Regeneração preserva versão anterior com sufixo `_v1` → nova salva como `_v2`
  - Nova MCP tool `historico_documentos(cliente, limite=10)` — consulta por cliente
  - Opção "Histórico de Documentos" no menu TUI Documentos
- **Geração em Lote + Nomenclatura Padronizada** (STORY-025, RULE-DOC-3.2/3.5)
  - `gerar_documentos_lote(cliente, documentos)` — MCP tool com pipeline 2 fases (pré-voo → geração)
  - `OpGenerateBatchDocuments(BaseOp)` — POP auditado com telemetria
  - Padrão `CLIENTE_SERVICO_TIPO_DATA.ext` com sanitização e fallback legado
  - Opção "Gerar Lote (Proposta + Contrato + Anexo)" no menu TUI Documentos
- **Testes:** 98 novos (4 stories), suite total **792/792 passando**

### Added (sprints anteriores)
- **Telemetria — Session Tracking** (STORY-020, RULE-TELEMETRY-1.1/1.2)
  - `session_tracker.py`: UUID por execução, detecção de interface (TUI/MCP), contadores monotônicos (total_sessoes, total_operacoes, primeiro_uso)
  - Persistência em `session.json` no diretório de configuração
- **Telemetria — Operation Tracking** (STORY-020, RULE-TELEMETRY-1.3/1.4)
  - `operation_tracker.py`: decorator `@track_operation` + escrita em `operation_log.jsonl`
  - Instrumentação: 35+ MCP tools (via `_log_tool_call`), 12 POPs (via `BaseOp.execute()`), menus TUI
  - Rotação automática: 10MB máximo, trunca para ≤8MB
- **NPS Evolutivo** (STORY-021, RULE-UX-9.1)
  - Comentário/sugestão opcional (textarea multi-linha)
  - Contexto automático: session_count, operation_count, interface, session_id
  - Tendência visual (📈📉➡️) e tabela das últimas 5 respostas
  - Classificação (Detrator/Neutro/Promotor) armazenada mas oculta na TUI
- **Export Unificado** (STORY-021, RULE-UX-9.2, RULE-TELEMETRY-1.5)
  - `telemetry_exporter.py`: gera .zip na Área de Trabalho com relatório NPS.md + operation_log.jsonl + session.json
  - Opção "Exportar Dados de Uso" (opção 7) no menu Configurações
  - Opção "Exportar para Email" no pós-NPS
  - 100% local — nenhuma requisição HTTP, LGPD por design
- **Testes:** 29 novos (18 STORY-020 + 11 STORY-021), suite total 732/732 passando
  - `get_clients_dataframe()` e `get_services_dataframe()` com fallback "ATIVO"
  - `_ensure_database_exists()` garante colunas Status+CodCliente ao criar base
- **Domain Model — Entidades de Domínio** (STORY-011, parcial ~60%)
  - `Client` entity com 5 métodos (soft_delete, restore, is_active, get_status, to_dict)
  - `Service` entity com 3 métodos (soft_delete, restore, is_active)
  - `FinanceEntry` com validação em `__post_init__`
- **CRUD — Ferramentas de Delete/Restore** (STORY-012)
  - `remover_cliente`: soft delete + .bak + POP auditado
  - `restaurar_cliente`: lista deletados + restaura + POP
  - `remover_servico`: soft delete + .bak + POP
  - `atualizar_servico`: 11 campos válidos + POP
  - `BaseOp` garante POP em todas operações destrutivas
- **CRUD — Validação Financeiro + INFO Files** (STORY-013/018)
  - Validação de tipo, cliente, duplicata, DataRegistro em `registrar_financeiro`
  - Multi-operação em `atualizar_ficha_cliente`: replace, remove, field, append
  - `OpUpdateClientInfo(BaseOp)` com validate→execute→log
- **Pipeline de Sincronização Unificado** (STORY-014)
  - `pipeline_sincronizacao()` com 3 direções + `dry_run=True`
  - 5 passos sequenciais: snapshot→diff→validate→apply→report
  - `SyncReport` com `to_dict()` e `resumo()` e elapsed time
  - `progress_callback` opcional nas funções batch
- **UX — Split menus.py + Helpers TUI** (STORY-015)
  - 4 handlers modulares: `menus_clients.py`, `menus_finance.py`, `menus_docs.py`, `menus_config.py`
  - `ProgressTracker` com elapsed time em operações batch
  - `error_suggestions` com `format_error_with_suggestion()` para erros contextuais
- **UX — Reestruturação Menu + Navegação** (STORY-016)
  - Subgrupos visuais (`--- Cadastro ---`, `--- Perigo ---`)
  - Atalho `g` para busca global via `parse_command()`
  - `listar_clientes` com paginação MCP
  - `confirm_action()` padronizado
- **Conformidade e Códigos** (STORY-017) — 5 novas ferramentas MCP
  - `verificar_conformidade_clientes`: auditoria de pastas e INFO files
  - `corrigir_conformidade`: auto-fix com criação de INFO files
  - `preencher_codigos_faltantes`: preenche CodCliente/CodServico NaN
  - `validar_codigos_servicos`: valida placeholders, formato, duplicatas
  - `corrigir_codigos_servicos`: correção automática de códigos inválidos
- **Testes:** 121+ novos, suite total 694/694 passando

## [1.4.0] - 2026-06-22

### Added
- **Sistema de nomenclatura configurável de arquivos INFO** (`InfoNamingGuide.md`)
  - `InfoPatternResolver` (Value Object) para resolver placeholders em patterns
  - 13 placeholders suportados: `{codCliente}`, `{nomeCliente}`, `{aliasCliente}`, `{codServico}`, `{aliasServico}`, `{versao}`, `{revisao}`, `{data}`, `{dataISO}`, `{ano}`, `{mes}`, `{timestamp}`, `{extensao}`
- `PathManager` com factory methods: `get_info_pattern()`, `get_info_glob()`, `get_info_header()`
- `settings.json`: nova chave `info_file_patterns` com patterns default e schema validation
- 2 novas ferramentas MCP: `verificar_conformidade_clientes`, `corrigir_conformidade`
- `ClientConformanceChecker`: auditoria de pastas e nomes de INFO files com auto-fix
- Script `scripts/migrate_info_to_pattern.py` para migração retroativa (dry-run/apply/rollback)
- `_resolve_info_filename()`, `_parse_revision_from_filename()` em `client_crud.py`
- Templates INFO agora usam headers configuráveis (`get_template_sections` + `to_header()`)
- Busca de INFO files via glob pattern em `sync_service.py` e `document_service.py`
- **Filtragem de pastas ocultas** (`.git`, `.obsidian`) em `list_client_folders()` e `sync_dashboard()` — não são mais tratadas como clientes fantasmas
- **`fill_missing_codes()`**: preenche `CodCliente` e `CodServico` NaN no banco de dados, com geração de códigos únicos e anti-colisão
- **`preencher_codigos_faltantes`**: nova ferramenta MCP (35 total) para preenchimento retroativo de códigos
- **`auto_fix` para `missing_info`**: `corrigir_conformidade` agora cria INFO files faltantes automaticamente a partir dos dados do banco
- **`generate_service_code()`**: função pública (antes privada `_generate_service_code`) com suporte a `existing_codes` para evitar colisões
- Exportação de dados (`export_client_data`, `export_service_data`) agora persiste códigos gerados de volta ao banco (DRY)
- `export_client_data` e `export_service_data` aceitam parâmetros `target_alias` para exportação seletiva

### Changed
- `export_client_data()` / `export_service_data()` usam `InfoPatternResolver` em vez de nomes fixos
- `_get_latest_file()` usa `to_glob()` do pattern em vez de alias fixo
- `normalize_info_files()` em `migrate_client_structure.py` renomeia para pattern configurável
- `criar_estrutura_servico` copia template com nome gerado pelo pattern
- `pipeline_novo_cliente` busca INFO-CLIENTE via glob pattern
- Fallback mantido para compatibilidade com `INFO-CLIENTE.md` legado
- Pastas com nome iniciado por `.` são ignoradas em todas as varreduras do sistema
- `_generate_service_code` refatorado para delegar a `generate_service_code()` (DRY)
- **Kill-Switch Installer**: instalador local (Menu Opção 7) agora usa script de shell nativo como fallback quando DLLs do `_internal/` estão bloqueadas. O script mata instâncias, copia `_internal`, cria marcador `.first_run`, e reinicia o EXE do local de instalação
- **First-run detection**: `main.py._first_run_setup()` cria atalhos e inicializa config na primeira execução pós-instalação (via marcador `.first_run`)
- **Cross-platform**: instalador gera `.bat` (Windows) ou `.sh` (Linux/macOS) conforme `sys.platform`, usando apenas comandos nativos (`taskkill`/`pkill`, `xcopy`/`cp`, `rmdir`/`rm`)
- Instalação agora é **agnóstica de SO** — eliminada dependência de PowerShell/COM para criação de atalhos (delegado ao first-run detection em `main.py`)
- **TUI — Clientes menu expandido**: opções 5 (Ler Ficha), 6 (Atualizar Ficha), 7 (Preencher Códigos), 8 (Serviços do Cliente: Listar/Criar)
- **TUI — Financeiro**: novo menu principal (5) com Registrar Entrada/Saída, Consultar por Cliente e Resumo Geral
- **TUI — Cadastro com verificação**: `create_client_ui` agora verifica duplicatas (nome + NIF) antes de cadastrar (pipeline seguro)
- **`create_service_entry()`** em `client_crud.py` — persiste serviço no DB com `CodServico` gerado automaticamente (ou explícito), com verificação de duplicata
- **`validate_service_codes()`** em `client_crud.py` — valida todos os `CodServico` no DB: detecta ausentes, placeholders (`000`), formato inválido e duplicatas
- **`fix_service_codes()`** em `client_crud.py` — corrige automaticamente códigos inválidos gerando novos únicos
- **MCP `criar_estrutura_servico`** agora persiste o serviço no DB com `CodServico` real (em vez de placeholder `normalized[:8]`)
- **TUI `create_client_servico_ui`** agora persiste o serviço no DB com `CodServico` real (em vez de `"000"`)
- **`validar_codigos_servicos`**: nova ferramenta MCP (37) + TUI (menu Serviços opção 3)
- **`corrigir_codigos_servicos`**: nova ferramenta MCP (38) + TUI (menu Serviços opção 4)
- **Conformance checker**: `check()` agora valida códigos de serviço do DB (`invalid_service_code`); `auto_fix()` corrige automaticamente
- 17 novos testes (create_service_entry, validate_service_codes, fix_service_codes, conformance)

### Fixed
- Pasta `.git` dentro de `CLIENTES/` não é mais listada como cliente não registrado
- `MCPClientService` faltava método `fill_missing_codes()` — adicionado em `mcp_services.py`
- NaN do pandas retornava `float` em vez de `''` no `.get()` do iterrows — tratado em `client_crud.py:313-315`
- **BUG** `resource_financeiro_resumo` (`foton://financeiro/resumo`) chamava `get_general_summary()` inexistente — corrigido para `get_firm_summary()`

### Deprecated
- `fix_info_files.py` — redirecionado para `migrate_info_to_pattern.py`

### Security
- Path sanitization em `auto_fix()` do `ClientConformanceChecker`

## [1.3.2] - 2026-06-08

### Fixed
- Menu de "Instalação / Atalhos" não aparecia no executável compilado do Windows devido a falsos negativos na detecção de GUI em ambientes de execução congelados.
- Menu de instalação agora é exibido independentemente do perfil de interface, desde que executado em Windows nativo.

## [1.3.1] - 2026-06-08

### Added
- Suporte nativo a ambientes **Headless** (Servidores Linux, VPS, Docker, Windows Server Core)
- Flag `--watcher` para iniciar o monitoramento de arquivos em modo daemon/background
- Flag `--version` para consulta rápida de versão via terminal
- Detecção inteligente de interface gráfica no Windows (via `SESSIONNAME` + probe `tkinter`)
- Fallback automático para ANSI bell (`\a`) caso `winsound` esteja indisponível (Linux/Headless)

### Fixed
- Crash ao carregar módulo Pomodoro no Linux devido a import top-level de `winsound`
- Crash ao tentar abrir interface visual em ambientes sem display (implementado `get_form_filler`)
- Erros de terminal ao usar `os.system('cls')` em Linux (substituído por sequências ANSI `\033[2J\033[H`)
- Possível crash por `EOFError` no ponto de entrada fatal se `stdin` estiver fechado
- Redirecionamento de `stdout` para `stderr` no modo Watcher para evitar poluição do protocolo MCP

## [1.3.0] - 2026-06-08

### Added
- Circuit breaker para ChromaDB (3 falhas → OPEN 60s, HALF_OPEN recovery)
- RotatingFileHandler para logs (5MB, 3 backups)
- Request correlation ID (`[req-{uuid}]`) em todas as 32 ferramentas MCP
- Schema validation para `dados_extras` (max 50 keys, valores escalares apenas)
- Skills granulares por domínio: foton-clients, foton-documents, foton-finance, foton-rag
- Metaskill foton-architecture com mapa de skills e orquestração
- 27 novos testes (12 circuit breaker + 15 path traversal)
- Parser aritmético seguro `safe_math.py` (ast.NodeVisitor, 27 testes)
- Entry point consolidado: `python -m foton_system.entry --mcp`
- Adapter Pattern: `FormInterfacePort` + `SystemIntegratorPort` (Windows, Linux, WebView, TUI, Null)
- `EnvironmentPorter` para detecção agnóstica de SO e capacidades
- JSON Schema validation no `Config._validate_settings()`
- Build multi-target: `windows-desktop`, `linux-server`, `linux-desktop`
- Modo `--tui` no entry point principal
- 5 testes para `TipService` + 4 testes para `AuditLogger`
- CI/CD pipeline documentado no `DeploymentGuide.md`

### Security
- `eval()` substituído por `safe_eval()` em `document_service.py` e `form_session.py`
- 23 blocos `bare except:` eliminados em 10 arquivos
- Path traversal sanitizado em `validar_template` via `Path(nome_template).name`
- Limpeza de arquivos temporários RAG via `tempfile.mkdtemp()` + `shutil.rmtree()` em `finally`
- Narrow `except Exception` em todas as 32 tools (ValueError/OSError/PermissionError específicos)

### Changed
- `client_service.py` (735 linhas) fatorado em 3 arquivos + facade
- `foton-architecture/SKILL.md` refatorada como metaskill delegando para skills granulares
- `DocsMcp.md` sincronizado com as 32 ferramentas atuais + seção de segurança
- MCP tools delegam para `client_crud.py`/`client_query.py` diretamente (sem `ClientService`)
- `SyncService` usa `DocumentService._parse_md_data` estático (sem `DocumentService(None, None)`)
- `build.py` agora suporta `--type lite|full` e `--target windows-desktop|linux-server|linux-desktop`
- `deploy.py` documentado no `DeploymentGuide.md` com pipeline proposto GitHub Actions
- `views/__init__.py` criado (diretório agora é pacote Python)
- `listar_clientes(limite=N)` com paginação e indicador "showing X of Y"
- `pipeline_novo_cliente` com verificação de NIF duplicado
- `chat.py` arquivado em `docs/04_ARCHIVES/`
- `enable_mcp` removido dos defaults (nunca era lido)

### Fixed
- Import de `uuid` ausente em `foton_mcp.py`
- `__init__.py` adicionado em `modules/finance/` e 5 subdiretórios
- Script `migrate_client_structure.py` movido para `foton_system/scripts/` com `.bat` wrapper
- Off-by-one no admin launcher
- Watcher "Desativar" agora realmente desativa
- Circuit breaker `_last_failure_time` resetado ao resetar
- Versionamento dinâmico (não mais hardcoded)
- TUI com 6 bugs de menu corrigidos
- MCP com 3 bugs críticos corrigidos (client/document/sync)
- `webview_bridge.py`: fallback `get_app_dir()` removido

## [1.2.0] - 2026-05

### Added
- TUI 2.0 responsiva com design adaptável (40-100 colunas)
- Visualizador de alta fidelidade (Preview) com cores dinâmicas
- Versionamento nativo - função "Salvar Como" cria versões (v1, v2, final)
- DNA centralizado (`info-Template.md`) como SSOT para templates
- Arquitetura modular com DependencyManager e plugins on-demand (AI pack)
- Sistema de didática integrada (TipService) com tags `[!DIDACTIC]`
- Modo Sandbox com flag `--sandbox` para experimentação segura
- Mecanismo Retry on Lock para arquivos Excel bloqueados (OneDrive)
- Integração WebView2 com fallback automático para navegador
- Builds dual: lite (rápida) e full (completa/offline)
- 4 novas ferramentas MCP: `pipeline_novo_cliente`, `pipeline_emitir_documento`, `importar_dados_servicos`, `configurar_agente`

### Changed
- Executável principal reduzido em 90% (lite)
- Templates INFO agora seguem hierarquia SSOT (Documento > Serviço > Cliente)
- Precisão matemática padronizada para `.2f`
- Formatação automática de documentos com case-insensitive para variáveis

## [1.1.0] - 2026-04

### Added
- Protocolo MCP com 21 ferramentas para agentes de IA
- RAG semântico local com ChromaDB e modelo paraphrase-multilingual-MiniLM-L12-v2
- Modo Sentinela (Watcher) para monitoramento proativo da base
- Pipeline de Novo Cliente com verificação automática de duplicatas
- Pipeline de Emissão de Documentos com validação de variáveis
- Indexação de conhecimento em arquivos `.md`
- Consulta contextual em projetos passados
- Build `--onedir` com inicialização instantânea
- Dashboard Sync (sincronização bidirecional com Excel)
- Skill Foton formalizada como Gemini CLI Skill

### Changed
- Serviço de documentos atualizado para suportar formatação automática
- Módulo financeiro refatorado para arquitetura hexagonal
- MCP docstrings otimizadas para LLMs

## [1.0.0] - 2026-03

### Added
- Primeira release estável do Foton System
- Interface de linha de comando (CLI) com menus interativos
- Gerenciamento de clientes com estrutura de pastas STR/HID/ELE
- Geração inteligente de documentos (contratos DOCX, propostas PPTX)
- Módulo financeiro com fluxo de caixa em CSV
- Dashboard financeiro do escritório
- Sistema de templates customizáveis
- Validação e sanitização de nomes de arquivo
- Gerenciador de Schema e Variáveis
- Auto-update com verificação segura no GitHub
- Launcher Administrativo
- Módulo de produtividade (Pomodoro)
- Suporte a Self-Bootstrapping e Workspace Portátil
- Packaged como executável único (PyInstaller OneFile)
- Licenciado sob GPL v3

---

## Links

- Repositório: <https://github.com/LAMP-LUCAS/fotonSystem>
- Releases: <https://github.com/LAMP-LUCAS/fotonSystem/releases>
