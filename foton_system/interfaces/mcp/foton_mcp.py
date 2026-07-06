"""
FOTON MCP Server - Model Context Protocol Interface

This module exposes FotonSystem tools to AI assistants (Gemini, Claude, etc.)
via the MCP (Model Context Protocol) over stdio.

ARCHITECTURE NOTES:
- Uses MCPServiceFactory for dependency injection (testable)
- Tools are thin wrappers that delegate to service layer
- Lazy loading via factory pattern for instant startup
- CRITICAL: No stdout output allowed outside mcp.run() — stdout is JSON-RPC
@story: STORY-026 @rule: RULE-DOC-2.2 @rule: RULE-DOC-2.3
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys
import os
import json
import subprocess
import time
import logging
import logging.handlers
import uuid
import functools
from typing import Optional

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

def _find_project_root() -> Path:
    """Retorna o diretório raiz do projeto (onde foton_system/ está)."""
    if getattr(sys, 'frozen', False):
        # Inside frozen EXE: look for the real project source on OneDrive
        candidates = [
            Path.home() / "OneDrive" / "LAMP_ARQUITETURA" / "fotonSystem",
            Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "LAMP_ARQUITETURA" / "fotonSystem",
            Path("C:\\Users") / os.environ.get("USERNAME", "Lucas") / "OneDrive" / "LAMP_ARQUITETURA" / "fotonSystem",
        ]
        for c in candidates:
            if (c / "foton_system" / "__init__.py").exists():
                return c
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "foton_system" / "__init__.py").exists():
            return parent
    return p.parents[3]

def _find_system_python() -> Path:
    """Retorna o caminho do Python do sistema (não o frozen) para subprocess RAG."""
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "python.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python312" / "python.exe",
        Path("C:\\Program Files") / "Python312" / "python.exe",
        Path("C:\\Python312") / "python.exe",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]

# --- LOGGING SETUP (file only, never stdout) ---
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

_logger = logging.getLogger("foton_mcp")

try:
    log_dir = PathManager.get_app_data_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "foton_mcp.log"

    # File handler with rotation — never attach a StreamHandler to stdout
    _handler = logging.handlers.RotatingFileHandler(
        str(log_file), maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
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
# HELPERS: Validation + Correlation ID
# ==============================================================================

_MAX_LENGTHS = {
    'nome': 200,
    'apelido': 100,
    'pergunta': 5000,
    'descricao': 500,
    'conteudo': 50000,
    'cod': 50,
    'nome_template': 200,
    'cliente': 200,
    'secao': 100,
    'pasta_alvo': 500,
    'nif': 20,
    'email': 200,
    'telefone': 30,
}

def _validate_str(value: str, field_name: str) -> None:
    """Validate string length. Raises ValueError if too long."""
    max_len = _MAX_LENGTHS.get(field_name)
    if max_len is not None and len(value) > max_len:
        raise ValueError(
            f"'{field_name}' exceeds max length ({max_len}): "
            f"got {len(value)} characters"
        )


def _log_tool_call(func):
    """Decorator: adds correlation ID + entry/exit logging + auto string validation + telemetry."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from foton_system.core.ops.operation_tracker import _write_operation_record
        from foton_system.core.ops.session_tracker import get_current_session, increment_operations
        from datetime import datetime, timezone

        req_id = str(uuid.uuid4())[:8]
        _logger.info(f"[req-{req_id}] Tool called: {func.__name__}")

        import inspect
        try:
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for param_name, param_value in bound.arguments.items():
                if isinstance(param_value, str) and param_value:
                    _validate_str(param_value, param_name)
        except ValueError as e:
            _logger.warning(f"[req-{req_id}] Validation failed: {e}")
            return f"❌ {e}"
        except TypeError:
            pass

        session = get_current_session()
        session_id = session.session_id if session else None
        interface = session.interface if session else "MCP"
        timestamp = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        sucesso = True
        metadados = {}

        try:
            result = func(*args, **kwargs)
            increment_operations()
            _logger.info(f"[req-{req_id}] Tool completed: {func.__name__}")
            return result
        except Exception:
            sucesso = False
            _logger.error(f"[req-{req_id}] Tool failed: {func.__name__}", exc_info=True)
            raise
        finally:
            elapsed = time.perf_counter() - start
            record = {
                "timestamp": timestamp,
                "session_id": session_id,
                "interface": interface,
                "operacao": func.__name__,
                "sucesso": sucesso,
                "duracao_ms": round(elapsed * 1000, 2),
                "metadados": metadados,
            }
            _write_operation_record(record)
    return wrapper


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
@_log_tool_call
def ping() -> str:
    """
    Verifies that the Foton MCP server is responsive.
    PROTOCOL: Use this as the very first tool call to ensure the link is active.
    """
    return f"🟢 FOTON MCP Online (pid={__import__('os').getpid()}, ts={int(time.time())})"


