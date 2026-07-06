# @story: STORY-030
# @rule: RULE-RAG-8.1, RULE-RAG-8.2, RULE-RAG-8.3, RULE-RAG-8.4

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelEntry:
    id: str
    name: str
    type: str
    dimensions: int
    ram_required_gb: float
    disk_required_gb: float
    requires_gpu: bool = False
    is_default: bool = False


_DEFAULT_MODELS = [
    ModelEntry(
        id="minilm",
        name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        type="embedding",
        dimensions=384,
        ram_required_gb=1.0,
        disk_required_gb=0.5,
        requires_gpu=False,
        is_default=True,
    ),
    ModelEntry(
        id="bgem3",
        name="BAAI/bge-m3",
        type="embedding",
        dimensions=1024,
        ram_required_gb=4.5,
        disk_required_gb=2.5,
        requires_gpu=False,
        is_default=False,
    ),
]


class ModelRegistry:
    _instance: Optional['ModelRegistry'] = None

    def __new__(cls) -> 'ModelRegistry':
        if cls._instance is None:
            cls._instance = super(ModelRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._models: Dict[str, ModelEntry] = {}
        for entry in _DEFAULT_MODELS:
            self._models[entry.id] = entry
        self._initialized = True

    def list_models(self) -> List[ModelEntry]:
        return list(self._models.values())

    def get(self, model_id: str) -> Optional[ModelEntry]:
        return self._models.get(model_id)

    def register(self, entry: ModelEntry) -> None:
        self._models[entry.id] = entry
        logger.info(f"Modelo registrado: {entry.id} ({entry.name})")

    def is_installed(self, model_id: str) -> bool:
        entry = self._models.get(model_id)
        if entry is None:
            logger.warning(f"is_installed: modelo '{model_id}' não encontrado no registry.")
            return False

        hf_home = os.environ.get(
            "HF_HOME",
            os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
        )
        hub_name = "models--" + entry.name.replace("/", "--")
        model_path = Path(hf_home) / "hub" / hub_name
        installed = model_path.exists()
        logger.debug(f"Modelo '{model_id}' em {model_path}: {'instalado' if installed else 'ausente'}")
        return installed

    def available_models(self, hardware_profile) -> List[ModelEntry]:
        available = []
        for entry in self._models.values():
            if hardware_profile.ram_available_gb < entry.ram_required_gb:
                continue
            if hardware_profile.disk_free_gb < entry.disk_required_gb:
                continue
            if entry.requires_gpu and not (hardware_profile.has_cuda or hardware_profile.has_mps):
                continue
            available.append(entry)
        return available

    @classmethod
    def reset(cls):
        cls._instance = None
