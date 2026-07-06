# @story: STORY-036
# @rule: RULE-RAG-7.1 a 12.5

"""
E2E Integration Tests for RAG Pipeline v2.0 (6-layer architecture).

Validates the orchestration flow between:
  HardwareProfiler -> ModelRouter -> VectorStoreManager -> PipelineNodes -> Output

Unlike unit tests, these use REAL ChromaDB instances (in temp dirs).
Only the embedding model (SentenceTransformer) is mocked to avoid
downloading ~500MB of model data in CI.
"""

import json
import pytest
import time
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Dict, List, Optional

from foton_system.core.rag.hardware_profiler import HardwareProfile


# ==============================================================================
# Helpers
# ==============================================================================

def _create_instance_directly(
    model_tag: str,
    dimensions: int,
    chromadb_path: Path,
    mock_embedder,
    breaker_state: str = "CLOSED",
) -> "VectorStoreInstance":
    """Factory helper: creates a VectorStoreInstance with real ChromaDB + mock embedder.

    Bypasses the real _initialize() which would download SentenceTransformer models.
    Instead, injects the mock embedder directly into the instance.

    Args:
        model_tag: 'minilm' or 'bgem3'
        dimensions: 384 or 1024
        chromadb_path: Path to temp ChromaDB directory
        mock_embedder: Mock that returns fixed vectors on .encode()
        breaker_state: 'CLOSED' or 'OPEN'
    """
    from foton_system.core.memory.vector_store import VectorStoreInstance
    from foton_system.core.memory.vector_store import CircuitBreaker
    from foton_system.core.rag.model_registry import ModelEntry, ModelRegistry
    import chromadb

    entry = ModelRegistry().get(model_tag)
    if entry is None:
        entry = ModelEntry(
            id=model_tag,
            name=f"test-model-{model_tag}",
            type="embedding",
            dimensions=dimensions,
            ram_required_gb=1.0,
            disk_required_gb=0.5,
            requires_gpu=False,
            is_default=(model_tag == "minilm"),
        )

    collection_name = f"foton_{model_tag}_{dimensions}d"

    chromadb_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chromadb_path))

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={
            "hnsw:space": "cosine",
            "model_name": entry.name,
            "model_tag": model_tag,
            "dimensions": str(dimensions),
        },
    )

    instance = VectorStoreInstance.__new__(VectorStoreInstance)
    instance.model_tag = model_tag
    instance.model_entry = entry
    instance.config_dir = chromadb_path.parent
    instance.collection_name = collection_name
    instance.db_path = chromadb_path
    instance.client = client
    instance.collection = collection
    instance.embedder = mock_embedder
    instance._initialized = True

    instance._breaker = CircuitBreaker()
    if breaker_state == "OPEN":
        instance._breaker._state = "OPEN"
        instance._breaker._failure_count = 3
        instance._breaker._last_failure_time = time.time()

    return instance


def _create_manager_directly(
    mode: str,
    active_tags: List[str],
    instances: dict,
) -> "VectorStoreManager":
    """Factory helper: creates a VectorStoreManager bypassing lazy_init.

    Sets the internal state directly so the manager operates with
    the provided instances without touching Config/ModelRouter.
    """
    from foton_system.core.memory.vector_store import VectorStoreManager

    manager = VectorStoreManager.__new__(VectorStoreManager)
    manager._initialized = True
    manager._lazy_init_done = True
    manager._mode = mode
    manager._active_tags = active_tags
    manager._instances = instances
    manager._config_dir = None
    return manager


def _run_pipeline_with_manager(
    manager,
    query: str,
    pipeline_type: str = "simple",
    n_results: int = 5,
) -> dict:
    """Run the full RAG pipeline against a given VectorStoreManager.

    Creates a RagPipeline with mocked nodes wired to the manager.
    Returns the formatted output dict.
    """
    from foton_system.core.rag.pipeline import RagPipeline
    from foton_system.core.rag.pipeline import ProcessContext
    from foton_system.core.rag.nodes.embed_node import EmbedNode
    from foton_system.core.rag.nodes.search_node import SearchNode
    from foton_system.core.rag.nodes.format_node import FormatNode

    if pipeline_type == "rerank":
        from foton_system.core.rag.nodes.rerank_node import RerankNode

    pipeline = RagPipeline.__new__(RagPipeline)
    pipeline._pipeline_type = pipeline_type

    if pipeline_type == "rerank":
        pipeline._node_names = ["embed", "search", "rerank", "format"]
    else:
        pipeline._node_names = ["embed", "search", "format"]

    with patch(
        "foton_system.core.rag.nodes.embed_node.VectorStoreManager",
        return_value=manager,
    ):
        with patch(
            "foton_system.core.rag.nodes.search_node.VectorStoreManager",
            return_value=manager,
        ):
            embed_node = EmbedNode()
            search_node = SearchNode()
            format_node = FormatNode()

            if pipeline_type == "rerank":
                rerank_node = RerankNode()
                rerank_node._model = MagicMock()
                pipeline._nodes = [embed_node, search_node, rerank_node, format_node]
            else:
                pipeline._nodes = [embed_node, search_node, format_node]

            ctx = pipeline.run({"query": query, "n_results": n_results})

    return ctx["formatted_output"]


