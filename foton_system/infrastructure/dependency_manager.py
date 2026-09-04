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
    def install_plugin(plugin_name: str, packages: List[str], extra_args: Optional[List[str]] = None) -> bool:
        """Cria um VENV e instala os pacotes solicitados.

        Args:
            plugin_name: Nome do plugin para o diretório do VENV.
            packages: Lista de pacotes pip a instalar.
            extra_args: Argumentos extras para o comando pip
                        (ex: ["--extra-index-url", "https://download.pytorch.org/whl/cu118"]).
        """
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
            if extra_args:
                cmd.extend(extra_args)
            subprocess.run(cmd, check=True)
            
            print(f"✅ Plugin '{plugin_name}' instalado com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao instalar plugin {plugin_name}: {e}")
            print(f"❌ Erro na instalação: {e}")
            return False

    @staticmethod
    def upgrade_torch_to_cuda() -> dict:
        """Instala torch com suporte CUDA no VENV do AI Pack.

        No Windows+py312, a ultima versao com CUDA e 2.5.1+cu121.
        Instala apenas no VENV isolado para nao corromper o Python global.

        Returns:
            dict com chaves: success, message, venv_path.
        """
        env_path = DependencyManager.get_plugin_env_path("ai_pack")
        if not env_path.exists():
            msg = "VENV do AI Pack nao encontrado. Instale o pacote de IA primeiro."
            logger.warning(msg)
            return {"success": False, "message": msg, "venv_path": None}

        python_exe = DependencyManager._get_python_executable(env_path)
        cuda_index = "https://download.pytorch.org/whl/cu121"

        print("\n[!] Instalando torch com suporte CUDA no VENV do AI Pack...")
        print(f"    VENV: {env_path}")
        print(f"    Index: {cuda_index}")
        print("    Download de ~2.4GB (torch 2.5.1+cu121 para Win+py312).\n")

        cmd = [
            str(python_exe), "-m", "pip", "install", "--force-reinstall",
            "--index-url", cuda_index,
            "torch",
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=600)
        except subprocess.TimeoutExpired:
            msg = "Timeout no download. Rede lenta ou conexao instavel."
            logger.error(msg)
            return {"success": False, "message": msg, "venv_path": str(env_path)}
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode(errors="replace")[:500]
            logger.error("Falha pip no VENV: %s", err)
            return {"success": False, "message": f"Erro pip: {err}", "venv_path": str(env_path)}

        check_cmd = [
            str(python_exe), "-c",
            "import torch; v=torch.__version__; "
            "c=torch.cuda.is_available(); "
            "n=torch.cuda.get_device_name(0) if c else 'N/A'; "
            "cu=torch.version.cuda or 'N/A'; "
            "print(f'{v}|{c}|{n}|{cu}')"
        ]
        try:
            result = subprocess.run(check_cmd, check=True, capture_output=True,
                                    text=True, timeout=30)
            version, cuda_avail, device, cu_ver = result.stdout.strip().split("|")
            if cuda_avail == "True":
                msg = f"torch {version} com CUDA {cu_ver} ativo no VENV. GPU: {device}"
                logger.info(msg)
                print(f"[OK] {msg}")
                return {"success": True, "message": msg, "venv_path": str(env_path)}
            else:
                msg = (f"torch {version} instalado no VENV, "
                       "mas CUDA nao disponivel. Verifique drivers NVIDIA.")
                logger.warning(msg)
                print(f"[!] {msg}")
                return {"success": False, "message": msg, "venv_path": str(env_path)}
        except Exception as e:
            msg = f"Falha ao verificar torch no VENV: {e}"
            logger.error(msg)
            print(f"[!] {msg}")
            print("    O torch foi instalado. Reinicie o programa para ativar CUDA.")
            return {"success": False, "message": msg, "venv_path": str(env_path)}

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
