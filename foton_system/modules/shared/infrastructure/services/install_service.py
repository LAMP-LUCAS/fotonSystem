import os
import sys
import shutil
from pathlib import Path
import winshell
from win32com.client import Dispatch
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

class InstallService:
    def __init__(self):
        self.app_name = "FotonSystem"
        self.install_dir = Path(os.environ.get('LOCALAPPDATA')) / self.app_name
        self.bin_dir = self.install_dir / "bin"

    def install(self):
        """Realiza a instalação completa no LocalAppData."""
        print(f"🛠️ Instalando {self.app_name} em LocalAppData...")
        
        # 1. Criar diretórios
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Copiar arquivos da aplicação
        exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        exe_path = Path(exe_path).resolve()
        
        target_exe = self.bin_dir / exe_path.name
        
        print(f"📂 Copiando binários para: {target_exe}")
        try:
            shutil.copy2(exe_path, target_exe)
            
            # Se não for onefile (dev mode), pode precisar copiar pastas
            # Mas assumindo o build .exe onefile que fizemos:
        except Exception as e:
            print(f"❌ Erro ao copiar arquivos: {e}")
            return

        # 3. Inicializar Configuração no AppData
        config_path = BootstrapService.initialize()
        print(f"✅ Configuração vinculada em: {config_path}")
        
        # 4. Criar Atalhos apontando para o LocalAppData
        if sys.platform == "win32":
            self._create_windows_shortcuts(target_exe)
            
        print(f"\n🎉 {self.app_name} instalado com sucesso!")
        print(f"Você já pode fechar esta janela e usar o atalho na Área de Trabalho.")

    def _create_windows_shortcuts(self, target_path: Path):
        try:
            target_path_str = str(target_path)
            work_dir = str(target_path.parent)
            
            shell = Dispatch('WScript.Shell')

            # Atalho Desktop
            desktop = winshell.desktop()
            lnk_path = os.path.join(desktop, f"{self.app_name}.lnk")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = target_path_str
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = target_path_str
            shortcut.Description = "Sistema de Gestão para Arquitetos"
            shortcut.save()
            print("✅ Atalho criado na Área de Trabalho")
            
            # Atalho Menu Iniciar
            start_menu = winshell.programs()
            lnk_path = os.path.join(start_menu, f"{self.app_name}.lnk")
            shortcut = shell.CreateShortCut(lnk_path)
            shortcut.Targetpath = target_path_str
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = target_path_str
            shortcut.save()
            print("✅ Atalho criado no Menu Iniciar")
            
        except Exception as e:
            print(f"⚠️ Erro ao criar atalhos: {e}")
