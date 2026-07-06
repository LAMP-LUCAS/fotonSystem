---
status: "draft"
sprint: "2026-SPRINT-9"
---

# STORY-041: Encerramento de Dívidas Técnicas v1.0 + Telemetria + NPS

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Quatro sub-tarefas independentes para fechar gaps identificados no Sprint Review 8:

1. **Remover Subprocess Mode (RAG-3.1):** Código morto `_find_system_python()` — resquício da arquitetura legada que não faz sentido na v2.0 in-process. Remover da spec e do código.
2. **Adicionar testes faltantes:** RAG-2.3 (metadados), RAG-2.4 (batch upsert), RAG-5.2 (formatação TUI).
3. **Telemetria inline nas tools RAG:** Timing real nas consultas + baseline script.
4. **Expansão NPS:** Incluir módulo RAG na pesquisa de satisfação.

## Regras

- **RAG-2.3 (herdado, sem teste):** Metadados dos chunks — fonte, header, linha — devem ser verificados em teste.
- **RAG-2.4 (herdado, sem teste):** Batch upsert de múltiplos chunks em uma chamada.
- **RAG-3.1 (herdado):** Subprocess mode — **remover** da spec e do código. Substituído pelo ModelRouter da v2.0.
- **RAG-5.2 (herdado, sem teste):** Formatação TUI com `>>>...<<<`, score percentual, alinhamento.
- **PRD — Métricas:** Baseline de performance + NPS ≥ 8.

## Critérios de Aceite

### A — Subprocess Mode
- [ ] Função `_find_system_python()` removida de `op_query_knowledge.py`
- [ ] RAG-3.1 removido da seção 3.0 em SPEC-RAG-v2.0.md
- [ ] Nenhum teste quebrado com a remoção
- [ ] Consulta RAG via MCP continua funcionando sem o código

### B — Testes Faltantes
- [ ] Teste RAG-2.3: chunk indexado contém metadados `fonte`, `header`, `linha_inicio`, `linha_fim`
- [ ] Teste RAG-2.4: `add_documents()` com lote de 5 chunks insere todos em uma chamada
- [ ] Teste RAG-5.2: formatação TUI exibe `[Score: XX%] — Fonte: path` + `>>>contexto<<<`

### C — Telemetria
- [ ] `OpQueryKnowledge.execute()` mede `duration_ms` com `time.perf_counter()`
- [ ] Log no formato `[RAG_PERF] consulta=<hash> duration_ms=1234 modelo=minilm pipeline=simple`
- [ ] MCP `consultar_conhecimento` retorna campo `duracao_ms` na resposta
- [ ] `scripts/performance_baseline.py` executa 10 consultas e gera JSON com p50/p95/p99
- [ ] Baseline script aceita flag `--mode` (minilm | bgem3 | dual)

### D — NPS
- [ ] Pergunta NPS adicionada ao questionário existente: *"Em uma escala de 0 a 10, o quanto o módulo de Consulta Inteligente (RAG) te ajuda a encontrar informações de projetos passados?"*
- [ ] Template em `.opencode/templates/NPS_RAG.md` com instruções de coleta e cálculo
- [ ] PRD atualizado com campo `primeira_coleta_nps` no histórico

## Arquivos

- `foton_system/core/ops/op_query_knowledge.py` — remover `_find_system_python()` + adicionar telemetria
- `foton_system/interfaces/mcp/foton_mcp.py` — retornar `duracao_ms` em `consultar_conhecimento`
- `specs/MOD-RAG/SPEC-RAG-v2.0.md` — remover RAG-3.1 da herança
- `tests/unit/test_op_index_knowledge.py` — testes RAG-2.3 e RAG-2.4
- `tests/unit/test_rag_filters.py` — teste RAG-5.2
- `scripts/performance_baseline.py` — novo
- `docs/prd/epics/EPIC-004.md` — adicionar campo NPS
- `.opencode/templates/NPS_RAG.md` — novo

## Estimativa

6h

## Dependências

Nenhuma (pode rodar em paralelo com STORY-030)
