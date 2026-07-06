---
status: "completed"
sprint: "2026-SPRINT-9"
completed: "2026-07-06"
---

# STORY-038: Performance Benchmarking e SLA Validation

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Criar suite de benchmarks automatizados para validar os SLAs definidos no PRD: consulta RAG ≤3s no modo MiniLM e ≤5s no modo BGE-M3 (CPU). Os benchmarks rodam com dataset controlado de 100 chunks e 10 queries padrão, reportando p50, p95 e p99 para cada operação crítica.

## Regras

- **PRD — Métricas:** Tempo de consulta RAG ≤3s (MiniLM), ≤5s (BGE-M3 CPU)
- **PRD — Métricas:** Download de modelos com feedback visível
- **RULE-RAG-7.4:** Profiler executa em < 100ms
- **RULE-RAG-11.3:** Pipeline executa nós sequencialmente

## Critérios de Aceite

- [x] Benchmark: MiniLM modo simple — p95 < 3s em 10 rodadas com dataset de 100 chunks
- [x] Benchmark: BGE-M3 modo simple (CPU) — p95 < 5s (mockado se GPU indisponível)
- [x] Benchmark: modo dual — p95 < 2× tempo single (overhead de merge aceitável)
- [x] Benchmark: indexação — 100 chunks em < 30s (MiniLM)
- [x] Benchmark: `HardwareProfiler.detect()` — p95 < 100ms
- [x] Script executável via `python -m pytest benchmarks/rag_benchmark.py -v --benchmark`
- [x] Falha com assert se SLA não for atingido (tolerância configurável via fixture)
- [x] Dataset fixo e versionado em `tests/fixtures/rag_benchmark_data/`
- [x] Relatório de benchmark exportável em JSON para CI/CD
- [x] Benchmark ignora CUDA se GPU não disponível (não falha, apenas reporta "skipped")

## Arquivos

- `benchmarks/rag_benchmark.py` (novo)
- `tests/fixtures/rag_benchmark_data/chunks.json` (100 chunks pré-definidos)
- `tests/fixtures/rag_benchmark_data/queries.json` (10 queries padrão)
- `pyproject.toml` ou `setup.cfg` — adicionar marker `benchmark`

## Estimativa

3h

## Dependências

- STORY-031 (VectorStoreManager) — para benchmark de query/indexação
- STORY-033 (Pipeline Nodes) — para benchmark de pipeline completo
