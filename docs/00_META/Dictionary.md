---
type: concept
domain: core
status: active
tags: [meta, dictionary, ddd, terms]
---
# 📖 Dicionário de Domínios e Termos (Dictionary)

Este documento serve como a **Ubiquitous Language** (DDD) do FOTON System. Aqui definimos o que cada termo significa para garantir que Humanos e IAs falem a mesma língua.

## 🏛️ Termos de Arquitetura

- **Centro de Verdade (Center of Truth):** Arquivo `.md` (INFO-CLIENTE, INFO-SERVICO) que detém a autoridade sobre os dados de um projeto. A partir da v1.4.0, o nome segue um pattern configurável.
- **Placeholder:** Token `{nome}` dentro de um pattern de arquivo INFO que é substituído por um valor real. Ex: `{codCliente}` → `JOS01`.
- **Pattern (InfoPattern):** Template de nome de arquivo com placeholders, configurado em `settings.json` sob `info_file_patterns`. Ex: `INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md`.
- **Glob Pattern:** Versão de busca onde placeholders são substituídos por `*`. Gerado automaticamente pelo `to_glob()`.
- **Pasta Oculta:** Diretório com nome iniciado por `.` (ex: `.git`, `.obsidian`). É automaticamente ignorado pelo sistema em todas as varreduras de pastas de clientes.
- **Preencher Códigos (fill_missing_codes):** Operação que varre o banco de dados e gera `CodCliente`/`CodServico` para registros que possuem `NaN`, persistindo os códigos gerados no Excel.
- **Conformance Checker:** Auditoria automatizada (MCP + classe) que verifica se todos os clientes/serviços seguem o pattern configurado. A partir da v1.4.1, também consegue **criar** INFO files faltantes via auto-fix.
- **Kill-Switch Installer:** Estratégia de instalação onde o EXE copia a si mesmo e delega a cópia das DLLs travadas (`_internal`) para um script nativo do SO. O script mata todas as instâncias do Foton, copia os arquivos (agora destravados), cria um marcador `.first_run`, e reinicia o EXE do local de instalação.
- **Deferred Copy:** Cópia adiada de `_internal/` via script de shell nativo (`.bat` no Windows, `.sh` no Unix). Necessário porque DLLs carregadas pelo PyInstaller ficam locked enquanto o processo existe.
- **First-Run Marker (`\`.first_run\`):** Arquivo temporário criado pelo script deferred no `bin_dir`. Na próxima inicialização, `main.py._first_run_setup()` detecta o marcador, cria atalhos via `integrator`, inicializa config, e remove o marcador.
- **Native Shell Template:** Script de shell gerado dinamicamente pelo `install_service.py` conforme `sys.platform`. Usa apenas comandos nativos do SO (`taskkill`/`pkill`, `xcopy`/`cp`, `rmdir`/`rm`), sem dependências externas.
- **RalphLoop:** Ciclo agêntico de "Pesquisa -> Plano -> Ação -> Validação".
- **Hexagonal Architecture:** Padrão que isola a lógica de negócio (Core) de implementações externas (Adapters).
- **Zettelkasten + PARA:** Sistema de organização de notas interligadas por grafos e esferas de responsabilidade.

## 👥 Termos de Negócio (Escritório)

- **Cliente:** Pessoa ou entidade que contrata os serviços de arquitetura.
- **Serviço (Service):** Um sub-projeto ou demanda específica vinculada a um cliente (ex: Projeto Executivo, Consultoria).
- **Template:** Modelo de documento (Word/PowerPoint) com variáveis `@tags`.
- **CUB (Custo Unitário Básico):** Índice usado para estimativas de custos de construção.

## 🤖 Termos Técnicos

- **MCP (Model Context Protocol):** Protocolo de comunicação entre o Foton e Assistentes de IA.
- **TUI (Terminal User Interface):** Interface de navegação via teclado no terminal.
- **Frontmatter:** Bloco de metadados YAML no início dos arquivos Markdown.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Protocolo: [[LlmProtocol]]
- Contexto LLM: [[LlmContext]]