@mcp.tool()
@_log_tool_call
def info_sistema() -> str:
    """
    Provides a comprehensive diagnostic of the Foton system's environment.
    CONTEXT: Call this at the start of a session to understand folder paths, client counts, 
    template availability, and active business rules (like missing variable placeholders).
    Returns path configurations and module availability.
    """
    try:
        config = _get_config()
        clients_dir = config.base_pasta_clientes
        templates_dir = config.templates_path
        mode_str = "🧪 SANDBOX (Ambiente de Teste)" if PathManager.is_sandbox_active() else "🏗️ PRODUÇÃO"

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
            f"  🛠️ Modo:      {mode_str}\n"
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
    except OSError as e:
        _logger.error(f"info_sistema I/O error: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        return f"❌ Error retrieving system info: {e}"


# ==============================================================================
# CLIENT TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def listar_clientes(limite: int = 0, pagina: int = 1, itens_por_pagina: int = 20) -> str:
    """
    Lists all registered clients in the architecture firm.
    PROTOCOL: Always call this before performing any operation on a client you're not 100% sure exists.
    OUTPUT: Indicates if the client has a "Center of Truth" (📁 = has INFO file) and the count of sub-services.
    PARAMS: limite: Maximum number of clients to show (0 = no limit). pagina: Page number (default 1). itens_por_pagina: Items per page (default 20).
    """
    try:
        clients = _get_factory().get_client_service().list_clients()

        if not clients:
            return "📭 No clients registered yet."

        total = len(clients)

        if limite > 0:
            start = 0
            end = limite
            total_paginas = 1
        else:
            start = (pagina - 1) * itens_por_pagina
            end = start + itens_por_pagina
            total_paginas = max(1, (total + itens_por_pagina - 1) // itens_por_pagina)

        display = clients[start:end]

        if not display:
            return f"📋 Nenhum cliente na pagina {pagina}. Total: {total} cliente(s)."

        if limite > 0:
            header = f"📋 {total} client(s) found (showing {len(display)}):\n"
        else:
            header = f"📋 {total} client(s) found — Página {pagina} de {total_paginas}:\n"

        output = header
        for c in display:
            marker = "📁" if c['has_info'] else "📂"
            svc_txt = f", {c['service_count']} serviço(s)" if c['service_count'] else ""
            output += f"  {marker} {c['name']}{svc_txt}\n"

        return output
    except OSError as e:
        _logger.error(f"listar_clientes I/O error: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"listar_clientes failed: {e}", exc_info=True)
        return f"❌ Error listing clients: {e}"


@mcp.tool()
@_log_tool_call
def cadastrar_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:
    """
    Creates a new client folder and master record.
    SAFETY: Use 'pipeline_novo_cliente' instead for a safer, non-duplicate workflow.
    Logic: Creates standard folders (ADMINISTRATIVO, FINANCEIRO, PROJETOS) and initial INFO and FINANCEIRO files.
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name as _normalize
        normalized = _normalize(nome)
        from foton_system.core.ops.op_create_client import OpCreateClient
        op = OpCreateClient(actor="Agent_MCP")
        result = op.execute(
            name=normalized,
            alias=apelido if apelido else None,
            nif=nif,
            email=email,
            phone=telefone
        )
        return (
            f"✅ Cliente criado com sucesso (POP Auditado)\n"
            f"   Nome original: {nome}\n"
            f"   Nome normalizado: {normalized}\n"
            f"   Pasta: {result['client_path']}\n"
            f"   Código: {result['client_id']}"
        )
    except ValueError as e:
        return f"⚠️ Invalid data: {e}"
    except Exception as e:
        _logger.error(f"cadastrar_cliente failed: {e}", exc_info=True)
        return f"❌ Error creating client: {e}"


@mcp.tool()
@_log_tool_call
def ler_ficha_cliente(cliente: str) -> str:
    """
    Reads the 'Center of Truth' (INFO-*.md) for a client.
    CONTEXT: This is the mandatory first step before generating documents. It provides project metadata, 
    technical decisions, and meeting notes needed to understand the client's current state.
    RESOLUTION: Support fuzzy/partial client name matching.
    """
    try:
        result = _get_factory().get_client_service().read_client_info(cliente)
        return (
            f"📋 Ficha do Cliente: {cliente}\n"
            f"📄 Arquivo: {result['filename']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{result['content']}"
        )
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"ler_ficha_cliente failed: {e}", exc_info=True)
        return f"❌ Error reading info: {e}"


@mcp.tool()
@_log_tool_call
def atualizar_ficha_cliente(cliente: str, secao: str, conteudo: str,
                            operacao: str = "append", campo: str = "") -> str:
    """
    Updates a client's INFO file (Center of Truth) with various operations.
    SAFETY: Automatically creates a .bak backup before modifying.

    Operations:
      - "append" (default): appends content to a Markdown section
      - "replace": replaces entire section content
      - "remove": removes section entirely (conteudo ignored)
      - "field": updates @campo value via regex pattern

    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      secao: Markdown section header (e.g., 'Notas de Reunião') — used as @campo name for 'field' operation
      conteudo: Content to write
      operacao: Operation type (append/replace/remove/field)
      campo: Field name for 'field' operation (e.g., 'areaTotal')
    """
    try:
        backup_name = _get_factory().get_client_service().update_client_info(
            cliente, secao, conteudo, operacao=operacao, campo=campo
        )
        op_labels = {
            "append": "Ficha atualizada",
            "replace": "Seção substituída",
            "remove": "Seção removida",
            "field": "Campo atualizado",
        }
        label = op_labels.get(operacao, "Ficha atualizada")
        result = f"✅ {label}: {cliente}\n   Backup: {backup_name}"
        if operacao == "field" and campo:
            result += f"\n   Campo: @{campo}"
        return result
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"atualizar_ficha_cliente failed: {e}", exc_info=True)
        return f"❌ Error updating info: {e}"


@mcp.tool()
@_log_tool_call
def listar_servicos_cliente(cliente: str) -> str:
    """
    Lists sub-projects/services within a client's main folder.
    CONTEXT: Each service represents a distinct project (e.g., 'Reforma Apto 502').
    Ignores system folders like '01_ADMINISTRATIVO'.
    """
    try:
        services = _get_factory().get_client_service().list_services(cliente)

        if not services:
            return f"📭 No services found for client '{cliente}'."

        output = f"📋 {len(services)} serviço(s) de {cliente}:\n"
        for svc in services:
            subdirs_str = ', '.join(svc['subdirs'])
            output += f"  📂 {svc['name']} ({svc['file_count']} arquivo(s)) [{subdirs_str}]\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_servicos_cliente failed: {e}", exc_info=True)
        return f"❌ Error listing services: {e}"


@mcp.tool()
@_log_tool_call
def remover_cliente(cliente: str, confirmar: bool = False) -> str:
    """
    Removes a client by marking as DELETADO (soft delete).
    Use with caution — this is irreversible without restore.
    PARAMETERS:
      confirmar: Must be True to execute. Default False (safety).
    """
    if not confirmar:
        return "⚠️ Operação cancelada. Use confirmar=True para confirmar a remoção."
    try:
        svc = _get_factory().get_client_service()
        result = svc.soft_delete_client(cliente, confirmar=True)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except Exception as e:
        _logger.error(f"remover_cliente failed: {e}", exc_info=True)
        return f"❌ Error removing client: {e}"


@mcp.tool()
@_log_tool_call
def restaurar_cliente(cliente: str) -> str:
    """
    Restores a previously deleted client.
    Lists deleted clients if no name provided or if client is not found.
    """
    try:
        svc = _get_factory().get_client_service()
        result = svc.restore_client(cliente)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except ValueError as e:
        deleted = svc.get_deleted_clients()
        if deleted:
            nomes = "\n".join(f"  - {c['nome'] or c['alias']} ({c['alias']})" for c in deleted)
            return f"❌ {e}\n\nClientes deletados disponíveis:\n{nomes}"
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"restaurar_cliente failed: {e}", exc_info=True)
        return f"❌ Error restoring client: {e}"


@mcp.tool()
@_log_tool_call
def remover_servico(cliente: str, servico: str, confirmar: bool = False) -> str:
    """
    Removes a service by marking as DELETADO (soft delete).
    PARAMETERS:
      confirmar: Must be True to execute. Default False (safety).
    """
    if not confirmar:
        return "⚠️ Operação cancelada. Use confirmar=True para confirmar a remoção."
    try:
        svc = _get_factory().get_client_service()
        result = svc.soft_delete_service(cliente, servico, confirmar=True)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except Exception as e:
        _logger.error(f"remover_servico failed: {e}", exc_info=True)
        return f"❌ Error removing service: {e}"


@mcp.tool()
@_log_tool_call
def restaurar_servico(cliente: str, servico: str) -> str:
    """
    Restores a previously deleted service.
    """
    try:
        svc = _get_factory().get_client_service()
        result = svc.restore_service(cliente, servico)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except ValueError as e:
        deleted = svc.get_deleted_services()
        if deleted:
            nomes = "\n".join(
                f"  - {s['client_alias']}/{s['alias']} ({s['codigo'] or 'sem código'})"
                for s in deleted
            )
            return f"❌ {e}\n\nServiços deletados disponíveis:\n{nomes}"
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"restaurar_servico failed: {e}", exc_info=True)
        return f"❌ Error restoring service: {e}"


@mcp.tool()
@_log_tool_call
def atualizar_servico(cliente: str, servico: str, campo: str, valor) -> str:
    """
    Updates a specific field of a service.
    Valid fields: Modalidade, Ano, Demanda, AreaTotal, AreaCoberta, AreaDescoberta,
                  Detalhes, Estilo, Ambientes, ValorProposta, ValorContrato
    """
    try:
        svc = _get_factory().get_client_service()
        result = svc.update_service_info(cliente, servico, campo, valor)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except Exception as e:
        _logger.error(f"atualizar_servico failed: {e}", exc_info=True)
        return f"❌ Error updating service: {e}"


@mcp.tool()
@_log_tool_call
def criar_estrutura_servico(cliente: str, nome: str) -> str:
    """
    Creates the full folder structure for a new service under a client.
    Includes {DOC}, {ADM}, {OP} with configurable op phases.
    The service is automatically registered in the database with a unique CodServico.
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      nome: Service name
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name as _normalize
        normalized = _normalize(nome)
        config = _get_config()
        svc = _get_factory().get_client_service()
        client_path = svc.resolve_client_path(cliente)
        client_alias = client_path.name
        service_path = client_path / normalized
        if service_path.exists():
            return f"⚠️ Service '{normalized}' already exists under '{cliente}'."
        service_path.mkdir(parents=True)
        (service_path / config.folder_doc).mkdir()
        (service_path / config.folder_adm).mkdir()
        op_path = service_path / config.folder_op
        op_path.mkdir()
        for phase in config.folder_op_phases:
            (op_path / phase).mkdir()
        entry = svc.create_service_entry(client_alias, normalized)
        cod_servico = entry['CodServico']
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        template_path = PathManager.get_info_template_path()
        if template_path.exists():
            from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
            resolver = InfoPatternResolver(config.info_file_patterns['servico'])
            info_filename = resolver.resolve(
                codServico=cod_servico,
                aliasServico=normalized,
                versao="00",
                revisao="00"
            )
            import shutil
            shutil.copy(template_path, service_path / info_filename)
        return (
            f"✅ Estrutura de serviço criada: '{normalized}' em '{cliente}'\n"
            f"   📁 {config.folder_doc}/\n"
            f"   📁 {config.folder_adm}/\n"
            f"   📁 {config.folder_op}/ ({', '.join(config.folder_op_phases)})\n"
            f"   🆔 Código do serviço: {cod_servico}"
        )
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"criar_estrutura_servico failed: {e}", exc_info=True)
        return f"❌ Error creating service structure: {e}"


# ==============================================================================
# FINANCIAL TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """
    Records a financial entry (income/expense) in the client's ledger.
    TYPES: 'ENTRADA' (credit) or 'SAIDA' (debit).
    Value: Always pass a positive float.
    """
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
    except ValueError as e:
        return f"❌ Invalid data: {e}"
    except OSError as e:
        _logger.error(f"registrar_financeiro I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"registrar_financeiro failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def consultar_financeiro(cliente: str) -> str:
    """
    Returns the financial balance and transaction summary for a specific client.
    """
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
    except ValueError as e:
        return f"❌ Invalid client: {e}"
    except OSError as e:
        _logger.error(f"consultar_financeiro I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"consultar_financeiro failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def resumo_financeiro_geral() -> str:
    """
    Firm-wide financial dashboard. 
    CONTEXT: Use this for high-level business intelligence to identify profitable clients or cash-flow issues.
    """
    try:
        results = _get_factory().get_finance_service().get_firm_summary()

        if not results:
            return "📭 No financial data found."

        total_income = sum(r['income'] for r in results)
        total_expense = sum(r['expense'] for r in results)

        output = f"📊 Dashboard Financeiro ({len(results)} clientes):\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for r in results:
            emoji = "🟢" if r['balance'] >= 0 else "🔴"
            output += f"  {emoji} {r['name']}: R$ {r['balance']:,.2f} (E: {r['income']:,.2f} | S: {r['expense']:,.2f})\n"

        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        total_balance = total_income - total_expense
        output += (
            f"  TOTAL: R$ {total_balance:,.2f} "
            f"(Rec: R$ {total_income:,.2f} | Desp: R$ {total_expense:,.2f})"
        )
        return output
    except OSError as e:
        _logger.error(f"resumo_financeiro_geral I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"resumo_financeiro_geral failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def pipeline_sincronizacao(direcao: str = "bidir", dry_run: bool = True) -> str:
    """
    Unified sync pipeline for Clients and Services.

    DIRECTIONS:
    - "pastas_to_db": Discover new folders -> add to database
    - "db_to_pastas": Ensure database entries have folders
    - "bidir": Both directions (default)

    PARAMETERS:
      dry_run: If True, only detect differences without applying (default True)

    Returns a consolidated report with counts and errors.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao=direcao, dry_run=dry_run)
        return report.resumo()
    except Exception as e:
        _logger.error(f"pipeline_sincronizacao failed: {e}", exc_info=True)
        return f"❌ Error running sync pipeline: {e}"


# ==============================================================================
# DOCUMENT TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def listar_templates(categoria: str = "") -> str:
    """
    Lists all available document templates (DOCX for contracts, PPTX for proposals).
    PROTOCOL: Show this to the user to let them choose the document type they want to generate.
    PARAMETERS:
      categoria: Optional category filter (e.g., 'proposta', 'contrato', 'administrativo')
    """
    try:
        result = _get_factory().get_document_service().list_templates()
        if not result.success:
            return f"❌ {result.message}"

        templates = result.templates or {}
        pptx = templates.get('pptx', [])
        docx = templates.get('docx', [])

        def format_template(t):
            desc = f" — {t.description}" if t.description else ""
            return f"{t.filename}{desc}"

        if categoria:
            pptx = [t for t in pptx if t.category == categoria]
            docx = [t for t in docx if t.category == categoria]

        output = "📄 Templates disponíveis:\n"
        if pptx:
            output += f"\n🟦 PPTX ({len(pptx)}):\n"
            for t in sorted(pptx, key=lambda x: x.filename):
                output += f"  • {format_template(t)}\n"
        if docx:
            output += f"\n🟩 DOCX ({len(docx)}):\n"
            for t in sorted(docx, key=lambda x: x.filename):
                output += f"  • {format_template(t)}\n"

        if not pptx and not docx:
            return "📭 No templates found."

        return output
    except OSError as e:
        _logger.error(f"listar_templates I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"listar_templates failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def listar_documentos_cliente(cliente: str, servico: str = "") -> str:
    """
    Lists existing files for a client or specific service.
    CONTEXT: Use this to check if a document was already generated before creating a duplicate.
    """
    try:
        config = _get_config()
        client_path = _resolve_client_path(config.base_pasta_clientes, cliente, config)

        safe_servico = Path(servico).name if servico else ""
        target = client_path / safe_servico if safe_servico else client_path

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
            return f"📭 No files found."

        total = sum(len(v) for v in files_by_folder.values())
        output = f"📂 {total} arquivo(s) em {target.name}:\n"

        for folder, files in sorted(files_by_folder.items()):
            output += f"\n  📁 {folder}/\n"
            for fname in files:
                output += f"    • {fname}\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_documentos_cliente failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def gerar_documento(cliente: str, nome_template: str, dados_extras: Optional[dict] = None) -> str:
    """
    Merging Engine: Template + Client Data = Generated Document.
    PROTOCOL: 
    1. Always run 'validar_template' first.
    2. Provide 'dados_extras' for variables not found in the INFO files.
    3. The file is saved with prefix 'GERADO_' in the client's folder.
    CASE-INSENSITIVITY: Variables are matched regardless of casing (@CLIENTE == @cliente).
    """
    try:
        dados_extras = dados_extras or {}
        _validate_dados_extras(dados_extras)
        from foton_system.core.ops.op_doc_gen import OpGenerateDocument
        op = OpGenerateDocument(actor="Agent_MCP")
        result = op.execute(
            client_id=cliente,
            client_name=cliente,
            template_name=nome_template,
            extra_data=dados_extras
        )
        return (
            f"✅ Documento Gerado (POP Auditado)\n"
            f"   Arquivo: {result['output_path']}"
        )
    except ValueError as e:
        return f"❌ Invalid dados_extras: {e}"
    except Exception as e:
        _logger.error(f"gerar_documento failed: {e}", exc_info=True)
        return f"❌ Erro POP: {e}"


@mcp.tool()
@_log_tool_call
def validar_template(cliente: str, nome_template: str, arquivo_dados: str = "") -> str:
    """
    Pre-flight validation: Checks if the INFO files provide all variables required by the template.
    Returns categorized report with resolved, missing, none_values and formulas.
    PROTOCOL: Mandatory check before calling 'gerar_documento'.
    AGNOSTICISM: Searches the entire folder hierarchy for information.
    """
    try:
        config = _get_config()
        factory = _get_factory()

        svc = factory.get_client_service()
        client_path = svc.resolve_client_path(cliente)

        safe_name = Path(nome_template).name
        template_path = config.templates_path / safe_name
        if not template_path.exists():
            return f"❌ Template not found: {safe_name}"

        doc_type = template_path.suffix.lstrip('.').lower()
        if arquivo_dados:
            data_path = client_path / arquivo_dados
        else:
            md_files = list(client_path.glob('*INFO*.md')) + list(client_path.glob('*.md'))
            if not md_files:
                return f"⚠️ No data files (.md) found in {client_path.name}"
            data_path = md_files[0]

        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        doc_service = MCPServiceFactory.get_instance().get_document_service()
        report = doc_service.validate_template_keys(str(template_path), str(data_path), doc_type)

        resolved = report.get("resolved", [])
        missing = report.get("missing", [])
        none_values = report.get("none_values", [])
        formulas = report.get("formulas", [])

        output = f"📋 Relatório de Pré-validação — '{nome_template}'\n"

        if resolved:
            output += f"\n✅ Resolvidas ({len(resolved)}):\n"
            for r in resolved[:20]:
                output += f"   {r['key']} → {r['value']}\n"
            if len(resolved) > 20:
                output += f"   ... e mais {len(resolved) - 20}\n"
        else:
            output += "\n⚠️ Nenhuma variável resolvida\n"

        if missing:
            output += f"\n❌ Não encontradas ({len(missing)}):\n"
            for k in missing:
                output += f"   {k}\n"

        if none_values:
            output += f"\n⚠️ Valores inválidos (None/---/vazio) ({len(none_values)}):\n"
            for k in none_values:
                output += f"   {k}\n"

        if formulas:
            output += f"\n🧮 Fórmulas validadas ({len(formulas)}):\n"
            for f in formulas:
                status_icon = "✅" if f.get("status") == "ok" else "❌"
                output += f"   {status_icon} {f['expression']} = {f['result']}\n"

        if not missing and not none_values:
            output += f"\n✅ Todos os placeholders verificados — template pronto para geração."

        return output
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Validation error: {e}"


# ==============================================================================
# DATA FILE TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def listar_arquivos_dados(cliente: str) -> str:
    """
    Lists data files (.md, .txt) available for a client.
    CONTEXT: These files contain key-value pairs used during document generation.
    """
    try:
        client_path = _get_factory().get_client_service().resolve_client_path(cliente)
        files = _get_factory().get_document_service().list_client_data_files(str(client_path))
        if not files:
            return f"📭 No data files found for '{cliente}'."
        output = f"📄 {len(files)} data file(s) for {cliente}:\n"
        for f in files:
            output += f"  • {Path(f).name}\n"
        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_arquivos_dados failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def criar_arquivo_dados(cliente: str, cod: str, descricao: str = "PROPOSTA") -> str:
    """
    Creates a custom data file for a client using the centralized template.
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      cod: Document code (e.g., 'ABC123')
      descricao: Description/short name (default 'PROPOSTA')
    """
    try:
        client_path = _get_factory().get_client_service().resolve_client_path(cliente)
        result = _get_factory().get_document_service().create_custom_data_file(
            str(client_path), cod, desc=descricao
        )
        if result:
            return f"✅ Data file created: {Path(result).name}"
        return "❌ Failed to create data file."
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"criar_arquivo_dados failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


# ==============================================================================
# HISTORY TOOLS (STORY-024)
# ==============================================================================

@mcp.tool()
@_log_tool_call
def historico_documentos(cliente: str, limite: int = 10) -> str:
    """
    Lists the version history of generated documents for a client.
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      limite: Maximum number of entries to show (default 10)
    CONTEXT: Returns JSONL-based history with versioning info.
    """
    try:
        factory = _get_factory()
        client_path = factory.get_client_service().resolve_client_path(cliente)
        doc_service = factory.get_document_service()
        entries = doc_service.get_history(client_path, limit=limite)

        if not entries:
            return f"📭 Nenhum histórico encontrado para '{cliente}'."

        total = len(entries)
        output = f"📜 Histórico de Documentos — '{cliente}' ({total} registro(s)):\n"
        for i, e in enumerate(entries, 1):
            status_icon = "✅" if e.get('status') == 'sucesso' else "❌"
            versao = e.get('versao', 1)
            versao_anterior = e.get('versao_anterior')
            ver_info = f"v{versao}"
            if versao_anterior:
                ver_info += f" (anterior: {versao_anterior})"
            output += (
                f"\n{status_icon} "
                f"[{e.get('data_hora', '?')}] "
                f"{e.get('nome_arquivo', '?')} "
                f"({ver_info})"
            )
        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"historico_documentos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def gerar_documentos_lote(cliente: str, documentos: list) -> str:
    """
    Generates multiple documents in a single batch operation.
    Phase 1: validates all templates. Phase 2: generates all (only if all pass).
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      documentos: List of dicts, each with {template: str, dados_extras?: dict, tipo?: str}
    CONTEXT: Use this to generate proposta + contrato + anexo simultaneously.
    """
    try:
        factory = _get_factory()
        doc_service = factory.get_document_service()

        normalized = []
        for doc in documentos:
            if not isinstance(doc, dict):
                return f"❌ Each item in 'documentos' must be a dict with 'template'."
            template_name = doc.get("template")
            if not template_name:
                return f"❌ Each item in 'documentos' must have a 'template' field."
            extra_data = doc.get("dados_extras", {})
            if not isinstance(extra_data, dict):
                extra_data = {}
            normalized.append({
                "template_name": template_name,
                "extra_data": extra_data,
            })

        result = doc_service.generate_batch(cliente, normalized)

        if not result.success:
            return f"❌ Lote falhou: {result.message}"

        batch = result.batch_result or {}
        items = batch.get("items", [])
        status = batch.get("status", "UNKNOWN")

        if status == "BATCH_BLOCKED":
            output = f"❌ Lote BLOQUEADO — pré-validação falhou:\n"
            for item in items:
                icon = "🔴" if item["status"] == "bloqueado" else "🟡"
                output += f"  {icon} {item['template_name']} → {item['status']}\n"
            output += "\nCorrija os templates com falha e tente novamente."
            return output

        output = f"✅ Lote concluído ({len(items)} documento(s)):\n"
        for item in items:
            icon = "✅" if item["status"] == "sucesso" else "❌"
            output += f"  {icon} {item['template_name']} → {item['output_path']}\n"
        return output

    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"gerar_documentos_lote failed: {e}", exc_info=True)
        return f"❌ Erro: {e}"


# ==============================================================================
# KNOWLEDGE / RAG TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def consultar_conhecimento(pergunta: str, cliente: str = "", tipo_doc: str = "") -> str:
    """
    Semantic search (RAG) across past projects and reference materials.
    PARAMETERS:
      pergunta: Question in natural language
      cliente: Optional — filter by client folder name
      tipo_doc: Optional — filter by document type (INFO, dados, proposta, etc.)
    CONTEXT: Use this to find 'How did we solve X for client Y before?' or 'What are the rules for Z?'.
    """
    try:
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Agent_MCP")
        kwargs = {"query": pergunta}
        if cliente.strip():
            kwargs["cliente"] = cliente.strip()
        if tipo_doc.strip():
            kwargs["tipo_doc"] = tipo_doc.strip()
        data = op.execute(**kwargs)

        if data.get("status") == "EMPTY":
            return "📭 Nenhum conhecimento relevante encontrado."

        output = []
        for i, r in enumerate(data.get("results", []), 1):
            ctx = r.get("contexto", r["document"])
            output.append(
                f"--- [{i}] Fonte: {r['source']} (Score: {r['score']:.0%}) ---\n"
                f"{ctx}\n"
            )

        return "\n".join(output)
    except ValueError as e:
        return f"❌ Invalid parameters: {e}"
    except Exception as e:
        return f"❌ Knowledge query error: {e}"


@mcp.tool()
@_log_tool_call
def indexar_conhecimento(pasta_alvo: str = "", cliente: str = "") -> str:
    """
    Updates the semantic database by indexing documents.
    PARAMETERS:
      pasta_alvo: Optional — specific folder path to index
      cliente: Optional — client name for selective indexing (only this client's folder)
    PROTOCOL: Run this after adding many new files or manually updating INFO files to ensure RAG stays current.
    """
    try:
        from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
        op = OpIndexKnowledge(actor="Agent_MCP")
        kwargs = {}
        if cliente.strip():
            kwargs["cliente"] = cliente.strip()
        elif pasta_alvo.strip():
            kwargs["target_path"] = pasta_alvo.strip()
        result = op.execute(**kwargs)
        return f"✅ Knowledge base updated! Files: {result['files_scanned']}, Chunks: {result['chunks_created']}"
    except ValueError as e:
        return f"❌ Invalid parameters: {e}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Indexing error: {e}"


@mcp.tool()
@_log_tool_call
def diagnostico_conhecimento() -> str:
    """
    Diagnostic of the semantic knowledge base.
    Returns: total chunks, circuit breaker status (CLOSED/OPEN), last indexation timestamp.
    """
    try:
        from foton_system.core.memory.vector_store import VectorStoreManager
        store = VectorStoreManager()
        diag = store.diagnostic()

        stores = diag.get("stores", {})
        if not stores:
            return "📊 **RAG Knowledge Base Diagnostic**\n  Nenhuma coleção encontrada."

        mode = diag.get("mode", "")
        if mode and mode != "minilm":
            lines = [f"📊 **RAG Knowledge Base Diagnostic** (mode: {mode})"]
        else:
            lines = ["📊 **RAG Knowledge Base Diagnostic**"]

        for tag, info in stores.items():
            model_name = info.get("model_name", tag)
            collection_name = info.get("collection_name", "N/A")
            dims = info.get("dimensions", "")
            dims_str = f"{dims}d" if dims else "N/A"
            lines.append(
                f"  • **{tag}**: {collection_name}"
                f" ({model_name}, {dims_str})"
                f" — {info['total_chunks']} chunks,"
                f" CB: {info['circuit_breaker_status']},"
                f" last: {info['ultima_indexacao']}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Diagnostic error: {e}"


# ==============================================================================
# MAINTENANCE TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def sincronizar_base() -> str:
    """
    Syncs the Excel Master Dashboard with the filesystem.
    Delegates to pipeline_sincronizacao (bidir) for unified sync.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="bidir", dry_run=False)
        return f"✅ Dashboard synchronized! {report.resumo()}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Sync error: {e}"


@mcp.tool()
@_log_tool_call
def sincronizar_clientes() -> str:
    """
    Discovers new client/service folders and adds them to the Excel database.
    Delegates to pipeline_sincronizacao (pastas_to_db) for unified sync.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="pastas_to_db", dry_run=False)
        return f"✅ Client & service databases synchronized! {report.resumo()}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Client sync error: {e}"


@mcp.tool()
@_log_tool_call
def sincronizar_pastas_clientes() -> str:
    """
    Creates client folders for entries in the database that are missing folders.
    Delegates to pipeline_sincronizacao (db_to_pastas) for unified sync.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="db_to_pastas", dry_run=False)
        return f"✅ Client folders synchronized. {report.resumo()}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def sincronizar_pastas_servicos(cliente: str = "") -> str:
    """
    Creates service folders for entries in the database that are missing folders.
    Delegates to pipeline_sincronizacao (db_to_pastas) for unified sync.
    PARAMETERS:
      cliente: Optional client alias to filter (default: all clients)
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="db_to_pastas", dry_run=False)
        return f"✅ Service folders synchronized. {report.resumo()}"
    except ValueError as e:
        return f"❌ Invalid client name: {e}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def exportar_dados_clientes() -> str:
    """
    Exports client data from the database to MD files in client folders.
    """
    try:
        result = _get_factory().get_client_service().export_client_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def exportar_dados_servicos() -> str:
    """
    Exports service data from the database to MD files in service folders.
    """
    try:
        result = _get_factory().get_client_service().export_service_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def importar_dados_clientes() -> str:
    """
    Importa dados de clientes dos arquivos INFO de volta para o banco de dados.
    """
    try:
        result = _get_factory().get_client_service().import_client_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def importar_dados_servicos() -> str:
    """
    Imports service data from MD files back into the database.
    """
    try:
        result = _get_factory().get_client_service().import_service_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def preencher_codigos_faltantes() -> str:
    """
    Preenche automaticamente CodCliente e CodServico faltantes (NaN) no banco de dados.
    Gera códigos únicos para todos os registros que ainda não possuem código.
    """
    try:
        result = _get_factory().get_client_service().fill_missing_codes()
        clientes = result['clientes_alterados']
        servicos = result['servicos_alterados']
        parts = []
        if clientes:
            parts.append(f"{clientes} cliente(s)")
        if servicos:
            parts.append(f"{servicos} serviço(s)")
        if not parts:
            return "✅ Nenhum código faltante encontrado. Todos os registros já possuem código."
        return f"✅ Códigos preenchidos para {' e '.join(parts)}."
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def validar_codigos_servicos() -> str:
    """
    Valida todos os códigos de serviço (CodServico) no banco de dados.
    Verifica códigos ausentes, placeholders, formato inválido e duplicatas.
    Sempre executa preencher_codigos_faltantes primeiro.
    """
    try:
        svc = _get_factory().get_client_service()
        svc.fill_missing_codes()
        issues = svc.validate_service_codes()
        if not issues:
            return "✅ Todos os códigos de serviço são válidos."
        lines = [f"📋 {len(issues)} código(s) de serviço com problema:\n"]
        for i, iss in enumerate(issues, 1):
            svc_label = f"{iss['client_alias']}/{iss['service_alias']}"
            lines.append(f"  [{i}] [{iss['issue'].upper()}] {svc_label}")
            lines.append(f"      Código atual: '{iss['cod_servico']}'")
            lines.append(f"      💡 Sugestão: {iss['suggested_fix']}")
            lines.append("")
        return "\n".join(lines)
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"validar_codigos_servicos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.tool()
@_log_tool_call
def corrigir_codigos_servicos() -> str:
    """
    Corrige automaticamente todos os códigos de serviço inválidos no banco de dados.
    Gera novos códigos únicos para placeholders, formatos inválidos e duplicatas.
    """
    try:
        svc = _get_factory().get_client_service()
        svc.fill_missing_codes()
        issues = svc.validate_service_codes()
        if not issues:
            return "✅ Todos os códigos de serviço já são válidos. Nenhuma correção necessária."
        fixed = svc.fix_service_codes(issues)
        return f"✅ {fixed} código(s) de serviço corrigido(s) automaticamente."
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"corrigir_codigos_servicos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


