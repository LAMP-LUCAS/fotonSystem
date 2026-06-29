import unittest
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
