# @story: STORY-036
# @rule: RULE-RAG-7.1 a 12.5

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Dict, List

from foton_system.core.rag.hardware_profiler import HardwareProfile
from foton_system.core.rag.model_registry import ModelEntry, ModelRegistry


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "rag_e2e"


# ==============================================================================
# Sample chunks for indexing
# ==============================================================================

@pytest.fixture
def sample_chunks() -> List[str]:
    """Three realistic document chunks for architecture firm context."""
    return [
        "A reforma do apartamento 502 inclui a substituicao do piso existente "
        "por porcelanato acetinado 80x80cm nas areas sociais.",
        "O custo total estimado da obra e de R$ 180.000,00, distribuidos em "
        "R$ 75.000,00 em materiais e R$ 85.000,00 em mao de obra.",
        "O escopo do projeto inclui: levantamento arquitetonico, estudo "
        "preliminar, anteprojeto, projeto legal e projeto executivo.",
    ]


@pytest.fixture
def sample_metadatas() -> List[Dict[str, str]]:
    """Metadata matching each sample chunk."""
    return [
        {"source": "clientes/ClienteX/PROJETOS/memorial.md", "filename": "memorial.md", "cliente": "ClienteX"},
        {"source": "clientes/ClienteX/FINANCEIRO/orcamento.md", "filename": "orcamento.md", "cliente": "ClienteX"},
        {"source": "clientes/ClienteY/PROJETOS/escopo.md", "filename": "escopo.md", "cliente": "ClienteY"},
    ]


@pytest.fixture
def sample_ids() -> List[str]:
    return ["chunk_001", "chunk_002", "chunk_003"]


# ==============================================================================
# Hardware profile fixture
# ==============================================================================

@pytest.fixture
def hardware_profile() -> HardwareProfile:
    """Realistic hardware profile for E2E tests (16GB RAM, no GPU)."""
    return HardwareProfile(
        cpu_cores=8,
        ram_total_gb=16.0,
        ram_available_gb=10.0,
        has_cuda=False,
        cuda_version="",
        has_mps=False,
        vram_gb=0.0,
        disk_free_gb=50.0,
    )


# ==============================================================================
# Mock embedder that returns fixed-dimension vectors
# ==============================================================================

@pytest.fixture
def mock_embedder_384d():
    """Mock SentenceTransformer returning 384-dim vectors (MiniLM).

    Each call to encode() returns embeddings matching the number of documents.
    """
    mock = MagicMock()

    def encode_side_effect(documents, *args, **kwargs):
        n = len(documents) if isinstance(documents, list) else 1
        mock_result = MagicMock()
        mock_result.tolist.return_value = [[0.1] * 384 for _ in range(n)]
        return mock_result

    mock.encode.side_effect = encode_side_effect
    return mock


@pytest.fixture
def mock_embedder_1024d():
    """Mock SentenceTransformer returning 1024-dim vectors (BGE-M3).

    Each call to encode() returns embeddings matching the number of documents.
    """
    mock = MagicMock()

    def encode_side_effect(documents, *args, **kwargs):
        n = len(documents) if isinstance(documents, list) else 1
        mock_result = MagicMock()
        mock_result.tolist.return_value = [[0.1] * 1024 for _ in range(n)]
        return mock_result

    mock.encode.side_effect = encode_side_effect
    return mock


# ==============================================================================
# Config fixtures
# ==============================================================================

@pytest.fixture
def config_minilm() -> dict:
    with open(FIXTURES_DIR / "config_minilm.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def config_dual() -> dict:
    with open(FIXTURES_DIR / "config_dual.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def config_empty() -> dict:
    with open(FIXTURES_DIR / "config_empty.json", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# ModelRegistry fixture (real catalog, no network needed)
# ==============================================================================

@pytest.fixture
def model_registry() -> ModelRegistry:
    uri = ModelRegistry._instance
    ModelRegistry._instance = None
    registry = ModelRegistry()
    ModelRegistry._instance = uri
    return registry


@pytest.fixture
def minilm_entry() -> ModelEntry:
    return ModelEntry(
        id="minilm",
        name="paraphrase-multilingual-MiniLM-L12-v2",
        type="embedding",
        dimensions=384,
        ram_required_gb=1.0,
        disk_required_gb=0.5,
        requires_gpu=False,
        is_default=True,
    )


@pytest.fixture
def bgem3_entry() -> ModelEntry:
    return ModelEntry(
        id="bgem3",
        name="BAAI/bge-m3",
        type="embedding",
        dimensions=1024,
        ram_required_gb=4.5,
        disk_required_gb=2.5,
        requires_gpu=False,
        is_default=False,
    )


# ==============================================================================
# E2E environment: temp ChromaDB dir + mock embedder
# ==============================================================================

class RagE2EEnvironment:
    """Holds all components needed for an E2E RAG test.

    Encapsulates:
    - Temp ChromaDB directory
    - Mocked embedder injection into VectorStoreInstance
    - Cleanup on exit
    """

    def __init__(self, tmp_path: Path, hardware_profile: HardwareProfile):
        self.tmp_path = tmp_path
        self.chromadb_path = tmp_path / "memory_db"
        self.chromadb_path.mkdir(parents=True, exist_ok=True)
        self.hardware = hardware_profile
        self._patches: List = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for p in self._patches:
            p.stop()
        shutil.rmtree(self.tmp_path, ignore_errors=True)

    def patch_embedder(self, model_tag: str, mock_embedder):
        """Inject mock embedder into VectorStoreInstance for a given tag."""
        from foton_system.core.memory.vector_store import VectorStoreInstance

        original_init = VectorStoreInstance._initialize

        def patched_init(instance):
            instance.embedder = mock_embedder
            instance._breaker = MagicMock()
            instance._breaker.call = lambda f, *a, **kw: f(*a, **kw)
            instance._initialized = True

        patcher = patch.object(VectorStoreInstance, "_initialize", patched_init)
        self._patches.append(patcher)
        patcher.start()

    def create_chromadb_collection(self, name: str, dimensions: int = 384):
        """Create a real ChromaDB collection for testing."""
        import chromadb
        client = chromadb.PersistentClient(path=str(self.chromadb_path))
        return client.get_or_create_collection(
            name=name,
            metadata={
                "hnsw:space": "cosine",
                "model_tag": name.split("_")[1],
                "dimensions": str(dimensions),
            },
        )


@pytest.fixture
def rag_e2e_env(tmp_path, hardware_profile):
    """Fixture that provides a RagE2EEnvironment."""
    env = RagE2EEnvironment(tmp_path, hardware_profile)
    yield env
    for p in env._patches:
        p.stop()
