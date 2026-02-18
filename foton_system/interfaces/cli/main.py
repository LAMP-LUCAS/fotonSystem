"""
FotonSystem CLI Entry Point

This is the main entry point for the CLI application.
It handles initialization, CLI arguments, and launches the menu system.

IMPORTANT: This module includes sys.path patching to ensure it can be run
from any working directory, both in development and frozen (EXE) modes.
"""

# --- CRITICAL: PATH PATCHING (Must be FIRST) ---
# This ensures the package can be found regardless of where Python is invoked from.
import sys
from pathlib import Path

def _ensure_import_path():
    """
    Adds the project root to sys.path if not already present.
    
    This allows running the CLI directly as:
      python foton_system/interfaces/cli/main.py
    
    Without requiring PYTHONPATH to be set or the package to be installed.
    """
    # In frozen mode (PyInstaller), imports are handled by the bootloader
    if getattr(sys, 'frozen', False):
        return
    
    # Find project root by traversing up from this file
    # This file is at: foton_system/interfaces/cli/main.py
    # Project root is 3 levels up
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[3]
    
    # Verify we found the correct root
    if (project_root / "foton_system" / "__init__.py").exists():
        root_str = str(project_root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)

# Execute path patching immediately on module load
_ensure_import_path()

# --- STANDARD IMPORTS (Now safe after path patching) ---
import argparse

from foton_system import __version__
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager


def show_welcome_message():
    """Displays a welcome message on first run."""
    print("")
    print("=" * 60)
    print("  🎉 Bem-vindo ao FotonSystem!")
    print("=" * 60)
    print("")
    print("  Este é o Sistema Operacional para Escritórios de Arquitetura.")
    print("  Todos os seus dados serão salvos em:")
    print(f"    📁 {PathManager.get_app_data_dir()}")
    print("")
    print("  Seus projetos serão organizados em:")
    print(f"    📂 {PathManager.get_user_projects_dir()}")
    print("")
    print("  Para alterar essas configurações, edite o arquivo:")
    print(f"    ⚙️ {PathManager.get_settings_path()}")
    print("")
    print("=" * 60)
    print("")


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="foton",
        description="FotonSystem - Sistema Operacional para Escritórios de Arquitetura",
        epilog="Desenvolvido por LAMP Arquitetura | https://github.com/LAMP-LUCAS/fotonSystem"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"FotonSystem v{__version__}"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Exibe informações sobre os caminhos do sistema"
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Recria o arquivo de configuração com valores padrão"
    )
    
    parser.add_argument(
        "--mcp-config",
        action="store_true",
        help="Exibe a configuração JSON para integração com Claude/Cursor MCP"
    )

    parser.add_argument(
        "--mcp",
        action="store_true",
        help="Inicia o servidor MCP (Model Context Protocol) para IA"
    )
    
    parser.add_argument(
        "--tui",
        action="store_const",
        const="tui",
        dest="ui_mode",
        help="Força o uso da Interface de Terminal (TUI)"
    )

    parser.add_argument(
        "--gui",
        action="store_const",
        const="gui",
        dest="ui_mode",
        help="Força o uso da Interface Gráfica (GUI)"
    )

    return parser.parse_args()



def show_system_info():
    """Displays system path information."""
    print("")
    print("📌 Informações do Sistema FotonSystem")
    print("-" * 50)
    print(f"  Versão:          v{__version__}")
    print(f"  Modo:            {'Executável' if PathManager.is_frozen() else 'Desenvolvimento'}")
    print(f"  Dados (AppData): {PathManager.get_app_data_dir()}")
    print(f"  Configuração:    {PathManager.get_settings_path()}")
    print(f"  Log:             {PathManager.get_log_path()}")
    print(f"  Projetos:        {PathManager.get_user_projects_dir()}")
    print(f"  Instalação:      {PathManager.get_install_dir()}")
    print("")


def show_mcp_config():
    """Displays the JSON configuration for MCP integration."""
    import json
    
    # Determine the correct path to the MCP script
    if PathManager.is_frozen():
        # In frozen mode, point to the EXE itself with the --mcp flag
        exe_path = str(PathManager.get_install_dir() / "foton_system_v1.0.0.exe")
        # Ensure we point to the actual running exe if possible
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
            
        mcp_cmd = exe_path
        mcp_args = ["--mcp"]
    else:
        # In dev mode, point to the Python script
        mcp_script = PathManager._find_project_root() / "foton_system" / "interfaces" / "mcp" / "foton_mcp.py"
        mcp_cmd = "python"
        mcp_args = [str(mcp_script)]
    
    # Build the config object
    config = {
        "mcpServers": {
            "foton": {
                "command": mcp_cmd,
                "args": mcp_args
            }
        }
    }
    
    print("")
    print("📋 Configuração MCP para Claude Desktop / Cursor:")
    print("-" * 50)
    print("")
    print("Cole o conteúdo abaixo no seu arquivo de configuração:")
    print("")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print("")
    print("-" * 50)
    print("📁 Localização do arquivo de configuração:")
    print("   Claude: %APPDATA%/Claude/claude_desktop_config.json")
    print("   Cursor: Settings > Features > MCP")
    print("")


def main():
    """Main entry point for the CLI application."""
    
    # Parse CLI arguments
    args = parse_args()
    
    # Handle --info flag (lightweight, no bootstrap needed)
    if args.info:
        show_system_info()
        sys.exit(0)
    
    # Handle --mcp-config flag (lightweight, no bootstrap needed)
    if args.mcp_config:
        show_mcp_config()
        sys.exit(0)

    # Handle --mcp flag (Launch MCP Server)
    if args.mcp:
        try:
            from foton_system.interfaces.mcp.foton_mcp import mcp
            print("🤖 Iniciando Servidor Foton MCP...")
            mcp.run()
        except ImportError as e:
            print(f"❌ Erro ao importar MCP: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Erro fatal no MCP: {e}")
            sys.exit(1)
        sys.exit(0)
    
    # Handle --reset-config flag
    if args.reset_config:
        config_path = PathManager.get_settings_path()
        if config_path.exists():
            config_path.unlink()
            print(f"✅ Configuração removida: {config_path}")
        print("⚙️ Uma nova configuração será criada na próxima execução.")
        sys.exit(0)
    
    # --- HEAVY INITIALIZATION STARTS HERE ---
    # Import BootstrapService only when actually needed (lazy import)
    from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
    
    # Check if first run
    is_first_run = BootstrapService.is_first_run()
    
    # Initialize environment (creates AppData, settings, etc)
    try:
        BootstrapService.initialize()
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        sys.exit(1)
    
    # Show welcome message on first run
    if is_first_run:
        show_welcome_message()
    
    # Check for updates (non-blocking)
    try:
        from foton_system.modules.shared.infrastructure.services.update_service import UpdateChecker
        UpdateChecker.check_for_updates()
    except Exception:
        pass  # Don't block startup on update error

    # Launch the menu system
    try:
        from foton_system.interfaces.cli.menus import MenuSystem
        from foton_system.interfaces.cli.ui_provider import get_ui_provider
        from foton_system.modules.shared.infrastructure.config.config import Config
        
        # Determine UI Mode (Priority: CLI Flag > Config > Auto)
        ui_mode = args.ui_mode or Config().ui_mode or 'auto'
        ui = get_ui_provider(ui_mode)
        
        menu = MenuSystem(ui_provider=ui)
        menu.run()

    except KeyboardInterrupt:
        print("\n👋 Até logo!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
