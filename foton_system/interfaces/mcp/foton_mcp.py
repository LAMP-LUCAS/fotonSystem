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

    This creates:
    - The client folder with standard sub-structure (01_ADMINISTRATIVO, 02_FINANCEIRO, 03_PROJETOS)
    - An INFO-CLIENTE.md file (the client's Single Source of Truth)
    - A FINANCEIRO.csv ledger file
    - A record in the master Excel database (baseClientes.xlsx)

    IMPORTANT: Before calling this, use 'listar_clientes' to verify the client does NOT
    already exist. Use 'pipeline_novo_cliente' for the full safe workflow.

    Args:
        nome: Full client name (required, min 3 chars)
        apelido: Short alias/code for the folder name (optional, auto-generated if blank)
        nif: Tax ID / CPF / CNPJ (optional)
        email: Contact email (optional)
        telefone: Contact phone (optional)
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

    The INFO-*.md file contains project context, technical decisions, meeting notes,
    and all relevant metadata. This is the FIRST file you should read before performing
    any operation on a client — it provides the context needed for document generation,
    financial operations, and decision-making.

    Args:
        cliente: Client folder name (exact or partial match). Example: 'ADRIELLE' or 'MP Incorporadora'
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
                f"   Expected pattern: *INFO*.md in {client_path}\n"
                f"   Use 'atualizar_ficha_cliente' to create one."
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

    SECURITY: This tool creates a backup (.bak) before modifying the file.
    It appends content to the specified section or creates a new section if it doesn't exist.

    Supported sections: 'Contexto do Projeto', 'Decisões Técnicas', 'Notas de Reunião',
    or any custom ## heading.

    Args:
        cliente: Client folder name
        secao: Section heading to update (e.g., 'Notas de Reunião')
        conteudo: Content to append to the section (markdown formatted)
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

    In FOTON, each client can have multiple services (e.g., 'ELISEU', 'EZEQUIAS' under 'ADRIELLE').
    Each service contains its own ARQ/ (architecture files) and DOC/ (documents) folders.
    Ignores system folders like DOC, ARQ, HID, ELE, STR, PL, EVT at the client root.

    Args:
        cliente: Client folder name (exact or partial match)
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
    Records a financial entry (income or expense) in the client's FINANCEIRO.csv ledger.
    This is an Audited Standard Operation (POP) — each entry is timestamped and logged.

    Args:
        cliente: Client folder name
        descricao: Description of the transaction (e.g., 'Entrada Projeto', 'Taxa RRT')
        valor: Monetary value (always positive, the 'tipo' determines debit/credit)
        tipo: 'ENTRADA' for income or 'SAIDA' for expense (default: ENTRADA)
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
    except ImportError:
        try:
            service = _get_factory().get_finance_service()
            result = service.register_entry(cliente, descricao, valor, tipo)
            if result.success:
                return f"💵 {result.message} (Saldo: R$ {result.balance:.2f})"
            return f"❌ {result.message}"
        except Exception as fallback_e:
            return f"❌ Erro: {fallback_e}"
    except Exception as e:
        _logger.error(f"registrar_financeiro failed: {e}", exc_info=True)
        return f"❌ Erro POP: {e}"


@mcp.tool()
def consultar_financeiro(cliente: str) -> str:
    """
    Returns the financial summary for a specific client: total income, total expenses,
    and current balance. Reads from the client's FINANCEIRO.csv ledger.

    Args:
        cliente: Client folder name
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
    Returns a financial dashboard of ALL clients: total income, expenses, and balance
    for each client that has a FINANCEIRO.csv file. Also shows the firm-wide totals.

    Use this for business intelligence and to quickly identify which clients have
    outstanding balances or need follow-up.
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
    Lists all available document templates (DOCX and PPTX) from the firm's KIT DOC folder.

    Templates follow the naming convention: NN-COD_DOC_TIPO_VER_REV_DESCRICAO.ext
    Examples: Proposals, Contracts, Briefings, Receipts, Delivery Terms, Portfolios.

    Use this to show the user which templates are available before generating a document.
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
    Lists all files belonging to a client, optionally filtered by a specific service.
    Groups files by subfolder (ARQ, DOC, etc.) and shows file type, size, and modification date.

    Use this to:
    - Check what documents already exist before generating new ones
    - Find specific files the user is looking for
    - Audit the completeness of a client's project folder

    Args:
        cliente: Client folder name
        servico: Optional service subfolder name to filter (e.g., 'ELISEU')
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
    Generates a document for a client by merging a template with client data (Audited POP).

    The pipeline: INFO-*.md (context) + Template (DOCX/PPTX) + Extra Data = Final Document.
    The generated file is saved in the client's folder with prefix 'GERADO_'.

    IMPORTANT: Before calling this, use 'validar_template' to check for missing variables,
    and 'listar_documentos_cliente' to verify no duplicate already exists.
    Use 'pipeline_emitir_documento' for the full safe workflow.

    Args:
        cliente: Client folder name
        nome_template: Template filename (e.g., '02-COD_DOC_CT_00_R00_PROPOSTA-PROJETO.docx')
        dados_extras: Optional dict of additional variables to inject into the template
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
        return f"✅ Documento Gerado (POP Auditado): {result['output_path']}"
    except ImportError as e:
        return f"❌ Módulo não encontrado: {e}"
    except Exception as e:
        _logger.error(f"gerar_documento failed: {e}", exc_info=True)
        return f"❌ Erro POP: {e}"


@mcp.tool()
def validar_template(cliente: str, nome_template: str, arquivo_dados: str = "") -> str:
    """
    Pre-flight validation: checks whether all template variables (e.g., {{NOME_CLIENTE}})
    are satisfied by the client's data files before generating the document.

    Returns:
    - ✅ if all variables are present
    - ⚠️ with a list of MISSING variables that need to be provided

    This is a NON-DESTRUCTIVE read-only operation. Always run this before 'gerar_documento'.

    Args:
        cliente: Client folder name
        nome_template: Template filename to validate against
        arquivo_dados: Optional specific data file to use (default: auto-detects *.md files)
    """
    _logger.info(f"Tool called: validar_template(cliente={cliente}, template={nome_template})")
    try:
        config = _get_config()
        factory = _get_factory()

        resolver = factory._get_path_resolver()
        client_path = resolver.resolve(cliente)

        template_path = config.templates_path / nome_template
        if not template_path.exists():
            return f"❌ Template not found: {nome_template}"

        doc_type = template_path.suffix.lstrip('.').lower()
        if doc_type not in ('docx', 'pptx'):
            return f"❌ Unsupported template type: {doc_type}"

        if arquivo_dados:
            data_path = client_path / arquivo_dados
        else:
            md_files = list(client_path.glob('*INFO*.md')) + list(client_path.glob('*.md'))
            if not md_files:
                return f"⚠️ No data files (.md) found in {client_path.name}"
            data_path = md_files[0]

        if not data_path.exists():
            return f"❌ Data file not found: {data_path.name}"

        from foton_system.modules.documents.application.use_cases.document_service import DocumentService
        from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
        from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter

        doc_service = DocumentService(PythonDocxAdapter(), PythonPPTXAdapter())
        missing = doc_service.validate_template_keys(str(template_path), str(data_path), doc_type)

        if not missing:
            return (
                f"✅ Pre-flight OK! Template '{nome_template}' has all variables satisfied.\n"
                f"   Data source: {data_path.name}\n"
                f"   Ready to generate with 'gerar_documento'."
            )

        output = (
            f"⚠️ Pre-flight: {len(missing)} variable(s) MISSING in template '{nome_template}':\n"
        )
        for key in missing:
            output += f"   ❌ {key}\n"
        output += f"\n   Data source: {data_path.name}"
        output += "\n   Provide these values via 'dados_extras' in 'gerar_documento', or update the INFO file."
        return output

    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"validar_template failed: {e}", exc_info=True)
        return f"❌ Erro na validação: {e}"


# ==============================================================================
# KNOWLEDGE / RAG TOOLS (Available in dev mode only — deps not bundled in EXE)
# ==============================================================================

@mcp.tool()
def consultar_conhecimento(pergunta: str) -> str:
    """
    Searches the firm's knowledge base (past projects, documents) using semantic search (RAG).
    Use this to find context, past decisions, or reference materials.

    NOTE: This tool requires chromadb and sentence-transformers, which may not be available
    in the compiled EXE version.

    Args:
        pergunta: Natural language question to search for
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
    except ImportError:
        return "⚠️ RAG unavailable: missing dependencies (chromadb, sentence-transformers)."
    except Exception as e:
        return f"❌ Knowledge query error: {e}"


@mcp.tool()
def indexar_conhecimento(pasta_alvo: str = "") -> str:
    """
    Indexes documents (.md, .txt) into the firm's knowledge base for semantic search.
    If no target path is given, indexes the entire client directory.

    NOTE: This tool requires chromadb and sentence-transformers.

    Args:
        pasta_alvo: Optional path to index (default: entire client base)
    """
    _logger.info(f"Tool called: indexar_conhecimento(alvo={pasta_alvo})")
    try:
        from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
        op = OpIndexKnowledge(actor="Agent_MCP")

        kwargs = {}
        if pasta_alvo.strip():
            kwargs["target_path"] = pasta_alvo

        result = op.execute(**kwargs)
        return (
            f"✅ Knowledge base updated!\n"
            f"   Files scanned: {result['files_scanned']}\n"
            f"   Chunks created: {result['chunks_created']}\n"
            f"   Target: {result['target']}"
        )
    except ImportError:
        return "⚠️ RAG unavailable: missing dependencies (chromadb, sentence-transformers)."
    except Exception as e:
        return f"❌ Indexing error: {e}"


# ==============================================================================
# SYNC / MAINTENANCE TOOLS
# ==============================================================================

@mcp.tool()
def sincronizar_base() -> str:
    """
    Synchronizes the master dashboard database (baseDados.xlsx) by scanning all client
    folders and their INFO-*.md files. This updates the Excel with current client data.

    Use this periodically or after bulk changes to client folders to keep the database
    in sync with the filesystem (the Single Source of Truth).
    """
    _logger.info("Tool called: sincronizar_base")
    try:
        from foton_system.modules.sync.sync_service import SyncService
        svc = SyncService()
        result = svc.sync_dashboard()

        if result is not None:
            return (
                f"✅ Dashboard synchronized!\n"
                f"   Records updated: {len(result)}\n"
                f"   Database: {_get_config().base_dados}"
            )
        return "⚠️ No clients found to synchronize."
    except Exception as e:
        _logger.error(f"sincronizar_base failed: {e}", exc_info=True)
        return f"❌ Sync error: {e}"


@mcp.tool()
def sincronizar_clientes() -> str:
    """
    Discovers new clients and services from the filesystem and registers them in the
    Excel databases (baseClientes.xlsx, baseServicos.xlsx).

    This performs TWO sync operations:
    1. Scans client folders → adds new ones to the clients database
    2. Scans service subfolders → adds new ones to the services database

    Use this after manually creating client folders or receiving new project folders
    via OneDrive sync.
    """
    _logger.info("Tool called: sincronizar_clientes")
    try:
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository

        repo = ExcelClientRepository()
        svc = ClientService(repo)

        svc.sync_clients_db_from_folders()
        svc.sync_services_db_from_folders()

        return (
            "✅ Client & service databases synchronized!\n"
            "   New clients and services discovered from folders have been registered."
        )
    except Exception as e:
        _logger.error(f"sincronizar_clientes failed: {e}", exc_info=True)
        return f"❌ Client sync error: {e}"


@mcp.tool()
def exportar_fichas() -> str:
    """
    Exports client data from the Excel database to INFO-*.md files in each client folder.
    Direction: Database → Files (generates/updates the Centros de Verdade).

    Uses versioned filenames (VER_REV) to avoid overwriting existing data.
    Only creates new files when data has changed.

    Use this after updating client data in the database to push changes to the filesystem.
    """
    _logger.info("Tool called: exportar_fichas")
    try:
        from foton_system.modules.clients.application.use_cases.client_service import ClientService
        from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository

        repo = ExcelClientRepository()
        svc = ClientService(repo)
        svc.export_client_data()

        return "✅ Client data exported to INFO-*.md files (versioned, no overwrites)."
    except Exception as e:
        _logger.error(f"exportar_fichas failed: {e}", exc_info=True)
        return f"❌ Export error: {e}"


# ==============================================================================
# INTELLIGENT PIPELINES
# ==============================================================================

@mcp.tool()
def pipeline_novo_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:
    """
    SAFE PIPELINE for creating a new client. Performs checks before acting:

    Step 1: Searches existing clients for duplicates (partial name match)
    Step 2: If duplicate found → returns warning with existing client info
    Step 3: If no duplicate → creates the client via 'cadastrar_cliente'
    Step 4: Reads back the created INFO file to confirm success

    This is the RECOMMENDED way to create clients — it prevents duplicates and
    verifies the result.

    Args:
        nome: Full client name (required)
        apelido: Short alias/code (optional)
        nif: Tax ID (optional)
        email: Contact email (optional)
        telefone: Contact phone (optional)
    """
    _logger.info(f"Tool called: pipeline_novo_cliente(nome={nome})")
    try:
        config = _get_config()
        clients_dir = config.base_pasta_clientes
        ignored = set(config.ignored_folders + ['.obsidian'])

        # Step 1: Check for duplicates
        search_term = nome.lower().replace(' ', '').replace('_', '')
        matches = []
        if clients_dir.exists():
            for d in clients_dir.iterdir():
                if d.is_dir() and d.name not in ignored:
                    folder_norm = d.name.lower().replace(' ', '').replace('_', '')
                    if search_term in folder_norm or folder_norm in search_term:
                        matches.append(d.name)

        # Step 2: Duplicate warning
        if matches:
            output = (
                f"⚠️ PIPELINE PARADO — Possível duplicata encontrada!\n"
                f"   Nome solicitado: '{nome}'\n"
                f"   Cliente(s) similar(es):\n"
            )
            for m in matches:
                output += f"     • {m}\n"
            output += (
                f"\n   Se deseja criar mesmo assim, use 'cadastrar_cliente' diretamente.\n"
                f"   Ou use 'ler_ficha_cliente' para verificar o cliente existente."
            )
            return output

        # Step 3: Create
        result = cadastrar_cliente(nome, apelido, nif, email, telefone)

        # Step 4: Verify
        if "✅" in result:
            ficha = ler_ficha_cliente(apelido if apelido else nome)
            return f"{result}\n\n--- Verificação ---\n{ficha}"

        return result
    except Exception as e:
        _logger.error(f"pipeline_novo_cliente failed: {e}", exc_info=True)
        return f"❌ Pipeline error: {e}"


@mcp.tool()
def pipeline_emitir_documento(cliente: str, nome_template: str, dados_extras: dict = {}) -> str:
    """
    SAFE PIPELINE for document generation. Performs a full pre-flight check WITHOUT
    generating any files. Returns a detailed report for the user to review.

    Step 1: VALIDATE — checks template variables vs. client data
    Step 2: CHECK DUPLICATES — searches for existing generated documents
    Step 3: REPORT — returns a pre-flight summary

    The pipeline NEVER generates the document automatically. After reviewing the report,
    the user must explicitly approve, and then you should call 'gerar_documento'.

    Args:
        cliente: Client folder name
        nome_template: Template filename to use
        dados_extras: Optional extra variables to inject
    """
    _logger.info(f"Tool called: pipeline_emitir_documento(cliente={cliente}, template={nome_template})")
    try:
        config = _get_config()
        client_path = _resolve_client_path(config.base_pasta_clientes, cliente, config)

        output = f"📋 PRÉ-VOO — Emissão de Documento\n"
        output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"   Cliente:  {client_path.name}\n"
        output += f"   Template: {nome_template}\n\n"

        # Step 1: Validate template
        validation = validar_template(cliente, nome_template)
        if "✅" in validation:
            output += "✅ VARIÁVEIS: Todas presentes\n"
        elif "⚠️" in validation:
            output += f"⚠️ VARIÁVEIS: {validation}\n"
        else:
            output += f"❌ VALIDAÇÃO: {validation}\n"
            output += "\n🛑 Pipeline interrompido — corrija os problemas acima antes de prosseguir."
            return output

        # Step 2: Check for duplicates
        template_base = Path(nome_template).stem
        existing = list(client_path.rglob(f"GERADO_*{template_base}*"))

        if existing:
            output += f"\n⚠️ DUPLICATAS: {len(existing)} documento(s) similar(es) já existe(m):\n"
            for ex in existing:
                size_kb = ex.stat().st_size / 1024
                output += f"   📄 {ex.name} ({size_kb:.0f} KB)\n"
        else:
            output += "✅ DUPLICATAS: Nenhum documento similar encontrado\n"

        # Step 3: Summary
        output += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        if "⚠️ VARIÁVEIS" in output:
            output += "⏸️  AÇÃO NECESSÁRIA: Forneça as variáveis faltantes antes de gerar.\n"
        elif existing:
            output += "⚠️ ATENÇÃO: Documento similar já existe. Confirme se deseja gerar novo.\n"
            output += "   Para gerar, chame: gerar_documento()\n"
        else:
            output += "✅ PRONTO: Todos os checks passaram. Confirme com o usuário para gerar.\n"
            output += "   Para gerar, chame: gerar_documento()\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"pipeline_emitir_documento failed: {e}", exc_info=True)
        return f"❌ Pipeline error: {e}"


# ==============================================================================
# HELPER: Client Path Resolution
# ==============================================================================

def _resolve_client_path(clients_dir: Path, cliente: str, config) -> Path:
    """
    Resolves a client name to a validated directory path.
    Supports exact match and partial/fuzzy matching.
    Raises ValueError if not found or ambiguous.
    """
    ignored = set(config.ignored_folders + ['.obsidian'])

    if not clients_dir.exists():
        raise ValueError(f"Client directory not found: {clients_dir}")

    # 1. Exact match
    exact = clients_dir / cliente
    if exact.exists() and exact.is_dir():
        return exact

    # 2. Case-insensitive / partial match
    search = cliente.lower()
    matches = []
    for d in clients_dir.iterdir():
        if d.is_dir() and d.name not in ignored:
            if search in d.name.lower():
                matches.append(d)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        names = [m.name for m in matches]
        raise ValueError(
            f"Ambiguous client name '{cliente}'. Found {len(matches)} matches: {', '.join(names)}. "
            f"Please be more specific."
        )
    else:
        raise ValueError(
            f"Client '{cliente}' not found. Use 'listar_clientes' to see available clients."
        )


# ==============================================================================
# SERVER RUN (called by main.py --mcp OR by __main__)
# ==============================================================================

def run_server():
    """
    Start the MCP stdio server with heartbeat monitoring.
    Called by main.py (EXE --mcp) or directly via python -m.
    """
    import threading
    import os

    def _heartbeat():
        while True:
            time.sleep(60)
            _logger.debug(f"💓 Heartbeat: Process alive (pid={os.getpid()})")

    t = threading.Thread(target=_heartbeat, daemon=True)
    t.start()

    _logger.info("Starting MCP stdio loop...")
    sys.stderr.write("[MCP] Foton server ready.\n")
    sys.stderr.flush()

    try:
        mcp.run()
    except Exception as e:
        _logger.critical(f"MCP loop crashed: {e}", exc_info=True)
        sys.stderr.write(f"[MCP] Critical Error: {e}\n")
        sys.exit(1)
    finally:
        _logger.info("MCP loop exited.")


if __name__ == "__main__":
    run_server()

