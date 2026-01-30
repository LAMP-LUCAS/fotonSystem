from mcp.server.fastmcp import FastMCP
from pathlib import Path
import sys
import traceback

# Adiciona raiz ao path para imports funcionarem
sys.path.append(str(Path(__file__).parents[3]))

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

# Serviços (Singleton-ish)
docx_adapter = PythonDocxAdapter()
pptx_adapter = PythonPPTXAdapter()
doc_service = DocumentService(docx_adapter, pptx_adapter)
fin_service = FinanceService()
sync_service = SyncService()

def _get_client_path(client_name: str) -> Path:
    """Valida e retorna o caminho seguro do cliente."""
    # Segurança: Impede path traversal
    safe_name = Path(client_name).name 
    base = Config().base_pasta_clientes
    client_path = base / safe_name
    
    if not client_path.exists():
        raise ValueError(f"Cliente '{safe_name}' não encontrado em {base}")
    
    return client_path

# --- FERRAMENTAS FINANCEIRAS ---

@mcp.tool()
def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """
    Registra uma entrada ou saída no fluxo de caixa do cliente.
    
    Args:
        cliente: Nome da pasta do cliente (ex: "PROJEFER")
        descricao: O que foi pago/recebido (ex: "Sinal Projeto")
        valor: Valor numérico (ex: 5000.00)
        tipo: "ENTRADA" ou "SAIDA"
    """
    try:
        path = _get_client_path(cliente)
        summary = fin_service.add_entry(path, descricao, valor, tipo)
        
        return (
            f"✅ **Registro Financeiro Sucesso**\n\n"
            f"Cliente: {cliente}\n"
            f"Movimento: {tipo} de R$ {valor:.2f} ({descricao})\n"
            f"---\n"
            f"💰 **Novo Saldo:** R$ {summary['saldo']:.2f}"
        )
    except Exception as e:
        return f"❌ Erro ao registrar: {str(e)}"

@mcp.tool()
def consultar_financeiro(cliente: str) -> str:
    """Retorna o resumo financeiro de um cliente."""
    try:
        path = _get_client_path(cliente)
        summary = fin_service.get_summary(path)
        
        return (
            f"📊 **Resumo Financeiro: {cliente}**\n\n"
            f"🟢 Entradas: R$ {summary['total_entradas']:.2f}\n"
            f"🔴 Saídas:   R$ {summary['total_saidas']:.2f}\n"
            f"💵 **Saldo:**  R$ {summary['saldo']:.2f}"
        )
    except Exception as e:
        return f"❌ Erro: {str(e)}"

# --- FERRAMENTAS DE DOCUMENTOS ---

@mcp.tool()
def listar_templates() -> str:
    """Lista todos os templates disponíveis para uso."""
    try:
        pptx = doc_service.list_templates("pptx")
        docx = doc_service.list_templates("docx")
        
        return (
            "## 📂 Templates Disponíveis\n\n"
            "### Apresentações (PPTX)\n" + 
            "\n".join([f"- {t}" for t in pptx]) + "\n\n"
            "### Documentos (DOCX)\n" + 
            "\n".join([f"- {t}" for t in docx])
        )
    except Exception as e:
        return f"Erro ao listar templates: {e}"

@mcp.tool()
def gerar_documento(cliente: str, nome_template: str, dados_extras: dict = {}) -> str:
    """
    Gera um documento (Proposta/Contrato) para o cliente.
    
    Args:
        cliente: Nome da pasta do cliente.
        nome_template: Nome exato do arquivo template (use listar_templates).
        dados_extras: Dicionário opcional para sobrescrever dados (ex: {"@valorProposta": 5000}).
    """
    try:
        client_path = _get_client_path(cliente)
        template_dir = Config().templates_path
        template_file = template_dir / nome_template
        
        if not template_file.exists():
            return f"❌ Template '{nome_template}' não encontrado."

        # Cria nome de saída
        output_name = f"GERADO_{nome_template}"
        output_path = client_path / output_name
        
        # Cria arquivo de dados temporário se necessário ou usa INFO
        # Por simplicidade do MCP, passamos o path do INFO-CLIENTE como "Data Path"
        # O DocumentService já sabe ler o contexto da pasta.
        # As 'dados_extras' injetados via memória não estão implementados no service base ainda,
        # então vamos criar um arquivo .json temporário para guiar a geração.
        
        temp_data_file = client_path / "temp_mcp_data.json"
        import json
        with open(temp_data_file, 'w', encoding='utf-8') as f:
            json.dump(dados_extras, f)
            
        doc_type = "pptx" if nome_template.endswith("pptx") else "docx"
        
        doc_service.generate_document(
            template_path=str(template_file),
            data_path=str(temp_data_file), # Usa o JSON temporário + Contexto Automático
            output_path=str(output_path),
            doc_type=doc_type
        )
        
        # Limpa temp
        if temp_data_file.exists():
            temp_data_file.unlink()

        return f"✅ **Documento Gerado!**\n\nLocal: {output_path}"

    except Exception as e:
        return f"❌ Falha na geração: {str(e)}\n{traceback.format_exc()}"

# --- FERRAMENTAS DE GESTÃO ---

@mcp.tool()
def sincronizar_dashboard() -> str:
    """Atualiza o Excel mestre com dados de todos os clientes."""
    try:
        df = sync_service.sync_dashboard()
        if df is None:
            return "Nenhum dado encontrado."
        return f"✅ Dashboard Sincronizado. {len(df)} projetos atualizados."
    except Exception as e:
        return f"Erro: {e}"

if __name__ == "__main__":
    # Inicia servidor MCP (Stdio por padrão)
    mcp.run()
