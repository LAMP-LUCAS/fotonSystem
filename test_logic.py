import sys
from pathlib import Path
import os

# Add the project root to sys.path
sys.path.append(r'C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\fotonSystem')

from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
from foton_system.modules.shared.infrastructure.config.config import Config

def test():
    config = Config()
    # Use .set() since properties are read-only
    config.set('caminho_pastaClientes', r'C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\CLIENTES')
    
    service = DocumentService(PythonDocxAdapter(), PythonPPTXAdapter(), config)
    
    # Path to a project deep inside
    data_path = Path(r'C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\CLIENTES\SIMONE_SEBASTIAO_TESTE\03_PROJETOS\APTO_502_ED-HENRY-MATISSE\502_DOC_CD_00_R00_INFO-APTO_502_ED-HENRY-MATISSE.md')
    
    print(f"--- Testando carregamento de contexto para: {data_path.name} ---")
    
    # DEBUG: Simulating the hierarchy loop
    current_dir = data_path.parent
    base_clients = config.base_pasta_clientes
    print(f"Base Clientes: {base_clients}")
    
    while current_dir != base_clients and current_dir != current_dir.parent:
        print(f"Verificando pasta: {current_dir.name}")
        info_files = list(current_dir.glob("*INFO*.md"))
        print(f"  Arquivos INFO encontrados: {[f.name for f in info_files]}")
        current_dir = current_dir.parent
    
    context = service._load_context_data(data_path)
    
    print("\nChaves finais no contexto (normalizadas):")
    for k in sorted(context.keys()):
        print(f"  {k}: {context[k]}")


if __name__ == "__main__":
    test()
