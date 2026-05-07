"""
FOTON MCP Server - Model Context Protocol Interface

This module exposes FotonSystem tools to AI assistants (Gemini, Claude, etc.)
via the MCP (Model Context Protocol) over stdio.

ARCHITECTURE NOTES:
- Uses MCPServiceFactory for dependency injection (testable)
- Tools are thin wrappers that delegate to service layer
- Lazy loading via factory pattern for instant startup
- CRITICAL: No stdout output allowed outside mcp.run() — stdout is JSON-RPC
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys
import time
import logging

# --- CRITICAL: PATH PATCHING (Must be FIRST) ---
def _ensure_import_path():
    """Adds project root to sys.path for development mode."""
    if getattr(sys, 'frozen', False):
        return

    current_file = Path(__file__).resolve()
    project_root = current_file.parents[3]

    if (project_root / "foton_system" / "__init__.py").exists():
        root_str = str(project_root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

_ensure_import_path()

# --- LOGGING SETUP (file only, never stdout) ---
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

_logger = logging.getLogger("foton_mcp")

try:
    log_dir = PathManager.get_app_data_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "foton_mcp.log"

    # File handler only — never attach a StreamHandler to stdout
    _handler = logging.FileHandler(str(log_file), encoding="utf-8")
    _handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False  # Don't let logs leak to root→stdout
    _logger.info("Module loaded. Initializing MCP server...")
    
    # Suppress mcp library's console logging (it uses rich StreamHandler)
    for name in ("mcp", "mcp.server", "mcp.server.lowlevel.server"):
        lib_logger = logging.getLogger(name)
        lib_logger.addHandler(_handler)  # Route to our file
        lib_logger.propagate = False      # Don't echo to console
except Exception as e:
    sys.stderr.write(f"[MCP] Logging setup failed: {e}\n")

# --- BOOTSTRAP (silent) ---
try:
    PathManager.ensure_directories()
except Exception as e:
    _logger.warning(f"Could not initialize directories: {e}")

# --- MCP SERVER INSTANCE ---
mcp = FastMCP("Foton Architecture System")
_logger.info("FastMCP initialized.")


# ==============================================================================
# SERVICE FACTORY (Lazy Loaded)
# ==============================================================================

_factory = None

def _get_factory():
    """Get or create the service factory singleton."""
    global _factory
    if _factory is None:
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        _factory = MCPServiceFactory.get_instance()
    return _factory


# ==============================================================================
# HELPER: Get Config (lazy, cached)
# ==============================================================================

_config = None

def _get_config():
    """Get or create the Config singleton."""
    global _config
    if _config is None:
        from foton_system.modules.shared.infrastructure.config.config import Config
        _config = Config()
    return _config


# ==============================================================================
# HEALTH CHECK
# ==============================================================================

@mcp.tool()
def ping() -> str:
    """
    Health check. Returns instantly if the FOTON MCP server is alive.
    Use this to verify connectivity before calling other tools.
    """
    _logger.info("Tool called: ping")
    return f"🟢 FOTON MCP Online (pid={__import__('os').getpid()}, ts={int(time.time())})"


@mcp.tool()
def info_sistema() -> str:
    """
    Returns a full diagnostic of the FOTON system: configured paths, client count,
    template count, module availability, and version info. Use this to understand
    the current system state and available resources before starting work.
    """
    _logger.info("Tool called: info_sistema")
    try:
        config = _get_config()
        clients_dir = config.base_pasta_clientes
        templates_dir = config.templates_path

        client_count = 0
        if clients_dir.exists():
            ignored = set(config.ignored_folders + ['.obsidian'])
            client_count = sum(
                1 for d in clients_dir.iterdir()
                if d.is_dir() and d.name not in ignored
            )

        template_count = 0
        if templates_dir.exists():
            template_count = sum(
                1 for f in templates_dir.iterdir()
                if f.suffix.lower() in ('.docx', '.pptx')
            )

        output = (
            "📊 FOTON System Status\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  📂 Clientes:  {clients_dir}\n"
            f"     → {client_count} cliente(s) encontrado(s)\n"
            f"  📄 Templates: {templates_dir}\n"
            f"     → {template_count} template(s) disponíveis\n"
            f"  💾 Base Dados: {config.base_dados}\n"
            f"  🚫 Pastas ignoradas: {', '.join(config.ignored_folders)}\n"
            f"  🧹 Limpar variáveis faltantes: {config.clean_missing_variables}\n"
            f"  📝 Placeholder: '{config.missing_variable_placeholder}'\n"
        )
        return output
    except Exception as e:
        return f"❌ Erro ao obter info do sistema: {e}"


# ==============================================================================
# CLIENT TOOLS
# ==============================================================================

@mcp.tool()
def listar_clientes() -> str:
    """
    Lists all registered clients (architecture projects) in the firm's directory.
    Each client is a folder inside the configured 'caminho_pastaClientes' path.

    Returns the client name, whether an INFO file exists (📁 = has INFO, 📂 = no INFO),
    and the count of services (sub-projects) under that client.

    Use this as the FIRST STEP when the user asks about clients, projects, or wants
    to perform any operation on a specific client.
    """
    _logger.info("Tool called: listar_clientes")
    try:
        config = _get_config()
        clients_dir = config.base_pasta_clientes

        if not clients_dir.exists():
            return f"⚠️ Client directory not found: {clients_dir}"

        ignored = set(config.ignored_folders + ['.obsidian'])

        clients = sorted([
            d.name for d in clients_dir.iterdir()
            if d.is_dir() and d.name not in ignored
        ])

        if not clients:
            return "📭 No clients registered yet."

        output = f"📋 {len(clients)} client(s) found:\n"
        for c in clients:
            client_path = clients_dir / c
            # Check for INFO file
            info_files = list(client_path.glob("*INFO*.md"))
            has_info = len(info_files) > 0
            # Count services (subfolders not in ignored list)
            services = [
                s.name for s in client_path.iterdir()
                if s.is_dir() and s.name not in ignored
            ]
            marker = "📁" if has_info else "📂"
            svc_txt = f", {len(services)} serviço(s)" if services else ""
            output += f"  {marker} {c}{svc_txt}\n"

        return output
    except Exception as e:
        _logger.error(f"listar_clientes failed: {e}", exc_info=True)
        return f"❌ Error listing clients: {e}"


@mcp.tool()
def cadastrar_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:
    """
    Creates a new client in the FOTON system (Audited Standard Operation / POP).
    """
    _logger.info(f"Tool called: cadastrar_cliente(nome={nome})")
    try:
        from foton_system.core.ops.op_create_client import OpCreateClient
        op = OpCreateClient(actor="Agent_MCP")
        result = op.execute(
            name=nome,
            alias=apelido if apelido else None,
            nif=nif,
            email=email,
            phone=telefone
        )
        return (
            f"✅ Cliente criado com sucesso (POP Auditado)\n"
            f"   Nome: {nome}\n"
            f"   Pasta: {result['client_path']}\n"
            f"   Código: {result['client_id']}"
        )
    except ValueError as e:
        return f"⚠️ Dados inválidos: {e}"
    except Exception as e:
        _logger.error(f"cadastrar_cliente failed: {e}", exc_info=True)
        return f"❌ Erro ao cadastrar cliente: {e}"


@mcp.tool()
def ler_ficha_cliente(cliente: str) -> str:
    """
    Reads the client's INFO file (the Single Source of Truth / Centro de Verdade).
    """
    _logger.info(f"Tool called: ler_ficha_cliente(cliente={cliente})")
    try:
        config = _get_config()
        clients_dir = config.base_pasta_clientes

        # Resolve client folder (exact or partial match)
        client_path = _resolve_client_path(clients_dir, cliente, config)

        # Find INFO file (pattern: *INFO*.md)
        info_files = list(client_path.glob("*INFO*.md"))
        if not info_files:
            return (
                f"⚠️ No INFO file found for client '{client_path.name}'.\n"
                f"   Expected pattern: *INFO*.md in {client_path}"
            )

        # Read the most recent INFO file
        info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
        content = info_file.read_text(encoding="utf-8")

        return (
            f"📋 Ficha do Cliente: {client_path.name}\n"
            f"📄 Arquivo: {info_file.name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{content}"
        )
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"ler_ficha_cliente failed: {e}", exc_info=True)
        return f"❌ Erro ao ler ficha: {e}"


@mcp.tool()
def atualizar_ficha_cliente(cliente: str, secao: str, conteudo: str) -> str:
    """
    Updates a section of the client's INFO-*.md file (the Single Source of Truth).
    """
    _logger.info(f"Tool called: atualizar_ficha_cliente(cliente={cliente}, secao={secao})")
    try:
        config = _get_config()
        client_path = _resolve_client_path(config.base_pasta_clientes, cliente, config)

        info_files = list(client_path.glob("*INFO*.md"))
        if not info_files:
            return f"⚠️ No INFO file found for '{client_path.name}'. Cannot update."

        info_file = sorted(info_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]

        # SECURITY: Backup before modifying
        import shutil
        backup = info_file.with_suffix('.md.bak')
        shutil.copy2(info_file, backup)
        _logger.info(f"Backup created: {backup}")

        content = info_file.read_text(encoding="utf-8")

        # Find section and append
        section_header = f"## {secao}"
        if section_header in content:
            # Append after the section header (before next ## or end of file)
            parts = content.split(section_header, 1)
            after_header = parts[1]

            # Find next section
            next_section_idx = after_header.find("\n## ")
            if next_section_idx == -1:
                # Append at end
                new_content = content + f"\n{conteudo}\n"
            else:
                insert_point = len(parts[0]) + len(section_header) + next_section_idx
                new_content = content[:insert_point] + f"\n{conteudo}\n" + content[insert_point:]
        else:
            # Create new section at end
            new_content = content.rstrip() + f"\n\n{section_header}\n{conteudo}\n"

        info_file.write_text(new_content, encoding="utf-8")

        return (
            f"✅ Ficha atualizada: {info_file.name}\n"
            f"   Seção: {secao}\n"
            f"   Backup: {backup.name}"
        )
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"atualizar_ficha_cliente failed: {e}", exc_info=True)
        return f"❌ Erro ao atualizar ficha: {e}"


@mcp.tool()
def listar_servicos_cliente(cliente: str) -> str:
    """
    Lists the services (sub-projects) under a specific client.
    """
    _logger.info(f"Tool called: listar_servicos_cliente(cliente={cliente})")
    try:
        config = _get_config()
        client_path = _resolve_client_path(config.base_pasta_clientes, cliente, config)
        ignored = set(config.ignored_folders + ['.obsidian'])

        services = sorted([
            d.name for d in client_path.iterdir()
            if d.is_dir() and d.name not in ignored
        ])

        if not services:
            return f"📭 No services found for client '{client_path.name}'."

        output = f"📋 {len(services)} serviço(s) de {client_path.name}:\n"
        for svc in services:
            svc_path = client_path / svc
            subdirs = [s.name for s in svc_path.iterdir() if s.is_dir()]
            file_count = sum(1 for f in svc_path.rglob('*') if f.is_file())
            output += f"  📂 {svc} ({file_count} arquivo(s)) [{', '.join(subdirs)}]\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_servicos_cliente failed: {e}", exc_info=True)
        return f"❌ Erro ao listar serviços: {e}"


# ==============================================================================
# FINANCIAL TOOLS
# ==============================================================================

@mcp.tool()
def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """
    Records a financial entry in the client's FINANCEIRO.csv ledger.
    """
    _logger.info(f"Tool called: registrar_financeiro(cliente={cliente}, valor={valor})")
    try:
        from foton_system.core.ops.op_finance_entry import OpFinanceEntry
        op = OpFinanceEntry(actor="Agent_MCP")
        result = op.execute(
            client_name=cliente,
            description=descricao,
            value=valor,
            type=tipo
        )
        return f"✅ {result['message']} (POP Auditado)"
    except Exception as e:
        _logger.error(f"registrar_financeiro failed: {e}", exc_info=True)
        return f"❌ Erro POP: {e}"


@mcp.tool()
def consultar_financeiro(cliente: str) -> str:
    """
    Returns the financial summary for a specific client.
    """
    _logger.info(f"Tool called: consultar_financeiro(cliente={cliente})")
    try:
        service = _get_factory().get_finance_service()
        result = service.get_summary(cliente)

        if result.success:
            return (
                f"💵 Financeiro de {cliente}:\n"
                f"   Receita:  R$ {result.total_income:.2f}\n"
                f"   Despesa:  R$ {result.total_expenses:.2f}\n"
                f"   Saldo:    R$ {result.balance:.2f}"
            )
        return f"❌ {result.message}"
    except Exception as e:
        _logger.error(f"consultar_financeiro failed: {e}", exc_info=True)
        return f"❌ Erro: {e}"


@mcp.tool()
def resumo_financeiro_geral() -> str:
    """
    Returns a financial dashboard of ALL clients.
    """
    _logger.info("Tool called: resumo_financeiro_geral")
    try:
        import csv
        config = _get_config()
        clients_dir = config.base_pasta_clientes

        if not clients_dir.exists():
            return f"⚠️ Client directory not found: {clients_dir}"

        ignored = set(config.ignored_folders + ['.obsidian'])
        results = []
        total_income = 0.0
        total_expense = 0.0

        for d in sorted(clients_dir.iterdir()):
            if not d.is_dir() or d.name in ignored:
                continue

            csv_file = d / "FINANCEIRO.csv"
            if not csv_file.exists():
                continue

            income = 0.0
            expense = 0.0
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        val = float(row.get('Valor', 0))
                        if row.get('Tipo', '').upper() == 'ENTRADA':
                            income += val
                        else:
                            expense += val
            except Exception:
                continue

            balance = income - expense
            total_income += income
            total_expense += expense
            results.append((d.name, income, expense, balance))

        if not results:
            return "📭 No financial data found across clients."

        output = f"📊 Dashboard Financeiro ({len(results)} clientes com dados):\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for name, inc, exp, bal in results:
            emoji = "🟢" if bal >= 0 else "🔴"
            output += f"  {emoji} {name}: R$ {bal:,.2f} (E: {inc:,.2f} | S: {exp:,.2f})\n"

        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        total_balance = total_income - total_expense
        output += (
            f"  TOTAL: R$ {total_balance:,.2f} "
            f"(Receita: R$ {total_income:,.2f} | Despesa: R$ {total_expense:,.2f})"
        )
        return output
    except Exception as e:
        _logger.error(f"resumo_financeiro_geral failed: {e}", exc_info=True)
        return f"❌ Erro: {e}"


# ==============================================================================
# DOCUMENT TOOLS
# ==============================================================================

@mcp.tool()
def listar_templates() -> str:
    """
    Lists all available document templates (DOCX and PPTX).
    """
    _logger.info("Tool called: listar_templates")
    try:
        config = _get_config()
        templates_dir = config.templates_path

        if not templates_dir.exists():
            return f"⚠️ Templates directory not found: {templates_dir}"

        pptx = sorted([f.name for f in templates_dir.glob("*.pptx")])
        docx = sorted([f.name for f in templates_dir.glob("*.docx")])

        output = f"📄 Templates disponíveis em: {templates_dir.name}\n"
        if pptx:
            output += f"\n🟦 PPTX ({len(pptx)}):\n"
            for t in pptx:
                output += f"  • {t}\n"
        if docx:
            output += f"\n🟩 DOCX ({len(docx)}):\n"
            for t in docx:
                output += f"  • {t}\n"

        if not pptx and not docx:
            return "📭 No templates found."

        return output
    except Exception as e:
        _logger.error(f"listar_templates failed: {e}", exc_info=True)
        return f"❌ Erro: {e}"


@mcp.tool()
def listar_documentos_cliente(cliente: str, servico: str = "") -> str:
    """
    Lists all files belonging to a client.
    """
    _logger.info(f"Tool called: listar_documentos_cliente(cliente={cliente}, servico={servico})")
    try:
        config = _get_config()
        client_path = _resolve_client_path(config.base_pasta_clientes, cliente, config)

        target = client_path / servico if servico else client_path

        if not target.exists():
            return f"⚠️ Path not found: {target}"

        files_by_folder = {}
        for f in sorted(target.rglob('*')):
            if not f.is_file():
                continue
            try:
                rel = f.relative_to(target)
            except ValueError:
                continue
            folder = str(rel.parent) if rel.parent != Path('.') else "(raiz)"
            if folder not in files_by_folder:
                files_by_folder[folder] = []
            size_kb = f.stat().st_size / 1024
            files_by_folder[folder].append(f"{rel.name} ({size_kb:.0f} KB)")

        if not files_by_folder:
            return f"📭 No files found in {target.name}."

        total = sum(len(v) for v in files_by_folder.values())
        scope = f"{client_path.name}/{servico}" if servico else client_path.name
        output = f"📂 {total} arquivo(s) em {scope}:\n"

        for folder, files in sorted(files_by_folder.items()):
            output += f"\n  📁 {folder}/\n"
            for fname in files:
                output += f"    • {fname}\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_documentos_cliente failed: {e}", exc_info=True)
        return f"❌ Erro: {e}"


@mcp.tool()
def gerar_documento(cliente: str, nome_template: str, dados_extras: dict = {}) -> str:
    """
    Generates a document for a client by merging a template with client data.
    """
    _logger.info(f"Tool called: gerar_documento(cliente={cliente}, template={nome_template})")
    try:
        from foton_system.core.ops.op_doc_gen import OpGenerateDocument
        op = OpGenerateDocument(actor="Agent_MCP")
        result = op.execute(
            client_name=cliente,
            template_name=nome_template,
            extra_data=dados_extras
        )
        return (
            f"✅ Documento Gerado (POP Auditado)\n"
            f"   Arquivo: {result['output_path']}"
        )
    except Exception as e:
        _logger.error(f"gerar_documento failed: {e}", exc_info=True)
        return f"❌ Erro POP: {e}"


@mcp.tool()
def validar_template(cliente: str, nome_template: str, arquivo_dados: str = "") -> str:
    """
    Pre-flight validation for document generation.
    """
    _logger.info(f"Tool called: validar_template(cliente={cliente}, template={nome_template})")
    try:
        config = _get_config()
        factory = _get_factory()

        svc = factory.get_client_service()
        client_path = svc.resolve_client_path(cliente)

        template_path = config.templates_path / nome_template
        if not template_path.exists():
            return f"❌ Template not found: {nome_template}"

        doc_type = template_path.suffix.lstrip('.').lower()
        if arquivo_dados:
            data_path = client_path / arquivo_dados
        else:
            md_files = list(client_path.glob('*INFO*.md')) + list(client_path.glob('*.md'))
            if not md_files:
                return f"⚠️ No data files (.md) found for {client_path.name}"
            data_path = md_files[0]

        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        doc_service = MCPServiceFactory.get_instance().get_document_service()
        missing = doc_service.validate_template_keys(str(template_path), str(data_path), doc_type)

        if not missing:
            return f"✅ Pre-flight OK! Template '{nome_template}' has all variables satisfied."

        output = f"⚠️ Pre-flight: {len(missing)} variable(s) MISSING:\n"
        for key in missing:
            output += f"   ❌ {key}\n"
        return output
    except Exception as e:
        return f"❌ Erro na validação: {e}"


# ==============================================================================
# KNOWLEDGE / RAG TOOLS
# ==============================================================================

@mcp.tool()
def consultar_conhecimento(pergunta: str) -> str:
    """
    Searches the firm's knowledge base using semantic search (RAG).
    """
    _logger.info(f"Tool called: consultar_conhecimento(pergunta='{pergunta[:50]}...')")
    try:
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Agent_MCP")
        result = op.execute(query=pergunta)

        if result["status"] == "EMPTY":
            return "📭 No relevant knowledge found in the database."

        output = []
        for i, r in enumerate(result["results"], 1):
            output.append(f"--- [{i}] Source: {r['source']} (Similarity: {r['score']:.0%}) ---\n{r['document']}\n")

        return "\n".join(output)
    except Exception as e:
        return f"❌ Knowledge query error: {e}"


@mcp.tool()
def indexar_conhecimento(pasta_alvo: str = "") -> str:
    """
    Indexes documents into the firm's knowledge base.
    """
    _logger.info(f"Tool called: indexar_conhecimento(alvo={pasta_alvo})")
    try:
        from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
        op = OpIndexKnowledge(actor="Agent_MCP")
        kwargs = {"target_path": pasta_alvo} if pasta_alvo.strip() else {}
        result = op.execute(**kwargs)
        return f"✅ Knowledge base updated! Files: {result['files_scanned']}, Chunks: {result['chunks_created']}"
    except Exception as e:
        return f"❌ Indexing error: {e}"


# ==============================================================================
# MAINTENANCE TOOLS
# ==============================================================================

@mcp.tool()
def sincronizar_base() -> str:
    """
    Synchronizes the master dashboard database.
    """
    _logger.info("Tool called: sincronizar_base")
    try:
        from foton_system.modules.sync.sync_service import SyncService
        svc = SyncService()
        result = svc.sync_dashboard()
        return f"✅ Dashboard synchronized! Records: {len(result)}" if result else "⚠️ No clients found."
    except Exception as e:
        return f"❌ Sync error: {e}"


@mcp.tool()
def sincronizar_clientes() -> str:
    """
    Discovers and registers new clients and services from folders.
    """
    _logger.info("Tool called: sincronizar_clientes")
    try:
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository
        repo = ExcelClientRepository()
        svc = ClientService(repo)
        svc.sync_clients_db_from_folders()
        svc.sync_services_db_from_folders()
        return "✅ Client & service databases synchronized!"
    except Exception as e:
        return f"❌ Client sync error: {e}"


# ==============================================================================
# PIPELINES
# ==============================================================================

@mcp.tool()
def pipeline_novo_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:
    """
    SAFE PIPELINE for creating a new client.
    """
    _logger.info(f"Tool called: pipeline_novo_cliente(nome={nome})")
    try:
        config = _get_config()
        factory = _get_factory()
        svc = factory.get_client_service()
        
        # Check for duplicates using new resolution logic if possible, or simple manual scan
        try:
            exists = svc.resolve_client_path(nome)
            return f"⚠️ PIPELINE PARADO — Cliente similar já existe: {exists.name}"
        except ValueError:
            pass # Good, doesn't exist

        result = cadastrar_cliente(nome, apelido, nif, email, telefone)
        return result
    except Exception as e:
        return f"❌ Pipeline error: {e}"


@mcp.tool()
def pipeline_emitir_documento(cliente: str, nome_template: str, dados_extras: dict = {}) -> str:
    """
    SAFE PIPELINE for document generation report.
    """
    _logger.info(f"Tool called: pipeline_emitir_documento(cliente={cliente}, template={nome_template})")
    try:
        config = _get_config()
        svc = _get_factory().get_client_service()
        client_path = svc.resolve_client_path(cliente)

        output = f"📋 PRÉ-VOO — Emissão de Documento\n"
        output += f"   Cliente:  {client_path.name}\n"
        output += f"   Template: {nome_template}\n\n"

        validation = validar_template(cliente, nome_template)
        output += f"{validation}\n"

        template_base = Path(nome_template).stem
        existing = list(client_path.rglob(f"GERADO_*{template_base}*"))
        if existing:
            output += f"\n⚠️ DUPLICATAS: {len(existing)} similar(es) já existe(m).\n"
        else:
            output += "✅ DUPLICATAS: Nenhum similar encontrado.\n"

        return output
    except Exception as e:
        return f"❌ Pipeline error: {e}"


# ==============================================================================
# HELPER: Internal Client Path Resolution
# ==============================================================================

def _resolve_client_path(clients_dir: Path, cliente: str, config) -> Path:
    """
    Internal helper used by old tests and some tools. 
    Now proxies to ClientService.
    """
    svc = _get_factory().get_client_service()
    return svc.resolve_client_path(cliente)


# ==============================================================================
# SERVER RUN
# ==============================================================================

def run_server():
    _logger.info("Starting MCP stdio loop...")
    sys.stderr.write("[MCP] Foton server ready.\n")
    sys.stderr.flush()
    try:
        mcp.run()
    except Exception as e:
        _logger.critical(f"MCP loop crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    run_server()
