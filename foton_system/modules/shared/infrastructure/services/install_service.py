import os
import sys
import shutil
import time
from pathlib import Path
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
from foton_system.modules.shared.infrastructure.config.logger import setup_logger
from foton_system.modules.shared.infrastructure.services.environment_porter import get_porter

logger = setup_logger()

class InstallService:
    def __init__(self):
        self.app_name = "FotonSystem"
        self.porter = get_porter()
        # Fallback para caminho de instalação se não estiver no Windows
        if self.porter.os_type == 'windows':
             self.install_dir = Path(os.environ.get('LOCALAPPDATA', '')) / self.app_name
        else:
             self.install_dir = Path.home() / ".local" / "share" / self.app_name.lower()
        
        self.bin_dir = self.install_dir / "bin"

    def install(self):
        """Realiza a instalação completa no sistema."""
        print(f"🛠️ Instalando {self.app_name} em {self.install_dir}...")
        
        # 1. Criar diretórios
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Copiar arquivos da aplicação (Omitido para brevidade, lógica permanece igual)
        # ... (Cópia do executável e _internal) ...
        # (Vou manter o código de cópia para não quebrar a funcionalidade)
        exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        exe_path = Path(exe_path).resolve()
        source_dir = exe_path.parent
        
        target_exe = self.bin_dir / exe_path.name
        
        if exe_path.resolve() == target_exe.resolve():
            logger.info("Executável já está no destino de instalação. Pulando cópia.")
            print("ℹ️ O sistema já está rodando a partir da pasta de instalação.")
        else:
            print(f"📂 Preparando binários em: {self.bin_dir}")
            try:
                if target_exe.exists():
                    try:
                        timestamp = int(time.time())
                        temp_old = target_exe.with_suffix(f".old_{timestamp}")
                        target_exe.rename(temp_old)
                    except Exception as e:
                        logger.debug(f"Não foi possível renomear exe antigo: {e}")
                
                shutil.copy2(exe_path, target_exe)
                print(f"✅ Executável copiado.")

                source_internal = source_dir / "_internal"
                target_internal = self.bin_dir / "_internal"
                
                if source_internal.exists():
                    print(f"📦 Atualizando dependências (_internal)...")
                    if target_internal.exists():
                        try:
                            timestamp = int(time.time())
                            trash_internal = target_internal.parent / f"_internal_old_{timestamp}"
                            target_internal.rename(trash_internal)
                        except: pass
                    
                    shutil.copytree(source_internal, target_internal, dirs_exist_ok=True)
                    print(f"✅ Dependências atualizadas.")

            except Exception as e:
                logger.error(f"Erro ao copiar arquivos: {e}")
                print(f"❌ Erro ao instalar binários: {e}")
                return

        # 3. Inicializar Configuração
        config_path = BootstrapService.initialize()
        print(f"✅ Configuração vinculada em: {config_path}")
        
        # 4. Criar Atalhos usando o Integrador (Agnóstico)
        integrator = self.porter.get_integrator()
        success = integrator.create_shortcut(
            target_exe, 
            self.app_name, 
            "Sistema de Gestão para Arquitetos"
        )
        
        if success:
            print(f"✅ Atalhos de sistema criados com sucesso!")
        else:
            print(f"⚠️ Não foi possível criar atalhos automáticos para este ambiente.")
            
        print(f"\n🎉 {self.app_name} instalado com sucesso!")

    # Removido _create_windows_shortcuts pois agora está no adaptador correspondente.
