import unittest
from foton_system.interfaces.mcp.foton_mcp import _validate_dados_extras


class TestValidateDadosExtras(unittest.TestCase):
    """D1: Tests for dados_extras validation [RULE-DOC-2.2]"""

    def test_valid_dict_passes(self):
        _validate_dados_extras({"@nome": "Joao", "@valor": "100"})

    def test_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            _validate_dados_extras("not a dict")

    def test_exceeds_max_keys_raises(self):
        big = {str(i): i for i in range(51)}
        with self.assertRaises(ValueError):
            _validate_dados_extras(big)

    def test_nested_dict_value_raises(self):
        with self.assertRaises(ValueError):
            _validate_dados_extras({"@data": {"nested": "val"}})

    def test_list_value_raises(self):
        with self.assertRaises(ValueError):
            _validate_dados_extras({"@items": [1, 2, 3]})

    def test_empty_key_raises(self):
        with self.assertRaises(ValueError):
            _validate_dados_extras({"": "empty"})

    def test_non_string_key_raises(self):
        with self.assertRaises(ValueError):
            _validate_dados_extras({1: "numeric key"})


class TestPathTraversalEnforcement(unittest.TestCase):
    """D2: Path traversal sanitization tests [RULE-DOC-2.3]"""

    def test_sanitize_path_component_blocks_traversal(self):
        from foton_system.interfaces.mcp.mcp_services import sanitize_path_component
        result = sanitize_path_component("../../etc/passwd")
        self.assertEqual(result, "passwd")

    def test_sanitize_keeps_normal_name(self):
        from foton_system.interfaces.mcp.mcp_services import sanitize_path_component
        result = sanitize_path_component("CLIENTE_NORMAL")
        self.assertEqual(result, "CLIENTE_NORMAL")

    def test_sanitize_empty_string(self):
        from foton_system.interfaces.mcp.mcp_services import sanitize_path_component
        result = sanitize_path_component("")
        self.assertEqual(result, "")

    def test_resolve_template_path_sanitizes(self):
        from foton_system.core.ops.op_doc_gen import _resolve_template_path
        with self.assertRaises(FileNotFoundError):
            _resolve_template_path("../../etc/passwd")

    def test_resolve_client_path_sanitizes(self):
        from foton_system.core.ops.op_doc_gen import _resolve_client_path
        with self.assertRaises(FileNotFoundError):
            _resolve_client_path("../../etc/passwd")


if __name__ == '__main__':
    unittest.main()
