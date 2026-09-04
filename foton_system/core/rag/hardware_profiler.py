# @story: STORY-030
# @rule: RULE-RAG-7.1, RULE-RAG-7.2, RULE-RAG-7.3, RULE-RAG-7.4, RULE-RAG-7.5

import os
import time
import shutil
import logging
import subprocess
import psutil
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

CACHE_DURATION = 60  # segundos


@dataclass
class HardwareProfile:
    cpu_cores: int = 0
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    has_cuda: bool = False
    cuda_version: str = ""
    has_mps: bool = False
    vram_gb: float = 0.0
    disk_free_gb: float = 0.0
    has_nvidia_gpu: bool = False
    nvidia_gpu_name: str = ""
    nvidia_driver_version: str = ""


@dataclass
class FeasibilityReport:
    model_id: str
    is_feasible: bool
    warnings: List[str] = field(default_factory=list)


# Mapeamento de requisitos conhecidos para validate_feasibility
_MODEL_REQUIREMENTS = {
    "minilm": {"ram_required_gb": 1.0, "disk_required_gb": 0.5, "requires_gpu": False},
    "bgem3": {"ram_required_gb": 4.5, "disk_required_gb": 2.5, "requires_gpu": False},
}


def _bytes_to_gb(b: int) -> float:
    return round(b / (1024 ** 3), 1)


def _detect_cuda():
    try:
        import torch
    except ImportError:
        return False, "", 0.0

    if not torch.cuda.is_available():
        return False, "", 0.0

    version = torch.version.cuda or ""
    try:
        props = torch.cuda.get_device_properties(0)
        vram = _bytes_to_gb(props.total_memory)
    except Exception:
        vram = 0.0

    return True, version, vram


def _detect_mps():
    try:
        import torch
    except ImportError:
        return False
    try:
        return torch.backends.mps.is_available()
    except Exception:
        return False


def _detect_nvidia_smi() -> Tuple[bool, str, str, float]:
    """Detecta GPU NVIDIA via nvidia-smi (independente do torch).

    Returns:
        Tuple (found, gpu_name, driver_version, vram_gb).
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False, "", "", 0.0
        line = result.stdout.strip().split("\n")[0]
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 4:
            name = parts[1]
            driver = parts[2]
            try:
                vram_mb = float(parts[3])
                vram_gb = round(vram_mb / 1024, 1)
            except (ValueError, IndexError):
                vram_gb = 0.0
            return True, name, driver, vram_gb
        return False, "", "", 0.0
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False, "", "", 0.0


class HardwareProfiler:
    def __init__(self):
        self._cache: Optional[HardwareProfile] = None
        self._cache_time: float = 0

    def detect(self) -> HardwareProfile:
        now = time.time()
        if self._cache is not None and (now - self._cache_time) < CACHE_DURATION:
            return self._cache

        cpu_cores = psutil.cpu_count(logical=True) or 0

        mem = psutil.virtual_memory()
        ram_total = _bytes_to_gb(mem.total)
        ram_available = _bytes_to_gb(mem.available)

        has_cuda, cuda_version, vram = _detect_cuda()
        has_mps = _detect_mps()
        has_nvidia, nvidia_name, nvidia_driver, nvidia_vram = _detect_nvidia_smi()

        try:
            cache_dir = os.environ.get(
                "HF_HOME",
                os.path.join(os.path.expanduser("~"), ".cache", "huggingface")
            )
            disk = shutil.disk_usage(cache_dir)
            disk_free = _bytes_to_gb(disk.free)
        except Exception:
            disk_free = 0.0

        profile = HardwareProfile(
            cpu_cores=cpu_cores,
            ram_total_gb=ram_total,
            ram_available_gb=ram_available,
            has_cuda=has_cuda,
            cuda_version=cuda_version,
            has_mps=has_mps,
            vram_gb=vram,
            disk_free_gb=disk_free,
            has_nvidia_gpu=has_nvidia,
            nvidia_gpu_name=nvidia_name,
            nvidia_driver_version=nvidia_driver,
        )

        self._cache = profile
        self._cache_time = now
        return profile

    def invalidate_cache(self):
        self._cache = None
        self._cache_time = 0


def recommended_mode(profile: HardwareProfile) -> str:
    if profile.has_cuda or profile.has_mps:
        return "gpu"
    if profile.ram_total_gb < 4:
        return "oom_risk"
    if profile.ram_total_gb < 8:
        return "cpu_safe"
    if profile.ram_total_gb <= 16:
        return "cpu_standard"
    return "gpu" if profile.ram_total_gb > 16 else "cpu_standard"


def validate_feasibility(model_id: str, profile: HardwareProfile) -> FeasibilityReport:
    reqs = _MODEL_REQUIREMENTS.get(model_id)
    if reqs is None:
        return FeasibilityReport(
            model_id=model_id,
            is_feasible=False,
            warnings=[f"Modelo '{model_id}' não é conhecido pelo validador."],
        )

    warnings = []

    if profile.ram_available_gb < reqs["ram_required_gb"]:
        warnings.append(
            f"RAM insuficiente: {profile.ram_available_gb:.1f}GB disponível, "
            f"mínimo {reqs['ram_required_gb']:.1f}GB requerido."
        )

    if profile.disk_free_gb < reqs["disk_required_gb"]:
        warnings.append(
            f"Disco insuficiente: {profile.disk_free_gb:.1f}GB livre, "
            f"mínimo {reqs['disk_required_gb']:.1f}GB requerido."
        )

    if reqs["requires_gpu"] and not (profile.has_cuda or profile.has_mps):
        warnings.append("Modelo requer GPU, mas nenhuma foi detectada.")

    is_feasible = len(warnings) == 0

    return FeasibilityReport(
        model_id=model_id,
        is_feasible=is_feasible,
        warnings=warnings,
    )
