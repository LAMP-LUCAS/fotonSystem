# @story: STORY-030
# @rule: RULE-RAG-7.1, RULE-RAG-7.2, RULE-RAG-7.3, RULE-RAG-7.4

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import time


class TestHardwareProfilerDetect(unittest.TestCase):
    """Tests for HardwareProfiler.detect() — RULE-RAG-7.1."""

    def setUp(self):
        self._patcher_psutil = patch('foton_system.core.rag.hardware_profiler.psutil')
        self._patcher_shutil = patch('foton_system.core.rag.hardware_profiler.shutil')
        self._patcher_cuda = patch('foton_system.core.rag.hardware_profiler._detect_cuda')
        self._patcher_mps = patch('foton_system.core.rag.hardware_profiler._detect_mps')
        self.mock_psutil = self._patcher_psutil.start()
        self.mock_shutil = self._patcher_shutil.start()
        self.mock_cuda = self._patcher_cuda.start()
        self.mock_mps = self._patcher_mps.start()
        self.addCleanup(self._patcher_psutil.stop)
        self.addCleanup(self._patcher_shutil.stop)
        self.addCleanup(self._patcher_cuda.stop)
        self.addCleanup(self._patcher_mps.stop)

        self.mock_psutil.cpu_count.return_value = 8

        mem = MagicMock()
        mem.total = 16 * 1024 ** 3
        mem.available = 8 * 1024 ** 3
        self.mock_psutil.virtual_memory.return_value = mem

        disk = MagicMock()
        disk.free = 50 * 1024 ** 3
        self.mock_shutil.disk_usage.return_value = disk

        self.mock_cuda.return_value = (False, "", 0.0)
        self.mock_mps.return_value = False

    def _make_profile(self):
        from foton_system.core.rag.hardware_profiler import HardwareProfiler
        profiler = HardwareProfiler()
        profiler._cache = None
        profiler._cache_time = 0
        return profiler.detect()

    def test_detect_returns_cpu_cores(self):
        profile = self._make_profile()
        self.assertEqual(profile.cpu_cores, 8)

    def test_detect_returns_ram_total_gb(self):
        profile = self._make_profile()
        self.assertAlmostEqual(profile.ram_total_gb, 16.0, places=1)

    def test_detect_returns_ram_available_gb(self):
        profile = self._make_profile()
        self.assertAlmostEqual(profile.ram_available_gb, 8.0, places=1)

    def test_detect_returns_disk_free_gb(self):
        profile = self._make_profile()
        self.assertAlmostEqual(profile.disk_free_gb, 50.0, places=1)

    def test_detect_no_cuda_by_default(self):
        profile = self._make_profile()
        self.assertFalse(profile.has_cuda)

    def test_detect_cuda_when_available(self):
        self.mock_cuda.return_value = (True, "11.8", 8.0)

        profile = self._make_profile()
        self.assertTrue(profile.has_cuda)
        self.assertEqual(profile.cuda_version, "11.8")
        self.assertAlmostEqual(profile.vram_gb, 8.0, places=1)

    def test_detect_mps_when_available(self):
        self.mock_mps.return_value = True

        profile = self._make_profile()
        self.assertTrue(profile.has_mps)


