# Script de Commit do FotonSystem
# Este script automatiza os commits das mudanças realizadas para a estratégia híbrida.

# 1. Caminhos e Infraestrutura
git add foton_system/modules/shared/infrastructure/services/path_manager.py
git add foton_system/modules/shared/infrastructure/bootstrap/bootstrap_service.py
git add foton_system/modules/shared/infrastructure/config/logger.py
git commit -m "feat: implementa PathManager e centraliza gestão de caminhos no AppData"

# 2. Build e Dependências
git add requirements.txt
git add foton_system/scripts/build.py
git add installer/foton_setup.iss
git add build_exe.py # Git vai registrar a deleção
git commit -m "refactor: otimiza build para estratégia híbrida e adiciona script Inno Setup"

# 3. Interfaces e UX
git add foton_system/interfaces/cli/main.py
git add run_foton.bat
git commit -m "feat: adiciona flags de sistema e mensagem de boas-vindas na CLI"

echo "✅ Commits sequenciais concluídos!"
