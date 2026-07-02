import json
from typing import Dict, Any, List
from pathlib import Path
from foton_system.core.ops.base_op import BaseOp
# @story: STORY-022 @rule: RULE-DOC-2.4 @rule: RULE-DOC-2.5
# @story: STORY-025 @rule: RULE-DOC-3.2 @rule: RULE-DOC-3.5
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
from foton_system.modules.documents.infrastructure.adapters.python_docx_adapter import PythonDocxAdapter
from foton_system.modules.documents.infrastructure.adapters.python_pptx_adapter import PythonPPTXAdapter
from foton_system.modules.shared.infrastructure.config.config import Config
from foton_system.modules.shared.infrastructure.bootstrap.bootstrap_service import BootstrapService


# @story: STORY-026 @rule: RULE-DOC-2.3
def _sanitize_name(name: str) -> str:
    """Sanitiza nome contra path traversal."""
    return Path(name).name

# @story: STORY-025 @rule: RULE-DOC-3.2
# @story: STORY-026 @rule: RULE-DOC-2.3

def _resolve_client_path(client_name):
    safe_name = _sanitize_name(client_name)
    base = Config().base_pasta_clientes
    client_path = base / safe_name
    if not client_path.exists():
        for p in base.iterdir():
            if p.is_dir() and safe_name.lower() in p.name.lower():
                client_path = p
                break
    if not client_path.exists():
        raise FileNotFoundError(f"Client folder for '{client_name}' not found.")
    return client_path


# @story: STORY-026 @rule: RULE-DOC-2.3
def _resolve_template_path(template_name):
    safe_name = _sanitize_name(template_name)
    template_dir = Config().templates_path
    template_path = template_dir / safe_name
    if not template_path.exists():
        if not safe_name.endswith(('.docx', '.pptx')):
            if (template_dir / f"{safe_name}.docx").exists():
                template_path = template_dir / f"{safe_name}.docx"
            elif (template_dir / f"{safe_name}.pptx").exists():
                template_path = template_dir / f"{safe_name}.pptx"
    if not template_path.exists():
        raise FileNotFoundError(f"Template '{template_name}' not found in {template_dir}")
    return template_path


class OpGenerateDocument(BaseOp):
    """
    # @story: STORY-025 @rule: RULE-DOC-3.2
    Standard Operation to generate a document from a template.
    Orchestrates Data gathering -> Template selection -> Generation.
    """

    telemetry_fields = ("client", "template", "output_path", "status")

    def validate(self, **kwargs) -> Dict[str, Any]:
        if not kwargs.get("client_name"):
            raise ValueError("Client Name is required.")
        if not kwargs.get("template_name"):
            raise ValueError("Template Name is required.")
        kwargs["extra_data"] = kwargs.get("extra_data", {})
        if isinstance(kwargs["extra_data"], str):
             try:
                 kwargs["extra_data"] = json.loads(kwargs["extra_data"])
             except (json.JSONDecodeError, TypeError):
                 pass
        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        docx_adapter = PythonDocxAdapter()
        pptx_adapter = PythonPPTXAdapter()
        service = DocumentService(docx_adapter, pptx_adapter)

        client_name = validated_data["client_name"]
        client_path = _resolve_client_path(client_name)

        template_name = validated_data["template_name"]
        template_path = _resolve_template_path(template_name)

        doc_type = "pptx" if template_path.suffix == ".pptx" else "docx"
        template_stem = template_path.stem

        output_name = service.build_standard_filename(
            client_name=client_path.name,
            template_stem=template_stem,
            doc_type=doc_type
        )
        output_path = client_path / output_name

        service.generate_document(
            template_path=str(template_path),
            data_path=str(client_path),
            output_path=str(output_path),
            doc_type=doc_type,
            extra_data=validated_data["extra_data"]
        )

        return {
            "status": "GENERATED",
            "output_path": str(output_path),
            "client": client_path.name,
            "template": template_path.name
        }


class OpGenerateBatchDocuments(BaseOp):
    """
    # @story: STORY-025 @rule: RULE-DOC-3.5
    Batch document generation.
    Phase 1: validate all items. Phase 2: generate all (only if all pass).
    Returns consolidated report with per-document status.
    """

    telemetry_fields = ("status",)

    def validate(self, **kwargs) -> Dict[str, Any]:
        if not kwargs.get("client_name"):
            raise ValueError("Client Name is required.")
        documentos = kwargs.get("documentos", [])
        if not isinstance(documentos, list) or not documentos:
            raise ValueError("documentos must be a non-empty list of dicts.")
        for i, doc in enumerate(documentos):
            if not isinstance(doc, dict):
                raise ValueError(f"documentos[{i}] must be a dict.")
            if not doc.get("template_name"):
                raise ValueError(f"documentos[{i}] missing 'template_name'.")
            doc["extra_data"] = doc.get("extra_data", {})
            if isinstance(doc["extra_data"], str):
                try:
                    doc["extra_data"] = json.loads(doc["extra_data"])
                except (json.JSONDecodeError, TypeError):
                    pass
        return kwargs

    def execute_logic(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        docx_adapter = PythonDocxAdapter()
        pptx_adapter = PythonPPTXAdapter()
        service = DocumentService(docx_adapter, pptx_adapter)

        client_name = validated_data["client_name"]
        client_path = _resolve_client_path(client_name)
        documentos = validated_data["documentos"]

        pre_flight_items = []
        for doc in documentos:
            template_name = doc["template_name"]
            template_path = _resolve_template_path(template_name)
            doc_type = "pptx" if template_path.suffix == ".pptx" else "docx"
            template_stem = template_path.stem

            output_name = service.build_standard_filename(
                client_name=client_path.name,
                template_stem=template_stem,
                doc_type=doc_type
            )
            output_path = client_path / output_name

            try:
                validation = service.validate_template_keys(
                    str(template_path), str(client_path), doc_type
                )
            except Exception as e:
                validation = {"missing": ["_ERROR_"], "none_values": [], "resolved": [], "formulas": []}

            pre_flight_items.append({
                "template_name": template_name,
                "doc_type": doc_type,
                "output_path": str(output_path),
                "template_path": str(template_path),
                "validation_valid": not validation.get("missing") and not validation.get("none_values"),
                "validation": validation,
            })

        all_valid = all(item["validation_valid"] for item in pre_flight_items)

        if not all_valid:
            results = []
            for item in pre_flight_items:
                status = "bloqueado" if not item["validation_valid"] else "bloqueado_por_dependencia"
                results.append({
                    "template_name": item["template_name"],
                    "output_path": item["output_path"],
                    "status": status,
                })
            return {"status": "BATCH_BLOCKED", "items": results}

        results = []
        for item in pre_flight_items:
            try:
                service.generate_document(
                    template_path=item["template_path"],
                    data_path=str(client_path),
                    output_path=item["output_path"],
                    doc_type=item["doc_type"],
                    extra_data={}
                )
                results.append({
                    "template_name": item["template_name"],
                    "output_path": item["output_path"],
                    "status": "sucesso",
                })
            except Exception as e:
                results.append({
                    "template_name": item["template_name"],
                    "output_path": item["output_path"],
                    "status": "erro",
                    "error": str(e),
                })

        return {"status": "BATCH_COMPLETED", "items": results}

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
