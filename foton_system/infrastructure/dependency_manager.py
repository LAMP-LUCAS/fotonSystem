"""
DependencyManager - Gerenciador de Plugins e Dependências On-Demand.

Este módulo permite que o Foton System permaneça leve, instalando pacotes pesados
(como os de IA/RAG) apenas quando solicitados pelo usuário em um VENV isolado.
"""

import os
import sys
import subprocess
import venv
import logging
from pathlib import Path
from typing import List, Optional

from foton_system.modules.shared.infrastructure.services.path_manager import PathManager

logger = logging.getLogger(__name__)

class DependencyManager:
    """Gerencia ambientes virtuais para plugins pesados."""

    @staticmethod
    def get_plugin_env_path(plugin_name: str) -> Path:
        """Retorna o caminho do ambiente virtual para um plugin específico."""
        return PathManager.get_app_data_dir() / "plugins" / plugin_name

    @staticmethod
    def is_plugin_installed(plugin_name: str, test_module: str) -> bool:
        """Verifica se o plugin está instalado no ambiente isolado."""
        env_path = DependencyManager.get_plugin_env_path(plugin_name)
        if not env_path.exists():
            return False
        
        python_exe = DependencyManager._get_python_executable(env_path)
        try:
            # Tenta importar o módulo de teste usando o python do VENV
            subprocess.run(
                [str(python_exe), "-c", f"import {test_module}"],
                check=True,
                capture_output=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def install_plugin(plugin_name: str, packages: List[str]) -> bool:
        """Cria um VENV e instala os pacotes solicitados."""
        env_path = DependencyManager.get_plugin_env_path(plugin_name)
        env_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n📦 Instalando Plugin: {plugin_name}")
        print(f"📂 Destino: {env_path}")
        print(f"⏳ Isso pode levar alguns minutos (download de {len(packages)} pacotes)...")

        try:
            # 1. Criar VENV
            venv.create(env_path, with_pip=True)
            
            # 2. Obter executável pip
            python_exe = DependencyManager._get_python_executable(env_path)
            
            # 3. Instalar pacotes
            cmd = [str(python_exe), "-m", "pip", "install", "--upgrade"] + packages
            subprocess.run(cmd, check=True)
            
            print(f"✅ Plugin '{plugin_name}' instalado com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao instalar plugin {plugin_name}: {e}")
            print(f"❌ Erro na instalação: {e}")
            return False

    @staticmethod
    def _get_python_executable(env_path: Path) -> Path:
        """Retorna o caminho do executável python dentro do VENV (Windows/Linux)."""
        if os.name == 'nt':
            return env_path / "Scripts" / "python.exe"
        return env_path / "bin" / "python"

    @staticmethod
    def get_plugin_python_path(plugin_name: str) -> Optional[str]:
        """Retorna o PYTHONPATH necessário para carregar o plugin."""
        env_path = DependencyManager.get_plugin_env_path(plugin_name)
        if os.name == 'nt':
            lib_path = env_path / "Lib" / "site-packages"
        else:
            # Para Linux/Mac, o caminho inclui a versão do python, ex: lib/python3.x/site-packages
            # Como o Foton é focado em Windows, simplificamos ou buscamos dinamicamente
            lib_path = next(env_path.glob("lib/python*/site-packages"), None)
        
        return str(lib_path) if lib_path and lib_path.exists() else None
