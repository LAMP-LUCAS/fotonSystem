import functools
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

_log_file_name = "operation_log.jsonl"
_MAX_BYTES = 10 * 1024 * 1024
_TRUNCATE_TARGET = 8 * 1024 * 1024


def _get_config_dir() -> Path:
    return BootstrapService.get_user_config_dir()


def _get_log_path() -> Path:
    return _get_config_dir() / _log_file_name


def _rotate_if_needed(log_path: Path):
    if not log_path.exists():
        return
    try:
        size = log_path.stat().st_size
        if size <= _MAX_BYTES:
            return
        with open(log_path, "r", encoding="utf-8", newline="") as f:
            lines = f.readlines()
        current_size = 0
        keep_lines = []
        for line in reversed(lines):
            line_len = len(line)
            if current_size + line_len > _TRUNCATE_TARGET and keep_lines:
                break
            keep_lines.append(line)
            current_size += line_len
        keep_lines.reverse()
        with open(log_path, "w", encoding="utf-8", newline="") as f:
            f.writelines(keep_lines)
    except OSError:
        pass


def _write_operation_record(record: dict):
    log_path = _get_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _rotate_if_needed(log_path)
    with open(log_path, "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def track_operation(nome: str, **metadados_fixos):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from foton_system.core.ops.session_tracker import get_current_session
            session = get_current_session()
            session_id = session.session_id if session else None
            interface = session.interface if session else "UNKNOWN"
            timestamp = datetime.now(timezone.utc).isoformat()
            start = time.perf_counter()
            sucesso = True
            metadados = dict(metadados_fixos)
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                sucesso = False
                raise
            finally:
                elapsed = time.perf_counter() - start
                record = {
                    "timestamp": timestamp,
                    "session_id": session_id,
                    "interface": interface,
                    "operacao": nome,
                    "sucesso": sucesso,
                    "duracao_ms": round(elapsed * 1000, 2),
                    "metadados": metadados,
                }
                _write_operation_record(record)
        return wrapper
    return decorator


def _reset_operation_state():
    pass