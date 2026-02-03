from typing import Dict, Any, List
from pathlib import Path
from foton_system.core.ops.base_op import BaseOp
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService
import json

class OpGenerateDocument(BaseOp):
    """
    Standard Operation to generate a document from a template.
    Orchestrates Data gathering -> Template selection -> Generation.
    """

    def validate(self, **kwargs) -> Dict[str, Any]:
        """
        Requires:
        - client_name (str)
        - template_name (str)
        Optional:
        - extra_data (dict)
        """
        if not kwargs.get("client_name"):
            raise ValueError("Client Name is required.")
        if not kwargs.get("template_name"):
            raise ValueError("Template Name is required.")
        
        # Normalize
        kwargs["extra_data"] = kwargs.get("extra_data", {})
        if isinstance(kwargs["extra_data"], str):
             try:
                 kwargs["extra_data"] = json.loads(kwargs["extra_data"])
             except:
                 pass # Keep as string if parsing fails, though doc service expects dict
                 
        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Setup Services
        docx_adapter = PythonDocxAdapter()
        pptx_adapter = PythonPPTXAdapter()
        service = DocumentService(docx_adapter, pptx_adapter)
        
        # 2. Resolve Client Path
        # Logic duplicated from MCP/Install service - ideally moved to a helper
        client_name = validated_data["client_name"]
        base = Config().base_pasta_clientes
        # Simple resolution for now
        client_path = base / client_name
        
        # If folder doesn't exist, try finding it by partial match or just accept it might fail in service
        if not client_path.exists():
             # Basic search strategy
             for p in base.iterdir():
                 if p.is_dir() and client_name.lower() in p.name.lower():
                     client_path = p
                     break
        
        if not client_path.exists():
            raise FileNotFoundError(f"Client folder for '{client_name}' not found.")

        # 3. Resolve Template
        template_name = validated_data["template_name"]
        template_dir = Config().templates_path
        template_path = template_dir / template_name
        
        if not template_path.exists():
             # Try appending extension if missing
             if not template_name.endswith(('.docx', '.pptx')):
                 # Check both
                 if (template_dir / f"{template_name}.docx").exists():
                     template_path = template_dir / f"{template_name}.docx"
                 elif (template_dir / f"{template_name}.pptx").exists():
                     template_path = template_dir / f"{template_name}.pptx"
                     
        if not template_path.exists():
             raise FileNotFoundError(f"Template '{template_name}' not found in {template_dir}")

        # 4. Prepare Data
        # We need to temporarily write JSON for the legacy service to read
        # TODO: Refactor Service to accept Dict directly to avoid IO
        temp_data_file = client_path / "temp_pop_data.json"
        with open(temp_data_file, 'w', encoding='utf-8') as f:
            json.dump(validated_data["extra_data"], f)

        # 5. Generate
        output_name = f"GERADO_{template_path.name}"
        output_path = client_path / output_name
        
        doc_type = "pptx" if template_path.suffix == ".pptx" else "docx"
        
        try:
            service.generate_document(
                template_path=str(template_path),
                data_path=str(temp_data_file),
                output_path=str(output_path),
                doc_type=doc_type
            )
        finally:
            if temp_data_file.exists():
                temp_data_file.unlink()

        return {
            "status": "GENERATED",
            "output_path": str(output_path),
            "client": client_path.name,
            "template": template_path.name
        }

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Generate Document (POP).")
    parser.add_argument("--client", required=True, help="Client Name")
    parser.add_argument("--template", required=True, help="Template Filename")
    parser.add_argument("--data", help="JSON string of extra data")
    
    args = parser.parse_args()
    
    try:
        op = OpGenerateDocument(actor="CLI_User")
        result = op.execute(
            client_name=args.client,
            template_name=args.template,
            extra_data=args.data
        )
        print(f"SUCCESS: Document created at {result['output_path']}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
