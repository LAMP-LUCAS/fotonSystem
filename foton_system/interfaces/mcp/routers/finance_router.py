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


def lucro_por_servico(cliente: str, servico: str) -> str:
    """
    Calculates net profit and profit margin percentage for a specific service of a client.
    RULE-FINANCEIRO-2.4
    """
    try:
        from foton_system.interfaces.mcp.routers.common import _resolve_client_path
        from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
        client_path = _resolve_client_path(cliente)
        service = FinanceService(CSVFinanceRepository())
        res = service.lucro_por_servico(client_path, servico)

        emoji = "🟢" if res['lucro_liquido'] >= 0 else "🔴"
        return (
            f"{emoji} Lucro por Serviço: {servico} ({cliente})\n"
            f"   Receitas: R$ {res['receitas']:,.2f}\n"
            f"   Despesas: R$ {res['despesas']:,.2f}\n"
            f"   Lucro Líquido: R$ {res['lucro_liquido']:,.2f}\n"
            f"   Margem: {res['margem_percentual']:.1f}%"
        )
    except Exception as e:
        _logger.error(f"lucro_por_servico failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def fluxo_caixa_projetado(dias: int = 30) -> str:
    """
    Projects future cash flow for 30, 60 or 90 days considering receivables.
    RULE-FINANCEIRO-2.5
    """
    try:
        from foton_system.interfaces.mcp.routers.common import _get_config
        from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
        cfg = _get_config()
        base = cfg.base_pasta_clientes
        client_paths = [p for p in base.iterdir() if p.is_dir() and not p.name.startswith(('.', '_'))] if base.exists() else []

        service = FinanceService(CSVFinanceRepository())
        res = service.fluxo_caixa_projetado(client_paths, dias=dias)

        emoji = "🟢" if res['saldo_projetado'] >= 0 else "🔴"
        output = (
            f"📈 Projeção de Fluxo de Caixa ({res['dias_projecao']} dias):\n"
            f"   Saldo Atual: R$ {res['saldo_atual']:,.2f}\n"
            f"   Entradas Previstas: R$ {res['entradas_projetadas']:,.2f} ({res['total_recebiveis']} recebíveis)\n"
            f"   {emoji} Saldo Projetado: R$ {res['saldo_projetado']:,.2f}"
        )
        return output
    except Exception as e:
        _logger.error(f"fluxo_caixa_projetado failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def painel_financeiro_cliente(cliente: str) -> str:
    """
    Complete financial health dashboard for a single client including category breakdown and budget warnings.
    RULE-FINANCEIRO-2.6
    """
    try:
        from foton_system.interfaces.mcp.routers.common import _resolve_client_path
        from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
        client_path = _resolve_client_path(cliente)
        service = FinanceService(CSVFinanceRepository())
        res = service.painel_financeiro_cliente(client_path)

        resumo = res['resumo']
        output = [
            f"📊 Painel Financeiro: {cliente}",
            f"   Receitas: R$ {resumo['total_entradas']:,.2f}",
            f"   Despesas: R$ {resumo['total_saidas']:,.2f}",
            f"   Saldo: R$ {resumo['saldo']:,.2f}",
        ]

        if res['despesas_por_categoria']:
            output.append("\n📁 Despesas por Categoria:")
            for cat, val in res['despesas_por_categoria'].items():
                output.append(f"   • {cat}: R$ {val:,.2f}")

        if res['servicos']:
            output.append("\n🏗 Lucro por Serviço:")
            for s in res['servicos']:
                output.append(f"   • {s['servico_cod']}: R$ {s['lucro_liquido']:,.2f} (Margem: {s['margem_percentual']}%)")

        if res['alertas_estouro']:
            output.append("\n⚠️ Alertas de Orçamento:")
            for a in res['alertas_estouro']:
                output.append(f"   • Atenção: Serviço {a['servico_cod']} atingiu {a['nivel']} do orçamento!")

        if res['inadimplencias']:
            output.append("\n⏰ Recebíveis em Aberto / Vencidos:")
            for ina in res['inadimplencias']:
                output.append(f"   • {ina['descricao']}: R$ {ina['valor']:,.2f} (Vencimento: {ina['vencimento']})")

        return "\n".join(output)
    except Exception as e:
        _logger.error(f"painel_financeiro_cliente failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def conciliar_extrato_bancario(cliente: str, extrato_csv: str) -> str:
    """
    Reconciles a bank statement CSV with the client's recorded transactions.
    RULE-FINANCEIRO-4.1 a 4.3
    """
    try:
        from foton_system.interfaces.mcp.routers.common import _resolve_client_path
        from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
        from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository
        client_path = _resolve_client_path(cliente)
        service = FinanceService(CSVFinanceRepository())
        res = service.importar_extrato_csv(client_path, extrato_csv)

        output = [
            f"📑 Resultado da Conciliação ({cliente}):",
            f"   Transações no Extrato: {res['total_extrato']}",
            f"   ✅ Conciliadas: {len(res['conciliados'])}",
            f"   ❓ Não identificadas no sistema: {len(res['sugeridos_novos_lancamentos'])}",
        ]
        if res['sugeridos_novos_lancamentos']:
            output.append("\n💡 Lançamentos sugeridos para inclusão:")
            for item in res['sugeridos_novos_lancamentos'][:5]:
                output.append(f"   • {item['data']} - {item['descricao']}: R$ {item['valor']:,.2f}")
        return "\n".join(output)
    except Exception as e:
        _logger.error(f"conciliar_extrato_bancario failed: {e}", exc_info=True)
        return f"❌ Error: {e}"


def register_finance_tools(mcp) -> None:
    """Registra as ferramentas financeiras na instância FastMCP."""
    mcp.tool()(_log_tool_call(registrar_financeiro))
    mcp.tool()(_log_tool_call(consultar_financeiro))
    mcp.tool()(_log_tool_call(resumo_financeiro_geral))
    mcp.tool()(_log_tool_call(lucro_por_servico))
    mcp.tool()(_log_tool_call(fluxo_caixa_projetado))
    mcp.tool()(_log_tool_call(painel_financeiro_cliente))
    mcp.tool()(_log_tool_call(conciliar_extrato_bancario))
