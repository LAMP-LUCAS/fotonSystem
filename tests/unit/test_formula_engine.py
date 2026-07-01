import unittest
from foton_system.core.ops.formula_engine import FormulaEngine, FormulaResult
from foton_system.modules.shared.domain.exceptions import FormulaError


class TestFormulaEngineResolve(unittest.TestCase):
    """Tests for FormulaEngine.resolve() — DocumentService replacement."""

    def setUp(self):
        self.engine = FormulaEngine()

    def test_resolve_simple_addition(self):
        data = {
            '@valA': '100',
            '@valB': '50',
            '@total': '[calculo: @valA + @valB]'
        }
        self.engine.resolve(data)
        self.assertEqual(data['@total'], '150.00')

    def test_resolve_complex_expression(self):
        data = {
            '@price': '100',
            '@qty': '3',
            '@total': '[calculo: @price * @qty]'
        }
        self.engine.resolve(data)
        self.assertEqual(data['@total'], '300.00')

    def test_resolve_with_brazilian_format(self):
        data = {
            '@valA': 'R$ 1.000,50',
            '@valB': '500,00',
            '@total': '[calculo: @valA + @valB]'
        }
        self.engine.resolve(data)
        self.assertEqual(data['@total'], '1500.50')

    def test_resolve_handles_missing_var_defaults_zero(self):
        data = {
            '@invalid': '[calculo: @missing + 100]'
        }
        self.engine.resolve(data)
        self.assertEqual(data['@invalid'], '100.00')

    def test_resolve_cascade_deep_dependency(self):
        data = {
            '@e': '[calculo: @d + 10] E',
            '@d': '[calculo: @c + 10] D',
            '@c': '[calculo: @b + 20] C',
            '@b': '[calculo: @a + 30] B',
            '@a': '100',
        }
        self.engine.resolve(data)
        self.assertEqual(data['@a'], '100')
        self.assertEqual(data['@b'], '130.00')
        self.assertEqual(data['@c'], '150.00')
        self.assertEqual(data['@d'], '160.00')
        self.assertEqual(data['@e'], '170.00')

    def test_resolve_cascade_complex_like_document_service(self):
        data = {
            '@areaCoberta': '440',
            '@projArqEng': '41600.52',
            '@procLegais': '105069.46',
            '@CUBref': '[calculo: 2768.47] Referencia CUB do mes',
            '@ACEqv': '[calculo: @areaCoberta] Area construida equivalente',
            '@execcub': '[calculo: @ACEqv * 6.13] Custo execucao baseado no CUB',
            '@execInfra': '[calculo: @execcub * 0.20] Custo de infraestrutura',
            '@execPais': '[calculo: @execcub * 0.05] Custo de paisagismo',
            '@execMob': '[calculo: @execcub * 0.05] Custo de mobiliario',
            '@totalParcial': '[calculo: @projArqEng + @procLegais] Soma dos custos parciais',
            '@totalExec': '[calculo: @execcub + @execInfra + @execPais + @execMob] Soma execucao',
            '@totalinss': '[calculo: @execcub * 0.20] Total INSS',
            '@totalGeral': '[calculo: @totalParcial + @totalExec + @totalinss] Total geral',
            '@Legais': '[calculo: @procLegais / @totalGeral] Percentual legais',
        }
        self.engine.resolve(data)
        self.assertEqual(data['@ACEqv'], '440.00')
        self.assertEqual(data['@execcub'], '2697.20')
        self.assertEqual(data['@execInfra'], '539.44')
        self.assertEqual(data['@execPais'], '134.86')
        self.assertEqual(data['@execMob'], '134.86')
        self.assertEqual(data['@totalParcial'], '146669.98')
        self.assertEqual(data['@totalExec'], '3506.36')
        self.assertEqual(data['@totalinss'], '539.44')
        self.assertEqual(data['@totalGeral'], '150715.78')
        self.assertEqual(data['@Legais'], '0.70')

    def test_resolve_circular_dependency_does_not_loop(self):
        data = {
            '@a': '[calculo: @b + 10] Desc A',
            '@b': '[calculo: @a + 20] Desc B'
        }
        self.engine.resolve(data)
        self.assertNotEqual(data['@a'], data['@b'])

    def test_resolve_case_insensitive(self):
        data = {
            '@valorproposta': '1000',
            '@parcela': '[calculo: @VALORPROPOSTA * 0.1]'
        }
        self.engine.resolve(data)
        self.assertEqual(data['@parcela'], '100.00')

    def test_resolve_preserves_non_formula_values(self):
        data = {
            '@nome': 'João',
            '@valor': '1000',
        }
        self.engine.resolve(data)
        self.assertEqual(data['@nome'], 'João')
        self.assertEqual(data['@valor'], '1000')


