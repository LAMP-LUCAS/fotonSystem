"""Tests for OperationTracker — @track_operation decorator and JSONL rotation."""

import json
import os
import tempfile
import time
import unittest
from unittest.mock import patch
from pathlib import Path

from foton_system.core.ops.operation_tracker import (
    track_operation, _reset_operation_state
)
from foton_system.core.ops.session_tracker import (
    start_session, _reset_session_state
)


class TestOperationTracker(unittest.TestCase):
    """Unit tests for operation tracking decorator."""

    def setUp(self):
        _reset_session_state()
        _reset_operation_state()
        self.temp_root = Path(tempfile.mkdtemp())

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_decorator_registra_linha_jsonl(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        start_session("TUI")

        @track_operation("test_op")
        def minha_funcao():
            return 42

        minha_funcao()
        log_file = self.temp_root / "operation_log.jsonl"
        self.assertTrue(log_file.exists())
        lines = log_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["operacao"], "test_op")

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_todos_campos_obrigatorios(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        session = start_session("TUI")

        @track_operation("validacao_op")
        def func():
            pass

        func()
        log_file = self.temp_root / "operation_log.jsonl"
        record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
        self.assertIn("timestamp", record)
        self.assertEqual(record["session_id"], session.session_id)
        self.assertEqual(record["interface"], "TUI")
        self.assertEqual(record["operacao"], "validacao_op")
        self.assertIn("sucesso", record)
        self.assertIn("duracao_ms", record)
        self.assertTrue(record["sucesso"])
        self.assertGreaterEqual(record["duracao_ms"], 0.0)

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_operacao_com_excecao_registra_falha(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        start_session("MCP")

        @track_operation("op_falha")
        def func_que_falha():
            raise ValueError("Algo deu errado")

        with self.assertRaises(ValueError):
            func_que_falha()

        log_file = self.temp_root / "operation_log.jsonl"
        record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
        self.assertFalse(record["sucesso"])
        self.assertGreaterEqual(record["duracao_ms"], 0.0)

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_metadados_sao_incluidos(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        start_session("TUI")

        @track_operation("op_meta", cliente="Teste", servicos=5)
        def func():
            pass

        func()
        log_file = self.temp_root / "operation_log.jsonl"
        record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(record["metadados"]["cliente"], "Teste")
        self.assertEqual(record["metadados"]["servicos"], 5)

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_multiplas_operacoes_acumulam(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        start_session("TUI")

        @track_operation("op1")
        def f1():
            pass

        @track_operation("op2")
        def f2():
            pass

        f1()
        f2()
        f1()
        log_file = self.temp_root / "operation_log.jsonl"
        lines = log_file.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 3)

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_rotacao_10mb_trunca_para_8mb(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        start_session("TUI")
        log_file = self.temp_root / "operation_log.jsonl"
        line = json.dumps({"operacao": "x", "session_id": "s", "interface": "TUI",
                           "timestamp": "now", "sucesso": True, "duracao_ms": 1.0,
                           "metadados": {}}) + "\n"
        target_size = 11 * 1024 * 1024
        line_bytes = len(line.encode("utf-8"))
        repeat_count = (target_size // line_bytes) + 10
        log_file.write_text(line * repeat_count, encoding="utf-8")
        size_before = log_file.stat().st_size
        self.assertGreaterEqual(size_before, 10 * 1024 * 1024)

        @track_operation("op_rotacao")
        def func():
            pass

        func()
        content_after = log_file.read_text(encoding="utf-8")
        lines_after = content_after.splitlines()
        last_line_len = len(lines_after[-1]) + 1
        trimmed_size = log_file.stat().st_size - last_line_len
        self.assertLessEqual(trimmed_size, 8 * 1024 * 1024)
        last = json.loads(lines_after[-1])
        self.assertEqual(last["operacao"], "op_rotacao")

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_rotacao_silenciosa_sem_excecao(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root
        start_session("TUI")
        log_file = self.temp_root / "operation_log.jsonl"
        line = json.dumps({"operacao": "x", "session_id": "s", "interface": "TUI",
                           "timestamp": "now", "sucesso": True, "duracao_ms": 1.0,
                           "metadados": {}}) + "\n"
        target_size = int(10.5 * 1024 * 1024)
        line_bytes = len(line.encode("utf-8"))
        repeat_count = (target_size // line_bytes) + 10
        log_file.write_text(line * repeat_count, encoding="utf-8")

        @track_operation("op_segura")
        def func():
            return "ok"

        result = func()
        self.assertEqual(result, "ok")

    @patch("foton_system.core.ops.operation_tracker.BootstrapService")
    @patch("foton_system.core.ops.session_tracker.BootstrapService")
    def test_sem_sessao_ativa_usa_session_id_none(self, mock_bs_sess, mock_bs_op):
        mock_bs_sess.get_user_config_dir.return_value = self.temp_root
        mock_bs_op.get_user_config_dir.return_value = self.temp_root

        @track_operation("op_sem_sessao")
        def func():
            pass

        func()
        log_file = self.temp_root / "operation_log.jsonl"
        record = json.loads(log_file.read_text(encoding="utf-8").splitlines()[0])
        self.assertIsNone(record["session_id"])

    def tearDown(self):
        import shutil
        _reset_session_state()
        _reset_operation_state()
        shutil.rmtree(self.temp_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()