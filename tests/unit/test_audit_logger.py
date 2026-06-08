"""Tests for AuditLogger — POP audit trail with JSONL persistence."""

import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from foton_system.core.ops.audit_logger import AuditLogger


class TestAuditLogger(unittest.TestCase):
    """Unit tests for AuditLogger log_event and get_recent_events."""

    def setUp(self):
        AuditLogger._instance = None
        self.temp_root = Path(tempfile.mkdtemp())

    @patch("foton_system.core.ops.audit_logger.BootstrapService")
    def test_log_event_writes_jsonl_line(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        AuditLogger._instance = None
        logger = AuditLogger()
        logger.log_event(
            op_name="test_op", actor="tester",
            client_id="CLI001", payload={"key": "val"},
            result={"ok": True}, status="success"
        )
        lines = (self.temp_root / "audit_events.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        event = json.loads(lines[0])
        self.assertEqual(event["op"], "test_op")
        self.assertEqual(event["status"], "success")

    @patch("foton_system.core.ops.audit_logger.BootstrapService")
    def test_get_recent_events_returns_list(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        AuditLogger._instance = None
        logger = AuditLogger()
        for i in range(3):
            logger.log_event("op", "tester", "CLI001", {}, {}, "success")
        events = logger.get_recent_events(limit=10)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["op"], "op")

    @patch("foton_system.core.ops.audit_logger.BootstrapService")
    def test_log_event_no_exception_on_permission_error(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        AuditLogger._instance = None
        logger = AuditLogger()

        # Simular permissão negada travando open()
        original_open = open
        def denied_open(*args, **kwargs):
            if "audit_events" in str(args[0]):
                raise PermissionError("Access denied")
            return original_open(*args, **kwargs)

        import builtins
        with patch.object(builtins, "open", denied_open):
            logger.log_event("op", "tester", "CLI001", {}, {}, "success")

        events = logger.get_recent_events(limit=10)
        self.assertEqual(len(events), 0)

    @patch("foton_system.core.ops.audit_logger.BootstrapService")
    def test_append_multiple_events(self, mock_bs):
        mock_bs.get_user_config_dir.return_value = self.temp_root
        AuditLogger._instance = None
        logger = AuditLogger()
        for i in range(5):
            logger.log_event("op", "tester", "CLI001", {"n": i}, {}, "success")
        events = logger.get_recent_events(limit=3)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["payload"]["n"], 4)
        self.assertEqual(events[-1]["payload"]["n"], 2)

    def tearDown(self):
        import shutil
        AuditLogger._instance = None
        shutil.rmtree(self.temp_root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
