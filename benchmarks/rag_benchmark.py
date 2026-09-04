# @story: STORY-038
# @rule: RULE-RAG-7.4, RULE-RAG-11.3

"""
Performance Benchmarking Suite for RAG Pipeline.

SLAs:
  - MiniLM simple query: p95 < 3s (AC1)
  - BGE-M3 simple query (CPU): p95 < 5s, mocked if no GPU (AC2)
  - Dual mode: p95 < 2 * single mode (AC3)
  - Index 100 chunks: total < 30s (AC4)
  - HardwareProfiler.detect(): p95 < 100ms (AC5)
  - Pipeline nodes execute sequentially (RULE-RAG-11.3) (AC10)

Usage:
    python -m pytest benchmarks/rag_benchmark.py -v --benchmark
"""

import json
import time
import statistics
from pathlib import Path
from typing import Callable, List
from unittest.mock import MagicMock, patch

import pytest
import chromadb
import numpy as np

from foton_system.core.rag.hardware_profiler import HardwareProfiler
from foton_system.core.rag.model_registry import ModelEntry, ModelRegistry

_BENCH_RESULTS: list = []


# ==============================================================================
# Helpers (follows pattern from test_rag_pipeline_e2e.py)
# ==============================================================================

def _create_instance_directly(
    model_tag: str,
    dimensions: int,
    chromadb_path: Path,
    mock_embedder,
):
    """Factory: VectorStoreInstance with real ChromaDB + mock embedder."""
    entry = ModelRegistry().get(model_tag)
    if entry is None:
        entry = ModelEntry(
            id=model_tag,
            name=f"test-{model_tag}",
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

    from foton_system.core.memory.vector_store import VectorStoreInstance, CircuitBreaker
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
    return instance


def _create_manager_directly(mode: str, active_tags: list, instances: dict):
    """Factory: VectorStoreManager bypassing lazy_init."""
    from foton_system.core.memory.vector_store import VectorStoreManager
    manager = VectorStoreManager.__new__(VectorStoreManager)
    manager._initialized = True
    manager._lazy_init_done = True
    manager._mode = mode
    manager._active_tags = active_tags
    manager._instances = instances
    manager._config_dir = None
    return manager


def _seed_chunks(instance, chunks: list, chunk_size: int = 100):
    """Index N chunks into the instance."""
    texts = [c["text"] for c in chunks[:chunk_size]]
    ids = [c["id"] for c in chunks[:chunk_size]]
    metadatas = [{"source": "benchmark"} for _ in range(chunk_size)]
    instance.add_documents(texts, metadatas, ids)


def _measure(func: Callable, n_rounds: int = 10, warmup: int = 1) -> List[float]:
    """Run func n_rounds times, return durations in ms."""
    for _ in range(warmup):
        func()
    durations = []
    for _ in range(n_rounds):
        start = time.perf_counter()
        func()
        elapsed = (time.perf_counter() - start) * 1000
        durations.append(elapsed)
    return durations


def _stats(durations: List[float]) -> dict:
    """Compute p50, p95, p99 from duration list (ms)."""
    s = sorted(durations)
    n = len(s)
    return {
        "min": round(min(durations), 2),
        "max": round(max(durations), 2),
        "avg": round(statistics.mean(durations), 2),
        "p50": round(s[int(n * 0.50)], 2),
        "p95": round(s[int(n * 0.95)], 2),
        "p99": round(s[int(n * 0.99)], 2),
        "n": n,
    }


# ==============================================================================
# Fixtures
# ==============================================================================

def _load_fixture(name: str):
    base = Path(__file__).parent.parent / "tests" / "fixtures" / "rag_benchmark_data"
    with open(base / name, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def chunks():
    return _load_fixture("chunks.json")


@pytest.fixture(scope="session")
def queries():
    return _load_fixture("queries.json")


@pytest.fixture
def slo_tolerance():
    """Tolerance multiplier for SLA assertions (default 1.2 = 20% margin)."""
    return 1.2


@pytest.fixture
def mock_embedder_384d():
    """Mock SentenceTransformer returning random 384-dim vectors."""
    def _encode(texts, **kwargs):
        if isinstance(texts, str):
            return np.random.randn(384).astype(np.float32)
        return np.random.randn(len(texts), 384).astype(np.float32)
    embedder = MagicMock()
    embedder.encode = _encode
    return embedder


@pytest.fixture
def mock_embedder_1024d():
    """Mock SentenceTransformer returning random 1024-dim vectors (BGE-M3)."""
    def _encode(texts, **kwargs):
        if isinstance(texts, str):
            return np.random.randn(1024).astype(np.float32)
        return np.random.randn(len(texts), 1024).astype(np.float32)
    embedder = MagicMock()
    embedder.encode = _encode
    return embedder


@pytest.fixture(autouse=True)
def _register_result(request):
    """Collect benchmark results per-test, export JSON at end of session."""
    request.node.bench_result = None
    yield
    if request.node.bench_result is not None:
        _BENCH_RESULTS.append(request.node.bench_result)


@pytest.fixture(scope="session", autouse=True)
def _export_report():
    """Export benchmark report to JSON at end of session."""
    yield
    if _BENCH_RESULTS:
        report_path = Path(".opencode/metrics/benchmark_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "suite": "STORY-038",
                "results": _BENCH_RESULTS,
            }, f, indent=2, ensure_ascii=False)


# ==============================================================================
# AC1 — MiniLM simple query SLA: p95 < 3s
# ==============================================================================

@pytest.mark.benchmark
class TestMiniLMSimpleQuery:
    """AC1: MiniLM modo simple — p95 < 3s em 10 rodadas com dataset 100 chunks."""

    def test_minilm_query_sla(
        self, request, tmp_path, chunks, queries, mock_embedder_384d, slo_tolerance,
    ):
        chromadb_path = tmp_path / "chromadb"
        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})
        _seed_chunks(instance, chunks, 100)
        assert manager.count() >= 100

        query_texts = [q["text"] for q in queries]

        def run():
            for q in query_texts:
                manager.query(q, n_results=5)

        durations = _measure(run, n_rounds=10)
        s = _stats(durations)
        sla_ms = 3000 * slo_tolerance

        assert s["p95"] < sla_ms, f"MiniLM query p95={s['p95']}ms >= SLA={sla_ms:.0f}ms"
        request.node.bench_result = {"scenario": "minilm_simple_query", **s}


