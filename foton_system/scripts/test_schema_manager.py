import sys
from pathlib import Path
import shutil

# Add project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from foton_system.scripts.manage_schema import SchemaManager

def test_manager():
    print("=== TESTANDO SCHEMA MANAGER ===")
    manager = SchemaManager()
    
    # 1. Add Test Variable
    print("\n1. Adicionando Variável de Teste...")
    key = "@TesteRename"
    manager.schema['variables'][key] = {
        "type": "string",
        "storage": "info_file",
        "description": "Teste",
        "default": None
    }
    manager._save_schema()
    
    # 2. Rename Test
    print("\n2. Renomeando...")
    new_key = "@TesteRenamed"
    manager.rename_variable(key, new_key)
    
    if new_key in manager.schema['variables'] and key not in manager.schema['variables']:
        print("✔ Schema atualizado corretamente.")
    else:
        print("✘ Falha no Schema.")

    # 3. Cleanup
    print("\n3. Limpeza...")
    if new_key in manager.schema['variables']:
        del manager.schema['variables'][new_key]
        manager._save_schema()
        print("✔ Limpeza concluída.")

if __name__ == "__main__":
    test_manager()
