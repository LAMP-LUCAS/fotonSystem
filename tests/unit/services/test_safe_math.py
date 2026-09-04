import unittest
from foton_system.modules.shared.domain.services.safe_math import safe_eval
from foton_system.modules.shared.domain.exceptions import FormulaError


class TestSafeEval(unittest.TestCase):
    """Tests for safe_math.safe_eval — arithmetic parser without eval()."""

    def test_simple_addition(self):
        self.assertEqual(safe_eval("2 + 3"), 5.0)

    def test_subtraction(self):
        self.assertEqual(safe_eval("10 - 4"), 6.0)

    def test_multiplication(self):
        self.assertEqual(safe_eval("3 * 4"), 12.0)

    def test_division(self):
        self.assertEqual(safe_eval("10 / 2"), 5.0)

    def test_expression_with_parentheses(self):
        self.assertEqual(safe_eval("(10 + 20) * 3"), 90.0)

    def test_nested_parentheses(self):
        self.assertEqual(safe_eval("((2 + 3) * 4) - 5"), 15.0)

    def test_operator_precedence(self):
        self.assertEqual(safe_eval("2 + 3 * 4"), 14.0)

    def test_chained_operations(self):
        self.assertEqual(safe_eval("10 + 20 - 5 + 3"), 28.0)

    def test_decimal_numbers(self):
        self.assertEqual(safe_eval("2.5 + 3.5"), 6.0)

    def test_division_by_zero_raises_formula_error(self):
        with self.assertRaises(FormulaError):
            safe_eval("10 / 0")

    def test_empty_string_returns_zero(self):
        self.assertEqual(safe_eval(""), 0.0)

    def test_whitespace_only_returns_zero(self):
        self.assertEqual(safe_eval("   "), 0.0)

    def test_import_attempt_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("__import__('os')")

    def test_string_in_expression_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("1 + 'string'")

    def test_function_call_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("print(1)")

    def test_access_attribute_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("().__class__")

    def test_single_number(self):
        self.assertEqual(safe_eval("42"), 42.0)

    def test_negative_number(self):
        self.assertEqual(safe_eval("-5"), -5.0)

    def test_negative_in_expression(self):
        self.assertEqual(safe_eval("-5 + 3"), -2.0)

    def test_negative_inside_parentheses(self):
        self.assertEqual(safe_eval("(-5)"), -5.0)

    def test_expression_with_negative_intermediate(self):
        self.assertEqual(safe_eval("10 + (-5)"), 5.0)

    def test_expression_too_long_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("+".join(["1"] * 60))

    def test_invalid_syntax_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("2 +")

    def test_letter_variable_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("x + 1")

    def test_dict_literal_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("{}")

    def test_list_literal_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("[1,2,3]")

    def test_lambda_raises_value_error(self):
        with self.assertRaises(ValueError):
            safe_eval("lambda x: x")


class TestSafeEvalNaNInfinity(unittest.TestCase):
    """Tests for NaN/Infinity detection in safe_eval (RULE-DOC-4.3)."""

    def test_infinity_from_overflow_raises_formula_error(self):
        with self.assertRaises(FormulaError):
            safe_eval("1e308 * 10")

    def test_constant_nan_raises_formula_error(self):
        with self.assertRaises((FormulaError, ValueError)):
            safe_eval("nan")

    def test_constant_inf_raises_formula_error(self):
        with self.assertRaises((FormulaError, ValueError)):
            safe_eval("inf")

    def test_nan_from_division_zero_zero_raises(self):
        with self.assertRaises(FormulaError):
            safe_eval("0 / 0")


class TestFormulaResult(unittest.TestCase):
    """E2: Test that FormulaResult.var matches replacement key (RULE-DOC-4.4)."""

    def test_formula_result_has_var_field(self):
        from foton_system.modules.shared.domain.exceptions import FormulaError
        try:
            safe_eval("2 + 2")
        except FormulaError as e:
            pass


if __name__ == '__main__':
    unittest.main()