class TestRecommendedMode(unittest.TestCase):
    """Tests for recommended_mode() — RULE-RAG-7.2."""

    def _make_profile(self, ram_total_gb=16.0, has_cuda=False, has_mps=False):
        from foton_system.core.rag.hardware_profiler import HardwareProfile
        return HardwareProfile(
            cpu_cores=4, ram_total_gb=ram_total_gb, ram_available_gb=ram_total_gb,
            has_cuda=has_cuda, cuda_version="", has_mps=has_mps, vram_gb=0, disk_free_gb=100
        )

    def test_cpu_safe_when_ram_below_8gb(self):
        from foton_system.core.rag.hardware_profiler import recommended_mode
        profile = self._make_profile(ram_total_gb=6.0)
        self.assertEqual(recommended_mode(profile), "cpu_safe")

    def test_cpu_standard_when_ram_8_to_16gb(self):
        from foton_system.core.rag.hardware_profiler import recommended_mode
        profile = self._make_profile(ram_total_gb=12.0)
        self.assertEqual(recommended_mode(profile), "cpu_standard")

    def test_gpu_when_cuda_available(self):
        from foton_system.core.rag.hardware_profiler import recommended_mode
        profile = self._make_profile(ram_total_gb=16.0, has_cuda=True)
        self.assertEqual(recommended_mode(profile), "gpu")

    def test_gpu_when_mps_available(self):
        from foton_system.core.rag.hardware_profiler import recommended_mode
        profile = self._make_profile(ram_total_gb=16.0, has_mps=True)
        self.assertEqual(recommended_mode(profile), "gpu")

    def test_oom_risk_when_ram_below_4gb(self):
        from foton_system.core.rag.hardware_profiler import recommended_mode
        profile = self._make_profile(ram_total_gb=3.0)
        self.assertEqual(recommended_mode(profile), "oom_risk")


class TestValidateFeasibility(unittest.TestCase):
    """Tests for validate_feasibility() — RULE-RAG-7.3."""

    def _make_profile(self, ram_available_gb=4.0, has_cuda=False):
        from foton_system.core.rag.hardware_profiler import HardwareProfile
        return HardwareProfile(
            cpu_cores=4, ram_total_gb=ram_available_gb + 2,
            ram_available_gb=ram_available_gb, has_cuda=has_cuda,
            cuda_version="", has_mps=False, vram_gb=0, disk_free_gb=100
        )

    def test_bgem3_infeasible_with_4gb_ram(self):
        from foton_system.core.rag.hardware_profiler import validate_feasibility
        profile = self._make_profile(ram_available_gb=4.0)
        report = validate_feasibility("bgem3", profile)
        self.assertFalse(report.is_feasible)
        self.assertTrue(len(report.warnings) > 0)
        self.assertIn("ram", " ".join(report.warnings).lower())

    def test_minilm_feasible_with_4gb_ram(self):
        from foton_system.core.rag.hardware_profiler import validate_feasibility
        profile = self._make_profile(ram_available_gb=4.0)
        report = validate_feasibility("minilm", profile)
        self.assertTrue(report.is_feasible)

    def test_unknown_model_returns_error(self):
        from foton_system.core.rag.hardware_profiler import validate_feasibility
        profile = self._make_profile(ram_available_gb=16.0)
        report = validate_feasibility("unknown_model_xyz", profile)
        self.assertFalse(report.is_feasible)


class TestProfilerCache(unittest.TestCase):
    """Tests for Profiler cache — RULE-RAG-7.4."""

    def setUp(self):
        self._patcher_psutil = patch('foton_system.core.rag.hardware_profiler.psutil')
        self._patcher_shutil = patch('foton_system.core.rag.hardware_profiler.shutil')
        self._patcher_cuda = patch('foton_system.core.rag.hardware_profiler._detect_cuda')
        self._patcher_mps = patch('foton_system.core.rag.hardware_profiler._detect_mps')
        self.mock_psutil = self._patcher_psutil.start()
        self.mock_shutil = self._patcher_shutil.start()
        self.mock_cuda = self._patcher_cuda.start()
        self.mock_mps = self._patcher_mps.start()
        self.addCleanup(self._patcher_psutil.stop)
        self.addCleanup(self._patcher_shutil.stop)
        self.addCleanup(self._patcher_cuda.stop)
        self.addCleanup(self._patcher_mps.stop)

        mem = MagicMock()
        mem.total = 16 * 1024 ** 3
        mem.available = 8 * 1024 ** 3
        self.mock_psutil.virtual_memory.return_value = mem
        self.mock_psutil.cpu_count.return_value = 8
        disk = MagicMock()
        disk.free = 50 * 1024 ** 3
        self.mock_shutil.disk_usage.return_value = disk
        self.mock_cuda.return_value = (False, "", 0.0)
        self.mock_mps.return_value = False

    def test_cache_returns_same_object_within_60s(self):
        from foton_system.core.rag.hardware_profiler import HardwareProfiler
        profiler = HardwareProfiler()
        profiler._cache = None
        profiler._cache_time = 0

        p1 = profiler.detect()
        p2 = profiler.detect()
        self.assertIs(p1, p2)
        self.assertEqual(self.mock_psutil.cpu_count.call_count, 1)

    def test_cache_expires_after_60s(self):
        from foton_system.core.rag.hardware_profiler import HardwareProfiler
        profiler = HardwareProfiler()
        profiler._cache = None
        profiler._cache_time = 0

        p1 = profiler.detect()
        profiler._cache_time = time.time() - 61
        p2 = profiler.detect()
        self.assertIsNot(p1, p2)


