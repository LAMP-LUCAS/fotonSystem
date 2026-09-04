import sys
import os
import time
import logging
from pathlib import Path

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
    _start_session()
    from foton_system.interfaces.mcp.foton_mcp import run_server
    run_server()
    _end_session()


def _start_watcher():
    """
    Start Watcher Service in headless (daemon) mode.
    Redirects stdout to stderr to avoid conflicts if MCP is also running.
    Blocks indefinitely until SIGTERM (Unix) or forever (Windows).
    """
    import signal
    _ensure_path()
    _start_session()
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


def _detect_interface() -> str:
    if "--mcp" in sys.argv:
        return "MCP"
    if "--watcher" in sys.argv:
        return "WATCHER"
    return "TUI"


def _start_session():
    from foton_system.core.ops.session_tracker import start_session
    interface = _detect_interface()
    try:
        session = start_session(interface)
        _logger.info(f"Session started: {session.session_id} ({interface})")
    except Exception as e:
        _logger.warning(f"Failed to start session: {e}")


def _end_session():
    from foton_system.core.ops.session_tracker import end_session
    try:
        end_session()
    except Exception as e:
        _logger.warning(f"Failed to end session: {e}")


def _first_run_setup():
    """Runs first-time setup (shortcuts + config) when launched from install dir."""
    if not getattr(sys, 'frozen', False):
        return
    bin_dir = Path(sys.executable).resolve().parent
    marker = bin_dir / '.first_run'
    if marker.exists():
        try:
            from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
            from foton_system.modules.shared.infrastructure.services.environment_porter import get_porter
            porter = get_porter()
            integrator = porter.get_integrator()
            integrator.create_shortcut(Path(sys.executable).resolve(), "FotonSystem", "Sistema de Gest\u00e3o para Arquitetos")
            BootstrapService.initialize()
            marker.unlink()
            print("Configura\u00e7\u00e3o inicial conclu\u00edda.")
        except Exception as e:
            _logger.warning(f"First-run setup failed: {e}")


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

        _first_run_setup()

        _start_session()

        step_time = time.perf_counter()
        main()
        _logger.info(f"Bootstrap step 'main()' took {time.perf_counter() - step_time:.2f}s")

        _end_session()

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
