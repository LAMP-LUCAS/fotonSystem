from abc import ABC, abstractmethod
import traceback
import time
from typing import Any, Dict, Optional
from foton_system.core.ops.audit_logger import AuditLogger


class BaseOp(ABC):
    """
    Abstract Base Class for all FOTON Standard Operating Procedures (POPs).
    Enforces validation, execution structure, and auditing.
    """
    
    def __init__(self, actor: str = "System"):
        self.actor = actor
        self.audit_logger = AuditLogger()
        self.op_name = self.__class__.__name__

    @abstractmethod
    def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Validates input arguments. 
        Must return the cleaned/validated dictionary of arguments or raise ValueError.
        """
        pass

    @abstractmethod
    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementation of the specific business logic.
        Returns a dictionary with the operation result.
        """
        pass

    def execute(self, client_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        The main entry point. Orchestrates Validation -> Execution -> Auditing -> Telemetry.
        """
        from foton_system.core.ops.session_tracker import get_current_session, increment_operations
        from foton_system.core.ops.operation_tracker import _write_operation_record
        
        status = "SUCCESS"
        result = {}
        validated_data = {}
        session = get_current_session()
        session_id = session.session_id if session else None
        interface = session.interface if session else "UNKNOWN"
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        
        try:
            # 1. Validation
            validated_data = self.validate(**kwargs)
            
            # 2. Execution
            result = self.execute_logic(validated_data)
            
            return result

        except Exception as e:
            status = "ERROR"
            result = {"error": str(e), "traceback": traceback.format_exc()}
            raise e
        
        finally:
            # 3. Auditing (Always runs, even on failure)
            self.audit_logger.log_event(
                op_name=self.op_name,
                actor=self.actor,
                client_id=client_id or validated_data.get("client_name", "UNKNOWN"),
                payload=kwargs, # Log raw inputs
                result=result,
                status=status
            )
            # 4. Telemetry (Always runs, even on failure)
            elapsed = time.perf_counter() - start
            sucesso = status == "SUCCESS"
            increment_operations()
            _write_operation_record({
                "timestamp": timestamp,
                "session_id": session_id,
                "interface": interface,
                "operacao": self.op_name,
                "sucesso": sucesso,
                "duracao_ms": round(elapsed * 1000, 2),
                "metadados": {"actor": self.actor, "client_id": client_id or "UNKNOWN"},
            })