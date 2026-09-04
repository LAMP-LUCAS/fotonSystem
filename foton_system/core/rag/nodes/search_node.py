from typing import Any, Dict, List, Optional

from foton_system.core.memory.vector_store import VectorStoreManager
from foton_system.core.rag.pipeline import PipelineNode, ProcessContext


class SearchNode(PipelineNode):
    name = "search"
    input_keys = ["query", "embeddings"]
    output_keys = ["raw_results"]

    def __init__(self, manager: Optional[Any] = None):
        self._manager = manager

    def execute(self, context: ProcessContext) -> ProcessContext:
        query = context["query"]
        embeddings = context["embeddings"]
        n_results = context.get("n_results", 5)
        where = context.get("where", None)

        manager = self._manager or context.get("vector_store_manager") or VectorStoreManager()

        if len(manager.active_tags) == 1:
            tag = manager.active_tags[0]
            instance = manager.get_instance(tag)
            if instance and tag in embeddings:
                raw = instance.query_with_embeddings(embeddings[tag], n_results, where)
            elif instance:
                raw = instance.query(query, n_results, where)
            else:
                raw = {"documents": [[]], "metadatas": [[]], "distances": [[]], "ids": [[]]}
        else:
            raw = manager.query_with_embeddings(embeddings, n_results, where)

        context["raw_results"] = self._normalize(raw)
        return context

    def _normalize(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]
        ids_list = raw.get("ids", [[]])[0]
        results = []
        for i in range(len(docs)):
            results.append({
                "document": docs[i],
                "source": (metas[i] if i < len(metas) else {}).get("filename", "Desconhecido"),
                "source_path": (metas[i] if i < len(metas) else {}).get("source", ""),
                "score": round(1 - dists[i], 4) if i < len(dists) else 0.0,
                "id": ids_list[i] if i < len(ids_list) else "",
            })
        return results
