"""JSON Schema validation for the `rag` section of settings.json.

@story: STORY-040
@rule: RULE-RAG-9.1
@rule: RULE-RAG-9.4
@rule: RULE-RAG-10.7
@rule: RULE-RAG-11.5
"""

import copy
import logging
from typing import Any, Dict

import jsonschema

logger = logging.getLogger("foton_config")

RAG_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "embedding_mode": {
            "type": "string",
            "enum": ["minilm", "bgem3", "dual"],
        },
        "pipeline": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["simple", "rerank"],
                },
                "nodes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "additionalProperties": False,
        },
        "models": {
            "type": "object",
            "properties": {
                "primary": {
                    "type": "string",
                },
                "fallback": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": True,
}

DEFAULT_RAG_CONFIG: Dict[str, Any] = {
    "embedding_mode": "minilm",
    "pipeline": {"type": "simple", "nodes": ["embed", "search", "format"]},
    "models": {"primary": "minilm", "fallback": ["minilm"]},
}

_VALID_EMBEDDING_MODES = {"minilm", "bgem3", "dual"}
_VALID_PIPELINE_TYPES = {"simple", "rerank"}
_KNOWN_KEYS = {"embedding_mode", "pipeline", "models"}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def validate_rag_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize RAG configuration with JSON Schema.

    Args:
        raw: Raw ``rag`` dict from settings.json (may be None/empty).

    Returns:
        A safe config dict with all defaults applied.
    """
    if not raw:
        logger.info("RAG config absent, using safe defaults")
        return copy.deepcopy(DEFAULT_RAG_CONFIG)

    result = copy.deepcopy(DEFAULT_RAG_CONFIG)
    validator = jsonschema.Draft7Validator(RAG_SCHEMA)
    errors = list(validator.iter_errors(raw))

    if not errors:
        _deep_merge(result, raw)
    else:
        for error in errors:
            path = ".".join(str(p) for p in error.absolute_path) or "root"
            logger.warning(
                "RAG config validation error at '%s': %s. Using default.",
                path,
                error.message,
            )

        if isinstance(raw.get("embedding_mode"), str) and raw["embedding_mode"] in _VALID_EMBEDDING_MODES:
            result["embedding_mode"] = raw["embedding_mode"]

        if isinstance(raw.get("pipeline"), dict):
            pipe = raw["pipeline"]
            if isinstance(pipe.get("type"), str) and pipe["type"] in _VALID_PIPELINE_TYPES:
                result["pipeline"]["type"] = pipe["type"]
            if isinstance(pipe.get("nodes"), list) and all(
                isinstance(n, str) for n in pipe["nodes"]
            ):
                result["pipeline"]["nodes"] = pipe["nodes"]

        if isinstance(raw.get("models"), dict):
            models = raw["models"]
            if isinstance(models.get("primary"), str):
                result["models"]["primary"] = models["primary"]
            if isinstance(models.get("fallback"), list) and all(
                isinstance(f, str) for f in models["fallback"]
            ):
                result["models"]["fallback"] = models["fallback"]

    # Remove unknown top-level keys (forward compat: ignore, don't propagate)
    for key in raw:
        if key not in _KNOWN_KEYS:
            logger.warning(
                "RAG config: unknown key '%s' ignored (forward compat)", key
            )
    result = {k: v for k, v in result.items() if k in _KNOWN_KEYS}

    return result
