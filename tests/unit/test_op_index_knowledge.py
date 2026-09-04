import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from foton_system.core.ops.op_index_knowledge import OpIndexKnowledge


class TestChunkTextHeaderAware(unittest.TestCase):
    """Tests for _chunk_text() header-aware splitting."""

    def setUp(self):
        self.op = OpIndexKnowledge(actor="Test")

    def test_no_headers_uses_simple_chunking(self):
        text = "a" * 300 + "b" * 300
        chunks = self.op._chunk_text(text, chunk_size=200)
        self.assertGreater(len(chunks), 1)
        self.assertEqual(chunks[0], "a" * 200)
        self.assertEqual(chunks[1], "a" * 150 + "b" * 50)

    def test_header_sections_become_chunks(self):
        text = "# Section 1\ncontent one\n\n## Section 2\ncontent two"
        chunks = self.op._chunk_text(text, chunk_size=500)
        self.assertEqual(len(chunks), 2)
        self.assertIn("Section 1", chunks[0])
        self.assertIn("Section 2", chunks[1])

    def test_long_section_prepends_header_to_each_subchunk(self):
        header = "# Big Section"
        body = "paragraph\n" * 100
        text = header + "\n" + body
        chunks = self.op._chunk_text(text, chunk_size=100)
        self.assertGreater(len(chunks), 1)
        for i, chunk in enumerate(chunks):
            if i == 0:
                self.assertIn("Big Section", chunk)
            else:
                self.assertIn("Big Section (cont.)", chunk)

    def test_empty_text_returns_empty_list(self):
        chunks = self.op._chunk_text("", chunk_size=500)
        self.assertEqual(chunks, [])

    def test_text_fits_in_one_chunk(self):
        text = "# Title\nSingle paragraph."
        chunks = self.op._chunk_text(text, chunk_size=500)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_consecutive_headers_with_no_content(self):
        text = "# H1\n## H2\n### H3\nsome content"
        chunks = self.op._chunk_text(text, chunk_size=500)
        self.assertEqual(len(chunks), 1)
        self.assertIn("H3", chunks[0])

    def test_overlap_between_subchunks(self):
        header = "# Long Section"
        body = "content " * 50
        text = header + "\n" + body
        chunks = self.op._chunk_text(text, chunk_size=100)
        if len(chunks) > 1:
            first_end = chunks[0][-50:]
            self.assertIn(first_end.strip(), chunks[1])


class _TempFileTestMixin:
    """Mixin that creates a temp directory with test files."""

    def _create_temp_file(self, content: str, name: str = "test.md"):
        tmpdir = Path(self._temp_dir.name)
        fpath = tmpdir / name
        fpath.write_text(content, encoding="utf-8")
        return fpath


class TestOpIndexKnowledgeMetadata(unittest.TestCase, _TempFileTestMixin):
    """Tests for chunk metadata fields (RULE-RAG-2.3)."""

    def setUp(self):
        self.op = OpIndexKnowledge(actor="Test")
        self._temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    @patch('foton_system.core.ops.op_index_knowledge.VectorStoreManager')
    @patch('foton_system.core.ops.op_index_knowledge.Config')
    def test_chunk_metadata_includes_required_fields(self, MockConfig, MockVectorStoreManager):
        """chunk metadata should contain source, filename, hash, chunk_index, linha_inicio, linha_fim."""
        mock_store = MagicMock()
        MockVectorStoreManager.return_value = mock_store
        base_path = Path(self._temp_dir.name)
        mock_cfg = MagicMock()
        mock_cfg.base_pasta_clientes = base_path
        MockConfig.return_value = mock_cfg

        self._create_temp_file("# S1\ncontent\n# S2\nmore", "INFO.md")

        with patch.object(self.op, '_calculate_file_hash', return_value="abc123"):
            self.op.execute_logic({"target_path_obj": base_path})

        call = mock_store.add_documents.call_args
        self.assertIsNotNone(call)
        _, kw = call
        metadatas = kw.get("metadatas", [])
        self.assertGreater(len(metadatas), 0)
        for meta in metadatas:
            for field in ("source", "filename", "hash", "chunk_index", "linha_inicio", "linha_fim"):
                self.assertIn(field, meta)

    @patch('foton_system.core.ops.op_index_knowledge.VectorStoreManager')
    @patch('foton_system.core.ops.op_index_knowledge.Config')
    def test_chunk_metadata_linha_values_monotonic(self, MockConfig, MockVectorStoreManager):
        """linha_inicio/linha_fim should be positive and monotonic."""
        mock_store = MagicMock()
        MockVectorStoreManager.return_value = mock_store
        base_path = Path(self._temp_dir.name)
        mock_cfg = MagicMock()
        mock_cfg.base_pasta_clientes = base_path
        MockConfig.return_value = mock_cfg

        content = "line1\na" * 300 + "\nline2\nb" * 300
        self._create_temp_file(content, "doc.txt")

        with patch.object(self.op, '_calculate_file_hash', return_value="abc123"):
            self.op.execute_logic({"target_path_obj": base_path})

        call = mock_store.add_documents.call_args
        self.assertIsNotNone(call)
        _, kw = call
        metadatas = kw.get("metadatas", [])
        self.assertGreater(len(metadatas), 1)
        for i, meta in enumerate(metadatas):
            self.assertGreater(meta["linha_inicio"], 0)
            self.assertGreaterEqual(meta["linha_fim"], meta["linha_inicio"])
            if i > 0:
                self.assertGreaterEqual(meta["linha_inicio"], metadatas[i - 1]["linha_fim"])


class TestOpIndexKnowledgeBatchUpsert(unittest.TestCase, _TempFileTestMixin):
    """Tests for batch upsert (RULE-RAG-2.4)."""

    def setUp(self):
        self.op = OpIndexKnowledge(actor="Test")
        self._temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    @patch('foton_system.core.ops.op_index_knowledge.VectorStoreManager')
    @patch('foton_system.core.ops.op_index_knowledge.Config')
    def test_add_documents_receives_multiple_chunks(self, MockConfig, MockVectorStoreManager):
        """add_documents should receive multiple chunks in one call."""
        mock_store = MagicMock()
        MockVectorStoreManager.return_value = mock_store
        base_path = Path(self._temp_dir.name)
        mock_cfg = MagicMock()
        mock_cfg.base_pasta_clientes = base_path
        MockConfig.return_value = mock_cfg

        self._create_temp_file("word " * 500, "doc.txt")

        with patch.object(self.op, '_calculate_file_hash', return_value="abc123"):
            self.op.execute_logic({"target_path_obj": base_path})

        call = mock_store.add_documents.call_args
        self.assertIsNotNone(call)
        _, kw = call
        docs = kw.get("documents", [])
        self.assertGreaterEqual(len(docs), 5)
