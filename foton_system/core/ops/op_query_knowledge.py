"""
OpQueryKnowledge - Consulta Semântica na Base de Conhecimento

Operação POP para buscar documentos relevantes por semelhança semântica.
Usa o VectorStore (ChromaDB) como backend.

Uso via CLI:
    python -m foton_system.core.ops.op_query_knowledge "projetos residenciais"

@story: STORY-041 @rule: RULE-RAG-4.1 @rule: RULE-RAG-4.2 @rule: RULE-RAG-4.3
"""

import hashlib
import logging
import re
import time
from typing import Dict, Any, List, Optional
from foton_system.core.ops.base_op import BaseOp

_logger = logging.getLogger("op_query_knowledge")


class OpQueryKnowledge(BaseOp):
    """
    Standard Operation para consulta à base de conhecimento vetorial.
    Busca documentos semanticamente similares à pergunta fornecida.
    """

    def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Valida os argumentos de consulta.

        Args (via kwargs):
            query: Texto da pergunta (obrigatório)
            n_results: Quantidade máxima de resultados (default: 5)
            cliente: Nome do cliente para filtrar (opcional)
            tipo_doc: Tipo de documento (INFO, dados, etc.) (opcional)

        Returns:
            Dicionário validado com 'query', 'n_results', 'cliente', 'tipo_doc'

        Raises:
            ValueError: Se a query estiver vazia
        """
        query = kwargs.get("query", "").strip()
        if not query:
            raise ValueError("A consulta (query) não pode estar vazia.")

        n_results = kwargs.get("n_results", 5)
        if not isinstance(n_results, int) or n_results < 1:
            n_results = 5

        cliente = kwargs.get("cliente", "").strip()
        tipo_doc = kwargs.get("tipo_doc", "").strip()

        return {
            "query": query,
            "n_results": n_results,
            "cliente": cliente,
            "tipo_doc": tipo_doc
        }

    def _build_where_filter(self, cliente: str, tipo_doc: str) -> Optional[Dict[str, Any]]:
        """Monta filtro de metadados para consulta ChromaDB."""
        where: Dict[str, Any] = {}
        if cliente:
            where["source"] = {"$contains": cliente}
        if tipo_doc:
            where["filename"] = {"$contains": tipo_doc}
        return where if where else None

    def _extract_contexto(self, document: str, query: str, context_chars: int = 100) -> str:
        """
        Extrai trecho de contexto (N chars antes/depois) delimitado por marcadores.
        Se o documento for curto, retorna o documento inteiro com marcadores.
        """
        if len(document) <= context_chars * 2:
            return f">>>{document}<<<"

        # Tenta encontrar o termo mais relevante da query no documento
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

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a busca semântica no banco vetorial.

        Returns:
            Dicionário com:
                - status: "FOUND" ou "EMPTY"
                - query: Texto da consulta original
                - results: Lista de dicts {document, source, score, contexto}
                - total: Quantidade de resultados
        """
        from foton_system.core.memory.vector_store import VectorStoreManager

        store = VectorStoreManager()
        query = validated_data["query"]
        n_results = validated_data["n_results"]
        cliente = validated_data.get("cliente", "")
        tipo_doc = validated_data.get("tipo_doc", "")

        where = self._build_where_filter(cliente, tipo_doc)

        query_kwargs: Dict[str, Any] = {"n_results": n_results}
        if where is not None:
            query_kwargs["where"] = where

        query_start = time.perf_counter()
        raw_results = store.query(query, **query_kwargs)
        query_time_ms = (time.perf_counter() - query_start) * 1000

        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        from foton_system.modules.shared.infrastructure.config.config import Config
        cfg = Config()
        _logger.info(
            "[RAG_PERF] consulta=%s duration_ms=%.0f modelo=%s pipeline=%s",
            query_hash, query_time_ms,
            cfg.rag_embedding_mode,
            cfg.rag_pipeline_type,
        )

        # Extrair resultados do formato ChromaDB
        documents = raw_results.get("documents", [[]])[0]
        metadatas = raw_results.get("metadatas", [[]])[0]
        distances = raw_results.get("distances", [[]])[0]

        if not documents:
            return {
                "status": "EMPTY",
                "query": query,
                "results": [],
                "total": 0
            }

        results: List[Dict[str, Any]] = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            contexto = self._extract_contexto(doc, query)
            results.append({
                "document": doc,
                "source": meta.get("filename", "Desconhecido"),
                "source_path": meta.get("source", ""),
                "score": round(1 - dist, 4),
                "contexto": contexto
            })

        return {
            "status": "FOUND",
            "query": query,
            "results": results,
            "total": len(results)
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m foton_system.core.ops.op_query_knowledge \"sua pergunta\"")
        sys.exit(1)

    query_text = " ".join(sys.argv[1:])
    op = OpQueryKnowledge(actor="CLI_User")
    result = op.execute(query=query_text)

    if result["status"] == "EMPTY":
        print("📭 Nenhum resultado encontrado na base de conhecimento.")
    else:
        print(f"🔍 {result['total']} resultados para: \"{result['query']}\"\n")
        for i, r in enumerate(result["results"], 1):
            print(f"--- [{i}] Fonte: {r['source']} (Similaridade: {r['score']:.2%}) ---")
            print(f"{r['document'][:300]}...")
            print()
