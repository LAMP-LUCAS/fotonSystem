import logging
from typing import Any, Dict, List, Optional

from foton_system.core.rag.pipeline import PipelineNode, ProcessContext

logger = logging.getLogger(__name__)

_HAS_CROSS_ENCODER: Optional[bool] = None


def _check_cross_encoder():
    global _HAS_CROSS_ENCODER
    if _HAS_CROSS_ENCODER is not None:
        return _HAS_CROSS_ENCODER
    try:
        from sentence_transformers import CrossEncoder
        _HAS_CROSS_ENCODER = True
    except ImportError:
        _HAS_CROSS_ENCODER = False
        logger.info("CrossEncoder não disponível — rerank desabilitado")
    return _HAS_CROSS_ENCODER


class RerankNode(PipelineNode):
    name = "rerank"
    input_keys = ["query", "raw_results"]
    output_keys = ["scored_results"]

    RERANK_MODEL = "BAAI/bge-reranker-v2-m3"

    def __init__(self) -> None:
        self._model: Optional[Any] = None

    def _get_model(self):
        if self._model is None and _check_cross_encoder():
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.RERANK_MODEL)
            except Exception as e:
                logger.warning("Falha ao carregar cross-encoder %s: %s", self.RERANK_MODEL, e)
        return self._model

    def execute(self, context: ProcessContext) -> ProcessContext:
        model = self._get_model()
        if model is None:
            logger.warning("RerankNode: cross-encoder não disponível — pulando rerank")
            context["scored_results"] = context.get("raw_results", [])
            return context

        query = context["query"]
        raw_results = context.get("raw_results", [])
        if not raw_results:
            context["scored_results"] = []
            return context

        pairs = [(query, r["document"]) for r in raw_results]
        try:
            scores = model.predict(pairs)
        except Exception as e:
            logger.warning("RerankNode: erro na predição — pulando rerank: %s", e)
            context["scored_results"] = raw_results
            return context

        for i, r in enumerate(raw_results):
            r["score"] = round(float(scores[i]), 4) if i < len(scores) else r.get("score", 0.0)

        reranked = sorted(raw_results, key=lambda x: x.get("score", 0.0), reverse=True)
        context["scored_results"] = reranked
        return context
