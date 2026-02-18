"""
Tests for Proactive Watcher Handler

Covers:
- Suggestion emission for INFO-CLIENTE files
- Suggestion emission for INFO-SERVICO files
- No suggestion for non-INFO files
- Debouncing prevents duplicate processing
- Graceful degradation when RAG is unavailable
"""

import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import time


class MockEvent:
    """Mock file system event for testing."""

    def __init__(self, src_path: str, is_directory: bool = False):
        self.src_path = src_path
        self.is_directory = is_directory


class TestWatcherProactiveSuggestions(unittest.TestCase):
    """Tests for proactive suggestion logic in handlers.py."""

    def setUp(self):
        from foton_system.core.watcher.handlers import FotonFileSystemEventHandler
        self.handler = FotonFileSystemEventHandler()
        # Force RAG to be unavailable for suggestion-only tests
        self.handler._rag_available = False

    def test_should_process_filters_directories(self):
        """Directories should not be processed."""
        event = MockEvent(r"C:\clients\JOAO", is_directory=True)
        self.assertFalse(self.handler._should_process(event))

    def test_should_process_accepts_md_files(self):
        """Markdown files should be processed."""
        event = MockEvent(r"C:\clients\JOAO\INFO-CLIENTE.md")
        self.assertTrue(self.handler._should_process(event))

    def test_should_process_accepts_txt_files(self):
        """Text files should be processed."""
        event = MockEvent(r"C:\clients\JOAO\notas.txt")
        self.assertTrue(self.handler._should_process(event))

    def test_should_process_rejects_non_text_files(self):
        """Non-text files should be rejected."""
        event = MockEvent(r"C:\clients\JOAO\foto.jpg")
        self.assertFalse(self.handler._should_process(event))

    def test_debounce_prevents_rapid_duplicates(self):
        """Same file changed rapidly should only be processed once."""
        path = r"C:\clients\JOAO\INFO-CLIENTE.md"
        event = MockEvent(path)

        # First event should pass
        self.assertTrue(self.handler._should_process(event))

        # Second immediate event should be debounced
        self.assertFalse(self.handler._should_process(event))

    @patch('builtins.print')
    def test_analyze_emits_suggestion_for_info_cliente(self, mock_print):
        """INFO-CLIENTE files should trigger client-specific suggestion."""
        self.handler._analyze_for_suggestions(r"C:\clients\JOAO\INFO-CLIENTE.md")

        # Check that suggestion was printed (at least one call contains "SUGESTÃO")
        printed = ' '.join([str(c) for c in mock_print.call_args_list])
        self.assertIn("SUGESTÃO PROATIVA", printed)
        self.assertIn("cliente", printed.lower())

    @patch('builtins.print')
    def test_analyze_emits_suggestion_for_info_servico(self, mock_print):
        """INFO-SERVICO files should trigger service-specific suggestion."""
        self.handler._analyze_for_suggestions(r"C:\clients\JOAO\INFO-SERVICO.md")

        printed = ' '.join([str(c) for c in mock_print.call_args_list])
        self.assertIn("SUGESTÃO PROATIVA", printed)
        self.assertIn("serviço", printed.lower())

    @patch('builtins.print')
    def test_analyze_no_suggestion_for_generic_files(self, mock_print):
        """Generic .md files should NOT trigger suggestions."""
        self.handler._analyze_for_suggestions(r"C:\clients\JOAO\notas.md")

        printed = ' '.join([str(c) for c in mock_print.call_args_list])
        self.assertNotIn("SUGESTÃO PROATIVA", printed)

    @patch('builtins.print')
    def test_trigger_index_graceful_when_rag_unavailable(self, mock_print):
        """Should not crash when RAG is unavailable."""
        self.handler._rag_available = False

        # Should not raise
        self.handler._trigger_index(r"C:\clients\JOAO\INFO-CLIENTE.md")


if __name__ == '__main__':
    unittest.main()
