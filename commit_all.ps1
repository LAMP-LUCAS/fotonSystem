Set-Location "C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\ADM\lamp\fotonSystem"

# 1. Infrastructure & Utils
git add foton_system/modules/shared/infrastructure/utils/formatting.py
git add foton_system/modules/shared/infrastructure/services/cub_service.py
git commit -m "Feat: Implementação de Middlewares (Formatação e CUB)"

# 2. Finance Module
git add foton_system/modules/finance/
git commit -m "Feat: Módulo Financeiro (Fluxo de Caixa em CSV)"

# 3. Sync Module
git add foton_system/modules/sync/
git commit -m "Feat: Dashboard Sync (Sincronização com Excel)"

# 4. MCP, Interfaces & Deps
git add foton_system/interfaces/mcp/
git add foton_system/interfaces/cli/chat.py
git add foton_system/scripts/config_gui.py
git add requirements.txt
git commit -m "Feat: Servidor MCP, GUI de Configuração e ferramentas para Agentes"

# 5. Core Updates
git add foton_system/modules/documents/application/use_cases/document_service.py
git commit -m "Refactor: Atualização do DocumentService e Bootstrap para MCP"

# 6. Tests
git add tests/
git commit -m "Test: Suite de testes automatizados e correções de QA"

# 7. Documentation
git add SYSTEM_MANIFEST.md
git add LLM_CONTEXT.md
git commit -m "Docs: Manuais para LLMs e Contexto do Sistema"

# 8. Build/Packaging
git add build_exe.py
git commit -m "Build: Script de Empacotamento OneFile"

echo "--- Histórico de Commits Recentes ---"
git log --oneline -n 8
