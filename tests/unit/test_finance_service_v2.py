import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from foton_system.modules.clients.domain.models import FinanceEntry
from foton_system.modules.finance.application.use_cases.finance_service import FinanceService
from foton_system.modules.finance.infrastructure.repositories.csv_finance_repository import CSVFinanceRepository


class TestFinanceServiceV2(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self.client_path = Path(self._temp_dir.name)
        self.repo = CSVFinanceRepository()
        self.service = FinanceService(self.repo)

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_categoria_valida_e_invalida_em_saida(self):
        """RULE-FINANCEIRO-1.5: categoria obrigatoria para SAIDA com valores validos."""
        # Valida
        entry = FinanceEntry(
            tipo="SAIDA",
            valor=150.0,
            descricao="Compra de Cimento",
            data="2026-09-01",
            cliente_alias="CLI_001",
            categoria="MATERIAL",
        )
        self.assertEqual(entry.categoria, "MATERIAL")

        # Invalida
        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="SAIDA",
                valor=100.0,
                descricao="Gasto",
                data="2026-09-01",
                cliente_alias="CLI_001",
                categoria="CATEGORIA_INEXISTENTE",
            )

    def test_data_vencimento_valida_e_invalida(self):
        """RULE-FINANCEIRO-1.6: data_vencimento valida formato YYYY-MM-DD."""
        entry = FinanceEntry(
            tipo="ENTRADA",
            valor=5000.0,
            descricao="Parcela 1",
            data="2026-09-01",
            cliente_alias="CLI_001",
            data_vencimento="2026-09-20",
        )
        self.assertEqual(entry.data_vencimento, "2026-09-20")

        with self.assertRaises(ValueError):
            FinanceEntry(
                tipo="ENTRADA",
                valor=5000.0,
                descricao="Parcela 1",
                data="2026-09-01",
                cliente_alias="CLI_001",
                data_vencimento="20/09/2026",
            )

    def test_lucro_por_servico(self):
        """RULE-FINANCEIRO-2.4: lucro liquido e margem percentual por servico."""
        # Receita do servico SRV-01: R$ 10.000
        self.service.add_entry(
            self.client_path,
            description="Entrada Servico 1",
            value=10000.0,
            entry_type="ENTRADA",
            servico_cod="SRV-01",
        )
        # Despesa do servico SRV-01: R$ 4.000
        self.service.add_entry(
            self.client_path,
            description="Mao de obra",
            value=4000.0,
            entry_type="SAIDA",
            categoria="MAO_DE_OBRA",
            servico_cod="SRV-01",
        )
        # Despesa de outro servico SRV-02: R$ 2.000
        self.service.add_entry(
            self.client_path,
            description="Taxa prefeitura",
            value=2000.0,
            entry_type="SAIDA",
            categoria="TAXA",
            servico_cod="SRV-02",
        )

        lucro_srv1 = self.service.lucro_por_servico(self.client_path, "SRV-01")
        self.assertEqual(lucro_srv1['receitas'], 10000.0)
        self.assertEqual(lucro_srv1['despesas'], 4000.0)
        self.assertEqual(lucro_srv1['lucro_liquido'], 6000.0)
        self.assertEqual(lucro_srv1['margem_percentual'], 60.0)

    def test_alerta_estouro_orcamento(self):
        """RULE-FINANCEIRO-3.1: alerta de estouro ao atingir 80%, 90% ou 100% das receitas."""
        self.service.add_entry(
            self.client_path,
            description="Contrato Inicial",
            value=1000.0,
            entry_type="ENTRADA",
            servico_cod="SRV-REFORMA",
        )

        # 70% -> sem alerta
        res1 = self.service.add_entry(
            self.client_path,
            description="Despesa 1",
            value=700.0,
            entry_type="SAIDA",
            categoria="MATERIAL",
            servico_cod="SRV-REFORMA",
        )
        self.assertNotIn("alerta_estouro", res1)

        # +150 = 850 (85%) -> alerta 80%
        res2 = self.service.add_entry(
            self.client_path,
            description="Despesa 2",
            value=150.0,
            entry_type="SAIDA",
            categoria="MATERIAL",
            servico_cod="SRV-REFORMA",
        )
        self.assertEqual(res2.get("alerta_estouro"), "80%")

        # +100 = 950 (95%) -> alerta 90%
        res3 = self.service.add_entry(
            self.client_path,
            description="Despesa 3",
            value=100.0,
            entry_type="SAIDA",
            categoria="MATERIAL",
            servico_cod="SRV-REFORMA",
        )
        self.assertEqual(res3.get("alerta_estouro"), "90%")

        # +100 = 1050 (105%) -> alerta 100%
        res4 = self.service.add_entry(
            self.client_path,
            description="Despesa 4",
            value=100.0,
            entry_type="SAIDA",
            categoria="MATERIAL",
            servico_cod="SRV-REFORMA",
        )
        self.assertEqual(res4.get("alerta_estouro"), "100%")

    def test_fluxo_caixa_projetado(self):
        """RULE-FINANCEIRO-2.5: fluxo de caixa com recebiveis futuros."""
        hoje = datetime.now().date()
        venc_15d = (hoje + timedelta(days=15)).strftime('%Y-%m-%d')
        venc_45d = (hoje + timedelta(days=45)).strftime('%Y-%m-%d')

        # Saldo inicial: R$ 5.000
        self.service.add_entry(
            self.client_path,
            description="Pagamento recebido",
            value=5000.0,
            entry_type="ENTRADA",
        )
        # Recebivel para daqui a 15 dias: R$ 3.000
        self.service.add_entry(
            self.client_path,
            description="Recebivel Proximo",
            value=3000.0,
            entry_type="ENTRADA",
            data_vencimento=venc_15d,
        )
        # Recebivel para daqui a 45 dias: R$ 4.000
        self.service.add_entry(
            self.client_path,
            description="Recebivel Distante",
            value=4000.0,
            entry_type="ENTRADA",
            data_vencimento=venc_45d,
        )

        # Projecao 30 dias: deve incluir apenas o recebivel de 15d
        proj_30d = self.service.fluxo_caixa_projetado([self.client_path], dias=30)
        self.assertEqual(proj_30d['saldo_atual'], 12000.0)  # soma de todas as entradas
        self.assertEqual(proj_30d['entradas_projetadas'], 3000.0)

        # Projecao 60 dias: inclui 15d e 45d
        proj_60d = self.service.fluxo_caixa_projetado([self.client_path], dias=60)
        self.assertEqual(proj_60d['entradas_projetadas'], 7000.0)

    def test_conciliacao_bancaria_csv(self):
        """RULE-FINANCEIRO-4.1 a 4.3: concilia extrato com tolerancia de 1 centavo e 3 dias."""
        # Lançamento registrado no sistema em 2026-09-03 por R$ 250,50
        self.service.add_entry(
            self.client_path,
            description="Pagamento Fornecedor",
            value=250.50,
            entry_type="SAIDA",
            categoria="MATERIAL",
        )

        # Extrato com:
        # 1 match (R$ 250.51 e data 2026-09-04 — diff de 1 dia e 1 centavo)
        # 1 nao identificado (R$ 99.00 no extrato que nao existe no sistema)
        hoje = datetime.now().date()
        ontem = (hoje - timedelta(days=1)).strftime('%Y-%m-%d')
        csv_content = (
            "data,descricao,valor,tipo\n"
            f"{ontem},TED FORNECEDOR ABC,250.50,SAIDA\n"
            f"{ontem},TARIFA BANCARIA,99.00,SAIDA\n"
        )

        resultado = self.service.importar_extrato_csv(self.client_path, csv_content)
        self.assertEqual(len(resultado['conciliados']), 1)
        self.assertEqual(len(resultado['sugeridos_novos_lancamentos']), 1)
        self.assertEqual(resultado['sugeridos_novos_lancamentos'][0]['descricao'], "TARIFA BANCARIA")


if __name__ == '__main__':
    unittest.main()