class TestMockedScenarios(unittest.TestCase):
    """Mocked edge cases: CUDA ausente, RAM baixa, disco cheio."""

    def setUp(self):
        self._patcher_psutil = patch('foton_system.core.rag.hardware_profiler.psutil')
        self._patcher_shutil = patch('foton_system.core.rag.hardware_profiler.shutil')
        self._patcher_cuda = patch('foton_system.core.rag.hardware_profiler._detect_cuda')
        self._patcher_mps = patch('foton_system.core.rag.hardware_profiler._detect_mps')
        self.mock_psutil = self._patcher_psutil.start()
        self.mock_shutil = self._patcher_shutil.start()
        self.mock_cuda = self._patcher_cuda.start()
        self.mock_mps = self._patcher_mps.start()
        self.addCleanup(self._patcher_psutil.stop)
        self.addCleanup(self._patcher_shutil.stop)
        self.addCleanup(self._patcher_cuda.stop)
        self.addCleanup(self._patcher_mps.stop)

        mem = MagicMock()
        mem.total = int(3.5 * 1024 ** 3)
        mem.available = int(1.0 * 1024 ** 3)
        self.mock_psutil.virtual_memory.return_value = mem
        self.mock_psutil.cpu_count.return_value = 2
        disk = MagicMock()
        disk.free = 0.5 * 1024 ** 3
        self.mock_shutil.disk_usage.return_value = disk
        self.mock_cuda.return_value = (False, "", 0.0)
        self.mock_mps.return_value = False

    def test_low_ram_scenario(self):
        from foton_system.core.rag.hardware_profiler import HardwareProfiler, recommended_mode
        profiler = HardwareProfiler()
        profiler._cache = None
        profiler._cache_time = 0
        profile = profiler.detect()
        self.assertLess(profile.ram_total_gb, 5)
        self.assertEqual(recommended_mode(profile), "oom_risk")

    def test_disk_full_scenario(self):
        from foton_system.core.rag.hardware_profiler import HardwareProfiler
        profiler = HardwareProfiler()
        profiler._cache = None
        profiler._cache_time = 0
        profile = profiler.detect()
        self.assertAlmostEqual(profile.disk_free_gb, 0.5, places=1)

    def test_cuda_absent_scenario(self):
        from foton_system.core.rag.hardware_profiler import HardwareProfiler
        profiler = HardwareProfiler()
        profiler._cache = None
        profiler._cache_time = 0
        profile = profiler.detect()
        self.assertFalse(profile.has_cuda)
        self.assertFalse(profile.has_mps)


class TestFeasibilityReport(unittest.TestCase):
    """Tests for FeasibilityReport dataclass."""

    def test_feasibility_report_creation(self):
        from foton_system.core.rag.hardware_profiler import FeasibilityReport
        report = FeasibilityReport(model_id="minilm", is_feasible=True, warnings=[])
        self.assertEqual(report.model_id, "minilm")
        self.assertTrue(report.is_feasible)
        self.assertEqual(report.warnings, [])


if __name__ == '__main__':
    unittest.main()
