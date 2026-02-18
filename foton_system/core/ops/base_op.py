from abc import ABC, abstractmethod
import traceback
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
        The main entry point. Orchestrates Validation -> Execution -> Auditing.
        """
        status = "SUCCESS"
        result = {}
        validated_data = {}
        
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
            # Filter passwords or sensitive data from payload if needed in future
            self.audit_logger.log_event(
                op_name=self.op_name,
                actor=self.actor,
                client_id=client_id or validated_data.get("client_name", "UNKNOWN"),
                payload=kwargs, # Log raw inputs
                result=result,
                status=status
            )
