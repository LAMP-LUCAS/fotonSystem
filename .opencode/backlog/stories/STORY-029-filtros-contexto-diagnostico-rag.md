---
status: "ready"
sprint: "2026-SPRINT-8"
---

# STORY-029: Filtros + Contexto + Diagnóstico RAG

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v1.0.md`

## Descrição

Implementar os refinamentos de UX que tornam o RAG utilizável no dia a dia: filtro por cliente e tipo de documento, contexto ao redor do match nos resultados, ferramenta de diagnóstico, e integração na TUI com atalho dedicado.

## Regras

- **RULE-RAG-4.1 (nova):** `consultar_conhecimento` aceita parâmetro `cliente` — filtra chunks pelo nome da pasta do cliente no `source`.
- **RULE-RAG-4.2 (nova):** `consultar_conhecimento` aceita parâmetro `tipo_doc` — filtra por tipo de arquivo (INFO, dados, etc.) via `filename` do metadado.
- **RULE-RAG-4.3 (nova):** Resultados exibem trecho de contexto (100 chars antes/depois) delimitado por marcadores visuais.
- **RULE-RAG-5.1:** TUI: atalho `g` no menu principal para acesso rápido à consulta semântica.
- **RULE-RAG-5.2:** TUI: resultado formatado com score, fonte e contexto.
- **RULE-RAG-5.3:** Indexação manual na TUI com feedback de progresso.
- **RULE-RAG-6.1 (nova):** MCP tool `diagnostico_conhecimento` — retorna total de chunks, status do circuit breaker (CLOSED/OPEN), data da última indexação.
- **RULE-RAG-6.2 (nova):** `indexar_conhecimento` aceita parâmetro `cliente` para re-indexação seletiva (apenas um cliente).

## Critérios de Aceite

- [ ] `consultar_conhecimento(pergunta, cliente="ClienteX")` filtra por cliente
- [ ] `consultar_conhecimento(pergunta, tipo_doc="INFO")` filtra por tipo de documento
- [ ] Resultados incluem campo `contexto` com 100 chars antes/depois do trecho relevante
- [ ] MCP tool `diagnostico_conhecimento` retorna `{total_chunks, circuit_breaker_status, ultima_indexacao}`
- [ ] `indexar_conhecimento(pasta_alvo="ClienteX")` indexa apenas um cliente
- [ ] TUI: atalho `g` no menu principal abre consulta semântica
- [ ] TUI: resultados exibem `[Score: XX%] — Fonte: path` + contexto
- [ ] TUI: indexação manual exibe progresso (arquivos escaneados, chunks criados)
- [ ] Testes: filtro cliente, filtro tipo_doc, contexto snippet, diagnóstico, indexação seletiva

## Arquivos Afetados

- `foton_system/core/ops/op_query_knowledge.py` — filtros + contexto
- `foton_system/core/ops/op_index_knowledge.py` — indexação seletiva
- `foton_system/core/memory/vector_store.py` — método diagnóstico
- `foton_system/interfaces/mcp/foton_mcp.py` — novos parâmetros + tool diagnóstico
- `foton_system/interfaces/cli/menus.py` — atalho `g`
- `foton_system/interfaces/cli/menus_config.py` — TUI formatada

## Estimativa

6h

## Dependências

- STORY-028 (SPEC já criada — desbloqueada)
