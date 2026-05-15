import sys
import yaml
from pathlib import Path

def validate_skill():
    print("--- Validando Estrutura de Skill ---")
    skill_path = Path(r'C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\.gemini\skills\foton-architecture\SKILL.md')
    if not skill_path.exists():
        print(f"❌ Erro: SKILL.md não encontrado em {skill_path}")
        return False
    
    try:
        content = skill_path.read_text(encoding='utf-8')
        if not content.startswith('---'):
            print("❌ Erro: SKILL.md não inicia com frontmatter YAML (---)")
            return False
        
        # Extrair e validar YAML
        parts = content.split('---')
        if len(parts) < 3:
            print("❌ Erro: SKILL.md frontmatter malformado")
            return False
            
        metadata = yaml.safe_load(parts[1])
        required = ['name', 'description']
        for field in required:
            if field not in metadata:
                print(f"❌ Erro: Campo '{field}' ausente no YAML")
                return False
        
        print(f"✅ Skill '{metadata['name']}' validada com sucesso.")
        return True
    except Exception as e:
        print(f"❌ Erro ao validar Skill: {e}")
        return False

def validate_mcp_source():
    print("\n--- Validando Código-Fonte do MCP ---")
    mcp_path = Path(r'C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\fotonSystem\foton_system\interfaces\mcp\foton_mcp.py')
    if not mcp_path.exists():
        print(f"❌ Erro: foton_mcp.py não encontrado em {mcp_path}")
        return False
    
    try:
        content = mcp_path.read_text(encoding='utf-8')
        required_tools = ['configurar_agente', 'gerar_documento', 'validar_template', 'listar_clientes']
        
        for t in required_tools:
            # Verifica se existe o decorador @mcp.tool() seguido da definição da função
            pattern = rf'@mcp\.tool\(.*?\)\s+def {t}'
            import re
            if not re.search(pattern, content, re.DOTALL):
                print(f"❌ Erro: Definição da ferramenta '{t}' não encontrada com padrão @mcp.tool")
                return False
        
        print(f"✅ Todas as {len(required_tools)} ferramentas essenciais foram encontradas e estão decoradas corretamente.")
        return True
    except Exception as e:
        print(f"❌ Erro ao validar fonte do MCP: {e}")
        return False

if __name__ == "__main__":
    s_ok = validate_skill()
    m_ok = validate_mcp_source()
    if s_ok and m_ok:
        print("\n🚀 Foton está pronto para operação AI-First!")
        sys.exit(0)
    else:
        print("\n🛑 Falha na validação de infraestrutura AI.")
        sys.exit(1)

