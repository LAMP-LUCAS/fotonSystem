---
status: "done"
sprint: "2026-SPRINT-8"
---

# STORY-028: SPEC-RAG-v1.0 — Formalização do Módulo RAG

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v1.0.md`

## Descrição

Criar a especificação técnica do módulo RAG com RULE-IDs rastreáveis. A infraestrutura, indexação e consulta já estão implementadas; esta story formaliza as regras de negócio existentes e define as novas para filtros, contexto, diagnóstico e TUI.

## Regras

- **RULE-RAG-1.1 a 1.4:** Infraestrutura (Singleton, ChromaDB, modelo, circuit breaker)
- **RULE-RAG-2.1 a 2.5:** Indexação (recursiva, chunking, metadados, batch, watcher)
- **RULE-RAG-3.1 a 3.4:** Consulta (MCP, score, fallback)
- Definição das regras novas: RAG-4.1 a 6.2

## Critérios de Aceite

- [ ] `specs/MOD-RAG/SPEC-RAG-v1.0.md` criada
- [ ] RULE-IDs documentados: 1.1 a 6.2
- [ ] Regras existentes demarcadas como "já implementado"
- [ ] Regras novas demarcadas como "NOVO v1.0"
- [ ] Changelog da spec preenchido

## Estimativa

1h

## Dependências

Nenhuma
