"""
Roteador MCP para ferramentas de Sincronização de Dados e Pastas.
"""

from foton_system.interfaces.mcp.routers.common import (
    _logger,
    _log_tool_call,
    _get_factory,
)


def pipeline_sincronizacao(direcao: str = "bidir", dry_run: bool = True) -> str:
    """
    Unified sync pipeline for Clients and Services.

    DIRECTIONS:
    - "pastas_to_db": Discover new folders -> add to database
    - "db_to_pastas": Ensure database entries have folders
    - "bidir": Both directions (default)

    PARAMETERS:
      dry_run: If True, only detect differences without applying (default True)

    Returns a consolidated report with counts and errors.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao=direcao, dry_run=dry_run)
        return report.resumo()
    except Exception as e:
        _logger.error(f"pipeline_sincronizacao failed: {e}", exc_info=True)
        return f"❌ Error running sync pipeline: {e}"


def sincronizar_base() -> str:
    """
    Syncs the Excel Master Dashboard with the filesystem.
    Delegates to pipeline_sincronizacao (bidir) for unified sync.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="bidir", dry_run=False)
        return f"✅ Dashboard synchronized! {report.resumo()}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Sync error: {e}"


def sincronizar_clientes() -> str:
    """
    Discovers new client/service folders and adds them to the Excel database.
    Delegates to pipeline_sincronizacao (pastas_to_db) for unified sync.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="pastas_to_db", dry_run=False)
        return f"✅ Client & service databases synchronized! {report.resumo()}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Client sync error: {e}"


def sincronizar_pastas_clientes() -> str:
    """
    Creates client folders for entries in the database that are missing folders.
    Delegates to pipeline_sincronizacao (db_to_pastas) for unified sync.
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="db_to_pastas", dry_run=False)
        return f"✅ Client folders synchronized. {report.resumo()}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def sincronizar_pastas_servicos(cliente: str = "") -> str:
    """
    Creates service folders for entries in the database that are missing folders.
    Delegates to pipeline_sincronizacao (db_to_pastas) for unified sync.
    PARAMETERS:
      cliente: Optional client alias to filter (default: all clients)
    """
    try:
        from foton_system.modules.clients.application.use_cases.pipeline_sync import pipeline_sincronizacao as _pipeline
        report = _pipeline(direcao="db_to_pastas", dry_run=False)
        return f"✅ Service folders synchronized. {report.resumo()}"
    except ValueError as e:
        return f"❌ Invalid client name: {e}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def exportar_dados_clientes() -> str:
    """
    Exports client data from the database to MD files in client folders.
    """
    try:
        result = _get_factory().get_client_service().export_client_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def exportar_dados_servicos() -> str:
    """
    Exports service data from the database to MD files in service folders.
    """
    try:
        result = _get_factory().get_client_service().export_service_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def importar_dados_clientes() -> str:
    """
    Importa dados de clientes dos arquivos INFO de volta para o banco de dados.
    """
    try:
        result = _get_factory().get_client_service().import_client_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def importar_dados_servicos() -> str:
    """
    Imports service data from MD files back into the database.
    """
    try:
        result = _get_factory().get_client_service().import_service_data()
        return f"✅ {result}"
    except OSError as e:
        return f"❌ File access error: {e}"
    except Exception as e:
        return f"❌ Error: {e}"


def register_sync_tools(mcp) -> None:
    """Registra as ferramentas de sincronização na instância FastMCP."""
    mcp.tool()(_log_tool_call(pipeline_sincronizacao))
    mcp.tool()(_log_tool_call(sincronizar_base))
    mcp.tool()(_log_tool_call(sincronizar_clientes))
    mcp.tool()(_log_tool_call(sincronizar_pastas_clientes))
    mcp.tool()(_log_tool_call(sincronizar_pastas_servicos))
    mcp.tool()(_log_tool_call(exportar_dados_clientes))
    mcp.tool()(_log_tool_call(exportar_dados_servicos))
    mcp.tool()(_log_tool_call(importar_dados_clientes))
    mcp.tool()(_log_tool_call(importar_dados_servicos))
