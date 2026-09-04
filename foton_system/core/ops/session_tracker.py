import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

_current_session = None
SESSION_FILE = "session.json"


class SessionState:
    def __init__(self, session_id: str, interface: str, timestamp_inicio: str,
                 total_sessoes_all_time: int = 1, total_operacoes_all_time: int = 0,
                 primeiro_uso: Optional[str] = None):
        self.session_id = session_id
        self.interface = interface
        self.timestamp_inicio = timestamp_inicio
        self.contador_operacoes = 0
        self.total_sessoes_all_time = total_sessoes_all_time
        self.total_operacoes_all_time = total_operacoes_all_time
        self.primeiro_uso = primeiro_uso or timestamp_inicio


def _get_config_dir() -> Path:
    return BootstrapService.get_user_config_dir()


def _get_session_path() -> Path:
    return _get_config_dir() / SESSION_FILE


def _load_persisted_state() -> dict:
    path = _get_session_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_session(session: SessionState):
    path = _get_session_path()
    data = {
        "session_id": session.session_id,
        "interface": session.interface,
        "timestamp_inicio": session.timestamp_inicio,
        "contador_operacoes": session.contador_operacoes,
        "total_sessoes_all_time": session.total_sessoes_all_time,
        "total_operacoes_all_time": session.total_operacoes_all_time,
        "primeiro_uso": session.primeiro_uso,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def start_session(interface: str) -> SessionState:
    global _current_session
    persisted = _load_persisted_state()
    total_sessoes = persisted.get("total_sessoes_all_time", 0) + 1
    total_operacoes = persisted.get("total_operacoes_all_time", 0)
    primeiro_uso = persisted.get("primeiro_uso")
    session_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    session = SessionState(
        session_id=session_id,
        interface=interface,
        timestamp_inicio=timestamp,
        total_sessoes_all_time=total_sessoes,
        total_operacoes_all_time=total_operacoes,
        primeiro_uso=primeiro_uso,
    )
    _save_session(session)
    _current_session = session
    return session


def end_session():
    global _current_session
    if _current_session is not None:
        _save_session(_current_session)


def get_current_session() -> Optional[SessionState]:
    return _current_session


def increment_operations():
    global _current_session
    if _current_session is not None:
        _current_session.contador_operacoes += 1
        _current_session.total_operacoes_all_time += 1


def _reset_session_state():
    global _current_session
    _current_session = None