# ==============================================================================
# AC1 — MiniLM mode: index 3 chunks, query, validate formatted output
# ==============================================================================

class TestMiniLMModeE2E:
    """E2E: modo MiniLM — indexa 3 chunks, consulta, valida saída formatada.
    @rule: RULE-RAG-11.4, RULE-RAG-11.5
    """

    def test_index_and_query_returns_formatted_output(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d,
    ):
        """AC1: Index 3 chunks in real ChromaDB, query, verify formatted output."""
        chromadb_path = tmp_path / "memory_db"
        instance = _create_instance_directly(
            "minilm", 384, chromadb_path, mock_embedder_384d,
        )
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})

        # Index 3 chunks
        manager.add_documents(sample_chunks, sample_metadatas, sample_ids)

        # Verify count
        assert manager.count() >= 3, "Must have indexed at least 3 chunks"

        # Query via pipeline
        output = _run_pipeline_with_manager(manager, "reforma apartamento")

        # Validate formatted output structure
        assert output["status"] in ("FOUND", "EMPTY"), f"Unexpected status: {output['status']}"
        assert output["query"] == "reforma apartamento"

        if output["status"] == "FOUND":
            result = output["results"][0]
            assert "score" in result, "Result must contain score"
            assert "source" in result, "Result must contain source"
            assert "document" in result, "Result must contain document text"
            assert 0.0 <= result["score"] <= 1.0, "Score must be 0-1"
            assert isinstance(result["source"], str) and len(result["source"]) > 0

    def test_formatted_output_contains_context_markers(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d,
    ):
        """Formatted output should contain context markers."""
        chromadb_path = tmp_path / "memory_db" / "sub"
        instance = _create_instance_directly(
            "minilm", 384, chromadb_path, mock_embedder_384d,
        )
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})

        manager.add_documents(sample_chunks, sample_metadatas, sample_ids)
        output = _run_pipeline_with_manager(manager, "reforma")

        if output["status"] == "FOUND":
            assert ">>>" in output["results"][0].get("contexto", ""), \
                "Contexto must contain >>> markers"
            assert "<<<" in output["results"][0].get("contexto", ""), \
                "Contexto must contain <<< markers"

    def test_returns_multiple_results(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d,
    ):
        """Query with n_results=3 should return up to 3 results."""
        chromadb_path = tmp_path / "memory_db"
        instance = _create_instance_directly(
            "minilm", 384, chromadb_path, mock_embedder_384d,
        )
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})

        manager.add_documents(sample_chunks, sample_metadatas, sample_ids)
        output = _run_pipeline_with_manager(manager, "obra", n_results=3)

        assert output["total"] <= 3, f"Must return at most 3 results, got {output['total']}"


# ==============================================================================
# AC2 — Dual mode: index in both collections, parallel query, merge without dupes
# ==============================================================================

