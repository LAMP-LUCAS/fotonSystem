import os
import sys
import shutil
from pathlib import Path
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()

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
        source_dir = exe_path.parent
        
        target_exe = self.bin_dir / exe_path.name
        
        if exe_path.resolve() == target_exe.resolve():
            logger.info("Executável já está no destino de instalação. Pulando cópia.")
            print("ℹ️ O sistema já está rodando a partir da pasta de instalação.")
        else:
            print(f"📂 Preparando binários em: {self.bin_dir}")
            try:
                # 2.1 Copiar o Executável
                if target_exe.exists():
                    try:
                        # Tentativa robusta: renomear o arquivo em uso
                        temp_old = target_exe.with_suffix(f".old_{int(time.time())}")
                        target_exe.rename(temp_old)
                        # Tenta deletar o arquivo renomeado (opcional)
                        try: temp_old.unlink()
                        except: pass
                    except Exception as e:
                        logger.debug(f"Não foi possível renomear exe antigo: {e}")
                
                shutil.copy2(exe_path, target_exe)
                print(f"✅ Executável copiado.")

                # 2.2 Copiar Pasta _internal (Essencial para builds --onedir)
                source_internal = source_dir / "_internal"
                target_internal = self.bin_dir / "_internal"
                
                if source_internal.exists():
                    print(f"📦 Atualizando dependências (_internal)... isso pode levar alguns segundos...")
                    
                    if target_internal.exists():
                        try:
                            # Tenta remover de forma limpa primeiro
                            shutil.rmtree(target_internal)
                        except Exception:
                            # Se falhar (Acesso Negado), renomeia a pasta antiga para sair do caminho
                            try:
                                timestamp = int(time.time())
                                trash_internal = target_internal.parent / f"_internal_old_{timestamp}"
                                target_internal.rename(trash_internal)
                                logger.info(f"Pasta _internal bloqueada. Renomeada para {trash_internal.name}")
                            except Exception as rename_err:
                                logger.error(f"Falha crítica ao mover _internal antigo: {rename_err}")
                                # Se não conseguir nem renomear, tentaremos o copytree com override
                                pass
                    
                    # Copia a pasta inteira (dirs_exist_ok garante que podemos mesclar se necessário)
                    shutil.copytree(source_internal, target_internal, dirs_exist_ok=True)
                    print(f"✅ Dependências atualizadas.")

            except Exception as e:
                logger.error(f"Erro ao copiar arquivos na instalação: {e}", exc_info=True)
                print(f"❌ Erro ao instalar binários: {e}")
                print("Dica: Verifique se não há outra instância do FotonSystem aberta.")
                return


        # 3. Inicializar Configuração no AppData
        config_path = BootstrapService.initialize()
        print(f"✅ Configuração vinculada em: {config_path}")
        
        # 4. Criar Atalhos apontando para o LocalAppData
        if sys.platform == "win32":
            self._create_windows_shortcuts(target_exe)
            
        print(f"\n🎉 {self.app_name} instalado com sucesso!")
        print(f"Você já pode fechar esta janela e usar o atalho na Área de Trabalho.")
        
        print(f"\n{'-'*60}")
        print(f"🤖 CONFIGURAÇÃO PARA AGENTES DE IA (MCP):")
        print(f"Para usar o Foton com Gemini ou Claude, adicione ao seu arquivo de config:")
        # Escape backslashes for JSON compatibility
        safe_path = str(target_exe).replace("\\", "\\\\")

        print(f"\n\"foton\": {{")
        print(f"  \"command\": \"{safe_path}\",")
        print(f"  \"args\": [\"--mcp\"]")
        print(f"}}\n{'-'*60}")

    def _create_windows_shortcuts(self, target_path: Path):
        try:
            import winshell
            from win32com.client import Dispatch

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
            logger.error(f"Erro ao criar atalhos: {e}", exc_info=True)
            print(f"⚠️ Erro ao criar atalhos: {e}")
