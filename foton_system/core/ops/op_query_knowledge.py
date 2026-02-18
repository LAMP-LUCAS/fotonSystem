"""
OpQueryKnowledge - Consulta Semântica na Base de Conhecimento

Operação POP para buscar documentos relevantes por semelhança semântica.
Usa o VectorStore (ChromaDB) como backend.

Uso via CLI:
    python -m foton_system.core.ops.op_query_knowledge "projetos residenciais"
"""

from typing import Dict, Any, List
from foton_system.core.ops.base_op import BaseOp


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

        Returns:
            Dicionário validado com 'query' e 'n_results'

        Raises:
            ValueError: Se a query estiver vazia
        """
        query = kwargs.get("query", "").strip()
        if not query:
            raise ValueError("A consulta (query) não pode estar vazia.")

        n_results = kwargs.get("n_results", 5)
        if not isinstance(n_results, int) or n_results < 1:
            n_results = 5

        return {"query": query, "n_results": n_results}

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a busca semântica no banco vetorial.

        Returns:
            Dicionário com:
                - status: "FOUND" ou "EMPTY"
                - query: Texto da consulta original
                - results: Lista de dicts {document, source, score}
                - total: Quantidade de resultados
        """
        from foton_system.core.memory.vector_store import VectorStore

        store = VectorStore()
        query = validated_data["query"]
        n_results = validated_data["n_results"]

        raw_results = store.query(query, n_results=n_results)

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
            results.append({
                "document": doc,
                "source": meta.get("filename", "Desconhecido"),
                "source_path": meta.get("source", ""),
                "score": round(1 - dist, 4)  # Converter distância cosseno em similaridade
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
