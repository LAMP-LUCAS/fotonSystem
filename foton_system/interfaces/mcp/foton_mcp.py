"""
FOTON MCP Server - Model Context Protocol Interface

This module exposes FotonSystem tools to AI assistants (Claude, Cursor, etc.)
via the MCP (Model Context Protocol).

ARCHITECTURE NOTES:
- Uses LAZY LOADING for all heavy dependencies (pandas, docx, etc.)
- BootstrapService is initialized once at startup
- Individual tools import their dependencies on-demand for instant startup
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
    # Ensure directories exist but DON'T load heavy config yet
    PathManager.ensure_directories()
except Exception as e:
    sys.stderr.write(f"[MCP] Warning: Could not initialize directories: {e}\n")

# --- MCP SERVER INITIALIZATION ---
mcp = FastMCP("Foton Architecture System")


# ==============================================================================
# HELPER FUNCTIONS (Lazy loaded dependencies)
# ==============================================================================

def _get_config():
    """Lazy-loads the Config singleton."""
    from foton_system.modules.shared.infrastructure.config.config import Config
    return Config()


def _get_client_path(client_name: str) -> Path:
    """
    Resolves and validates a client path.
    
    Args:
        client_name: Name of the client folder (e.g., "730_Residencia_Silva")
    
    Returns:
        Path to the client folder
    
    Raises:
        ValueError: If client not found
    """
    safe_name = Path(client_name).name  # Prevent directory traversal
    config = _get_config()
    base = config.base_pasta_clientes
    
    if not base or not base.exists():
        raise ValueError(f"Pasta de clientes não configurada ou não encontrada: {base}")
    
    client_path = base / safe_name
    
    if not client_path.exists():
        # Try to find partial match
        matches = [d for d in base.iterdir() if d.is_dir() and safe_name.lower() in d.name.lower()]
        if matches:
            client_path = matches[0]
        else:
            raise ValueError(f"Cliente '{safe_name}' não encontrado em {base}")
    
    return client_path


# ==============================================================================
# FINANCIAL TOOLS (POP-Audited)
# ==============================================================================

@mcp.tool()
def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """Registra uma entrada ou saída no fluxo de caixa (via POP Auditado)."""
    try:
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
        return f"❌ Módulo não encontrado: {e}"
    except Exception as e:
        return f"❌ Erro POP: {e}"


@mcp.tool()
def consultar_financeiro(cliente: str) -> str:
    """Retorna o resumo financeiro."""
    try:
        from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
        
        path = _get_client_path(cliente)
        fin_repo = CSVFinanceRepository()
        fin_service = FinanceService(fin_repo)
        summary = fin_service.get_summary(path)
        return f"💵 Saldo: R$ {summary['saldo']:.2f} (Entradas: {summary['total_entradas']:.2f})"
    except Exception as e:
        return f"❌ Erro: {e}"


# ==============================================================================
# DOCUMENT TOOLS (POP-Audited)
# ==============================================================================

@mcp.tool()
def listar_templates() -> str:
    """Lista templates disponíveis."""
    try:
        from foton_system.modules.documents.application.use_cases.document_service import DocumentService
        from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
        from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
        
        config = _get_config()
        config.templates_path.mkdir(parents=True, exist_ok=True)
        
        docx_adapter = PythonDocxAdapter()
        pptx_adapter = PythonPPTXAdapter()
        doc_service = DocumentService(docx_adapter, pptx_adapter)
        
        pptx = doc_service.list_templates("pptx")
        docx = doc_service.list_templates("docx")
        return f"PPTX: {pptx}\nDOCX: {docx}"
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
        from foton_system.core.memory.vector_store import VectorStore
        store = VectorStore()
        results = store.query(pergunta, n_results=4)
        
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        
        if not documents:
            return "📭 Nenhum conhecimento relevante encontrado na base."
        
        output = []
        for i, doc in enumerate(documents):
            meta = metadatas[i]
            source = meta.get('filename', 'Unknown')
            output.append(f"--- [Fonte: {source}] ---\n{doc}\n")
        
        return "\n".join(output)
    except ImportError as e:
        return f"❌ Módulo de memória não disponível: {e}"
    except Exception as e:
        return f"❌ Erro Memória: {e}"


# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    mcp.run()
