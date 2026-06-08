# Changelog

Todas as mudanças notáveis no Foton System são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o versionamento segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- *(nothing yet)*

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