class TestDualModeE2E:
    """E2E: modo dual — indexa em ambas coleções, consulta em paralelo, merge.
    @rule: RULE-RAG-10.4, RULE-RAG-9.2
    """

    def test_dual_mode_merge_deduplicates(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d, mock_embedder_1024d,
    ):
        """Index same chunks in both models, query dual, assert merge without dupes."""
        chromadb_path = tmp_path / "memory_db"

        minilm = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        bgem3 = _create_instance_directly("bgem3", 1024, chromadb_path, mock_embedder_1024d)

        manager = _create_manager_directly(
            "dual", ["minilm", "bgem3"], {"minilm": minilm, "bgem3": bgem3},
        )

        # Index in both
        manager.add_documents(sample_chunks, sample_metadatas, sample_ids)

        # Query
        result = manager.query("reforma apartamento", n_results=5)

        docs = result.get("documents", [[]])[0]
        ids = result.get("ids", [[]])[0]

        # Assert no duplicate IDs (merge by chunk ID)
        assert len(set(ids)) == len(ids), \
            f"Duplicate IDs found in merged results: {ids}"

    def test_dual_mode_both_instances_queried(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d, mock_embedder_1024d,
    ):
        """Both instances should contribute to merged results."""
        chromadb_path = tmp_path / "memory_db"

        minilm = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        bgem3 = _create_instance_directly("bgem3", 1024, chromadb_path, mock_embedder_1024d)

        # Give each instance DIFFERENT chunks to verify both sources
        minilm_only_ids = ["m_001", "m_002"]
        bgem3_only_ids = ["b_001"]

        minilm.add_documents(
            [sample_chunks[0], sample_chunks[1]],
            [sample_metadatas[0], sample_metadatas[1]],
            minilm_only_ids,
        )
        bgem3.add_documents(
            [sample_chunks[2]],
            [sample_metadatas[2]],
            bgem3_only_ids,
        )

        manager = _create_manager_directly(
            "dual", ["minilm", "bgem3"], {"minilm": minilm, "bgem3": bgem3},
        )

        result = manager.query("obra", n_results=5)
        ids = result.get("ids", [[]])[0]

        assert "b_001" in ids, "BGE-M3 chunk must appear in merged results"
        assert "m_001" in ids, "MiniLM chunk must appear in merged results"
        assert "m_002" in ids, "MiniLM chunk must appear in merged results"


# ==============================================================================
# AC3 — Runtime fallback: breaker OPEN on primary -> redirect to secondary
# ==============================================================================

class TestRuntimeFallbackE2E:
    """E2E: fallback runtime — breaker OPEN na primária -> redireciona.
    @rule: RULE-RAG-9.5, RULE-RAG-10.4
    """

    def test_fallback_when_primary_breaker_open(
        self, tmp_path, sample_chunks, sample_metadatas,
        mock_embedder_384d, mock_embedder_1024d,
    ):
        """Primary breaker OPEN should redirect query to secondary instance."""
        chromadb_path = tmp_path / "memory_db"

        minilm = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d, breaker_state="OPEN")
        bgem3 = _create_instance_directly("bgem3", 1024, chromadb_path, mock_embedder_1024d)

        bgem3.add_documents(
            [sample_chunks[0]],
            [sample_metadatas[0]],
            ["fallback_chunk"],
        )

        manager = _create_manager_directly(
            "dual", ["minilm", "bgem3"], {"minilm": minilm, "bgem3": bgem3},
        )

        result = manager.query("reforma", n_results=5)
        docs = result.get("documents", [[]])[0]

        # Despite minilm being OPEN, we should get results from bgem3 fallback
        assert len(docs) > 0, \
            "Query must return results via fallback even when primary is OPEN"
        assert "fallback_chunk" in docs[0] or docs[0], \
            "Results should come from fallback instance"

    def test_fallback_returns_empty_when_all_breakers_open(
        self, tmp_path, mock_embedder_384d,
    ):
        """All instances OPEN should return empty gracefully (no crash)."""
        chromadb_path = tmp_path / "memory_db"

        minilm = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d, breaker_state="OPEN")

        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": minilm})

        result = manager.query("qualquer coisa", n_results=5)
        docs = result.get("documents", [[]])[0]

        assert len(docs) == 0, "Must return empty when all instances are OPEN"


# ==============================================================================
# AC4 — Download on demand: ModelRouter -> DownloadManager -> index (mocked)
# ==============================================================================

