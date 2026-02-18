import time
import threading
from watchdog.observers import Observer
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()


class WatcherService:
    """
    Manages the lifecycle of the File System Observer ("The Sentinel").
    Runs in a daemon thread to not block the CLI.
    
    Features graceful degradation if dependencies fail.
    """
    _instance = None
    _observer = None
    _thread = None
    _running = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WatcherService, cls).__new__(cls)
        return cls._instance

    def start(self):
        if self._running:
            print("⚠️ Watcher already running.")
            return

        print("🛡️ Starting Sentinel (Active Watcher)...")
        
        try:
            from foton_system.core.watcher.handlers import FotonFileSystemEventHandler
            
            path_to_watch = Config().base_pasta_clientes
            if not path_to_watch or not path_to_watch.exists():
                print(f"⚠️ Watcher Warning: Path {path_to_watch} does not exist.")
                if path_to_watch:
                    path_to_watch.mkdir(parents=True, exist_ok=True)
                else:
                    logger.error("Watcher: Pasta de clientes não configurada.")
                    print("❌ Erro: Pasta de clientes não configurada. Configure em Configurações.")
                    return

            self._observer = Observer()
            event_handler = FotonFileSystemEventHandler()
            
            self._observer.schedule(event_handler, str(path_to_watch), recursive=True)
            self._observer.start()
            self._running = True
            
            print(f"✅ Sentinel Active! Monitoring: {path_to_watch}")
            print("   (Edits to .md files will auto-update the AI Memory)")
            logger.info(f"Watcher started monitoring: {path_to_watch}")
            
        except ImportError as e:
            logger.error(f"Watcher failed to start (missing dependency): {e}", exc_info=True)
            print(f"❌ Erro ao iniciar Watcher: Dependência faltando ({e})")
            print("   Dica: O módulo 'watchdog' pode não estar instalado corretamente.")
        except Exception as e:
            logger.error(f"Watcher failed to start: {e}", exc_info=True)
            print(f"❌ Erro ao iniciar Watcher: {e}")

    def stop(self):
        if self._observer and self._running:
            print("🛑 Stopping Sentinel...")
            try:
                self._observer.stop()
                self._observer.join(timeout=5)
                self._running = False
                self._instance = None
                print("Sentinel Offline.")
                logger.info("Watcher stopped.")
            except Exception as e:
                logger.error(f"Error stopping watcher: {e}")
                print(f"⚠️ Erro ao parar Watcher: {e}")

