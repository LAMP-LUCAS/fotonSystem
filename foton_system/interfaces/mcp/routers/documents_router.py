"""
Roteador MCP para ferramentas de Geração, Validação e Histórico de Documentos.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from foton_system.interfaces.mcp.routers.common import (
    _logger,
    _log_tool_call,
    _get_factory,
    _get_config,
    _validate_dados_extras,
    _resolve_client_path,
)


def listar_templates(categoria: str = "") -> str:
    """
    Lists all available document templates (DOCX for contracts, PPTX for proposals).
    PROTOCOL: Show this to the user to let them choose the document type they want to generate.
    PARAMETERS:
      categoria: Optional category filter (e.g., 'proposta', 'contrato', 'administrativo')
    """
    try:
        result = _get_factory().get_document_service().list_templates()
        if not result.success:
            return f"❌ {result.message}"

        templates = result.templates or {}
        pptx = templates.get('pptx', [])
        docx = templates.get('docx', [])

        def format_template(t):
            desc = f" — {t.description}" if t.description else ""
            return f"{t.filename}{desc}"

        if categoria:
            pptx = [t for t in pptx if t.category == categoria]
            docx = [t for t in docx if t.category == categoria]

        output = "📄 Templates disponíveis:\n"
        if pptx:
            output += f"\n🟦 PPTX ({len(pptx)}):\n"
            for t in sorted(pptx, key=lambda x: x.filename):
                output += f"  • {format_template(t)}\n"
        if docx:
            output += f"\n🟩 DOCX ({len(docx)}):\n"
            for t in sorted(docx, key=lambda x: x.filename):
                output += f"  • {format_template(t)}\n"

        if not pptx and not docx:
            return "📭 No templates found."

        return output
    except OSError as e:
        _logger.error(f"listar_templates I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"listar_templates failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def listar_documentos_cliente(cliente: str, servico: str = "") -> str:
    """
    Lists existing files for a client or specific service.
    CONTEXT: Use this to check if a document was already generated before creating a duplicate.
    """
    try:
        config = _get_config()
        client_path = _resolve_client_path(config.base_pasta_clientes, cliente, config)

        safe_servico = Path(servico).name if servico else ""
        target = client_path / safe_servico if safe_servico else client_path

        if not target.exists():
            return f"⚠️ Path not found: {target}"

        files_by_folder = {}
        for f in sorted(target.rglob('*')):
            if not f.is_file():
                continue
            try:
                rel = f.relative_to(target)
            except ValueError:
                continue
            folder = str(rel.parent) if rel.parent != Path('.') else "(raiz)"
            if folder not in files_by_folder:
                files_by_folder[folder] = []
            size_kb = f.stat().st_size / 1024
            files_by_folder[folder].append(f"{rel.name} ({size_kb:.0f} KB)")

        if not files_by_folder:
            return f"📭 No files found."

        total = sum(len(v) for v in files_by_folder.values())
        output = f"📂 {total} arquivo(s) em {target.name}:\n"

        for folder, files in sorted(files_by_folder.items()):
            output += f"\n  📁 {folder}/\n"
            for fname in files:
                output += f"    • {fname}\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_documentos_cliente failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def gerar_documento(cliente: str, nome_template: str, dados_extras: Optional[dict] = None) -> str:
    """
    Merging Engine: Template + Client Data = Generated Document.
    PROTOCOL: 
    1. Always run 'validar_template' first.
    2. Provide 'dados_extras' for variables not found in the INFO files.
    3. The file is saved with prefix 'GERADO_' in the client's folder.
    CASE-INSENSITIVITY: Variables are matched regardless of casing (@CLIENTE == @cliente).
    """
    try:
        dados_extras = dados_extras or {}
        _validate_dados_extras(dados_extras)
        from foton_system.core.ops.op_doc_gen import OpGenerateDocument
        op = OpGenerateDocument(actor="Agent_MCP")
        result = op.execute(
            client_id=cliente,
            client_name=cliente,
            template_name=nome_template,
            extra_data=dados_extras
        )
        return (
            f"✅ Documento Gerado (POP Auditado)\n"
            f"   Arquivo: {result['output_path']}"
        )
    except ValueError as e:
        return f"❌ Invalid dados_extras: {e}"
    except Exception as e:
        _logger.error(f"gerar_documento failed: {e}", exc_info=True)
        return f"❌ Erro POP: {e}"


def validar_template(cliente: str, nome_template: str, arquivo_dados: str = "") -> str:
    """
    Pre-flight validation: Checks if the INFO files provide all variables required by the template.
    Returns categorized report with resolved, missing, none_values and formulas.
    PROTOCOL: Mandatory check before calling 'gerar_documento'.
    AGNOSTICISM: Searches the entire folder hierarchy for information.
    """
    try:
        config = _get_config()
        factory = _get_factory()

        svc = factory.get_client_service()
        client_path = svc.resolve_client_path(cliente)

        safe_name = Path(nome_template).name
        template_path = config.templates_path / safe_name
        if not template_path.exists():
            return f"❌ Template not found: {safe_name}"

        doc_type = template_path.suffix.lstrip('.').lower()
        if arquivo_dados:
            data_path = client_path / arquivo_dados
        else:
            md_files = list(client_path.glob('*INFO*.md')) + list(client_path.glob('*.md'))
            if not md_files:
                return f"⚠️ No data files (.md) found in {client_path.name}"
            data_path = md_files[0]

        doc_service = factory.get_document_service()
        report = doc_service.validate_template_keys(str(template_path), str(data_path), doc_type)

        resolved = report.get("resolved", [])
        missing = report.get("missing", [])
        none_values = report.get("none_values", [])
        formulas = report.get("formulas", [])

        output = f"📋 Relatório de Pré-validação — '{nome_template}'\n"

        if resolved:
            output += f"\n✅ Resolvidas ({len(resolved)}):\n"
            for r in resolved[:20]:
                output += f"   {r['key']} → {r['value']}\n"
            if len(resolved) > 20:
                output += f"   ... e mais {len(resolved) - 20}\n"
        else:
            output += "\n⚠️ Nenhuma variável resolvida\n"

        if missing:
            output += f"\n❌ Não encontradas ({len(missing)}):\n"
            for k in missing:
                output += f"   {k}\n"

        if none_values:
            output += f"\n⚠️ Valores inválidos (None/---/vazio) ({len(none_values)}):\n"
            for k in none_values:
                output += f"   {k}\n"

        if formulas:
            output += f"\n🧮 Fórmulas validadas ({len(formulas)}):\n"
            for f in formulas:
                status_icon = "✅" if f.get("status") == "ok" else "❌"
                output += f"   {status_icon} {f['expression']} = {f['result']}\n"

        if not missing and not none_values:
            output += f"\n✅ Todos os placeholders verificados — template pronto para geração."

        return output
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Validation error: {e}"


def listar_arquivos_dados(cliente: str) -> str:
    """
    Lists data files (.md, .txt) available for a client.
    CONTEXT: These files contain key-value pairs used during document generation.
    """
    try:
        client_path = _get_factory().get_client_service().resolve_client_path(cliente)
        files = _get_factory().get_document_service().list_client_data_files(str(client_path))
        if not files:
            return f"📭 No data files found for '{cliente}'."
        output = f"📄 {len(files)} data file(s) for {cliente}:\n"
        for f in files:
            output += f"  • {Path(f).name}\n"
        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_arquivos_dados failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def criar_arquivo_dados(cliente: str, cod: str, descricao: str = "PROPOSTA") -> str:
    """
    Creates a custom data file for a client using the centralized template.
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      cod: Document code (e.g., 'ABC123')
      descricao: Description/short name (default 'PROPOSTA')
    """
    try:
        client_path = _get_factory().get_client_service().resolve_client_path(cliente)
        result = _get_factory().get_document_service().create_custom_data_file(
            str(client_path), cod, desc=descricao
        )
        if result:
            return f"✅ Data file created: {Path(result).name}"
        return "❌ Failed to create data file."
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"criar_arquivo_dados failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def historico_documentos(cliente: str, limite: int = 10) -> str:
    """
    Lists the version history of generated documents for a client.
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      limite: Maximum number of entries to show (default 10)
    CONTEXT: Returns JSONL-based history with versioning info.
    """
    try:
        factory = _get_factory()
        client_path = factory.get_client_service().resolve_client_path(cliente)
        doc_service = factory.get_document_service()
        entries = doc_service.get_history(client_path, limit=limite)

        if not entries:
            return f"📭 Nenhum histórico encontrado para '{cliente}'."

        total = len(entries)
        output = f"📜 Histórico de Documentos — '{cliente}' ({total} registro(s)):\n"
        for i, e in enumerate(entries, 1):
            status_icon = "✅" if e.get('status') == 'sucesso' else "❌"
            versao = e.get('versao', 1)
            versao_anterior = e.get('versao_anterior')
            ver_info = f"v{versao}"
            if versao_anterior:
                ver_info += f" (anterior: {versao_anterior})"
            output += (
                f"\n{status_icon} "
                f"[{e.get('data_hora', '?')}] "
                f"{e.get('nome_arquivo', '?')} "
                f"({ver_info})"
            )
        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"historico_documentos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def gerar_documentos_lote(cliente: str, documentos: list) -> str:
    """
    Generates multiple documents in a single batch operation.
    Phase 1: validates all templates. Phase 2: generates all (only if all pass).
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      documentos: List of dicts, each with {template: str, dados_extras?: dict, tipo?: str}
    CONTEXT: Use this to generate proposta + contrato + anexo simultaneously.
    """
    try:
        factory = _get_factory()
        doc_service = factory.get_document_service()

        normalized = []
        for doc in documentos:
            if not isinstance(doc, dict):
                return f"❌ Each item in 'documentos' must be a dict with 'template'."
            template_name = doc.get("template")
            if not template_name:
                return f"❌ Each item in 'documentos' must have a 'template' field."
            extra_data = doc.get("dados_extras", {})
            if not isinstance(extra_data, dict):
                extra_data = {}
            normalized.append({
                "template_name": template_name,
                "extra_data": extra_data,
            })

        result = doc_service.generate_batch(cliente, normalized)

        if not result.success:
            return f"❌ Lote falhou: {result.message}"

        batch = result.batch_result or {}
        items = batch.get("items", [])
        status = batch.get("status", "UNKNOWN")

        if status == "BATCH_BLOCKED":
            output = f"❌ Lote BLOQUEADO — pré-validação falhou:\n"
            for item in items:
                icon = "🔴" if item["status"] == "bloqueado" else "🟡"
                output += f"  {icon} {item['template_name']} → {item['status']}\n"
            output += "\nCorrija os templates com falha e tente novamente."
            return output

        output = f"✅ Lote concluído ({len(items)} documento(s)):\n"
        for item in items:
            icon = "✅" if item["status"] == "sucesso" else "❌"
            output += f"  {icon} {item['template_name']} → {item['output_path']}\n"
        return output

    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"gerar_documentos_lote failed: {e}", exc_info=True)
        return f"❌ Erro: {e}"


def pipeline_emitir_documento(cliente: str, nome_template: str, dados_extras: Optional[dict] = None) -> str:
    """
    SAFE pre-flight report before document generation.
    AI RECOMMENDED: Always run this before 'gerar_documento' to provide a summary to the user.
    Logic: Validates variables AND checks for existing generated files to avoid duplicates.
    """
    try:
        dados_extras = dados_extras or {}
        _validate_dados_extras(dados_extras)
        svc = _get_factory().get_client_service()
        client_path = svc.resolve_client_path(cliente)

        output = f"📋 PRE-FLIGHT — Document Generation\n"
        output += f"   Client:  {client_path.name}\n"
        output += f"   Template: {nome_template}\n\n"

        validation = validar_template(cliente, nome_template)
        output += f"{validation}\n"

        template_base = Path(nome_template).stem
        existing = list(client_path.rglob(f"GERADO_*{template_base}*"))
        if existing:
            output += f"\n⚠️ DUPLICATES: {len(existing)} similar file(s) found in {client_path.name}.\n"
        else:
            output += "✅ DUPLICATES: No similar files found.\n"

        output += "\nPROTOCOL: Review this report and confirm with the user before calling 'gerar_documento'."
        return output
    except ValueError as e:
        return f"❌ Invalid dados_extras: {e}"
    except Exception as e:
        return f"❌ Pipeline error: {e}"


def register_documents_tools(mcp) -> None:
    """Registra as ferramentas de documentos na instância FastMCP."""
    mcp.tool()(_log_tool_call(listar_templates))
    mcp.tool()(_log_tool_call(listar_documentos_cliente))
    mcp.tool()(_log_tool_call(gerar_documento))
    mcp.tool()(_log_tool_call(validar_template))
    mcp.tool()(_log_tool_call(listar_arquivos_dados))
    mcp.tool()(_log_tool_call(criar_arquivo_dados))
    mcp.tool()(_log_tool_call(historico_documentos))
    mcp.tool()(_log_tool_call(gerar_documentos_lote))
    mcp.tool()(_log_tool_call(pipeline_emitir_documento))