# ==============================================================================
# PIPELINES (AI RECOMMENDED FLOWS)
# ==============================================================================

@mcp.tool()
@_log_tool_call
def configurar_agente() -> str:
    """
    Automates the formal installation of the Foton AI Skill into the Gemini CLI.
    Copies the SKILL.md from the repository to the local .gemini/skills folder.
    AI RECOMMENDED: Run this to enable specialized architectural reasoning from the repository source.
    """
    try:
        config = _get_config()
        # Source is in the repository
        # Assume foton_system is inside the repo root
        repo_root = Path(__file__).resolve().parents[3]
        repo_skill_file = repo_root / "skills" / "foton-architecture" / "SKILL.md"
        
        if not repo_skill_file.exists():
             return f"❌ Erro: Arquivo de origem não encontrado no repositório: {repo_skill_file}"

        # Destination is the official workspace skill path
        workspace_root = config.base_pasta_clientes.parent
        skill_dir = workspace_root / ".gemini" / "skills" / "foton-architecture"
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        target_skill_file = skill_dir / "SKILL.md"
        
        # Copy content from repo to local installation
        content = repo_skill_file.read_text(encoding="utf-8")
        target_skill_file.write_text(content, encoding="utf-8")
        
        return (
            f"✅ Foton Skill instalada a partir do repositório!\n"
            f"   Origem: {repo_skill_file}\n"
            f"   Destino: {target_skill_file}\n"
            f"   ⚠️ IMPORTANTE: Execute o comando '/skills reload' no chat para ativar a expertise."
        )
    except (OSError, PermissionError) as e:
        _logger.error(f"configurar_agente file error: {e}", exc_info=True)
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"configurar_agente failed: {e}", exc_info=True)
        return f"❌ Erro ao configurar skill: {e}"




