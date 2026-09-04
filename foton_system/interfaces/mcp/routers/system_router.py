"""
Roteador MCP para ferramentas de Infraestrutura e Diagnóstico do Sistema.
"""

import os
import time
from pathlib import Path

from foton_system.interfaces.mcp.routers.common import (
    _logger,
    _log_tool_call,
    _get_config,
)
from foton_system.modules.shared.infrastructure.services.path_manager import PathManager


def ping() -> str:
    """
    Verifies that the Foton MCP server is responsive.
    PROTOCOL: Use this as the very first tool call to ensure the link is active.
    """
    return f"🟢 FOTON MCP Online (pid={os.getpid()}, ts={int(time.time())})"


def info_sistema() -> str:
    """
    Provides a comprehensive diagnostic of the Foton system's environment.
    CONTEXT: Call this at the start of a session to understand folder paths, client counts, 
    template availability, and active business rules (like missing variable placeholders).
    Returns path configurations and module availability.
    """
    try:
        config = _get_config()
        clients_dir = config.base_pasta_clientes
        templates_dir = config.templates_path
        mode_str = "🧪 SANDBOX (Ambiente de Teste)" if PathManager.is_sandbox_active() else "🏗️ PRODUÇÃO"

        client_count = 0
        if clients_dir.exists():
            ignored = set(config.ignored_folders + ['.obsidian'])
            client_count = sum(
                1 for d in clients_dir.iterdir()
                if d.is_dir() and d.name not in ignored
            )

        template_count = 0
        if templates_dir.exists():
            template_count = sum(
                1 for f in templates_dir.iterdir()
                if f.suffix.lower() in ('.docx', '.pptx')
            )

        output = (
            "📊 FOTON System Status\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  🛠️ Modo:      {mode_str}\n"
            f"  📂 Clientes:  {clients_dir}\n"
            f"     → {client_count} cliente(s) encontrado(s)\n"
            f"  📄 Templates: {templates_dir}\n"
            f"     → {template_count} template(s) disponíveis\n"
            f"  💾 Base Dados: {config.base_dados}\n"
            f"  🚫 Pastas ignoradas: {', '.join(config.ignored_folders)}\n"
            f"  🧹 Limpar variáveis faltantes: {config.clean_missing_variables}\n"
            f"  📝 Placeholder: '{config.missing_variable_placeholder}'\n"
        )
        return output
    except OSError as e:
        _logger.error(f"info_sistema I/O error: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        return f"❌ Error retrieving system info: {e}"


def consultar_cub() -> str:
    """
    Returns the current CUB (Custo Unitário Básico) reference month and download URL.
    CONTEXT: Used in document generation for construction cost estimates (@LinkCUB, @ReferenciaCUB).
    """
    try:
        from foton_system.modules.shared.infrastructure.services.cub_service import CubService
        ref = CubService.get_reference_label()
        url = CubService.get_dynamic_url()
        return (
            f"📊 CUB Reference\n"
            f"   Mês: {ref}\n"
            f"   URL: {url}\n"
            f"   Fonte: SINDUSCON-GO"
        )
    except (OSError, ConnectionError) as e:
        _logger.error(f"consultar_cub network error: {e}", exc_info=True)
        return f"❌ CUB connection error: {e}"
    except Exception as e:
        _logger.error(f"consultar_cub failed: {e}", exc_info=True)
        return f"❌ CUB error: {e}"


def verificar_atualizacao() -> str:
    """
    Checks GitHub for a newer version of the Foton System.
    PROTOCOL: Run periodically to ensure the system is up-to-date.
    """
    try:
        from foton_system.modules.shared.infrastructure.services.update_service import UpdateChecker
        from foton_system import __version__
        has_update, latest, url = UpdateChecker.check_for_updates()
        if has_update:
            return (
                f"🔄 Nova versão disponível!\n"
                f"   Atual:    v{__version__}\n"
                f"   Recente:  v{latest}\n"
                f"   URL:      {url}"
            )
        return f"✅ Sistema atualizado (v{__version__})"
    except (OSError, ConnectionError) as e:
        _logger.error(f"verificar_atualizacao network error: {e}", exc_info=True)
        return f"❌ Network error: {e}"
    except Exception as e:
        _logger.error(f"verificar_atualizacao failed: {e}", exc_info=True)
        return f"❌ Update check error: {e}"


def consultar_auditoria(limite: int = 10) -> str:
    """
    Shows the most recent audit events (POP operations).
    PARAMETERS:
      limite: Number of events to show (default 10)
    """
    try:
        from foton_system.core.ops.audit_logger import AuditLogger
        events = AuditLogger().get_recent_events(limit=limite)
        if not events:
            return "📭 No audit events found."

        output = f"📋 Últimos {len(events)} eventos de auditoria:\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for e in events:
            ts = e.get('timestamp', '?')
            op = e.get('op', '?')
            actor = e.get('actor', '?')
            client = e.get('client_id', '?')
            status = e.get('status', '?')
            output += f"  [{ts}] {op} by {actor} → {client} [{status}]\n"
        return output
    except ValueError as e:
        return f"❌ Invalid parameter: {e}"
    except OSError as e:
        _logger.error(f"consultar_auditoria I/O: {e}", exc_info=True)
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"consultar_auditoria failed: {e}", exc_info=True)
        return f"❌ Audit error: {e}"


def configurar_agente() -> str:
    """
    Automates the formal installation of the Foton AI Skill into the Gemini CLI.
    Copies the SKILL.md from the repository to the local .gemini/skills folder.
    AI RECOMMENDED: Run this to enable specialized architectural reasoning from the repository source.
    """
    try:
        config = _get_config()
        # Source is in the repository
        # Assume foton_system is inside the repo root
        repo_root = Path(__file__).resolve().parents[4]
        repo_skill_file = repo_root / "skills" / "foton-architecture" / "SKILL.md"
        
        if not repo_skill_file.exists():
            return f"❌ Erro: Arquivo de origem não encontrado no repositório: {repo_skill_file}"

        # Destination is the official workspace skill path
        workspace_root = config.base_pasta_clientes.parent
        skill_dir = workspace_root / ".gemini" / "skills" / "foton-architecture"
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        target_skill_file = skill_dir / "SKILL.md"
        
        # Copy content from repo to local installation
        content = repo_skill_file.read_text(encoding="utf-8")
        target_skill_file.write_text(content, encoding="utf-8")
        
        return (
            f"✅ Foton Skill instalada a partir do repositório!\n"
            f"   Origem: {repo_skill_file}\n"
            f"   Destino: {target_skill_file}\n"
            f"   ⚠️ IMPORTANTE: Execute o comando '/skills reload' no chat para ativar a expertise."
        )
    except (OSError, PermissionError) as e:
        _logger.error(f"configurar_agente file error: {e}", exc_info=True)
        return f"❌ File access error: {e}"
    except Exception as e:
        _logger.error(f"configurar_agente failed: {e}", exc_info=True)
        return f"❌ Erro ao configurar skill: {e}"


def register_system_tools(mcp) -> None:
    """Registra as ferramentas de sistema na instância FastMCP."""
    mcp.tool()(_log_tool_call(ping))
    mcp.tool()(_log_tool_call(info_sistema))
    mcp.tool()(_log_tool_call(consultar_cub))
    mcp.tool()(_log_tool_call(verificar_atualizacao))
    mcp.tool()(_log_tool_call(consultar_auditoria))
    mcp.tool()(_log_tool_call(configurar_agente))
