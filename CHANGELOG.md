# Changelog

Todas as mudanças notáveis no Foton System são documentadas aqui.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o versionamento segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Circuit breaker para ChromaDB (3 falhas → OPEN 60s, HALF_OPEN recovery)
- RotatingFileHandler para logs (5MB, 3 backups)
- Request correlation ID (`[req-{uuid}]`) em todas as 32 ferramentas MCP
- Schema validation para `dados_extras` (max 50 keys, valores escalares apenas)
- Skills granulares por domínio: foton-clients, foton-documents, foton-finance, foton-rag
- Metaskill foton-architecture com mapa de skills e orquestração
- 27 novos testes (12 circuit breaker + 15 path traversal)

### Security
- Path traversal sanitizado em `validar_template` via `Path(nome_template).name`
- Limpeza de arquivos temporários RAG via `tempfile.mkdtemp()` + `shutil.rmtree()` em `finally`
- Narrow `except Exception` em todas as 32 tools (ValueError/OSError/PermissionError específicos)

### Changed
- `client_service.py` (735 linhas) fatorado em 3 arquivos + facade
- `foton-architecture/SKILL.md` refatorada como metaskill delegando para skills granulares
- `DocsMcp.md` sincronizado com as 32 ferramentas atuais + seção de segurança

### Fixed
- Import de `uuid` ausente em `foton_mcp.py`
- `__init__.py` adicionado em `modules/finance/` e 5 subdiretórios
- Script `migrate_client_structure.py` movido para `foton_system/scripts/` com `.bat` wrapper

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
