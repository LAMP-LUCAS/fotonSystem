import re
from typing import Any, Dict, List

from foton_system.core.rag.pipeline import PipelineNode, ProcessContext


class FormatNode(PipelineNode):
    name = "format"
    input_keys = ["query", "raw_results"]
    output_keys = ["formatted_output"]

    def execute(self, context: ProcessContext) -> ProcessContext:
        query = context["query"]
        results = context.get("scored_results") or context.get("raw_results", [])

        if not results:
            context["formatted_output"] = {
                "status": "EMPTY",
                "query": query,
                "results": [],
                "total": 0,
            }
            return context

        formatted = []
        for r in results:
            doc = r.get("document", "")
            contexto = self._extract_contexto(doc, query)
            formatted.append({
                "document": doc,
                "source": r.get("source", "Desconhecido"),
                "source_path": r.get("source_path", ""),
                "score": r.get("score", 0.0),
                "contexto": contexto,
            })

        context["formatted_output"] = {
            "status": "FOUND",
            "query": query,
            "results": formatted,
            "total": len(formatted),
        }
        return context

    def _extract_contexto(self, document: str, query: str, context_chars: int = 100) -> str:
        if len(document) <= context_chars * 2:
            return f">>>{document}<<<"
        terms = re.findall(r'\w+', query.lower())
        best_pos = 0
        for term in terms:
            pos = document.lower().find(term)
            if pos > 0:
                best_pos = pos
                break
        start = max(0, best_pos - context_chars)
        end = min(len(document), best_pos + context_chars)
        prefix = "" if start == 0 else "..."
        suffix = "" if end == len(document) else "..."
        snippet = document[start:end]
        return f"{prefix}>>>{snippet}<<<{suffix}"
