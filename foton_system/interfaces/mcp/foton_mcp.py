from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys
import traceback

# Adiciona raiz ao path para imports funcionarem
sys.path.append(str(Path(__file__).parents[3]))

# --- BOOTSTRAP (CRÍTICO PARA MCP) ---
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
try:
    BootstrapService.initialize()
except Exception as e:
    sys.stderr.write(f"Erro fatal no Bootstrap MCP: {e}\n")

from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
from foton_system.modules.finance.finance_service import FinanceService
from foton_system.modules.sync.sync_service import SyncService

# Inicialização
logger = setup_logger()
mcp = FastMCP("Foton Architecture System")

# Serviços
docx_adapter = PythonDocxAdapter()
pptx_adapter = PythonPPTXAdapter()
doc_service = DocumentService(docx_adapter, pptx_adapter)
fin_service = FinanceService()
sync_service = SyncService()

def _get_client_path(client_name: str) -> Path:
    safe_name = Path(client_name).name 
    base = Config().base_pasta_clientes
    
    if not base or not base.exists():
        BootstrapService.initialize()
        base = Config().base_pasta_clientes
        
    client_path = base / safe_name
    
    if not client_path.exists():
        raise ValueError(f"Cliente '{safe_name}' não encontrado em {base}")
    
    return client_path

# --- FERRAMENTAS FINANCEIRAS ---

@mcp.tool()
def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """Registra uma entrada ou saída no fluxo de caixa."""
    try:
        path = _get_client_path(cliente)
        summary = fin_service.add_entry(path, descricao, valor, tipo)
        return f"✅ Sucesso. Novo Saldo: R$ {summary['saldo']:.2f}"
    except Exception as e:
        return f"❌ Erro: {e}"

@mcp.tool()
def consultar_financeiro(cliente: str) -> str:
    """Retorna o resumo financeiro."""
    try:
        path = _get_client_path(cliente)
        summary = fin_service.get_summary(path)
        return f"💵 Saldo: R$ {summary['saldo']:.2f} (Entradas: {summary['total_entradas']:.2f})"
    except Exception as e:
        return f"❌ Erro: {e}"

# --- FERRAMENTAS DE DOCUMENTOS ---

@mcp.tool()
def listar_templates() -> str:
    """Lista templates disponíveis."""
    try:
        Config().templates_path.mkdir(parents=True, exist_ok=True)
        pptx = doc_service.list_templates("pptx")
        docx = doc_service.list_templates("docx")
        return f"PPTX: {pptx}\nDOCX: {docx}"
    except Exception as e:
        return f"Erro: {e}"

@mcp.tool()
def gerar_documento(cliente: str, nome_template: str, dados_extras: dict = {}) -> str:
    """Gera um documento para o cliente."""
    try:
        client_path = _get_client_path(cliente)
        template_dir = Config().templates_path
        template_file = template_dir / nome_template
        
        output_name = f"GERADO_{nome_template}"
        output_path = client_path / output_name
        
        temp_data_file = client_path / "temp_mcp_data.json"
        import json
        with open(temp_data_file, 'w', encoding='utf-8') as f:
            json.dump(dados_extras, f)
            
        doc_type = "pptx" if nome_template.endswith("pptx") else "docx"
        
        doc_service.generate_document(
            template_path=str(template_file),
            data_path=str(temp_data_file), 
            output_path=str(output_path),
            doc_type=doc_type
        )
        if temp_data_file.exists(): temp_data_file.unlink()
        return f"✅ Documento criado em: {output_path}"
    except Exception as e:
        return f"❌ Erro: {e}"

@mcp.tool()
def sincronizar_dashboard() -> str:
    """Sincroniza Excel mestre."""
    try:
        sync_service.sync_dashboard()
        return "✅ Dashboard Sincronizado."
    except Exception as e:
        return f"Erro: {e}"

# --- FERRAMENTAS DE SISTEMA ---

@mcp.tool()
def atualizar_configuracao(chave: str, valor: str) -> str:
    """
    Atualiza uma configuração do sistema.
    Chaves: caminho_pastaClientes, caminho_templates, caminho_baseDados
    """
    try:
        config = Config()
        if "caminho" in chave:
            path_val = Path(valor)
            # Permite configurar mesmo se não existir (o usuário pode criar depois)
            # mas avisa
            if not path_val.exists() and not path_val.parent.exists():
                return f"⚠️ Aviso: O caminho '{valor}' parece inválido, mas foi salvo."
        
        config.set(chave, valor)
        config.save()
        return f"✅ Configuração '{chave}' atualizada para: {valor}"
    except Exception as e:
        return f"❌ Erro ao configurar: {e}"

if __name__ == "__main__":
    mcp.run()
