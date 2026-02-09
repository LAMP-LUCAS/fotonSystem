from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
from foton_system.modules.shared.infrastructure.config.logger import setup_logger

logger = setup_logger()


class FotonFileSystemEventHandler(FileSystemEventHandler):
    """
    Handles file system events to trigger proactive agent actions.
    Mainly: Re-indexing memory when documentation changes.
    
    Note: VectorStore dependencies are loaded lazily to prevent crashes
    if chromadb/sentence-transformers are not installed.
    """
    
    def __init__(self):
        self.last_triggered = {}
        self.debounce_seconds = 2.0
        self._op_indexer = None
        self._rag_available = None  # Cached availability check

    def _is_rag_available(self) -> bool:
        """Check if RAG/VectorStore dependencies are available."""
        if self._rag_available is not None:
            return self._rag_available
        
        try:
            from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
            self._op_indexer = OpIndexKnowledge(actor="Watcher_Service")
            self._rag_available = True
            logger.info("Watcher: RAG/VectorStore disponível.")
        except ImportError as e:
            self._rag_available = False
            logger.warning(f"Watcher: RAG indisponível (dependência faltando: {e}). Modo degradado ativado.")
        except Exception as e:
            self._rag_available = False
            logger.warning(f"Watcher: RAG indisponível ({e}). Modo degradado ativado.")
        
        return self._rag_available

    def _should_process(self, event) -> bool:
        if event.is_directory:
            return False
            
        path = Path(event.src_path)
        
        # Filter extensions we care about for RAG
        if path.suffix.lower() not in ['.md', '.txt']:
            return False
            
        # Debounce: Prevent double events (common in Windows editors)
        now = time.time()
        last = self.last_triggered.get(event.src_path, 0)
        if now - last < self.debounce_seconds:
            return False
            
        self.last_triggered[event.src_path] = now
        return True

    def on_modified(self, event):
        if self._should_process(event):
            print(f"👀 Watcher detected modification: {Path(event.src_path).name}")
            self._trigger_index(event.src_path)

    def on_created(self, event):
        if self._should_process(event):
            print(f"👀 Watcher detected creation: {Path(event.src_path).name}")
            self._trigger_index(event.src_path)

    def _trigger_index(self, file_path):
        # Check RAG availability first (lazy check)
        if not self._is_rag_available():
            print(f"ℹ️ Watcher: Arquivo detectado, mas RAG está desativado (modo degradado).")
            logger.debug(f"File change ignored (RAG unavailable): {file_path}")
            return
        
        try:
            target_folder = Path(file_path).parent
            print(f"🧠 Updating Memory for context: {target_folder.name}...")
            
            res = self._op_indexer.execute(target_path=str(target_folder))
            
            print(f"✅ Memory Updated! (Processed {res.get('chunks_created', 0)} chunks)")
            
        except Exception as e:
            logger.error(f"Watcher Error during indexing: {e}", exc_info=True)
            print(f"❌ Watcher Error: {e}")

