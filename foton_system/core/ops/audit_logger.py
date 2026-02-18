import json
import logging
from datetime import datetime
from pathlib import Path
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService

class AuditLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuditLogger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # Determine log path based on environment
        # Users data folder is the safest place used by BootstrapService
        try:
            config_dir = BootstrapService.get_user_config_dir()
            config_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = config_dir / "audit_events.jsonl"
            
            # Also setup a standard python logger for console output/debug
            self.logger = logging.getLogger("foton_audit")
            self.logger.setLevel(logging.INFO)
        except Exception as e:
            # Fallback to local execution directory if bootstrap fails (rare)
            self.log_file = Path("audit_events.jsonl")

    def log_event(self, op_name: str, actor: str, client_id: str, payload: dict, result: dict, status: str):
        """
        Logs a structured event to the audit trail.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "op": op_name,
            "actor": actor,
            "client_id": client_id,
            "payload": payload,  # Input params
            "result": result,    # Output metrics
            "status": status
        }
        
        try:
            # Append to JSONL file
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as e:
            # If we can't maintain the audit trail, we should at least print to stderr
            print(f"[AUDIT FAIL] Could not write to {self.log_file}: {e}")

    def get_recent_events(self, limit=10):
        """Reads the last N events for analysis."""
        events = []
        if not self.log_file.exists():
            return events
            
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines[-limit:]):
                    events.append(json.loads(line))
        except Exception:
            pass
        return events
