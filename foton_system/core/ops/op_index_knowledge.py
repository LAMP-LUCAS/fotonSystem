import hashlib
from pathlib import Path
from typing import Dict, Any, List
from foton_system.core.ops.base_op import BaseOp
from foton_system.core.memory.vector_store import VectorStore
from foton_system.modules.shared.infrastructure.config.config import Config

class OpIndexKnowledge(BaseOp):
    """
    Standard Operation to index files into the Vector Store ("The Harvester").
    Scans client folders, chunks content, and updates ChromaDB.
    """
    
    def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Optional: 'target_path' to scan specific folder.
        Default: Scans entire 'base_pasta_clientes'.
        """
        path = kwargs.get("target_path")
        if path:
            p = Path(path)
            if not p.exists():
                raise ValueError(f"Path {path} does not exist.")
            kwargs["target_path_obj"] = p
        else:
             # Default to all clients
             kwargs["target_path_obj"] = Config().base_pasta_clientes
             
        return kwargs

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Helper to get MD5 hash of file."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        Simple overlapping chunker. 
        TODO: Improve with header-aware splitting (Markdown).
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - 50 # 50 char overlap
        return chunks

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        target_path = validated_data["target_path_obj"]
        store = VectorStore()
        
        indexed_count = 0
        skipped_count = 0
        
        # Files to look for
        extensions = ['*.md', '*.txt']
        
        files_to_process = []
        for ext in extensions:
            files_to_process.extend(target_path.rglob(ext))
            
        docs_to_add = []
        ids_to_add = []
        metadatas_to_add = []
        
        for file_path in files_to_process:
            try:
                # 1. Check Hash to avoid re-indexing
                # (Simplification: We query by ID=filepath to check metadata hash)
                # For this MVP iteration, we will simply UPSERT everything.
                # Optimization for V2: Check existing hash in DB before reading.
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                if not content.strip():
                    continue

                chunks = self._chunk_text(content)
                current_hash = self._calculate_file_hash(file_path)
                
                for i, chunk in enumerate(chunks):
                    # Robust ID: Path + Chunk Index
                    # Flatten path relative to base for cleaner ID
                    try:
                        rel_path = file_path.relative_to(Config().base_pasta_clientes)
                    except ValueError:
                        rel_path = file_path.name

                    chunk_id = f"{rel_path}::chunk_{i}"
                    
                    docs_to_add.append(chunk)
                    ids_to_add.append(chunk_id)
                    metadatas_to_add.append({
                        "source": str(file_path),
                        "filename": file_path.name,
                        "hash": current_hash,
                        "chunk_index": i
                    })
                    
                indexed_count += 1
                
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")
                
        # Batch add to Chroma
        if docs_to_add:
            # Add in batches of 100 to avoid memory spikes
            batch_size = 100
            for i in range(0, len(docs_to_add), batch_size):
                store.add_documents(
                    documents=docs_to_add[i:i+batch_size],
                    metadatas=metadatas_to_add[i:i+batch_size],
                    ids=ids_to_add[i:i+batch_size]
                )

        return {
            "status": "INDEXED",
            "files_scanned": indexed_count,
            "chunks_created": len(docs_to_add),
            "target": str(target_path)
        }

if __name__ == "__main__":
    op = OpIndexKnowledge(actor="CLI_User")
    res = op.execute()
    print(f"Knowledge Base Updated: {res['chunks_created']} chunks from {res['files_scanned']} files.")
