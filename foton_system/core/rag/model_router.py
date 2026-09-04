# @story: STORY-031
# @rule: RULE-RAG-9.1, RULE-RAG-9.2, RULE-RAG-9.3, RULE-RAG-9.4, RULE-RAG-9.5

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_MODE_MODEL_MAP = {
    "minilm": ["minilm"],
    "bgem3": ["bgem3"],
    "dual": ["minilm", "bgem3"],
}


class ModelRouter:
    @staticmethod
    def resolve(
        config: dict,
        hardware,
        registry,
    ) -> List[str]:
        rag_cfg = config.get("rag", {})
        mode = rag_cfg.get("mode", "minilm")
        models_config = rag_cfg.get("models", {})

        primary = models_config.get("primary", mode if mode in _MODE_MODEL_MAP else "minilm")
        fallback_list = models_config.get("fallback", [])

        if mode == "dual":
            candidates = _MODE_MODEL_MAP.get("dual", ["minilm", "bgem3"])
        else:
            candidates = [primary]

        resolved = []
        for model_id in candidates:
            if not registry.get(model_id):
                logger.warning("Modelo '%s' não encontrado no registry", model_id)
                continue
            feasible = registry.get(model_id)
            if hardware:
                from foton_system.core.rag.hardware_profiler import validate_feasibility
                report = validate_feasibility(model_id, hardware)
                if not report.is_feasible:
                    logger.warning("Modelo '%s' inviável no hardware: %s", model_id, report.warnings)
                    continue
            resolved.append(model_id)

        if not resolved:
            for fallback_id in fallback_list:
                if registry.get(fallback_id):
                    logger.info("Fallback para modelo '%s'", fallback_id)
                    resolved.append(fallback_id)
                    break

        if not resolved:
            if registry.get("minilm"):
                logger.warning("Nenhum modelo configurado disponível. Usando minilm como fallback duro.")
                resolved.append("minilm")

        logger.info("ModelRouter.resolve() -> %s", resolved)
        return resolved

    @staticmethod
    def validate_pipeline_feasibility(config: dict, hardware) -> List[str]:
        warnings = []
        if not hardware:
            return warnings

        rag_cfg = config.get("rag", {})
        mode = rag_cfg.get("mode", "minilm")

        if mode == "dual" and hardware.ram_total_gb < 8:
            warnings.append(
                f"Modo dual requer ≥8GB RAM. Detectado: {hardware.ram_total_gb:.1f}GB. "
                "Considere modo single 'minilm'."
            )

        models_config = rag_cfg.get("models", {})
        primary = models_config.get("primary", mode if mode in _MODE_MODEL_MAP else "minilm")

        from foton_system.core.rag.hardware_profiler import validate_feasibility as vf
        report = vf(primary, hardware)
        warnings.extend(report.warnings)

        if mode == "dual":
            secondary = "bgem3" if primary == "minilm" else "minilm"
            report2 = vf(secondary, hardware)
            warnings.extend(report2.warnings)

        return warnings

    @staticmethod
    def runtime_fallback(
        failed_model_id: str,
        active_instances: List[str],
    ) -> Optional[str]:
        for other in active_instances:
            if other != failed_model_id:
                logger.info("Runtime fallback: '%s' -> '%s'", failed_model_id, other)
                return other
        return None
