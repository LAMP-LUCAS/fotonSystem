from typing import Dict, Any
from pathlib import Path
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
from foton_system.modules.shared.infrastructure.config.config import Config

class OpFinanceEntry(BaseOp):
    """
    Standard Operation to register a financial entry (Income/Expense).
    Updates Client CSV (Dispersed) and ensures audit trail.
    """

    def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Requires:
        - client_name (str) OR client_path (str)
        - description (str)
        - value (float/str)
        - type (str): 'ENTRADA' or 'SAIDA'
        """
        client = kwargs.get("client_name") or kwargs.get("client_path")
        if not client:
             raise ValueError("Must provide 'client_name' or 'client_path'.")

        desc = kwargs.get("description")
        if not desc:
            raise ValueError("Description is required.")

        try:
            val = float(kwargs.get("value", 0))
            if val <= 0:
                 raise ValueError("Value must be positive.")
            kwargs["value"] = val
        except ValueError:
            raise ValueError("Invalid number for 'value'.")

        entry_type = kwargs.get("type", "ENTRADA").upper()
        if entry_type not in ["ENTRADA", "SAIDA"]:
             raise ValueError("Type must be 'ENTRADA' or 'SAIDA'.")
        kwargs["type"] = entry_type
        
        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Resolve Client Path
        # This logic mimics _get_client_path but is self-contained or reuses service
        raw_client = validated_data.get("client_name") or validated_data.get("client_path")
        
        # Try to resolve if it's just a name
        client_path = Path(raw_client)
        if not client_path.is_absolute():
             base = Config().base_pasta_clientes
             client_path = base / raw_client
        
        if not client_path.exists():
            raise FileNotFoundError(f"Client folder not found: {client_path}")

        # 2. Setup Service
        repo = CSVFinanceRepository()
        service = FinanceService(repo)

        # 3. Execute
        summary = service.add_entry(
            client_path=client_path,
            description=validated_data["description"],
            value=validated_data["value"],
            entry_type=validated_data["type"]
        )

        # 4. Return BI Metrics
        return {
            "status": "REGISTERED",
            "client": client_path.name,
            "new_balance": summary["saldo"],
            "total_in": summary["total_entradas"],
            "total_out": summary["total_saidas"],
            "message": f"Entry registered. New Balance: R$ {summary['saldo']:.2f}"
        }

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Register Finance Entry (POP).")
    parser.add_argument("--client", required=True, help="Client Name or Path")
    parser.add_argument("--desc", required=True, help="Description")
    parser.add_argument("--value", required=True, type=float, help="Amount")
    parser.add_argument("--type", default="ENTRADA", choices=["ENTRADA", "SAIDA"], help="Type")
    
    args = parser.parse_args()
    
    try:
        op = OpFinanceEntry(actor="CLI_User")
        result = op.execute(
            client_name=args.client,
            description=args.desc,
            value=args.value,
            type=args.type
        )
        print(f"SUCCESS: {result['message']}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
