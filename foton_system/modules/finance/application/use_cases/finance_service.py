from pathlib import Path
from datetime import datetime, timedelta
import csv
import io
from typing import Dict, Any, Optional, List

from foton_system.modules.shared.infrastructure.utils.formatting import FotonFormatter
from foton_system.modules.finance.application.ports.finance_repository_port import FinanceRepositoryPort
from foton_system.modules.clients.domain.models import FinanceEntry
from foton_system.modules.clients.domain.models.finance_entry import CATEGORIAS_SAIDA_VALIDAS


class FinanceService:
    def __init__(self, repository: FinanceRepositoryPort):
        self.repository = repository
        self.headers = [
            'Data',
            'Descricao',
            'Tipo',
            'Valor',
            'Categoria',
            'DataVencimento',
            'ServicoCod',
            'Conciliado',
        ]

    def add_entry(
        self,
        client_path: Path,
        description: str = "",
        value: Any = 0.0,
        entry_type: str = 'ENTRADA',
        entry: Optional[FinanceEntry] = None,
        categoria: str = "OUTROS",
        data_vencimento: Optional[str] = None,
        servico_cod: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Adiciona uma movimentacao financeira e retorna o resumo com metricas v2.0.

        Suporta:
        1. Modo legado por argumentos posicionais/nomeados.
        2. Modo v2.0 com categoria, data_vencimento, servico_cod e alerta de estouro.
        3. Modo objeto tipado: entry=FinanceEntry(...)
        """
        if entry is not None:
            description = entry.descricao
            clean_value = float(entry.valor)
            entry_type = entry.tipo.upper()
            today = entry.data or datetime.now().strftime('%Y-%m-%d')
            cat = entry.categoria or ("OUTROS" if entry_type == "SAIDA" else "")
            venc = entry.data_vencimento or ""
            serv = entry.servico_cod or ""
            conciliado_str = "SIM" if entry.conciliado else "NAO"
        else:
            if isinstance(value, str):
                clean_value = FotonFormatter.parse_br_number(value)
            else:
                clean_value = float(value)
            entry_type = entry_type.upper()
            today = datetime.now().strftime('%Y-%m-%d')
            cat = (categoria or "OUTROS").strip().upper() if entry_type == "SAIDA" else ""
            if entry_type == "SAIDA" and cat not in CATEGORIAS_SAIDA_VALIDAS:
                cat = "OUTROS"
            venc = str(data_vencimento).strip() if data_vencimento else ""
            serv = str(servico_cod).strip() if servico_cod else ""
            conciliado_str = "NAO"

        entry_row = [
            today,
            description,
            entry_type,
            f"{clean_value:.2f}",
            cat,
            venc,
            serv,
            conciliado_str,
        ]

        existing_entries = self.repository.get_entries(client_path)
        is_duplicate = any(
            e.descricao == description
            and abs(float(e.valor) - clean_value) < 0.01
            and e.data == today
            for e in existing_entries
        )

        self.repository.save_entry(client_path, entry_row, self.headers)
        summary = self.get_summary(client_path)

        if is_duplicate:
            summary['duplicate_warning'] = True

        # RULE-FINANCEIRO-3.1: Alerta de estouro de orcamento por servico
        if entry_type == 'SAIDA' and serv:
            alerta = self._check_budget_overflow(client_path, serv)
            if alerta:
                summary['alerta_estouro'] = alerta

        return summary

    def get_summary(self, client_path: Path) -> Dict[str, float]:
        """Calcula o resumo financeiro a partir das entradas do repositorio."""
        entries = self.repository.get_entries(client_path)

        entradas = 0.0
        saidas = 0.0

        for entry in entries:
            try:
                val = float(entry.valor)
                if entry.tipo == 'ENTRADA':
                    entradas += val
                else:
                    saidas += val
            except (ValueError, AttributeError):
                continue

        return {
            'total_entradas': entradas,
            'total_saidas': saidas,
            'saldo': entradas - saidas,
        }

    def lucro_por_servico(self, client_path: Path, servico_cod: str) -> Dict[str, Any]:
        """
        RULE-FINANCEIRO-2.4: Calcula e retorna lucro liquido por servico.
        Formula: entradas - saidas vinculadas ao servico, margem percentual.
        """
        entries = self.repository.get_entries(client_path)
        cod_alvo = str(servico_cod).strip().upper()

        entradas_serv = 0.0
        saidas_serv = 0.0

        for e in entries:
            entry_serv = str(e.servico_cod or "").strip().upper()
            if entry_serv == cod_alvo:
                try:
                    val = float(e.valor)
                    if e.tipo == 'ENTRADA':
                        entradas_serv += val
                    else:
                        saidas_serv += val
                except (ValueError, AttributeError):
                    continue

        lucro = entradas_serv - saidas_serv
        margem = (lucro / entradas_serv * 100.0) if entradas_serv > 0 else 0.0

        return {
            'servico_cod': servico_cod,
            'receitas': entradas_serv,
            'despesas': saidas_serv,
            'lucro_liquido': lucro,
            'margem_percentual': round(margem, 2),
        }

    def _check_budget_overflow(self, client_path: Path, servico_cod: str) -> Optional[str]:
        """RULE-FINANCEIRO-3.1: Alerta se despesas atingirem 80%, 90% ou 100% das receitas do servico."""
        info = self.lucro_por_servico(client_path, servico_cod)
        receitas = info['receitas']
        despesas = info['despesas']

        if receitas <= 0:
            return None

        ratio = despesas / receitas
        if ratio >= 1.0:
            return "100%"
        elif ratio >= 0.9:
            return "90%"
        elif ratio >= 0.8:
            return "80%"
        return None

    def fluxo_caixa_projetado(self, client_paths: List[Path], dias: int = 30) -> Dict[str, Any]:
        """
        RULE-FINANCEIRO-2.5: Projeta saldo futuro para 30, 60 e 90 dias.
        Calculo: saldo atual + recebiveis com data_vencimento no periodo.
        """
        saldo_atual_total = 0.0
        entradas_projetadas = 0.0
        hoje = datetime.now().date()
        data_limite = hoje + timedelta(days=dias)

        recebiveis_detalhe = []

        for p in client_paths:
            try:
                summary = self.get_summary(p)
                saldo_atual_total += summary['saldo']

                entries = self.repository.get_entries(p)
                for e in entries:
                    if e.tipo == 'ENTRADA' and e.data_vencimento:
                        try:
                            venc_date = datetime.strptime(e.data_vencimento, '%Y-%m-%d').date()
                            if hoje <= venc_date <= data_limite:
                                val = float(e.valor)
                                entradas_projetadas += val
                                recebiveis_detalhe.append({
                                    'cliente': p.name,
                                    'descricao': e.descricao,
                                    'valor': val,
                                    'vencimento': e.data_vencimento,
                                })
                        except (ValueError, TypeError):
                            continue
            except Exception:
                continue

        return {
            'dias_projecao': dias,
            'saldo_atual': saldo_atual_total,
            'entradas_projetadas': entradas_projetadas,
            'saldo_projetado': saldo_atual_total + entradas_projetadas,
            'total_recebiveis': len(recebiveis_detalhe),
            'detalhes': recebiveis_detalhe,
        }

    def painel_financeiro_cliente(self, client_path: Path) -> Dict[str, Any]:
        """
        RULE-FINANCEIRO-2.6: Dashboard analitico do cliente.
        Inclui lucro, despesas por categoria, servicos e alertas.
        """
        summary = self.get_summary(client_path)
        entries = self.repository.get_entries(client_path)

        despesas_por_cat = {cat: 0.0 for cat in CATEGORIAS_SAIDA_VALIDAS}
        servicos_set = set()
        inadimplencias = []
        hoje = datetime.now().date()

        for e in entries:
            if e.servico_cod:
                servicos_set.add(e.servico_cod)

            if e.tipo == 'SAIDA':
                cat = e.categoria or "OUTROS"
                if cat not in despesas_por_cat:
                    cat = "OUTROS"
                try:
                    despesas_por_cat[cat] += float(e.valor)
                except (ValueError, TypeError):
                    pass
            elif e.tipo == 'ENTRADA' and e.data_vencimento and not e.conciliado:
                try:
                    venc_date = datetime.strptime(e.data_vencimento, '%Y-%m-%d').date()
                    if venc_date < hoje:
                        inadimplencias.append({
                            'descricao': e.descricao,
                            'valor': float(e.valor),
                            'vencimento': e.data_vencimento,
                        })
                except (ValueError, TypeError):
                    pass

        servicos_lucro = [
            self.lucro_por_servico(client_path, s) for s in sorted(servicos_set)
        ]

        # Verifica alertas de orcamento nos servicos
        alertas_estouro = []
        for sl in servicos_lucro:
            serv = sl['servico_cod']
            alerta = self._check_budget_overflow(client_path, serv)
            if alerta:
                alertas_estouro.append({'servico_cod': serv, 'nivel': alerta})

        return {
            'cliente': client_path.name,
            'resumo': summary,
            'despesas_por_categoria': {k: v for k, v in despesas_por_cat.items() if v > 0},
            'servicos': servicos_lucro,
            'alertas_estouro': alertas_estouro,
            'inadimplencias': inadimplencias,
        }

    def importar_extrato_csv(self, client_path: Path, csv_content: str) -> Dict[str, Any]:
        """
        RULE-FINANCEIRO-4.1 a 4.3: Conciliacao bancaria a partir de CSV.
        Compara valor (tolerancia R$ 0,01) e data (+/- 3 dias).
        """
        existing_entries = self.repository.get_entries(client_path)
        reader = csv.DictReader(io.StringIO(csv_content.strip()))

        conciliados = []
        nao_identificados = []

        used_sys_indices = set()

        for ext_row in reader:
            try:
                ext_val = abs(float(ext_row.get('valor', 0) or 0))
                ext_data_str = ext_row.get('data', '').strip()
                ext_desc = ext_row.get('descricao', '').strip()
                ext_tipo = ext_row.get('tipo', 'SAIDA').strip().upper()
                ext_date = datetime.strptime(ext_data_str, '%Y-%m-%d').date()
            except Exception:
                continue

            matched = False
            for idx, sys_entry in enumerate(existing_entries):
                if idx in used_sys_indices:
                    continue
                if sys_entry.tipo.upper() != ext_tipo:
                    continue
                if abs(float(sys_entry.valor) - ext_val) <= 0.01:
                    try:
                        sys_date = datetime.strptime(sys_entry.data, '%Y-%m-%d').date()
                        if abs((sys_date - ext_date).days) <= 3:
                            matched = True
                            used_sys_indices.add(idx)
                            conciliados.append({
                                'sistema': sys_entry.descricao,
                                'extrato': ext_desc,
                                'valor': ext_val,
                                'data': ext_data_str,
                            })
                            break
                    except Exception:
                        continue

            if not matched:
                nao_identificados.append({
                    'data': ext_data_str,
                    'descricao': ext_desc,
                    'valor': ext_val,
                    'tipo': ext_tipo,
                })

        nao_conciliados = [
            existing_entries[i].descricao
            for i in range(len(existing_entries))
            if i not in used_sys_indices
        ]

        return {
            'total_extrato': len(conciliados) + len(nao_identificados),
            'conciliados': conciliados,
            'nao_conciliados_sistema': nao_conciliados,
            'sugeridos_novos_lancamentos': nao_identificados,
        }

    def get_firm_summary(self, client_paths: list, progress_callback=None) -> list:
        """Aggregate financial summaries across multiple clients."""
        results = []
        for p in client_paths:
            try:
                summary = self.get_summary(p)
            except Exception:
                continue
            finally:
                if progress_callback:
                    progress_callback(p.name)
            if summary.get('total_entradas', 0) == 0 and summary.get('total_saidas', 0) == 0:
                continue
            results.append({
                'name': p.name,
                'income': summary['total_entradas'],
                'expense': summary['total_saidas'],
                'balance': summary['saldo'],
            })
        return results