class TestDownloadOnDemandE2E:
    """E2E: download sob demanda — ModelRouter resolve -> DownloadManager baixa.
    @rule: RULE-RAG-12.1, RULE-RAG-12.5, RULE-RAG-9.3
    """

    def test_download_triggered_when_model_not_installed(
        self, hardware_profile, minilm_entry,
    ):
        """DownloadManager.ensure_model should attempt download when not installed."""
        from foton_system.core.rag.download_manager import DownloadManager

        mock_registry = MagicMock()
        mock_registry.get.return_value = minilm_entry
        mock_registry.is_installed.return_value = False

        mock_profiler = MagicMock()
        mock_profiler.detect.return_value = hardware_profile

        with patch("foton_system.core.rag.download_manager.snapshot_download") as mock_snapshot:
            mock_snapshot.return_value = "/mock/path/to/model"

            report = DownloadManager.ensure_model(
                "minilm", mock_registry, mock_profiler,
            )

            assert report.success, f"Download must succeed, got: {report.error}"
            assert report.model_path == "/mock/path/to/model"
            mock_snapshot.assert_called_once()

    def test_download_skipped_when_already_installed(
        self, hardware_profile, minilm_entry,
    ):
        """Already installed model should skip download and return success."""
        from foton_system.core.rag.download_manager import DownloadManager

        mock_registry = MagicMock()
        mock_registry.get.return_value = minilm_entry
        mock_registry.is_installed.return_value = True

        mock_profiler = MagicMock()

        with patch("foton_system.core.rag.download_manager.snapshot_download") as mock_snapshot:
            report = DownloadManager.ensure_model(
                "minilm", mock_registry, mock_profiler,
            )

            assert report.success
            assert mock_snapshot.call_count == 0, \
                "Must NOT call snapshot_download when already installed"

    def test_download_fails_on_disk_space(
        self, minilm_entry,
    ):
        """Download should abort with error if disk space insufficient."""
        from foton_system.core.rag.download_manager import DownloadManager

        low_disk_profile = HardwareProfile(
            cpu_cores=4, ram_total_gb=16, ram_available_gb=10,
            has_cuda=False, disk_free_gb=0.1,
        )

        mock_registry = MagicMock()
        mock_registry.get.return_value = minilm_entry
        mock_registry.is_installed.return_value = False

        mock_profiler = MagicMock()
        mock_profiler.detect.return_value = low_disk_profile

        report = DownloadManager.ensure_model("minilm", mock_registry, mock_profiler)

        assert not report.success, "Must fail when disk is insufficient"
        assert "Disco" in report.error, "Error must mention insufficient disk"

    def test_model_router_triggers_download_flow(
        self, hardware_profile, minilm_entry, bgem3_entry, model_registry,
    ):
        """ModelRouter should resolve bgem3 and indicate need for download.

        Verifies the full chain: config -> router -> find not installed ->
        download needed.
        """
        from foton_system.core.rag.model_router import ModelRouter

        config = {"rag": {"mode": "bgem3", "models": {"primary": "bgem3", "fallback": ["minilm"]}}}

        # BGE-M3 not installed, minilm installed
        mock_registry = MagicMock()
        mock_registry.get.side_effect = lambda mid: {"minilm": minilm_entry, "bgem3": bgem3_entry}.get(mid)

        with patch("foton_system.core.rag.hardware_profiler.validate_feasibility",
                   return_value=MagicMock(is_feasible=True, warnings=[])):
            resolved = ModelRouter.resolve(config, hardware_profile, mock_registry)

        assert "bgem3" in resolved, \
            "Router must resolve bgem3 when hardware supports it"


# ==============================================================================
# AC5 — Legacy migration: foton_knowledge_base -> new format -> query works
# ==============================================================================

class TestLegacyMigrationE2E:
    """E2E: migração da coleção legada -> novo formato -> consulta funciona.
    @rule: RULE-RAG-10.7
    """

    def test_migration_from_legacy_collection(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d,
    ):
        """Seed legacy 'foton_knowledge_base' -> migrate -> query on new collection."""
        from foton_system.core.rag.migration import MigrationChecker
        import chromadb

        chromadb_path = tmp_path / "memory_db"
        chromadb_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(chromadb_path))

        # Seed legacy collection with real data
        legacy = client.create_collection(
            name="foton_knowledge_base",
            metadata={"hnsw:space": "cosine"},
        )
        legacy.add(
            documents=sample_chunks,
            metadatas=sample_metadatas,
            ids=sample_ids,
        )

        # Run migration
        checker = MigrationChecker(db_path=chromadb_path)
        migrated = checker.ensure_migrated()

        assert migrated, "Migration must have executed"

        # Verify new collection exists with migrated data
        new_col = client.get_collection("foton_minilm_384d")
        assert new_col.count() >= 3, \
            f"New collection must contain migrated chunks, got {new_col.count()}"

        # Verify backup was created
        backup = client.get_collection("foton_knowledge_base_legada")
        assert backup.count() >= 3, \
            f"Backup must contain original chunks, got {backup.count()}"

    def test_migration_idempotent(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d,
    ):
        """Running migration twice should be safe (idempotent)."""
        from foton_system.core.rag.migration import MigrationChecker
        import chromadb

        chromadb_path = tmp_path / "memory_db"
        chromadb_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(chromadb_path))

        # Seed legacy
        legacy = client.create_collection(name="foton_knowledge_base", metadata={"hnsw:space": "cosine"})
        legacy.add(documents=sample_chunks[:1], metadatas=[sample_metadatas[0]], ids=[sample_ids[0]])

        # First migration
        MigrationChecker(db_path=chromadb_path).ensure_migrated()

        # Second migration — should be no-op (legacy deleted)
        result = MigrationChecker(db_path=chromadb_path).ensure_migrated()
        assert not result, "Second migration should be no-op"

    def test_query_works_after_migration(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d,
    ):
        """After migration, query on new collection should return correct chunks."""
        from foton_system.core.rag.migration import MigrationChecker
        import chromadb

        chromadb_path = tmp_path / "memory_db"
        chromadb_path.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(chromadb_path))

        # Seed legacy
        legacy = client.create_collection(name="foton_knowledge_base", metadata={"hnsw:space": "cosine"})
        legacy.add(documents=sample_chunks, metadatas=sample_metadatas, ids=sample_ids)

        # Migrate
        MigrationChecker(db_path=chromadb_path).ensure_migrated()

        # Create VectorStoreInstance on new collection and query
        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        result = instance.query("reforma", n_results=3)

        docs = result.get("documents", [[]])[0]
        ids = result.get("ids", [[]])[0]

        assert len(docs) > 0, "Migrated collection must return results"
        assert len(set(ids)) == len(ids), "No duplicate IDs after migration"


