"""Tests for SessionTracker — session.json persistence and monotonic counters."""

import json
import uuid
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from foton_system.core.ops.session_tracker import (
    start_session, end_session, get_current_session,
    increment_operations, _reset_session_state, SessionState
)


class TestSessionTracker(unittest.TestCase):
    """Unit tests for session lifecycle and persistence."""

    def setUp(self):
        _reset_session_state()
        self.temp_root = Path(tempfile.mkdtemp())

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_start_session_cria_session_json(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("TUI")
        self.assertIsNotNone(session)
        self.assertEqual(session.interface, "TUI")
        self.assertEqual(session.total_sessoes_all_time, 1)
        session_file = self.temp_root / "session.json"
        self.assertTrue(session_file.exists())
        data = json.loads(session_file.read_text(encoding="utf-8"))
        self.assertEqual(data["total_sessoes_all_time"], 1)
        self.assertEqual(data["interface"], "TUI")

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_session_id_e_uuid_valido(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("MCP")
        parsed = uuid.UUID(session.session_id)
        self.assertEqual(str(parsed), session.session_id)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_segunda_execucao_incrementa_total(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        first = start_session("TUI")
        self.assertEqual(first.total_sessoes_all_time, 1)
        first_primeiro_uso = first.primeiro_uso
        end_session()
        _reset_session_state()
        second = start_session("TUI")
        self.assertEqual(second.total_sessoes_all_time, 2)
        self.assertEqual(second.primeiro_uso, first_primeiro_uso)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_primeiro_uso_mantido_entre_sessoes(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        s1 = start_session("TUI")
        end_session()
        _reset_session_state()
        s2 = start_session("MCP")
        self.assertEqual(s2.primeiro_uso, s1.primeiro_uso)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_increment_operations_soma_contador(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("TUI")
        self.assertEqual(session.contador_operacoes, 0)
        increment_operations()
        self.assertEqual(session.contador_operacoes, 1)
        increment_operations()
        self.assertEqual(session.contador_operacoes, 2)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_end_session_persiste_contadores(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("TUI")
        increment_operations()
        increment_operations()
        end_session()
        session_file = self.temp_root / "session.json"
        data = json.loads(session_file.read_text(encoding="utf-8"))
        self.assertEqual(data["total_operacoes_all_time"], 2)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_total_operacoes_acumula_entre_sessoes(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        s1 = start_session("TUI")
        increment_operations()
        increment_operations()
        end_session()
        _reset_session_state()
        s2 = start_session("TUI")
        self.assertEqual(s2.total_operacoes_all_time, 2)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_interface_mcp_detectada(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("MCP")
        self.assertEqual(session.interface, "MCP")

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_get_current_session_retorna_sessao_ativa(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("TUI")
        self.assertIs(get_current_session(), session)

    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_start_session_sem_json_existente(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        session = start_session("TUI")
        self.assertEqual(session.total_sessoes_all_time, 1)
        self.assertIsNotNone(session.primeiro_uso)

    def tearDown(self):
        import shutil
        _reset_session_state()
        shutil.rmtree(self.temp_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
