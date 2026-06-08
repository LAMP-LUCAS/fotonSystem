import sys
import os
import time
import logging

_logger = logging.getLogger("foton_bootstrap")


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
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    _ensure_path()
    from foton_system.interfaces.mcp.foton_mcp import run_server
    run_server()


def _start_watcher():
    """
    Start Watcher Service in headless (daemon) mode.
    Redirects stdout to stderr to avoid conflicts if MCP is also running.
    Blocks indefinitely until SIGTERM (Unix) or forever (Windows).
    """
    import signal
    _ensure_path()
    original_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        from foton_system.core.watcher.service import WatcherService
        watcher = WatcherService()
        watcher.start()
        sys.stdout = original_stdout
        print("✅ Watcher iniciado em background.", file=sys.stderr)
        # Block until signal (Unix) or sleep forever (Windows)
        try:
            signal.pause()
        except AttributeError:
            while True:
                time.sleep(1e10)
    except Exception as e:
        sys.stdout = original_stdout
        print(f"❌ Erro ao iniciar watcher: {e}", file=sys.stderr)
        sys.exit(1)


_bootstrap_start: float = 0.0
"""Global bootstrap timer baseline, set by safety_entry()."""


# Ultra-Safe Entry Point
def safety_entry():
    """Provides immediate visual feedback and robust error handling."""
    global _bootstrap_start
    _bootstrap_start = time.perf_counter()

    # ── SANDBOX MODE: Global Activation ──
    if "--sandbox" in sys.argv:
        _ensure_path()
        from foton_system.modules.shared.infrastructure.services.sandbox_service import SandboxService
        SandboxService.initialize_sandbox()

    # ── TUI MODE: Strip flag so it doesn't conflict with CLI argparse ──
    if "--tui" in sys.argv:
        sys.argv = [a for a in sys.argv if a != "--tui"]

    # ── MCP MODE: Must be checked FIRST — zero stdout before mcp.run() ──
    if "--mcp" in sys.argv:
        _start_mcp()
        _log_bootstrap_time()
        return

    # ── WATCHER MODE: Start file system watcher headless ──
    if "--watcher" in sys.argv:
        _start_watcher()
        _log_bootstrap_time()
        return

    # ── VERSION MODE ──
    if "--version" in sys.argv:
        from foton_system import __version__
        print(f"Foton System v{__version__}")
        return

    # ── CLI MODE: visual feedback is OK ──
    sys.stderr.write('\033[2J\033[H')

    print("\033[36m" + "="*60)
    print("\033[36m" + "Initializing FOTON SYSTEM".center(60))
    print("\033[36m" + "="*60 + "\033[0m")
    print("\033[90m" + "Loading core modules...".center(60) + "\033[0m")

    try:
        _ensure_path()

        step_time: float = time.perf_counter()
        print("\033[33m[  WAIT  ]\033[0m Bootstrapping interface...")
        from foton_system.interfaces.cli.main import main
        _logger.info(f"Bootstrap step 'import cli' took {time.perf_counter() - step_time:.2f}s")

        print("\033[32m[   OK   ]\033[0m System ready.")
        time.sleep(0.5)

        step_time = time.perf_counter()
        main()
        _logger.info(f"Bootstrap step 'main()' took {time.perf_counter() - step_time:.2f}s")

        _log_bootstrap_time()

    except Exception as e:
        import traceback
        print("\n" + "\033[41m" + " FATAL ERROR DURING STARTUP ".center(60) + "\033[0m")
        print("\033[31m" + "-"*60)
        traceback.print_exc()
        print("-"*60 + "\033[0m")
        print("\033[33mDiagnostic Info:\033[0m")
        from foton_system import __version__
        print(f"  Version: {__version__}")
        print(f"  Frozen: {getattr(sys, 'frozen', False)}")
        print(f"  Base Path: {getattr(sys, '_MEIPASS', os.getcwd())}")
        print("\n\033[36mPressione ENTER para fechar e reportar o erro...\033[0m")
        try:
            input()
        except EOFError:
            pass
        sys.exit(1)


def _log_bootstrap_time() -> None:
    """Loga o tempo total de bootstrap desde safety_entry()."""
    elapsed: float = time.perf_counter() - _bootstrap_start
    msg: str = f"Bootstrap completed in {elapsed:.2f}s"
    try:
        _logger.info(msg)
    except NameError:
        pass
    sys.stderr.write(f"[FOTON] {msg}\n")

if __name__ == "__main__":
    safety_entry()
