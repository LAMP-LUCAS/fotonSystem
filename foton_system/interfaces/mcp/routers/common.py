"""
Componentes e helpers compartilhados para os sub-roteadores MCP.
"""

import functools
import inspect
import logging
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any

_logger = logging.getLogger("foton_mcp")

# ==============================================================================
# HELPERS: Validation + Correlation ID + Telemetry
# ==============================================================================

_MAX_LENGTHS = {
    'nome': 200,
    'apelido': 100,
    'pergunta': 5000,
    'descricao': 500,
    'conteudo': 50000,
    'cod': 50,
    'nome_template': 200,
    'cliente': 200,
    'secao': 100,
    'pasta_alvo': 500,
    'nif': 20,
    'email': 200,
    'telefone': 30,
}

def _validate_str(value: str, field_name: str) -> None:
    """Validate string length. Raises ValueError if too long."""
    max_len = _MAX_LENGTHS.get(field_name)
    if max_len is not None and len(value) > max_len:
        raise ValueError(
            f"'{field_name}' exceeds max length ({max_len}): "
            f"got {len(value)} characters"
        )


def _log_tool_call(func):
    """Decorator: adds correlation ID + entry/exit logging + auto string validation + telemetry."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from foton_system.core.ops.operation_tracker import _write_operation_record
        from foton_system.core.ops.session_tracker import get_current_session, increment_operations
        from datetime import datetime, timezone

        req_id = str(uuid.uuid4())[:8]
        _logger.info(f"[req-{req_id}] Tool called: {func.__name__}")

        try:
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for param_name, param_value in bound.arguments.items():
                if isinstance(param_value, str) and param_value:
                    _validate_str(param_value, param_name)
        except ValueError as e:
            _logger.warning(f"[req-{req_id}] Validation failed: {e}")
            return f"❌ {e}"
        except TypeError:
            pass

        session = get_current_session()
        session_id = session.session_id if session else None
        interface = session.interface if session else "MCP"
        timestamp = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        sucesso = True
        metadados = {}

        try:
            result = func(*args, **kwargs)
            increment_operations()
            _logger.info(f"[req-{req_id}] Tool completed: {func.__name__}")
            return result
        except Exception:
            sucesso = False
            _logger.error(f"[req-{req_id}] Tool failed: {func.__name__}", exc_info=True)
            raise
        finally:
            elapsed = time.perf_counter() - start
            record = {
                "timestamp": timestamp,
                "session_id": session_id,
                "interface": interface,
                "operacao": func.__name__,
                "sucesso": sucesso,
                "duracao_ms": round(elapsed * 1000, 2),
                "metadados": metadados,
            }
            _write_operation_record(record)
    return wrapper


# ==============================================================================
# SERVICE FACTORY (Lazy Loaded)
# ==============================================================================

_factory = None

def _get_factory():
    """Get or create the service factory singleton."""
    import sys
    mcp_mod = sys.modules.get("foton_system.interfaces.mcp.foton_mcp")
    if mcp_mod is not None:
        target = getattr(mcp_mod, "_get_factory", None)
        if target is not None and target is not _get_factory:
            return target()

    global _factory
    if _factory is None:
        from foton_system.interfaces.mcp.mcp_services import MCPServiceFactory
        _factory = MCPServiceFactory.get_instance()
    return _factory


# ==============================================================================
# HELPER: Get Config (lazy, cached)
# ==============================================================================

_config = None

def _get_config():
    """Get or create the Config singleton."""
    import sys
    mcp_mod = sys.modules.get("foton_system.interfaces.mcp.foton_mcp")
    if mcp_mod is not None:
        target = getattr(mcp_mod, "_get_config", None)
        if target is not None and target is not _get_config:
            return target()

    global _config
    if _config is None:
        from foton_system.modules.shared.infrastructure.config.config import Config
        _config = Config()
    return _config


# ==============================================================================
# HELPER: Dados Extras Validation
# ==============================================================================

_MAX_DADOS_EXTRAS_KEYS = 50

def _validate_dados_extras(dados_extras: dict) -> None:
    """Validates dados_extras schema. Raises ValueError on invalid data."""
    if not isinstance(dados_extras, dict):
        raise ValueError("dados_extras must be a dict")

    if len(dados_extras) > _MAX_DADOS_EXTRAS_KEYS:
        raise ValueError(
            f"dados_extras exceeds max keys ({_MAX_DADOS_EXTRAS_KEYS}): "
            f"got {len(dados_extras)} keys"
        )

    for k, v in dados_extras.items():
        if not isinstance(k, str):
            raise ValueError(f"dados_extras keys must be strings, got {type(k).__name__}")
        if not k.strip():
            raise ValueError("dados_extras keys cannot be empty")
        if isinstance(v, (dict, list)):
            raise ValueError(
                f"dados_extras values must be str/int/float, "
                f"got {type(v).__name__} for key '{k}'"
            )


# ==============================================================================
# HELPER: Internal Client Path Resolution
# ==============================================================================

def _resolve_client_path(clients_dir: Path, cliente: str, config) -> Path:
    """Internal proxy to ClientService."""
    import sys
    mcp_mod = sys.modules.get("foton_system.interfaces.mcp.foton_mcp")
    if mcp_mod is not None:
        target = getattr(mcp_mod, "_resolve_client_path", None)
        if target is not None and target is not _resolve_client_path:
            return target(clients_dir, cliente, config)
    svc = _get_factory().get_client_service()
    return svc.resolve_client_path(cliente)
