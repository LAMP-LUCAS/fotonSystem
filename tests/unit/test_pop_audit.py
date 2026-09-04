import unittest
from unittest.mock import patch, MagicMock


class TestPopAudit(unittest.TestCase):
    """D4: Tests for POP audit logging [RULE-DOC-3.4]"""

    @patch('foton_system.core.ops.op_doc_gen.Config')
    @patch('foton_system.core.ops.base_op.AuditLogger')
    @patch('foton_system.core.ops.op_doc_gen.DocumentService')
    def test_generate_document_logs_audit_event(self, MockDocService, MockAudit, MockConfig):
        mock_audit_instance = MagicMock()
        MockAudit.return_value = mock_audit_instance
        mock_config = MagicMock()
        mock_config.base_pasta_clientes = MagicMock()
        mock_config.base_pasta_clientes.exists.return_value = True
        mock_config.templates_path = MagicMock()
        mock_config.templates_path.exists.return_value = True
        MockConfig.return_value = mock_config

        from foton_system.core.ops.op_doc_gen import OpGenerateDocument
        op = OpGenerateDocument(actor="TestAgent")

        mock_client_path = MagicMock()
        mock_client_path.name = "CLIENTE_TESTE"
        mock_client_path.exists.return_value = True

        mock_template_path = MagicMock()
        mock_template_path.suffix = ".docx"
        mock_template_path.stem = "PROPOSTA"
        mock_template_path.exists.return_value = True

        with patch('foton_system.core.ops.op_doc_gen._resolve_client_path', return_value=mock_client_path), \
             patch('foton_system.core.ops.op_doc_gen._resolve_template_path', return_value=mock_template_path), \
             patch('foton_system.core.ops.session_tracker.get_current_session', return_value=None), \
             patch('foton_system.core.ops.session_tracker.increment_operations'), \
             patch('foton_system.core.ops.operation_tracker._write_operation_record'):
            try:
                op.execute(
                    client_id="CLIENTE_TESTE",
                    client_name="CLIENTE_TESTE",
                    template_name="PROPOSTA.docx",
                    extra_data={}
                )
            except Exception:
                pass

        mock_audit_instance.log_event.assert_called_once()
        call_kwargs = mock_audit_instance.log_event.call_args[1]
        self.assertIn("op_name", call_kwargs)
        self.assertEqual(call_kwargs["op_name"], "OpGenerateDocument")
        self.assertIn("client_id", call_kwargs)
        self.assertEqual(call_kwargs["client_id"], "CLIENTE_TESTE")
        self.assertIn("status", call_kwargs)


if __name__ == '__main__':
    unittest.main()