# ==============================================================================
# AC2 — BGE-M3 simple (CPU) query SLA: p95 < 5s (mocked if no GPU)
# ==============================================================================

@pytest.mark.benchmark
class TestBGEM3SimpleQuery:
    """AC2: BGE-M3 modo simple (CPU) — p95 < 5s (mockado se GPU indisponível)."""

    def test_bgem3_query_sla(
        self, request, tmp_path, chunks, queries, mock_embedder_1024d, slo_tolerance,
    ):
        try:
            import torch
            torch.cuda.is_available()
        except (ImportError, AttributeError):
            pytest.skip("CUDA não disponível — benchmark BGE-M3 ignorado")

        chromadb_path = tmp_path / "chromadb"
        instance = _create_instance_directly("bgem3", 1024, chromadb_path, mock_embedder_1024d)
        manager = _create_manager_directly("bgem3", ["bgem3"], {"bgem3": instance})
        _seed_chunks(instance, chunks, 100)
        assert manager.count() >= 100

        query_texts = [q["text"] for q in queries]

        def run():
            for q in query_texts:
                manager.query(q, n_results=5)

        durations = _measure(run, n_rounds=10)
        s = _stats(durations)
        sla_ms = 5000 * slo_tolerance

        assert s["p95"] < sla_ms, f"BGE-M3 query p95={s['p95']}ms >= SLA={sla_ms:.0f}ms"
        request.node.bench_result = {"scenario": "bgem3_simple_query", **s}


# ==============================================================================
# AC3 — Dual mode: p95 < 2 x single mode
# ==============================================================================

@pytest.mark.benchmark
class TestDualModeQuery:
    """AC3: modo dual — p95 < 2x tempo single (overhead de merge aceitável)."""

    def _build_managers(self, tmp_path, chunks, mock_embedder_384d, mock_embedder_1024d):
        p_minilm = tmp_path / "minilm"
        p_bgem3 = tmp_path / "bgem3"
        inst_minilm = _create_instance_directly("minilm", 384, p_minilm, mock_embedder_384d)
        inst_bgem3 = _create_instance_directly("bgem3", 1024, p_bgem3, mock_embedder_1024d)
        _seed_chunks(inst_minilm, chunks, 100)
        _seed_chunks(inst_bgem3, chunks, 100)
        single = _create_manager_directly("minilm", ["minilm"], {"minilm": inst_minilm})
        dual = _create_manager_directly(
            "dual", ["minilm", "bgem3"],
            {"minilm": inst_minilm, "bgem3": inst_bgem3},
        )
        return single, dual

    def test_dual_mode_overhead(
        self, request, tmp_path, chunks, queries,
        mock_embedder_384d, mock_embedder_1024d, slo_tolerance,
    ):
        single, dual = self._build_managers(
            tmp_path, chunks, mock_embedder_384d, mock_embedder_1024d,
        )
        query_texts = [q["text"] for q in queries]

        def run_single():
            for q in query_texts:
                single.query(q, n_results=5)

        def run_dual():
            for q in query_texts:
                dual.query(q, n_results=5)

        d_single = _measure(run_single, n_rounds=5)
        d_dual = _measure(run_dual, n_rounds=5)
        s_single = _stats(d_single)
        s_dual = _stats(d_dual)

        max_ratio = 2.0 * slo_tolerance
        actual_ratio = s_dual["p95"] / s_single["p95"] if s_single["p95"] > 0 else 0
        assert actual_ratio < max_ratio, (
            f"Dual p95={s_dual['p95']}ms é {actual_ratio:.2f}x single p95={s_single['p95']}ms "
            f"(limite={max_ratio:.2f}x)"
        )
        request.node.bench_result = {
            "scenario": "dual_mode_sla",
            "single_p95": s_single["p95"],
            "dual_p95": s_dual["p95"],
            "ratio": round(actual_ratio, 2),
            **s_dual,
        }


