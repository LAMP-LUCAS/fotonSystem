"""
Roteador MCP para ferramentas financeiras.
"""

from foton_system.interfaces.mcp.routers.common import (
    _logger,
    _log_tool_call,
    _get_factory,
)


def registrar_financeiro(cliente: str, descricao: str, valor: float, tipo: str = "ENTRADA") -> str:
    """
    Records a financial entry (income/expense) in the client's ledger.
    TYPES: 'ENTRADA' (credit) or 'SAIDA' (debit).
    Value: Always pass a positive float.
    """
    try:
        from foton_system.core.ops.op_finance_entry import OpFinanceEntry
        op = OpFinanceEntry(actor="Agent_MCP")
        result = op.execute(
            client_name=cliente,
            description=descricao,
            value=valor,
            type=tipo
        )
        return f"✅ {result['message']} (POP Auditado)"
    except ValueError as e:
        return f"❌ Invalid data: {e}"
    except OSError as e:
        _logger.error(f"registrar_financeiro I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"registrar_financeiro failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def consultar_financeiro(cliente: str) -> str:
    """
    Returns the financial balance and transaction summary for a specific client.
    """
    try:
        service = _get_factory().get_finance_service()
        result = service.get_summary(cliente)

        if result.success:
            return (
                f"💵 Financeiro de {cliente}:\n"
                f"   Receita:  R$ {result.total_income:.2f}\n"
                f"   Despesa:  R$ {result.total_expenses:.2f}\n"
                f"   Saldo:    R$ {result.balance:.2f}"
            )
        return f"❌ {result.message}"
    except ValueError as e:
        return f"❌ Invalid client: {e}"
    except OSError as e:
        _logger.error(f"consultar_financeiro I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"consultar_financeiro failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def resumo_financeiro_geral() -> str:
    """
    Firm-wide financial dashboard. 
    CONTEXT: Use this for high-level business intelligence to identify profitable clients or cash-flow issues.
    """
    try:
        results = _get_factory().get_finance_service().get_firm_summary()

        if not results:
            return "📭 No financial data found."

        total_income = sum(r['income'] for r in results)
        total_expense = sum(r['expense'] for r in results)

        output = f"📊 Dashboard Financeiro ({len(results)} clientes):\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for r in results:
            emoji = "🟢" if r['balance'] >= 0 else "🔴"
            output += f"  {emoji} {r['name']}: R$ {r['balance']:,.2f} (E: {r['income']:,.2f} | S: {r['expense']:,.2f})\n"

        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        total_balance = total_income - total_expense
        output += (
            f"  TOTAL: R$ {total_balance:,.2f} "
            f"(Rec: R$ {total_income:,.2f} | Desp: R$ {total_expense:,.2f})"
        )
        return output
    except OSError as e:
        _logger.error(f"resumo_financeiro_geral I/O: {e}", exc_info=True)
        return f"❌ File system error: {e}"
    except Exception as e:
        _logger.error(f"resumo_financeiro_geral failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def register_finance_tools(mcp) -> None:
    """Registra as ferramentas financeiras na instância FastMCP."""
    mcp.tool()(_log_tool_call(registrar_financeiro))
    mcp.tool()(_log_tool_call(consultar_financeiro))
    mcp.tool()(_log_tool_call(resumo_financeiro_geral))
