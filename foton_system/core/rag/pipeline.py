from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from typing import Any, Dict, List, Optional, Iterator

from foton_system.modules.shared.infrastructure.config.config import Config

_VALID_CONTEXT_KEYS: set = {
    "query", "embeddings", "raw_results", "scored_results",
    "formatted_output", "n_results", "where",
}

_NODE_REGISTRY: Dict[str, str] = {
    "embed": "foton_system.core.rag.nodes.embed_node.EmbedNode",
    "search": "foton_system.core.rag.nodes.search_node.SearchNode",
    "rerank": "foton_system.core.rag.nodes.rerank_node.RerankNode",
    "format": "foton_system.core.rag.nodes.format_node.FormatNode",
}

_PIPELINE_PRESETS: Dict[str, List[str]] = {
    "simple": ["embed", "search", "format"],
    "rerank": ["embed", "search", "rerank", "format"],
}


class ProcessContext(MutableMapping):
    _keys: set

    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        self._keys = set(_VALID_CONTEXT_KEYS)
        self._data: Dict[str, Any] = {}
        if initial:
            for k, v in initial.items():
                self._validate_key(k)
                self._data[k] = v

    def _validate_key(self, key: str) -> None:
        if key not in self._keys:
            raise KeyError(f"Chave '{key}' não é válida para ProcessContext. Válidas: {sorted(self._keys)}")

    def __getitem__(self, key: str) -> Any:
        self._validate_key(key)
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._validate_key(key)
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        self._validate_key(key)
        del self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key not in self._keys:
            self._keys.add(key)
        if key not in self._data:
            self._data[key] = default
        return self._data[key]

    def __repr__(self) -> str:
        return f"ProcessContext({self._data})"


class PipelineNode(ABC):
    name: str = ""
    input_keys: List[str] = []
    output_keys: List[str] = []

    @abstractmethod
    def execute(self, context: ProcessContext) -> ProcessContext:
        ...


class RagPipeline:
    def __init__(self, pipeline_type: Optional[str] = None, nodes: Optional[List[str]] = None) -> None:
        self._pipeline_type = pipeline_type or "simple"
        self._node_names = nodes or _PIPELINE_PRESETS.get(self._pipeline_type, _PIPELINE_PRESETS["simple"])
        self._nodes: List[PipelineNode] = []
        self._build()

    def _build(self) -> None:
        for name in self._node_names:
            node = self._instantiate_node(name)
            if node is None:
                if name == "rerank":
                    continue
                raise ValueError(f"Nó de pipeline desconhecido: '{name}'")
            self._nodes.append(node)

    def _instantiate_node(self, name: str) -> Optional[PipelineNode]:
        import importlib
        path = _NODE_REGISTRY.get(name)
        if not path:
            return None
        mod_path, cls_name = path.rsplit(".", 1)
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            return cls()
        except Exception:
            if name == "rerank":
                return None
            raise

    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> ProcessContext:
        context = ProcessContext(initial_context or {})
        context.setdefault("n_results", 5)
        context.setdefault("where", None)
        for node in self._nodes:
            context = node.execute(context)
        return context

    @classmethod
    def from_config(cls) -> "RagPipeline":
        config = Config()
        rag_cfg = config.rag_config
        pipeline_cfg = rag_cfg.get("pipeline", {})
        pipeline_type = pipeline_cfg.get("type", "simple")
        custom_nodes = pipeline_cfg.get("nodes", None)
        return cls(pipeline_type=pipeline_type, nodes=custom_nodes)