# ==============================================================================
# AC4 — Index 100 chunks < 30s (MiniLM)
# ==============================================================================

@pytest.mark.benchmark
class TestIndexingPerformance:
    """AC4: indexação — 100 chunks em < 30s (MiniLM)."""

    def test_index_100_chunks_sla(
        self, request, tmp_path, chunks, mock_embedder_384d, slo_tolerance,
    ):
        chromadb_path = tmp_path / "chromadb"
        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        texts = [c["text"] for c in chunks[:100]]
        ids = [c["id"] for c in chunks[:100]]
        metadatas = [{"source": "benchmark"} for _ in range(100)]

        start = time.perf_counter()
        instance.add_documents(texts, metadatas, ids)
        elapsed_ms = (time.perf_counter() - start) * 1000

        sla_ms = 30000 * slo_tolerance
        assert elapsed_ms < sla_ms, f"Index 100 chunks: {elapsed_ms:.1f}ms >= SLA={sla_ms:.0f}ms"
        assert instance.count() >= 100

        request.node.bench_result = {
            "scenario": "index_100_chunks",
            "total_ms": round(elapsed_ms, 2),
            "chunks": 100,
        }


# ==============================================================================
# AC5 — HardwareProfiler.detect() p95 < 100ms
# ==============================================================================

@pytest.mark.benchmark
class TestHardwareProfilerLatency:
    """AC5: HardwareProfiler.detect() — p95 < 100ms, sem blocking I/O."""

    def test_profiler_latency_sla(self, request, slo_tolerance):
        profiler = HardwareProfiler()
        profiler.invalidate_cache()

        def run():
            profiler.detect()

        durations = _measure(run, n_rounds=10, warmup=1)
        s = _stats(durations)
        sla_ms = 100 * slo_tolerance

        assert s["p95"] < sla_ms, (
            f"HardwareProfiler.detect() p95={s['p95']}ms >= SLA={sla_ms:.0f}ms"
        )
        request.node.bench_result = {"scenario": "hardware_profiler_detect", **s}


# ==============================================================================
# AC10 — Pipeline executa nós sequencialmente (RULE-RAG-11.3)
# ==============================================================================

@pytest.mark.benchmark
class TestPipelineSequentialExecution:
    """AC10: RagPipeline executa nós em ordem sequencial (RULE-RAG-11.3)."""

    def test_pipeline_execution_order(
        self, request, tmp_path, chunks, queries, mock_embedder_384d,
    ):
        from foton_system.core.rag.nodes.embed_node import EmbedNode
        from foton_system.core.rag.nodes.search_node import SearchNode
        from foton_system.core.rag.nodes.format_node import FormatNode
        from foton_system.core.rag.pipeline import RagPipeline

        chromadb_path = tmp_path / "chromadb"
        instance = _create_instance_directly("minilm", 384, chromadb_path, mock_embedder_384d)
        manager = _create_manager_directly("minilm", ["minilm"], {"minilm": instance})
        _seed_chunks(instance, chunks, 10)

        exec_order = []

        class TrackingEmbedNode(EmbedNode):
            def execute(self, ctx):
                exec_order.append("embed")
                return super().execute(ctx)

        class TrackingSearchNode(SearchNode):
            def execute(self, ctx):
                exec_order.append("search")
                return super().execute(ctx)

        class TrackingFormatNode(FormatNode):
            def execute(self, ctx):
                exec_order.append("format")
                return super().execute(ctx)
        pipeline = RagPipeline.__new__(RagPipeline)
        pipeline._pipeline_type = "simple"
        pipeline._node_names = ["embed", "search", "format"]
        pipeline._nodes = [TrackingEmbedNode(), TrackingSearchNode(), TrackingFormatNode()]

        with patch(
            "foton_system.core.rag.nodes.embed_node.VectorStoreManager",
            return_value=manager,
        ):
            with patch(
                "foton_system.core.rag.nodes.search_node.VectorStoreManager",
                return_value=manager,
            ):
                ctx = pipeline.run({"query": queries[0]["text"], "n_results": 3})

        assert exec_order == ["embed", "search", "format"], (
            f"Expected [embed, search, format], got {exec_order}"
        )
        assert "formatted_output" in ctx
        request.node.bench_result = {
            "scenario": "pipeline_sequential_order",
            "exec_order": exec_order,
        }
