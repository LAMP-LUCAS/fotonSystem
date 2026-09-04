"""
FOTON MCP Server - Model Context Protocol Interface

This module exposes FotonSystem tools to AI assistants (Gemini, Claude, etc.)
via the MCP (Model Context Protocol) over stdio.

ARCHITECTURE NOTES:
- Tools are organized in modular domain routers (interfaces/mcp/routers/)
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
import logging
import logging.handlers

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
# SUB-ROUTERS IMPORT & REGISTRATION
# ==============================================================================
from foton_system.interfaces.mcp.routers.common import (
    _validate_str,
    _log_tool_call,
    _get_factory,
    _get_config,
    _validate_dados_extras,
    _resolve_client_path,
)
from foton_system.interfaces.mcp.routers.clients_router import (
    listar_clientes,
    cadastrar_cliente,
    ler_ficha_cliente,
    atualizar_ficha_cliente,
    listar_servicos_cliente,
    remover_cliente,
    restaurar_cliente,
    remover_servico,
    restaurar_servico,
    atualizar_servico,
    criar_estrutura_servico,
    preencher_codigos_faltantes,
    validar_codigos_servicos,
    corrigir_codigos_servicos,
    pipeline_novo_cliente,
    verificar_conformidade_clientes,
    corrigir_conformidade,
    register_clients_tools,
)
from foton_system.interfaces.mcp.routers.documents_router import (
    listar_templates,
    listar_documentos_cliente,
    gerar_documento,
    validar_template,
    listar_arquivos_dados,
    criar_arquivo_dados,
    historico_documentos,
    gerar_documentos_lote,
    pipeline_emitir_documento,
    register_documents_tools,
)
from foton_system.interfaces.mcp.routers.finance_router import (
    registrar_financeiro,
    consultar_financeiro,
    resumo_financeiro_geral,
    register_finance_tools,
)
from foton_system.interfaces.mcp.routers.rag_router import (
    consultar_conhecimento,
    indexar_conhecimento,
    diagnostico_conhecimento,
    register_rag_tools,
)
from foton_system.interfaces.mcp.routers.sync_router import (
    pipeline_sincronizacao,
    sincronizar_base,
    sincronizar_clientes,
    sincronizar_pastas_clientes,
    sincronizar_pastas_servicos,
    exportar_dados_clientes,
    exportar_dados_servicos,
    importar_dados_clientes,
    importar_dados_servicos,
    register_sync_tools,
)
from foton_system.interfaces.mcp.routers.system_router import (
    ping,
    info_sistema,
    consultar_cub,
    verificar_atualizacao,
    consultar_auditoria,
    configurar_agente,
    register_system_tools,
)

# Registra todos os sub-roteadores na instância FastMCP
register_system_tools(mcp)
register_clients_tools(mcp)
register_documents_tools(mcp)
register_finance_tools(mcp)
register_rag_tools(mcp)
register_sync_tools(mcp)

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
