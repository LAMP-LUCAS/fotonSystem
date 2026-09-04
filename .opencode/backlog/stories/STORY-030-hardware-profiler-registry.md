---
status: "done"
sprint: "2026-SPRINT-9"
---

# STORY-030: Hardware Profiler + Model Registry

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Implementar as duas camadas de base da nova arquitetura RAG: o Hardware Profiler (detecção de CPU, RAM, GPU) e o Model Registry (catálogo de modelos de embedding e rerank conhecidos). Estas camadas são pré-requisito para todas as demais, pois o roteamento de modelos e a validação de viabilidade dependem delas.

## Regras

- **RULE-RAG-7.1:** `HardwareProfiler.detect()` retorna `HardwareProfile` com CPU cores, RAM total/disponível, CUDA/MPS, VRAM, disco livre.
- **RULE-RAG-7.2:** `recommended_mode(profile)` → "cpu_safe" | "cpu_standard" | "gpu" | "oom_risk".
- **RULE-RAG-7.3:** `validate_feasibility(model_id, profile)` → `FeasibilityReport` com warnings.
- **RULE-RAG-7.4:** Profiler executa em < 100ms, cache de 60s.
- **RULE-RAG-8.1:** `ModelRegistry` — catálogo singleton de modelos conhecidos.
- **RULE-RAG-8.2:** `is_installed(model_id)` via cache HuggingFace.
- **RULE-RAG-8.3:** `available_models(hardware)` filtra por viabilidade.
- **RULE-RAG-8.4:** Registry extensível via configuração (plugin).

## Critérios de Aceite

- [ ] `HardwareProfiler.detect()` retorna CPU cores, RAM total (GB), RAM disponível (GB)
- [ ] `HardwareProfiler.detect()` detecta CUDA (se disponível) e VRAM
- [ ] `HardwareProfiler.detect()` detecta MPS (Apple Silicon) se disponível
- [ ] `HardwareProfiler.detect()` retorna espaço livre em disco no cache dir
- [ ] `recommended_mode(profile)` retorna modo seguro se RAM < 8GB
- [ ] `validate_feasibility("bgem3", profile_com_4gb_ram)` retorna `is_feasible=False` + warning
- [ ] `ModelRegistry` contém entries para minilm (384d) e bgem3 (1024d)
- [ ] `is_installed("minilm")` retorna True se modelo está em HF_HOME
- [ ] `available_models(profile)` exclui modelos inviáveis (RAM insuficiente)
- [ ] Profiler tem cache de 60s (não redetecta a cada chamada)
- [ ] Testes mockados para CUDA ausente, RAM baixa, disco cheio

## Arquivos

- `foton_system/core/rag/hardware_profiler.py` (novo)
- `foton_system/core/rag/model_registry.py` (novo)

## Estimativa

4h

## Dependências

Nenhuma (pode iniciar em paralelo com STORY-032)