@mcp.tool()
@_log_tool_call
def pipeline_novo_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:

    """
    SAFE workflow to create a client while checking for duplicates.
    AI RECOMMENDED: Always prefer this over 'cadastrar_cliente'.
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name as _normalize
        normalized = _normalize(nome)
        factory = _get_factory()
        svc = factory.get_client_service()

        try:
            exists = svc.resolve_client_path(normalized)
            return f"⚠️ PIPELINE STOPPED — A similar client already exists: {exists.name}. Use 'ler_ficha_cliente' to verify."
        except ValueError:
            pass

        if nif:
            existing = svc.list_clients()
            base = _get_config().base_pasta_clientes
            from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
            info_glob = PathManager.get_info_glob("cliente")
            for c in existing:
                info_paths = list((base / c['name']).glob(info_glob))
                info_path = info_paths[0] if info_paths else None
                if info_path and info_path.exists():
                    try:
                        for line in info_path.read_text(encoding='utf-8').splitlines():
                            if line.strip().lower().startswith('@nif'):
                                stored = line.split(';', 1)[-1].strip()
                                if stored == nif:
                                    return f"⚠️ PIPELINE STOPPED — NIF '{nif}' already registered under '{c['name']}'."
                    except Exception:
                        continue

        result = cadastrar_cliente(nome, apelido, nif, email, telefone)
        return result
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Pipeline error: {e}"


@mcp.tool()
@_log_tool_call
def pipeline_emitir_documento(cliente: str, nome_template: str, dados_extras: Optional[dict] = None) -> str:
    """
    SAFE pre-flight report before document generation.
    AI RECOMMENDED: Always run this before 'gerar_documento' to provide a summary to the user.
    Logic: Validates variables AND checks for existing generated files to avoid duplicates.
    """
    try:
        dados_extras = dados_extras or {}
        _validate_dados_extras(dados_extras)
        svc = _get_factory().get_client_service()
        client_path = svc.resolve_client_path(cliente)

        output = f"📋 PRE-FLIGHT — Document Generation\n"
        output += f"   Client:  {client_path.name}\n"
        output += f"   Template: {nome_template}\n\n"

        validation = validar_template(cliente, nome_template)
        output += f"{validation}\n"

        template_base = Path(nome_template).stem
        existing = list(client_path.rglob(f"GERADO_*{template_base}*"))
        if existing:
            output += f"\n⚠️ DUPLICATES: {len(existing)} similar file(s) found in {client_path.name}.\n"
        else:
            output += "✅ DUPLICATES: No similar files found.\n"

        output += "\nPROTOCOL: Review this report and confirm with the user before calling 'gerar_documento'."
        return output
    except ValueError as e:
        return f"❌ Invalid dados_extras: {e}"
    except Exception as e:
        return f"❌ Pipeline error: {e}"


# ==============================================================================
# INFRASTRUCTURE TOOLS
# ==============================================================================

@mcp.tool()
@_log_tool_call
def consultar_cub() -> str:
    """
    Returns the current CUB (Custo Unitário Básico) reference month and download URL.
    CONTEXT: Used in document generation for construction cost estimates (@LinkCUB, @ReferenciaCUB).
    """
    try:
        from foton_system.modules.shared.infrastructure.services.cub_service import CubService
        ref = CubService.get_reference_label()
        url = CubService.get_dynamic_url()
        return (
            f"📊 CUB Reference\n"
            f"   Mês: {ref}\n"
            f"   URL: {url}\n"
            f"   Fonte: SINDUSCON-GO"
        )
    except (OSError, ConnectionError) as e:
        _logger.error(f"consultar_cub network error: {e}", exc_info=True)
        return f"❌ CUB connection error: {e}"
    except Exception as e:
        _logger.error(f"consultar_cub failed: {e}", exc_info=True)
        return f"❌ CUB error: {e}"


@mcp.tool()
@_log_tool_call
def verificar_atualizacao() -> str:
    """
    Checks GitHub for a newer version of the Foton System.
    PROTOCOL: Run periodically to ensure the system is up-to-date.
    """
    try:
        from foton_system.modules.shared.infrastructure.services.update_service import UpdateChecker
        from foton_system import __version__
        has_update, latest, url = UpdateChecker.check_for_updates()
        if has_update:
            return (
                f"🔄 Nova versão disponível!\n"
                f"   Atual:    v{__version__}\n"
                f"   Recente:  v{latest}\n"
                f"   URL:      {url}"
            )
        return f"✅ Sistema atualizado (v{__version__})"
    except (OSError, ConnectionError) as e:
        _logger.error(f"verificar_atualizacao network error: {e}", exc_info=True)
        return f"❌ Network error: {e}"
    except Exception as e:
        _logger.error(f"verificar_atualizacao failed: {e}", exc_info=True)
        return f"❌ Update check error: {e}"


@mcp.tool()
@_log_tool_call
def consultar_auditoria(limite: int = 10) -> str:
    """
    Shows the most recent audit events (POP operations).
    PARAMETERS:
      limite: Number of events to show (default 10)
    """
    try:
        from foton_system.core.ops.audit_logger import AuditLogger
        events = AuditLogger().get_recent_events(limit=limite)
        if not events:
            return "📭 No audit events found."

        output = f"📋 Últimos {len(events)} eventos de auditoria:\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for e in events:
            ts = e.get('timestamp', '?')
            op = e.get('op', '?')
            actor = e.get('actor', '?')
            client = e.get('client_id', '?')
            status = e.get('status', '?')
            output += f"  [{ts}] {op} by {actor} → {client} [{status}]\n"
        return output
    except ValueError as e:
        return f"❌ Invalid parameter: {e}"
    except OSError as e:
        _logger.error(f"consultar_auditoria I/O: {e}", exc_info=True)
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"consultar_auditoria failed: {e}", exc_info=True)
        return f"❌ Audit error: {e}"


@mcp.tool()
@_log_tool_call
def verificar_conformidade_clientes(modo: str = "check") -> str:
    """
    Audits client folders for naming and INFO file pattern compliance.
    PARAMETERS:
      modo: 'check' (default) — list non-conformant items
            'all' — list all items including previously accepted
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_conformance import ClientConformanceChecker
        config = _get_config()
        checker = ClientConformanceChecker(config)
        items = checker.check()

        if not items:
            return "✅ All clients conform to the configured patterns."

        lines = [f"📋 {len(items)} non-conformant item(s) found:\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"  [{i}] [{item.severity.upper()}] {item.tipo}")
            lines.append(f"      {item.description}")
            if item.suggested_fix:
                lines.append(f"      💡 Fix: {item.suggested_fix}")
            lines.append(f"      📁 {item.path}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        _logger.error(f"verificar_conformidade_clientes failed: {e}", exc_info=True)
        return f"❌ Conformance check error: {e}"


@mcp.tool()
@_log_tool_call
def corrigir_conformidade(item_id: str) -> str:
    """
    Applies the suggested fix for a specific non-conformant item.
    PARAMETERS:
      item_id: The item ID from verificar_conformidade_clientes output
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_conformance import ClientConformanceChecker
        config = _get_config()
        checker = ClientConformanceChecker(config)
        items = checker.check()

        target = next((i for i in items if i.item_id == item_id), None)
        if not target:
            return f"❌ Item '{item_id}' not found or already fixed."

        success = checker.auto_fix(target)
        if success:
            return f"✅ Fixed: {target.description}"
        return f"❌ Failed to fix: {target.description}"
    except Exception as e:
        _logger.error(f"corrigir_conformidade failed: {e}", exc_info=True)
        return f"❌ Fix error: {e}"


# ==============================================================================
# HELPER: dados_extras Validation
# ==============================================================================

_MAX_DADOS_EXTRAS_KEYS = 50

def _validate_dados_extras(dados_extras: dict) -> None:
    """Validates dados_extras schema. Raises ValueError on invalid data."""
    if not isinstance(dados_extras, dict):
        raise ValueError("dados_extras must be a dict")

    if len(dados_extras) > _MAX_DADOS_EXTRAS_KEYS:
        raise ValueError(
            f"dados_extras exceeds max keys ({_MAX_DADOS_EXTRAS_KEYS}): "
            f"got {len(dados_extras)} keys"
        )

    for k, v in dados_extras.items():
        if not isinstance(k, str):
            raise ValueError(f"dados_extras keys must be strings, got {type(k).__name__}")
        if not k.strip():
            raise ValueError("dados_extras keys cannot be empty")
        if isinstance(v, (dict, list)):
            raise ValueError(
                f"dados_extras values must be str/int/float, "
                f"got {type(v).__name__} for key '{k}'"
            )


# ==============================================================================
# HELPER: Internal Client Path Resolution
# ==============================================================================

def _resolve_client_path(clients_dir: Path, cliente: str, config) -> Path:
    """
    Internal proxy to ClientService.
    """
    svc = _get_factory().get_client_service()
    return svc.resolve_client_path(cliente)


# ==============================================================================
# MCP RESOURCES
# ==============================================================================

@mcp.resource("foton://clientes/{nome}/INFO")
def resource_cliente_info(nome: str) -> str:
    """Retorna o conteúdo do Centro de Verdade (INFO-*.md) de um cliente."""
    try:
        result = _get_factory().get_client_service().read_client_info(nome)
        return result['content']
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"resource_cliente_info failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.resource("foton://clientes/{nome}/servicos")
def resource_cliente_servicos(nome: str) -> str:
    """Retorna a lista de serviços de um cliente."""
    try:
        services = _get_factory().get_client_service().list_services(nome)
        if not services:
            return f"📭 No services found for client '{nome}'."
        output = f"📋 {len(services)} serviço(s) de {nome}:\n"
        for svc in services:
            subdirs_str = ', '.join(svc['subdirs'])
            output += f"  📂 {svc['name']} ({svc['file_count']} arquivo(s)) [{subdirs_str}]\n"
        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"resource_cliente_servicos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


@mcp.resource("foton://financeiro/resumo")
def resource_financeiro_resumo() -> str:
    """Retorna o dashboard financeiro geral do escritório."""
    try:
        client_list = _get_factory().get_finance_service().get_firm_summary()
        total_entradas = sum(c.get('income', 0) for c in client_list)
        total_saidas = sum(c.get('expense', 0) for c in client_list)
        saldo = total_entradas - total_saidas
        return (
            f"📊 Resumo Financeiro Geral\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  ✅ Entradas: R$ {total_entradas:,.2f}\n"
            f"  ❌ Saídas:   R$ {total_saidas:,.2f}\n"
            f"  {'🟢' if saldo >= 0 else '🔴'} Saldo:    R$ {saldo:,.2f}\n"
            f"  📁 Clientes: {len(client_list)}\n"
        )
    except Exception as e:
        _logger.error(f"resource_financeiro_resumo failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


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
