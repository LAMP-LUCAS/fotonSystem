import time
import threading
from watchdog.observers import Observer
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.core.watcher.handlers import FotonFileSystemEventHandler

class WatcherService:
    """
    Manages the lifecycle of the File System Observer ("The Sentinel").
    Runs in a daemon thread to not block the CLI.
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
        
        path_to_watch = Config().base_pasta_clientes
        if not path_to_watch.exists():
            print(f"⚠️ Watcher Warning: Path {path_to_watch} does not exist.")
            path_to_watch.mkdir(parents=True, exist_ok=True)

        self._observer = Observer()
        event_handler = FotonFileSystemEventHandler()
        
        self._observer.schedule(event_handler, str(path_to_watch), recursive=True)
        self._observer.start()
        self._running = True
        
        print(f"✅ Sentinel Active! Monitoring: {path_to_watch}")
        print("   (Edits to .md files will auto-update the AI Memory)")

    def stop(self):
        if self._observer and self._running:
            print("🛑 Stopping Sentinel...")
            self._observer.stop()
            self._observer.join()
            self._running = False
            self._instance = None # Reset
            print("Sentinel Offline.")
