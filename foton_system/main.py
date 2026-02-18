import sys
import os
import time

<<<<<<< HEAD
# Ultra-Safe Entry Point
def safety_entry():
    """Provides immediate visual feedback and robust error handling."""
    # 1. Clear Screen for premium feel
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\033[36m" + "="*60)
    print("\033[36m" + "Initializing FOTON SYSTEM".center(60))
    print("\033[36m" + "="*60 + "\033[0m")
    print("\033[90m" + "Loading core modules...".center(60) + "\033[0m")

    try:
        # 2. Fix Path for both Dev and Frozen (PyInstaller)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            # In frozen mode, the root is inside _MEIPASS
            if base_path not in sys.path:
                sys.path.append(base_path)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)

        # 3. Check for MCP flag (suppress UI for tool communication)
        if "--mcp" in sys.argv:
            from foton_system.interfaces.mcp.foton_mcp import mcp
            mcp.run()
            return

        # 4. Deferred Import of heavy modules to show "Loading" status
        print("\033[33m[  WAIT  ]\033[0m Bootstrapping interface...")
        from foton_system.interfaces.cli.main import main
        
        print("\033[32m[   OK   ]\033[0m System ready.")
        time.sleep(0.5) 
        
=======

def _ensure_path():
    """Fix sys.path for both Dev and Frozen (PyInstaller) modes."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        if base_path not in sys.path:
            sys.path.append(base_path)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)


def _start_mcp():
    """
    Start MCP server in stdio mode.
    CRITICAL: This function must produce ZERO stdout output before mcp.run().
    All diagnostics go to stderr or log file.
    """
    _ensure_path()
    from foton_system.interfaces.mcp.foton_mcp import run_server
    run_server()


# Ultra-Safe Entry Point
def safety_entry():
    """Provides immediate visual feedback and robust error handling."""
    # ── MCP MODE: Must be checked FIRST — zero stdout before mcp.run() ──
    if "--mcp" in sys.argv:
        _start_mcp()
        return

    # ── CLI MODE: visual feedback is OK ──
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\033[36m" + "="*60)
    print("\033[36m" + "Initializing FOTON SYSTEM".center(60))
    print("\033[36m" + "="*60 + "\033[0m")
    print("\033[90m" + "Loading core modules...".center(60) + "\033[0m")

    try:
        _ensure_path()

        # Deferred Import of heavy modules to show "Loading" status
        print("\033[33m[  WAIT  ]\033[0m Bootstrapping interface...")
        from foton_system.interfaces.cli.main import main

        print("\033[32m[   OK   ]\033[0m System ready.")
        time.sleep(0.5)

>>>>>>> bd7b97aaa2f383cac97855c4cb7eca8ddf31252a
        main()

    except Exception as e:
        import traceback
        print("\n" + "\033[41m" + " FATAL ERROR DURING STARTUP ".center(60) + "\033[0m")
        print("\033[31m" + "-"*60)
        traceback.print_exc()
        print("-"*60 + "\033[0m")
        print("\033[33mDiagnostic Info:\033[0m")
        print(f"  Version: 1.0.0")
        print(f"  Frozen: {getattr(sys, 'frozen', False)}")
        print(f"  Base Path: {getattr(sys, '_MEIPASS', os.getcwd())}")
        print("\n\033[36mPressione ENTER para fechar e reportar o erro...\033[0m")
        input()
        sys.exit(1)

if __name__ == "__main__":
    safety_entry()
