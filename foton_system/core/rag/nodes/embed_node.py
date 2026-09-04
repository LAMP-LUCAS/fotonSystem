from typing import Any, Dict, List, Optional

from foton_system.core.memory.vector_store import VectorStoreManager
from foton_system.core.rag.pipeline import PipelineNode, ProcessContext


class EmbedNode(PipelineNode):
    name = "embed"
    input_keys = ["query"]
    output_keys = ["embeddings"]

    def __init__(self, manager: Optional[Any] = None):
        self._manager = manager

    def execute(self, context: ProcessContext) -> ProcessContext:
        query = context["query"]
        manager = self._manager or context.get("vector_store_manager") or VectorStoreManager()
        embeddings: Dict[str, List[float]] = {}
        for tag in manager.active_tags:
            instance = manager.get_instance(tag)
            if instance:
                embeddings[tag] = instance.embed_query(query)
        context["embeddings"] = embeddings
        return context
