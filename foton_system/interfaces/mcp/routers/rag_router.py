"""
Roteador MCP para ferramentas de Recuperação Semântica (RAG).
"""

import time
from foton_system.interfaces.mcp.routers.common import (
    _logger,
    _log_tool_call,
)


def consultar_conhecimento(pergunta: str, cliente: str = "", tipo_doc: str = "") -> str:
    """
    Semantic search (RAG) across past projects and reference materials.
    PARAMETERS:
      pergunta: Question in natural language
      cliente: Optional — filter by client folder name
      tipo_doc: Optional — filter by document type (INFO, dados, proposta, etc.)
    CONTEXT: Use this to find 'How did we solve X for client Y before?' or 'What are the rules for Z?'.
    """
    mcp_start = time.perf_counter()
    try:
        from foton_system.core.ops.op_query_knowledge import OpQueryKnowledge
        op = OpQueryKnowledge(actor="Agent_MCP")
        kwargs = {"query": pergunta}
        if cliente.strip():
            kwargs["cliente"] = cliente.strip()
        if tipo_doc.strip():
            kwargs["tipo_doc"] = tipo_doc.strip()
        data = op.execute(**kwargs)

        duracao_ms = round((time.perf_counter() - mcp_start) * 1000, 1)

        if data.get("status") == "EMPTY":
            return f"📭 Nenhum conhecimento relevante encontrado. (duracao_ms={duracao_ms})"

        output = []
        for i, r in enumerate(data.get("results", []), 1):
            ctx = r.get("contexto", r["document"])
            output.append(
                f"--- [{i}] Fonte: {r['source']} (Score: {r['score']:.0%}) ---\n"
                f"{ctx}\n"
            )

        output.append(f"\n⏱ duracao_ms={duracao_ms}")
        return "\n".join(output)
    except ValueError as e:
        return f"❌ Invalid parameters: {e}"
    except Exception as e:
        return f"❌ Knowledge query error: {e}"


def indexar_conhecimento(pasta_alvo: str = "", cliente: str = "") -> str:
    """
    Updates the semantic database by indexing documents.
    PARAMETERS:
      pasta_alvo: Optional — specific folder path to index
      cliente: Optional — client name for selective indexing (only this client's folder)
    PROTOCOL: Run this after adding many new files or manually updating INFO files to ensure RAG stays current.
    """
    try:
        from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge
        op = OpIndexKnowledge(actor="Agent_MCP")
        kwargs = {}
        if cliente.strip():
            kwargs["cliente"] = cliente.strip()
        elif pasta_alvo.strip():
            kwargs["target_path"] = pasta_alvo.strip()
        result = op.execute(**kwargs)
        return f"✅ Knowledge base updated! Files: {result['files_scanned']}, Chunks: {result['chunks_created']}"
    except ValueError as e:
        return f"❌ Invalid parameters: {e}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Indexing error: {e}"


def diagnostico_conhecimento() -> str:
    """
    Diagnostic of the semantic knowledge base.
    Returns: total chunks, circuit breaker status (CLOSED/OPEN), last indexation timestamp.
    """
    try:
        from foton_system.core.memory.vector_store import VectorStoreManager
        store = VectorStoreManager()
        diag = store.diagnostic()

        stores = diag.get("stores", {})
        if not stores:
            return "📊 **RAG Knowledge Base Diagnostic**\n  Nenhuma coleção encontrada."

        mode = diag.get("mode", "")
        if mode and mode != "minilm":
            lines = [f"📊 **RAG Knowledge Base Diagnostic** (mode: {mode})"]
        else:
            lines = ["📊 **RAG Knowledge Base Diagnostic**"]

        for tag, info in stores.items():
            model_name = info.get("model_name", tag)
            collection_name = info.get("collection_name", "N/A")
            dims = info.get("dimensions", "")
            dims_str = f"{dims}d" if dims else "N/A"
            lines.append(
                f"  • **{tag}**: {collection_name}"
                f" ({model_name}, {dims_str})"
                f" — {info['total_chunks']} chunks,"
                f" CB: {info['circuit_breaker_status']},"
                f" last: {info['ultima_indexacao']}"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Diagnostic error: {e}"


def register_rag_tools(mcp) -> None:
    """Registra as ferramentas de RAG na instância FastMCP."""
    mcp.tool()(_log_tool_call(consultar_conhecimento))
    mcp.tool()(_log_tool_call(indexar_conhecimento))
    mcp.tool()(_log_tool_call(diagnostico_conhecimento))
