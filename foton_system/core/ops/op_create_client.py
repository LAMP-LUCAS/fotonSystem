from pathlib import Path
from typing import Dict, Any
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.clients.application.use_cases.client_service import ClientService
from foton_system.modules.clients.infrastructure.repositories.excel_client_repository import ExcelClientRepository

class OpCreateClient(BaseOp):
    """
    Standard Operation to create a new client.
    Enforces folder structure and registers in the master database.
    """
    
    def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Validates input arguments.
        Requires: 'name' (str)
        Optional: 'alias' (str), 'nif' (str), 'email' (str), 'phone' (str)
        """
        name = kwargs.get("name")
        if not name or not isinstance(name, str) or len(name.strip()) < 3:
            raise ValueError("Client name is required and must actully be a name (min 3 chars).")
        
        # Normalize
        kwargs["name"] = name.strip()
        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the client creation logic.
        """
        # 1. Setup Service (Ideally dependency injection, but for POP we keep it contained)
        repo = ExcelClientRepository()
        service = ClientService(repo)
        
        name = validated_data["name"]
        alias = validated_data.get("alias")
        nif = validated_data.get("nif", "N/A")
        email = validated_data.get("email", "N/A")
        phone = validated_data.get("phone", "N/A")

        # 2. Execute via Domain Service
        # The service handles folder creation and Excel registration
        # We wrap it here to ensure it's audited as an "Operation"
        client_data = {
            "nome": name,
            "apelido": alias,
            "nif": nif,
            "email": email,
            "telefone": phone
        }
        
        # Note: ClientService.create_client might need to be call-compatible
        # We will assume for now we use the service. 
        # Checking existing service signature: create_client(self, name: str, tax_id: str, email: str, phone: str, alias: str = None)
        
        created_client = service.create_client(
            name=name,
            tax_id=nif,
            email=email,
            phone=phone,
            alias=alias
        )
        
        # 3. Verify Result (Self-Correction/Verification)
        client_path = Path(created_client.caminho)
        if not client_path.exists():
             raise RuntimeError(f"Service reported success but folder {client_path} does not exist.")
             
        # 4. Return robust result (for API/CLI/Agent)
        return {
            "client_id": created_client.codigo,
            "client_path": str(created_client.caminho),
            "status": "CREATED",
            "message": f"Client '{name}' created successfully at {client_path.name}"
        }

if __name__ == "__main__":
    # CLI Entry Point for Manual/admin usage
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Create a new client (POP).")
    parser.add_argument("--name", required=True, help="Full name of the client")
    parser.add_argument("--alias", help="Short code/alias for the client")
    parser.add_argument("--nif", help="Tax ID")
    parser.add_argument("--email", help="Contact email")
    parser.add_argument("--phone", help="Contact phone")
    
    args = parser.parse_args()
    
    try:
        op = OpCreateClient(actor="CLI_User")
        result = op.execute(
            name=args.name,
            alias=args.alias,
            nif=args.nif,
            email=args.email,
            phone=args.phone
        )
        print(f"SUCCESS: {result['message']}")
        print(f"Path: {result['client_path']}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