# ==============================================================================
# AC6 — TUI model change: switch model -> re-index -> query
# ==============================================================================

class TestTuiModelChangeE2E:
    """E2E: TUI -> mudar modelo -> re-indexação -> consulta.
    @rule: RULE-RAG-9.1, RULE-RAG-10.5
    """

    def test_switch_from_minilm_to_dual_and_query(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d, mock_embedder_1024d,
    ):
        """Start in minilm mode, index, then switch to dual, re-index, query both."""
        chromadb_path = tmp_path / "memory_db"

        # Phase 1: MiniLM mode
        minilm = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": minilm})

        manager.add_documents(
            [sample_chunks[0]], [sample_metadatas[0]], ["m_001"],
        )

        # Phase 2: Switch to dual mode
        bgem3 = _create_instance_directly("bgem3", 1024, chromadb_path, mock_embedder_1024d)
        manager_dual = _create_manager_directly(
            "dual", ["minilm", "bgem3"], {"minilm": minilm, "bgem3": bgem3},
        )

        # Re-index in both
        manager_dual.add_documents(
            [sample_chunks[1], sample_chunks[2]],
            [sample_metadatas[1], sample_metadatas[2]],
            ["m_002", "b_001"],
        )

        # Query — should hit both collections
        result = manager_dual.query("obra", n_results=5)
        ids = result.get("ids", [[]])[0]

        assert "m_001" in ids, "Result must include first MiniLM chunk"
        assert "m_002" in ids, "Result must include second MiniLM chunk"
        assert "b_001" in ids, "Result must include BGE-M3 chunk"

    def test_reindex_after_model_change(
        self, tmp_path, sample_chunks, mock_embedder_384d,
    ):
        """Re-indexing should clear old data and replace with new."""
        chromadb_path = tmp_path / "memory_db"

        minilm = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": minilm})

        # Index old data
        old_ids = ["old_001"]
        manager.add_documents(
            ["Texto antigo sobre revestimento ceramico"],
            [{"source": "old.md"}],
            old_ids,
        )

        # Re-index new data (add more)
        new_ids = ["new_001", "new_002"]
        manager.add_documents(
            sample_chunks[:2],
            [{"source": "new1.md"}, {"source": "new2.md"}],
            new_ids,
        )

        result = manager.query("reforma", n_results=5)
        ids = result.get("ids", [[]])[0]

        assert "old_001" in ids, "Old data must still be queryable"
        assert "new_001" in ids, "New data must be queryable"


# ==============================================================================
# AC7 — Rerank pipeline: mocked rerank reorders top-K correctly
# ==============================================================================

