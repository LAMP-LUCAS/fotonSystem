"""
FOTON MCP Server - Model Context Protocol Interface

This module exposes FotonSystem tools to AI assistants (Claude, Cursor, etc.)
via the MCP (Model Context Protocol).

ARCHITECTURE NOTES:
- Uses MCPServiceFactory for dependency injection (testable)
- Tools are thin wrappers that delegate to service layer
- Lazy loading via factory pattern for instant startup
"""

from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys

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

# --- LIGHTWEIGHT BOOTSTRAP (Fast startup) ---
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

try:
    PathManager.ensure_directories()
except Exception as e:
    sys.stderr.write(f"[MCP] Warning: Could not initialize directories: {e}\n")

# --- MCP SERVER INITIALIZATION ---
mcp = FastMCP("Foton Architecture System")


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
# FINANCIAL TOOLS (POP-Audited)
# ==============================================================================

@mcp.tool()
def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """Registra uma entrada ou saída no fluxo de caixa (via POP Auditado)."""
    try:
        # For auditing, still use OpFinanceEntry
        from foton_system.core.ops.op_finance_entry import OpFinanceEntry
        op = OpFinanceEntry(actor="Agent_MCP")
        result = op.execute(
            client_name=cliente,
            description=descricao,
            value=valor,
            type=tipo
        )
        return f"{result['message']} (Auditado)"
    except ImportError as e:
        # Fallback to service layer without auditing
        try:
            service = _get_factory().get_finance_service()
            result = service.register_entry(cliente, descricao, valor, tipo)
            if result.success:
                return f"💵 {result.message} (Saldo: R$ {result.balance:.2f})"
            return f"❌ {result.message}"
        except Exception as fallback_e:
            return f"❌ Erro: {fallback_e}"
    except Exception as e:
        return f"❌ Erro POP: {e}"


@mcp.tool()
def consultar_financeiro(cliente: str) -> str:
    """Retorna o resumo financeiro."""
    try:
        service = _get_factory().get_finance_service()
        result = service.get_summary(cliente)
        
        if result.success:
            return f"💵 Saldo: R$ {result.balance:.2f} (Entradas: {result.total_income:.2f})"
        return f"❌ {result.message}"
    except Exception as e:
        return f"❌ Erro: {e}"


# ==============================================================================
# DOCUMENT TOOLS (POP-Audited)
# ==============================================================================

@mcp.tool()
def listar_templates() -> str:
    """Lista templates disponíveis."""
    try:
        service = _get_factory().get_document_service()
        result = service.list_templates()
        
        if result.success and result.templates:
            pptx = result.templates.get('pptx', [])
            docx = result.templates.get('docx', [])
            return f"PPTX: {pptx}\nDOCX: {docx}"
        return f"❌ {result.message}"
    except Exception as e:
        return f"Erro: {e}"


@mcp.tool()
def gerar_documento(cliente: str, nome_template: str, dados_extras: dict = {}) -> str:
    """Gera um documento para o cliente (via POP Auditado)."""
    try:
        from foton_system.core.ops.op_doc_gen import OpGenerateDocument
        op = OpGenerateDocument(actor="Agent_MCP")
        result = op.execute(
            client_name=cliente,
            template_name=nome_template,
            extra_data=dados_extras
        )
        return f"✅ Documento Auditado: {result['output_path']}"
    except ImportError as e:
        return f"❌ Módulo não encontrado: {e}"
    except Exception as e:
        return f"❌ Erro POP: {e}"


# ==============================================================================
# KNOWLEDGE / RAG TOOLS
# ==============================================================================

@mcp.tool()
def consultar_conhecimento(pergunta: str) -> str:
    """
    Pesquisa na memória do escritório (Projetos passados, documentos).
    Use isso para entender contextos, decisões anteriores ou modelos.
    """
    try:
        service = _get_factory().get_knowledge_service()
        result = service.query(pergunta)
        
        if not result.success or not result.documents:
            return "📭 Nenhum conhecimento relevante encontrado na base."
        
        output = []
        for i, (doc, source) in enumerate(zip(result.documents, result.sources)):
            output.append(f"--- [Fonte: {source}] ---\n{doc}\n")
        
        return "\n".join(output)
    except Exception as e:
        return f"❌ Erro Memória: {e}"


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    mcp.run()