class TestFormulaEngineEvaluateExpression(unittest.TestCase):
    """Tests for evaluate_expression() — FormSession harmonization."""

    def setUp(self):
        self.engine = FormulaEngine()

    def test_evaluate_simple_addition(self):
        result = self.engine.evaluate_expression('2 + 3', {})
        self.assertEqual(result, 5.0)

    def test_evaluate_with_var_map(self):
        result = self.engine.evaluate_expression('@a + @b', {'@a': '10', '@b': '20'})
        self.assertEqual(result, 30.0)

    def test_evaluate_brazilian_format(self):
        result = self.engine.evaluate_expression('@a + @b', {'@a': '1.000,50', '@b': '500,00'})
        self.assertEqual(result, 1500.50)

    def test_evaluate_handles_percent_suffix(self):
        result = self.engine.evaluate_expression('@a', {'@a': '50%'})
        self.assertEqual(result, 0.5)

    def test_evaluate_missing_var_defaults_zero(self):
        result = self.engine.evaluate_expression('@missing + 100', {})
        self.assertEqual(result, 100.0)

    def test_evaluate_division_by_zero_raises_formula_error(self):
        with self.assertRaises(FormulaError):
            self.engine.evaluate_expression('10 / 0', {})

    def test_evaluate_empty_expression_returns_zero(self):
        result = self.engine.evaluate_expression('', {})
        self.assertEqual(result, 0.0)

    def test_evaluate_invalid_syntax_raises_formula_error(self):
        with self.assertRaises(FormulaError):
            self.engine.evaluate_expression('2 +', {})


class TestFormulaEngineReport(unittest.TestCase):
    """Tests for FormulaEngine.report() — RULE-DOC-4.4."""

    def setUp(self):
        self.engine = FormulaEngine()

    def test_report_returns_empty_list_initially(self):
        report = self.engine.report()
        self.assertEqual(report, [])

    def test_report_after_resolve_contains_entries(self):
        data = {
            '@a': '10',
            '@b': '20',
            '@total': '[calculo: @a + @b] Soma'
        }
        self.engine.resolve(data)
        report = self.engine.report()
        self.assertGreater(len(report), 0)

    def test_report_entry_structure(self):
        data = {
            '@a': '10',
            '@b': '20',
            '@total': '[calculo: @a + @b] Soma'
        }
        self.engine.resolve(data)
        entry = self.engine.report()[0]
        self.assertIn('var', entry.__dataclass_fields__ if hasattr(entry, '__dataclass_fields__') else dir(entry))
        self.assertTrue(hasattr(entry, 'var'))
        self.assertTrue(hasattr(entry, 'expression'))
        self.assertTrue(hasattr(entry, 'result'))
        self.assertTrue(hasattr(entry, 'status'))

    def test_report_shows_ok_for_valid(self):
        data = {
            '@a': '10',
            '@total': '[calculo: @a * 2]'
        }
        self.engine.resolve(data)
        entry = self.engine.report()[0]
        self.assertEqual(entry.status, 'OK')
        self.assertEqual(entry.result, 20.0)
        self.assertEqual(entry.expression, '@a * 2')

    def test_report_shows_error_on_failure(self):
        data = {
            '@total': '[calculo: 10 / 0]'
        }
        self.engine.resolve(data)
        entry = self.engine.report()[0]
        self.assertEqual(entry.status, 'ERRO')

    def test_report_after_evaluate_expression_contains_entry(self):
        self.engine.evaluate_expression('2 + 3', {})
        report = self.engine.report()
        self.assertGreater(len(report), 0)

    def test_report_resets_on_new_resolve(self):
        data1 = {'@a': '[calculo: 1 + 1]'}
        self.engine.resolve(data1)
        self.assertEqual(len(self.engine.report()), 1)

        data2 = {'@b': '[calculo: 2 + 2]'}
        self.engine.resolve(data2)
        self.assertEqual(len(self.engine.report()), 1)


if __name__ == '__main__':
    unittest.main()
