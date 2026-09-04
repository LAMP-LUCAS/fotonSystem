---
status: "draft"
sprint: "2026-SPRINT-9"
---

# STORY-037: Expandir MCP `diagnostico_conhecimento` para Multi-Modelo

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Atualizar a ferramenta MCP `diagnostico_conhecimento` (criada em STORY-029) para refletir a arquitetura multi-modelo do RAG v2.0. O diagnóstico deve exibir todas as coleções ativas com seus metadados individuais (modelo, dimensões, chunks, status circuit breaker) e o modo de operação atual (minilm | bgem3 | dual).

## Regras

- **RULE-RAG-10.6:** `VectorStoreManager.diagnostic()` agrega diagnóstico de todas as instâncias.
- **RULE-RAG-10.7:** Backward compat: sem config `rag`, exibe diagnóstico simples.
- **RULE-RAG-6.2:** Diagnóstico deve incluir total_chunks, cb_status, ultima_indexacao (herdado).

## Critérios de Aceite

- [ ] `diagnostico_conhecimento()` retorna `mode` (minilm | bgem3 | dual)
- [ ] Lista cada coleção ativa com: `colecao`, `modelo`, `dimensoes`, `total_chunks`, `status_circuit_breaker`, `ultima_indexacao`
- [ ] Em modo legado (sem config `rag`), exibe diagnóstico de coleção única sem `mode`
- [ ] Campo `ultima_indexacao` em ISO datetime legível (não timestamp bruto)
- [ ] Se nenhuma coleção existe, retorna diagnóstico vazio com mensagem informativa
- [ ] Testes: MCP tool retorna JSON estruturado; legado compat; multi-coleção; coleção vazia
- [ ] Testes de contrato: schema da resposta não quebra consumidores existentes (TUI, CLI)

## Arquivos

- `foton_system/interfaces/mcp/foton_mcp.py` — modificar handler `diagnostico_conhecimento`
- `tests/unit/mcp/test_foton_mcp_rag.py` — testes do novo formato

## Estimativa

2h

## Dependências

- STORY-031 (VectorStoreManager.diagnostic())
