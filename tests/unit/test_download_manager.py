"""
Tests for STORY-032: DownloadManager

Covers:
- RULE-RAG-12.1: ensure_model() downloads or returns cached
- RULE-RAG-12.2: progress_callback(bytes, total) on each chunk
- RULE-RAG-12.3: Abort with clear error if disk insufficient
- RULE-RAG-12.4: MCP mode (sync with logs, no callback)
- RULE-RAG-12.5: Cache in HF_HOME, auto-reuse
"""

import unittest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass


@dataclass
class FakeHardwareProfile:
    cpu_cores: int = 4
    ram_total_gb: float = 16.0
    ram_available_gb: float = 9.0
    has_cuda: bool = False
    cuda_version: str = ""
    has_mps: bool = False
    vram_gb: float = 0.0
    disk_free_gb: float = 50.0


@dataclass
class FakeModelEntry:
    id: str = "minilm"
    name: str = "paraphrase-multilingual-MiniLM-L12-v2"
    type: str = "embedding"
    dimensions: int = 384
    ram_required_gb: float = 1.0
    disk_required_gb: float = 0.5
    requires_gpu: bool = False
    is_default: bool = True


class TestDownloadManagerEnsureModel(unittest.TestCase):
    """RULE-RAG-12.1, 12.3, 12.5"""

    def setUp(self):
        self.mock_registry = MagicMock()
        self.mock_profiler = MagicMock()
        self.entry_minilm = FakeModelEntry()
        self.entry_bgem3 = FakeModelEntry(
            id="bgem3",
            name="BAAI/bge-m3",
            dimensions=1024,
            ram_required_gb=4.5,
            disk_required_gb=2.5,
        )

        def fake_get(model_id):
            mapping = {"minilm": self.entry_minilm, "bgem3": self.entry_bgem3}
            return mapping.get(model_id)

        self.mock_registry.get.side_effect = fake_get

    def test_ensure_model_already_installed_returns_immediately(self):
        self.mock_registry.is_installed.return_value = True
        from foton_system.core.rag.download_manager import DownloadManager

        report = DownloadManager.ensure_model(
            "minilm", self.mock_registry, self.mock_profiler
        )
        self.assertTrue(report.success)
        self.assertIn("MiniLM", report.model_path)

    def test_ensure_model_downloads_and_returns_report(self):
        self.mock_registry.is_installed.return_value = False
        profile = FakeHardwareProfile(disk_free_gb=50)
        self.mock_profiler.detect.return_value = profile

        with patch(
            "foton_system.core.rag.download_manager.snapshot_download"
        ) as mock_snapshot:
            mock_snapshot.return_value = "/fake/path/minilm"

            from foton_system.core.rag.download_manager import DownloadManager

            report = DownloadManager.ensure_model(
                "minilm", self.mock_registry, self.mock_profiler
            )

            mock_snapshot.assert_called_once()
            self.assertTrue(report.success)
            self.assertIn("minilm", report.model_path)

    def test_ensure_model_unknown_model_id_returns_error(self):
        self.mock_registry.get.return_value = None
        self.mock_registry.is_installed.return_value = False

        from foton_system.core.rag.download_manager import DownloadManager

        report = DownloadManager.ensure_model(
            "nonexistent", self.mock_registry, self.mock_profiler
        )
        self.assertFalse(report.success)

    def test_abort_when_disk_insufficient(self):
        self.mock_registry.is_installed.return_value = False
        hw = FakeHardwareProfile(disk_free_gb=0.1)
        self.mock_profiler.detect.return_value = hw

        from foton_system.core.rag.download_manager import DownloadManager

        report = DownloadManager.ensure_model(
            "bgem3", self.mock_registry, self.mock_profiler
        )
        self.assertFalse(report.success)

    def test_cache_reused_when_already_installed(self):
        self.mock_registry.is_installed.return_value = True

        from foton_system.core.rag.download_manager import DownloadManager

        with patch(
            "foton_system.core.rag.download_manager.snapshot_download"
        ) as mock_snapshot:
            report = DownloadManager.ensure_model(
                "minilm", self.mock_registry, self.mock_profiler
            )
            mock_snapshot.assert_not_called()
            self.assertTrue(report.success)


class TestDownloadManagerProgressCallback(unittest.TestCase):
    """RULE-RAG-12.2"""

    def setUp(self):
        self.mock_registry = MagicMock()
        self.mock_profiler = MagicMock()
        self.entry = FakeModelEntry()
        self.mock_registry.is_installed.return_value = False
        self.mock_registry.get.return_value = self.entry
        self.mock_profiler.detect.return_value = FakeHardwareProfile(disk_free_gb=50)

    def test_progress_callback_receives_bytes_and_total(self):
        call_log = []

        def fake_progress(bytes_done, total_bytes):
            call_log.append((bytes_done, total_bytes))

        def fake_snapshot(repo_id, local_files_only=False, callback=None):
            if callback:
                callback(50_000_000, 100_000_000)
            return "/fake/path"

        from foton_system.core.rag.download_manager import DownloadManager

        with patch(
            "foton_system.core.rag.download_manager.snapshot_download",
            side_effect=fake_snapshot,
        ), patch(
            "foton_system.core.rag.download_manager.MODEL_SIZES",
            {"minilm": 100_000_000},
            create=True,
        ):
            DownloadManager.ensure_model(
                "minilm",
                self.mock_registry,
                self.mock_profiler,
                progress_callback=fake_progress,
            )

            self.assertTrue(len(call_log) > 0, "callback should be called")
            for bytes_done, total in call_log:
                self.assertIsInstance(bytes_done, int)
                self.assertEqual(total, 100_000_000)


class TestDownloadManagerMCPSyncMode(unittest.TestCase):
    """RULE-RAG-12.4"""

    def test_mcp_mode_no_callback_sync_download(self):
        mock_registry = MagicMock()
        mock_profiler = MagicMock()
        entry = FakeModelEntry()
        mock_registry.is_installed.return_value = False
        mock_registry.get.return_value = entry
        mock_profiler.detect.return_value = FakeHardwareProfile(disk_free_gb=50)

        with patch(
            "foton_system.core.rag.download_manager.snapshot_download"
        ) as mock_snapshot:
            mock_snapshot.return_value = "/fake/path"
            from foton_system.core.rag.download_manager import DownloadManager

            report = DownloadManager.ensure_model(
                "minilm", mock_registry, mock_profiler
            )
            self.assertTrue(report.success)

    def test_mcp_mode_none_callback_does_not_crash(self):
        mock_registry = MagicMock()
        mock_profiler = MagicMock()
        entry = FakeModelEntry()
        mock_registry.is_installed.return_value = False
        mock_registry.get.return_value = entry
        mock_profiler.detect.return_value = FakeHardwareProfile(disk_free_gb=50)

        with patch(
            "foton_system.core.rag.download_manager.snapshot_download"
        ) as mock_snapshot:
            mock_snapshot.return_value = "/fake/path"
            from foton_system.core.rag.download_manager import DownloadManager

            report = DownloadManager.ensure_model(
                "minilm",
                mock_registry,
                mock_profiler,
                progress_callback=None,
            )
            self.assertTrue(report.success)


if __name__ == "__main__":
    unittest.main()