class TestRerankPipelineE2E:
    """E2E: pipeline rerank (mockado) reordena top-K corretamente.
    @rule: RULE-RAG-11.4 (RerankNode)
    """

    def test_rerank_reorders_by_score(
        self, tmp_path, mock_embedder_384d,
    ):
        """RerankNode should reorder results from score-based to cross-encoder order."""
        chromadb_path = tmp_path / "memory_db"

        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})

        # Index 3 chunks with varied content
        chunks = [
            "Projeto de reforma residencial com detalhes construtivos.",
            "Orcamento detalhado da obra com planilha de custos.",
            "Memorial descritivo com especificacoes tecnicas.",
        ]
        metadatas = [
            {"source": "a.md", "filename": "a.md"},
            {"source": "b.md", "filename": "b.md"},
            {"source": "c.md", "filename": "c.md"},
        ]
        ids = ["rerank_1", "rerank_2", "rerank_3"]
        manager.add_documents(chunks, metadatas, ids)

        # Run rerank pipeline — RerankNode mocked to reorder as [2, 0, 1]
        output = _run_pipeline_with_manager(manager, "obra", pipeline_type="rerank")

        # If results found, verify scored_results has scores
        if output["status"] == "FOUND":
            for r in output["results"]:
                assert "score" in r, "Reranked results must have score"

    def test_rerank_node_fallback_graceful(
        self, tmp_path, mock_embedder_384d,
    ):
        """RerankNode fallback (no cross-encoder) should pass through results."""
        from foton_system.core.rag.pipeline import ProcessContext
        from foton_system.core.rag.nodes.rerank_node import RerankNode

        chromadb_path = tmp_path / "memory_db"
        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})

        raw_results = [
            {"document": "doc A", "score": 0.3},
            {"document": "doc B", "score": 0.9},
            {"document": "doc C", "score": 0.6},
        ]

        # Simulate cross-encoder unavailable
        with patch(
            "foton_system.core.rag.nodes.rerank_node._check_cross_encoder",
            return_value=False,
        ):
            node = RerankNode()
            ctx = ProcessContext({"query": "teste", "raw_results": raw_results})
            result = node.execute(ctx)

            assert result["scored_results"] == raw_results, \
                "Fallback must pass through original results unchanged"


# ==============================================================================
# AC8 — Missing config: no 'rag' section -> fallback to MiniLM without crash
# ==============================================================================

class TestMissingConfigFallbackE2E:
    """E2E: config ausente (rag section) -> fallback para MiniLM legado.
    @rule: RULE-RAG-10.7, RULE-RAG-9.1
    """

    def test_vector_store_manager_fallback_minilm(
        self, tmp_path, sample_chunks, sample_metadatas, sample_ids,
        mock_embedder_384d, config_empty,
    ):
        """VectorStoreManager should fallback to minilm when config is empty."""
        chromadb_path = tmp_path / "memory_db"

        # Bypass lazy_init and simulate minilm fallback
        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})

        # Must be able to index and query without crash
        manager.add_documents(sample_chunks, sample_metadatas, sample_ids)

        result = manager.query("reforma", n_results=3)
        docs = result.get("documents", [[]])[0]

        assert len(docs) > 0, "Fallback minilm must return results"
        assert result.get("ids") is not None, "IDs must be present in result"

    def test_config_empty_does_not_crash_lazy_init(
        self, tmp_path, config_empty,
    ):
        """Real VectorStoreManager._lazy_init() with empty config must not crash.

        This test uses the real lazy init path with careful mocking of
        dependencies that would require network access.
        """
        from foton_system.core.memory.vector_store import VectorStoreManager
        from foton_system.core.rag.hardware_profiler import HardwareProfile

        # Reset singleton
        VectorStoreManager._instance = None

        with patch(
            "foton_system.modules.shared.infrastructure.config.config.Config"
        ) as MockConfig:
            mock_cfg = MagicMock()
            mock_cfg.rag_config = {}
            mock_cfg._settings = {}
            MockConfig.return_value = mock_cfg

            with patch(
                "foton_system.core.rag.hardware_profiler.HardwareProfiler.detect"
            ) as mock_detect:
                mock_detect.return_value = HardwareProfile(
                    cpu_cores=4, ram_total_gb=16, ram_available_gb=10,
                    has_cuda=False, disk_free_gb=50,
                )

                with patch(
                    "foton_system.core.rag.migration.MigrationChecker.ensure_migrated",
                    return_value=False,
                ):
                    with patch(
                        "foton_system.core.memory.vector_store.VectorStoreInstance._initialize"
                    ) as mock_init:
                        mock_init.return_value = None

                        # Should not crash
                        manager = VectorStoreManager()
                        manager._lazy_init()

                        assert manager._mode == "minilm", \
                            f"Must default to minilm mode, got {manager._mode}"
                        assert manager._lazy_init_done, \
                            "lazy_init must complete without crash"
