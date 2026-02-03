from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import logging
from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge

class FotonFileSystemEventHandler(FileSystemEventHandler):
    """
    Handles file system events to trigger proactive agent actions.
    Mainly: Re-indexing memory when documentation changes.
    """
    
    def __init__(self):
        self.last_triggered = {}
        self.debounce_seconds = 2.0
        self.op_indexer = OpIndexKnowledge(actor="Watcher_Service")

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
        try:
            # We trigger the Op targeting explicitly THIS file's parent or the file itself
            # The Op currently takes a target_path (folder). 
            # Ideally we pass the specific file to avoid re-scanning the whole folder.
            # For MVP: We scan the parent folder of the file.
            
            target_folder = Path(file_path).parent
            print(f"🧠 Updating Memory for context: {target_folder.name}...")
            
            # Run Op
            # Note: In a real heavy system, this should be queued.
            # Here we run it in the watcher thread (blocker) but safe for small edits.
            res = self.op_indexer.execute(target_path=str(target_folder))
            
            print(f"✅ Memory Updated! (Processed {res.get('chunks_created', 0)} chunks)")
            
        except Exception as e:
            print(f"❌ Watcher Error: {e}")
