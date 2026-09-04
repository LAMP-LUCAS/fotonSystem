---
status: "draft"
sprint: "2026-SPRINT-9"
---

# STORY-036: Testes de Integração End-to-End do Pipeline RAG

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Validar o fluxo completo de orquestração entre as 6 camadas do RAG v2.0: `TUI/HardwareProfiler → ModelRouter → DownloadManager → VectorStoreManager (indexação) → PipelineNodes (consulta) → saída formatada`. Garantir que a integração entre componentes não produz vazamento de contexto, falhas de merge em modo dual, ou inconsistência de dados entre coleções.

## Regras

- **RULE-RAG-7.1 a 7.4** — HardwareProfiler consultado antes de qualquer operação de modelo
- **RULE-RAG-9.1 a 9.5** — ModelRouter + fallback em cenário real
- **RULE-RAG-10.1 a 10.7** — VectorStoreManager multi-instância operando em conjunto
- **RULE-RAG-11.1 a 11.5** — Pipeline completo (embed → search → format / rerank)
- **RULE-RAG-12.1 a 12.5** — Download sob demanda antes da indexação

## Critérios de Aceite

- [ ] Teste E2E: modo MiniLM — indexa 3 chunks, consulta, valida saída formatada com score + fonte + `>>>...<<<`
- [ ] Teste E2E: modo dual — indexa em ambas coleções, consulta em paralelo, merge sem duplicatas
- [ ] Teste E2E: fallback runtime — breaker OPEN na primária → redireciona para secundária, consulta completa
- [ ] Teste E2E: download sob demanda → ModelRouter resolve → DownloadManager baixa → indexação imediata (mockado)
- [ ] Teste E2E: migração da coleção legada `foton_knowledge_base` → novo formato → consulta funciona
- [ ] Teste E2E: TUI → mudar modelo → confirmação → re-indexação → consulta
- [ ] Teste E2E: pipeline rerank (mockado) reordena top-K corretamente
- [ ] Teste E2E: config ausente (`rag` section) → fallback para MiniLM legado sem crash

## Arquivos

- `tests/integration/test_rag_pipeline_e2e.py` (novo)
- `tests/integration/conftest.py` (novo ou estendido com fixtures E2E)
- `tests/fixtures/rag_e2e/` — chunks de teste, configs mockadas

## Estimativa

6h

## Dependências

- STORY-030 (Hardware Profiler + Registry)
- STORY-031 (Model Router + VectorStoreManager)
- STORY-032 (Download Manager)
- STORY-033 (Pipeline Nodes)
- STORY-035 (Migration + Backward Compat)
