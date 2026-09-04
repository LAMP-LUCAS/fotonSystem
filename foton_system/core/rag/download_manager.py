# @story: STORY-032
# @rule: RULE-RAG-12.1, RULE-RAG-12.2, RULE-RAG-12.3, RULE-RAG-12.4, RULE-RAG-12.5

import os
import time
import logging
from dataclasses import dataclass
from typing import Callable, Optional

try:
    from huggingface_hub import snapshot_download
except ImportError:
    snapshot_download = None

logger = logging.getLogger(__name__)

# Tamanhos conhecidos de modelos (bytes) para cálculo de progresso
# Valores aproximados — o huggingface_hub pode fornecer o real via metadata
MODEL_SIZES = {
    "minilm": 450_000_000,
    "bgem3": 2_200_000_000,
}


@dataclass
class DownloadReport:
    success: bool
    model_path: str = ""
    download_size_mb: float = 0.0
    elapsed_seconds: float = 0.0
    error: str = ""


class DownloadManager:

    @staticmethod
    def ensure_model(
        model_id: str,
        registry,
        profiler,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> DownloadReport:
        entry = registry.get(model_id)
        if entry is None:
            return DownloadReport(
                success=False,
                error=f"Modelo '{model_id}' não encontrado no registry.",
            )

        if registry.is_installed(model_id):
            logger.info(f"Modelo '{model_id}' já está instalado. Reutilizando cache.")
            return DownloadReport(
                success=True,
                model_path=os.path.join(
                    os.environ.get(
                        "HF_HOME",
                        os.path.join(os.path.expanduser("~"), ".cache", "huggingface"),
                    ),
                    "hub",
                    entry.name.replace("/", "--"),
                ),
            )

        hardware = profiler.detect()
        if hardware.disk_free_gb < entry.disk_required_gb:
            return DownloadReport(
                success=False,
                error=(
                    f"Disco insuficiente: {hardware.disk_free_gb:.1f}GB livre, "
                    f"mínimo {entry.disk_required_gb:.1f}GB requerido para '{model_id}'."
                ),
            )

        logger.info(f"Iniciando download do modelo '{model_id}' ({entry.name})...")
        start = time.time()
        total_size = MODEL_SIZES.get(model_id, 0)

        try:
            if snapshot_download is None:
                raise ImportError("huggingface_hub não está instalado.")

            if progress_callback is not None:

                class ProgressCapture:
                    def __init__(self, cb, total):
                        self._cb = cb
                        self._total = total

                    def __call__(self, current, total=None):
                        total = total or self._total
                        self._cb(current, total)

                progress = ProgressCapture(progress_callback, total_size)
                path = snapshot_download(
                    repo_id=entry.name,
                    local_files_only=False,
                    callback=progress.__call__,
                )
            else:
                path = snapshot_download(
                    repo_id=entry.name,
                    local_files_only=False,
                )

            elapsed = time.time() - start
            logger.info(
                f"Download concluído: '{model_id}' em {elapsed:.1f}s "
                f"({total_size / 1_000_000:.0f}MB)"
            )

            return DownloadReport(
                success=True,
                model_path=path,
                download_size_mb=round(total_size / 1_000_000, 1),
                elapsed_seconds=round(elapsed, 1),
            )

        except Exception as exc:
            logger.error(f"Falha no download do modelo '{model_id}': {exc}")
            return DownloadReport(
                success=False,
                error=f"Falha no download: {exc}",
            )