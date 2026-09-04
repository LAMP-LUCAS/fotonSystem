---
status: "done"
sprint: "2026-SPRINT-9"
---

# STORY-035: Migration + Backward Compatibility

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Criar o script de migração que converte a coleção legada `foton_knowledge_base` (nome antigo, sem metadata de modelo) para o novo formato `foton_minilm_384d` com metadata completa. Garantir que instalações existentes continuem funcionando sem config `rag` — o sistema deve detectar a ausência e operar em modo MiniLM legado.

## Regras

- **RULE-RAG-10.7:** Backward compatibility: config `rag` ausente → modo minilm legado.

## Critérios de Aceite

- [ ] Script `migration.py` detecta coleção `foton_knowledge_base` existente
- [ ] Migração cria nova coleção `foton_minilm_384d` copiando dados + metadados
- [ ] Metadata da nova coleção contém `{model_name, model_tag, dimensions, created_at}`
- [ ] Após migração, coleção legada é renomeada para `_legada` (backup)
- [ ] Sem config `rag` em settings.json, VectorStoreManager opera como MiniLM puro
- [ ] Sem config `rag` e sem coleção migrada, cria `foton_minilm_384d` do zero
- [ ] Mensagem clara ao usuário se migração for necessária
- [ ] Testes: migração de coleção, fallback sem config, criação do zero

## Arquivos

- `foton_system/core/rag/migration.py` (novo) — migração + compat checker

## Estimativa

2h

## Dependências

- STORY-031 (VectorStoreManager) — para testar backward compat
