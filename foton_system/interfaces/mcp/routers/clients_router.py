"""
Roteador MCP para ferramentas de Clientes, Serviços e Conformidade.
"""

from pathlib import Path
from typing import Optional

from foton_system.interfaces.mcp.routers.common import (
    _logger,
    _log_tool_call,
    _get_factory,
    _get_config,
)


def listar_clientes(limite: int = 0, pagina: int = 1, itens_por_pagina: int = 20) -> str:
    """
    Lists all registered clients in the architecture firm.
    PROTOCOL: Always call this before performing any operation on a client you're not 100% sure exists.
    OUTPUT: Indicates if the client has a "Center of Truth" (📁 = has INFO file) and the count of sub-services.
    PARAMS: limite: Maximum number of clients to show (0 = no limit). pagina: Page number (default 1). itens_por_pagina: Items per page (default 20).
    """
    try:
        clients = _get_factory().get_client_service().list_clients()

        if not clients:
            return "📭 No clients registered yet."

        total = len(clients)

        if limite > 0:
            start = 0
            end = limite
            total_paginas = 1
        else:
            start = (pagina - 1) * itens_por_pagina
            end = start + itens_por_pagina
            total_paginas = max(1, (total + itens_por_pagina - 1) // itens_por_pagina)

        display = clients[start:end]

        if not display:
            return f"📋 Nenhum cliente na pagina {pagina}. Total: {total} cliente(s)."

        if limite > 0:
            header = f"📋 {total} client(s) found (showing {len(display)}):\n"
        else:
            header = f"📋 {total} client(s) found — Página {pagina} de {total_paginas}:\n"

        output = header
        for c in display:
            marker = "📁" if c['has_info'] else "📂"
            svc_txt = f", {c['service_count']} serviço(s)" if c['service_count'] else ""
            output += f"  {marker} {c['name']}{svc_txt}\n"

        return output
    except OSError as e:
        _logger.error(f"listar_clientes I/O error: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"listar_clientes failed: {e}", exc_info=True)
        return f"❌ Error listing clients: {e}"


def cadastrar_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:
    """
    Creates a new client folder and master record.
    SAFETY: Use 'pipeline_novo_cliente' instead for a safer, non-duplicate workflow.
    Logic: Creates standard folders (ADMINISTRATIVO, FINANCEIRO, PROJETOS) and initial INFO and FINANCEIRO files.
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name as _normalize
        normalized = _normalize(nome)
        from foton_system.core.ops.op_create_client import OpCreateClient
        op = OpCreateClient(actor="Agent_MCP")
        result = op.execute(
            name=normalized,
            alias=apelido if apelido else None,
            nif=nif,
            email=email,
            phone=telefone
        )
        return (
            f"✅ Cliente criado com sucesso (POP Auditado)\n"
            f"   Nome original: {nome}\n"
            f"   Nome normalizado: {normalized}\n"
            f"   Pasta: {result['client_path']}\n"
            f"   Código: {result['client_id']}"
        )
    except ValueError as e:
        return f"⚠️ Invalid data: {e}"
    except Exception as e:
        _logger.error(f"cadastrar_cliente failed: {e}", exc_info=True)
        return f"❌ Error creating client: {e}"


def ler_ficha_cliente(cliente: str) -> str:
    """
    Reads the 'Center of Truth' (INFO-*.md) for a client.
    CONTEXT: This is the mandatory first step before generating documents. It provides project metadata, 
    technical decisions, and meeting notes needed to understand the client's current state.
    RESOLUTION: Support fuzzy/partial client name matching.
    """
    try:
        result = _get_factory().get_client_service().read_client_info(cliente)
        return (
            f"📋 Ficha do Cliente: {cliente}\n"
            f"📄 Arquivo: {result['filename']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{result['content']}"
        )
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"ler_ficha_cliente failed: {e}", exc_info=True)
        return f"❌ Error reading info: {e}"


def atualizar_ficha_cliente(cliente: str, secao: str, conteudo: str,
                            operacao: str = "append", campo: str = "") -> str:
    """
    Updates a client's INFO file (Center of Truth) with various operations.
    SAFETY: Automatically creates a .bak backup before modifying.

    Operations:
      - "append" (default): appends content to a Markdown section
      - "replace": replaces entire section content
      - "remove": removes section entirely (conteudo ignored)
      - "field": updates @campo value via regex pattern

    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      secao: Markdown section header (e.g., 'Notas de Reunião') — used as @campo name for 'field' operation
      conteudo: Content to write
      operacao: Operation type (append/replace/remove/field)
      campo: Field name for 'field' operation (e.g., 'areaTotal')
    """
    try:
        backup_name = _get_factory().get_client_service().update_client_info(
            cliente, secao, conteudo, operacao=operacao, campo=campo
        )
        op_labels = {
            "append": "Ficha atualizada",
            "replace": "Seção substituída",
            "remove": "Seção removida",
            "field": "Campo atualizado",
        }
        label = op_labels.get(operacao, "Ficha atualizada")
        result = f"✅ {label}: {cliente}\n   Backup: {backup_name}"
        if operacao == "field" and campo:
            result += f"\n   Campo: @{campo}"
        return result
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"atualizar_ficha_cliente failed: {e}", exc_info=True)
        return f"❌ Error updating info: {e}"


def listar_servicos_cliente(cliente: str) -> str:
    """
    Lists sub-projects/services within a client's main folder.
    CONTEXT: Each service represents a distinct project (e.g., 'Reforma Apto 502').
    Ignores system folders like '01_ADMINISTRATIVO'.
    """
    try:
        services = _get_factory().get_client_service().list_services(cliente)

        if not services:
            return f"📭 No services found for client '{cliente}'."

        output = f"📋 {len(services)} serviço(s) de {cliente}:\n"
        for svc in services:
            subdirs_str = ', '.join(svc['subdirs'])
            output += f"  📂 {svc['name']} ({svc['file_count']} arquivo(s)) [{subdirs_str}]\n"

        return output
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"listar_servicos_cliente failed: {e}", exc_info=True)
        return f"❌ Error listing services: {e}"


def remover_cliente(cliente: str, confirmar: bool = False) -> str:
    """
    Removes a client by marking as DELETADO (soft delete).
    Use with caution — this is irreversible without restore.
    PARAMETERS:
      confirmar: Must be True to execute. Default False (safety).
    """
    if not confirmar:
        return "⚠️ Operação cancelada. Use confirmar=True para confirmar a remoção."
    try:
        svc = _get_factory().get_client_service()
        result = svc.soft_delete_client(cliente, confirmar=True)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except Exception as e:
        _logger.error(f"remover_cliente failed: {e}", exc_info=True)
        return f"❌ Error removing client: {e}"


def restaurar_cliente(cliente: str) -> str:
    """
    Restores a previously deleted client.
    Lists deleted clients if no name provided or if client is not found.
    """
    try:
        svc = _get_factory().get_client_service()
        result = svc.restore_client(cliente)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except ValueError as e:
        deleted = svc.get_deleted_clients()
        if deleted:
            nomes = "\n".join(f"  - {c['nome'] or c['alias']} ({c['alias']})" for c in deleted)
            return f"❌ {e}\n\nClientes deletados disponíveis:\n{nomes}"
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"restaurar_cliente failed: {e}", exc_info=True)
        return f"❌ Error restoring client: {e}"


def remover_servico(cliente: str, servico: str, confirmar: bool = False) -> str:
    """
    Removes a service by marking as DELETADO (soft delete).
    PARAMETERS:
      confirmar: Must be True to execute. Default False (safety).
    """
    if not confirmar:
        return "⚠️ Operação cancelada. Use confirmar=True para confirmar a remoção."
    try:
        svc = _get_factory().get_client_service()
        result = svc.soft_delete_service(cliente, servico, confirmar=True)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except Exception as e:
        _logger.error(f"remover_servico failed: {e}", exc_info=True)
        return f"❌ Error removing service: {e}"


def restaurar_servico(cliente: str, servico: str) -> str:
    """
    Restores a previously deleted service.
    """
    try:
        svc = _get_factory().get_client_service()
        result = svc.restore_service(cliente, servico)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except ValueError as e:
        deleted = svc.get_deleted_services()
        if deleted:
            nomes = "\n".join(
                f"  - {s['client_alias']}/{s['alias']} ({s['codigo'] or 'sem código'})"
                for s in deleted
            )
            return f"❌ {e}\n\nServiços deletados disponíveis:\n{nomes}"
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"restaurar_servico failed: {e}", exc_info=True)
        return f"❌ Error restoring service: {e}"


def atualizar_servico(cliente: str, servico: str, campo: str, valor) -> str:
    """
    Updates a specific field of a service.
    Valid fields: Modalidade, Ano, Demanda, AreaTotal, AreaCoberta, AreaDescoberta,
                  Detalhes, Estilo, Ambientes, ValorProposta, ValorContrato
    """
    try:
        svc = _get_factory().get_client_service()
        result = svc.update_service_info(cliente, servico, campo, valor)
        if result["success"]:
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
    except Exception as e:
        _logger.error(f"atualizar_servico failed: {e}", exc_info=True)
        return f"❌ Error updating service: {e}"


def criar_estrutura_servico(cliente: str, nome: str) -> str:
    """
    Creates the full folder structure for a new service under a client.
    Includes {DOC}, {ADM}, {OP} with configurable op phases.
    The service is automatically registered in the database with a unique CodServico.
    PARAMETERS:
      cliente: Client name (supports fuzzy match)
      nome: Service name
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name as _normalize
        normalized = _normalize(nome)
        config = _get_config()
        svc = _get_factory().get_client_service()
        client_path = svc.resolve_client_path(cliente)
        client_alias = client_path.name
        service_path = client_path / normalized
        if service_path.exists():
            return f"⚠️ Service '{normalized}' already exists under '{cliente}'."
        service_path.mkdir(parents=True)
        (service_path / config.folder_doc).mkdir()
        (service_path / config.folder_adm).mkdir()
        op_path = service_path / config.folder_op
        op_path.mkdir()
        for phase in config.folder_op_phases:
            (op_path / phase).mkdir()
        entry = svc.create_service_entry(client_alias, normalized)
        cod_servico = entry['CodServico']
        from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
        template_path = PathManager.get_info_template_path()
        if template_path.exists():
            from foton_system.modules.shared.domain.info_pattern_resolver import InfoPatternResolver
            resolver = InfoPatternResolver(config.info_file_patterns['servico'])
            info_filename = resolver.resolve(
                codServico=cod_servico,
                aliasServico=normalized,
                versao="00",
                revisao="00"
            )
            import shutil
            shutil.copy(template_path, service_path / info_filename)
        return (
            f"✅ Estrutura de serviço criada: '{normalized}' em '{cliente}'\n"
            f"   📁 {config.folder_doc}/\n"
            f"   📁 {config.folder_adm}/\n"
            f"   📁 {config.folder_op}/ ({', '.join(config.folder_op_phases)})\n"
            f"   🆔 Código do serviço: {cod_servico}"
        )
    except ValueError as e:
        return f"❌ {e}"
    except Exception as e:
        _logger.error(f"criar_estrutura_servico failed: {e}", exc_info=True)
        return f"❌ Error creating service structure: {e}"


def preencher_codigos_faltantes() -> str:
    """
    Preenche automaticamente CodCliente e CodServico faltantes (NaN) no banco de dados.
    Gera códigos únicos para todos os registros que ainda não possuem código.
    """
    try:
        result = _get_factory().get_client_service().fill_missing_codes()
        clientes = result['clientes_alterados']
        servicos = result['servicos_alterados']
        parts = []
        if clientes:
            parts.append(f"{clientes} cliente(s)")
        if servicos:
            parts.append(f"{servicos} serviço(s)")
        if not parts:
            return "✅ Nenhum código faltante encontrado. Todos os registros já possuem código."
        return f"✅ Códigos preenchidos para {' e '.join(parts)}."
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def validar_codigos_servicos() -> str:
    """
    Valida todos os códigos de serviço (CodServico) no banco de dados.
    Verifica códigos ausentes, placeholders, formato inválido e duplicatas.
    Sempre executa preencher_codigos_faltantes primeiro.
    """
    try:
        svc = _get_factory().get_client_service()
        svc.fill_missing_codes()
        issues = svc.validate_service_codes()
        if not issues:
            return "✅ Todos os códigos de serviço são válidos."
        lines = [f"📋 {len(issues)} código(s) de serviço com problema:\n"]
        for i, iss in enumerate(issues, 1):
            svc_label = f"{iss['client_alias']}/{iss['service_alias']}"
            lines.append(f"  [{i}] [{iss['issue'].upper()}] {svc_label}")
            lines.append(f"      Código atual: '{iss['cod_servico']}'")
            lines.append(f"      💡 Sugestão: {iss['suggested_fix']}")
            lines.append("")
        return "\n".join(lines)
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"validar_codigos_servicos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def corrigir_codigos_servicos() -> str:
    """
    Corrige automaticamente todos os códigos de serviço inválidos no banco de dados.
    Gera novos códigos únicos para placeholders, formatos inválidos e duplicatas.
    """
    try:
        svc = _get_factory().get_client_service()
        svc.fill_missing_codes()
        issues = svc.validate_service_codes()
        if not issues:
            return "✅ Todos os códigos de serviço já são válidos. Nenhuma correção necessária."
        fixed = svc.fix_service_codes(issues)
        return f"✅ {fixed} código(s) de serviço corrigido(s) automaticamente."
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"corrigir_codigos_servicos failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def pipeline_novo_cliente(nome: str, apelido: str = "", nif: str = "", email: str = "", telefone: str = "") -> str:
    """
    SAFE workflow to create a client while checking for duplicates.
    AI RECOMMENDED: Always prefer this over 'cadastrar_cliente'.
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_validation import normalize_client_name as _normalize
        normalized = _normalize(nome)
        factory = _get_factory()
        svc = factory.get_client_service()

        try:
            exists = svc.resolve_client_path(normalized)
            return f"⚠️ PIPELINE STOPPED — A similar client already exists: {exists.name}. Use 'ler_ficha_cliente' to verify."
        except ValueError:
            pass

        if nif:
            existing = svc.list_clients()
            base = _get_config().base_pasta_clientes
            from foton_system.modules.shared.infrastructure.services.path_manager import PathManager
            info_glob = PathManager.get_info_glob("cliente")
            for c in existing:
                info_paths = list((base / c['name']).glob(info_glob))
                info_path = info_paths[0] if info_paths else None
                if info_path and info_path.exists():
                    try:
                        for line in info_path.read_text(encoding='utf-8').splitlines():
                            if line.strip().lower().startswith('@nif'):
                                stored = line.split(';', 1)[-1].strip()
                                if stored == nif:
                                    return f"⚠️ PIPELINE STOPPED — NIF '{nif}' already registered under '{c['name']}'."
                    except Exception:
                        continue

        result = cadastrar_cliente(nome, apelido, nif, email, telefone)
        return result
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Pipeline error: {e}"


def verificar_conformidade_clientes(modo: str = "check") -> str:
    """
    Audits client folders for naming and INFO file pattern compliance.
    PARAMETERS:
      modo: 'check' (default) — list non-conformant items
            'all' — list all items including previously accepted
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_conformance import ClientConformanceChecker
        config = _get_config()
        checker = ClientConformanceChecker(config)
        items = checker.check()

        if not items:
            return "✅ All clients conform to the configured patterns."

        lines = [f"📋 {len(items)} non-conformant item(s) found:\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"  [{i}] [{item.severity.upper()}] {item.tipo}")
            lines.append(f"      {item.description}")
            if item.suggested_fix:
                lines.append(f"      💡 Fix: {item.suggested_fix}")
            lines.append(f"      📁 {item.path}")
            lines.append("")
        return "\n".join(lines)
    except Exception as e:
        _logger.error(f"verificar_conformidade_clientes failed: {e}", exc_info=True)
        return f"❌ Conformance check error: {e}"


def corrigir_conformidade(item_id: str) -> str:
    """
    Applies the suggested fix for a specific non-conformant item.
    PARAMETERS:
      item_id: The item ID from verificar_conformidade_clientes output
    """
    try:
        from foton_system.modules.clients.application.use_cases.client_conformance import ClientConformanceChecker
        config = _get_config()
        checker = ClientConformanceChecker(config)
        items = checker.check()

        target = next((i for i in items if i.item_id == item_id), None)
        if not target:
            return f"❌ Item '{item_id}' not found or already fixed."

        success = checker.auto_fix(target)
        if success:
            return f"✅ Fixed: {target.description}"
        return f"❌ Failed to fix: {target.description}"
    except Exception as e:
        _logger.error(f"corrigir_conformidade failed: {e}", exc_info=True)
        return f"❌ Fix error: {e}"


def register_clients_tools(mcp) -> None:
    """Registra as ferramentas de clientes na instância FastMCP."""
    mcp.tool()(_log_tool_call(listar_clientes))
    mcp.tool()(_log_tool_call(cadastrar_cliente))
    mcp.tool()(_log_tool_call(ler_ficha_cliente))
    mcp.tool()(_log_tool_call(atualizar_ficha_cliente))
    mcp.tool()(_log_tool_call(listar_servicos_cliente))
    mcp.tool()(_log_tool_call(remover_cliente))
    mcp.tool()(_log_tool_call(restaurar_cliente))
    mcp.tool()(_log_tool_call(remover_servico))
    mcp.tool()(_log_tool_call(restaurar_servico))
    mcp.tool()(_log_tool_call(atualizar_servico))
    mcp.tool()(_log_tool_call(criar_estrutura_servico))
    mcp.tool()(_log_tool_call(preencher_codigos_faltantes))
    mcp.tool()(_log_tool_call(validar_codigos_servicos))
    mcp.tool()(_log_tool_call(corrigir_codigos_servicos))
    mcp.tool()(_log_tool_call(pipeline_novo_cliente))
    mcp.tool()(_log_tool_call(verificar_conformidade_clientes))
    mcp.tool()(_log_tool_call(corrigir_conformidade))
