---
status: "completed"
sprint: "2026-SPRINT-9"
---

# STORY-040: Validação de Schema e Configuração RAG

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Implementar validação rigorosa da seção `rag` em `settings.json` com schema JSON tipado. Garantir que configuração inválida não derruba o sistema — fallback para defaults com warning logado. Expor properties tipadas na classe `Config` para consumo pelas camadas superiores.

## Regras

- **RULE-RAG-9.1:** `ModelRouter.resolve()` lê config do settings.json
- **RULE-RAG-9.4:** `validate_pipeline_feasibility()` usa valores da config
- **RULE-RAG-10.7:** Backward compat: config `rag` ausente → modo minilm legado
- **RULE-RAG-11.5:** Pipeline configurável via settings.json

## Critérios de Aceite

- [ ] Schema JSON para `rag` define todos os campos com tipos e valores permitidos:
  - `embedding_mode`: enum(`"minilm"`, `"bgem3"`, `"dual"`), default `"minilm"`
  - `pipeline.type`: enum(`"simple"`, `"rerank"`), default `"simple"`
  - `pipeline.nodes`: array de strings, default `["embed", "search", "format"]`
  - `models.primary`: string, default `"minilm"`
  - `models.fallback`: array de strings, default `["minilm"]`
- [ ] Schema usa `jsonschema` ou equivalente para validação
- [ ] Valor inválido (ex: `embedding_mode: "gpt"`) → erro de validação com mensagem clara + fallback para default
- [ ] Config `rag` totalmente ausente → defaults seguros + warning no log
- [ ] Campo desconhecido dentro de `rag` → warning ignorado (forward compat)
- [ ] `Config` expõe properties: `rag_embedding_mode → str`, `rag_pipeline_type → str`, `rag_models_primary → str`, `rag_models_fallback → list[str]`
- [ ] Properties retornam valores validados (já passaram pelo schema)
- [ ] Testes: schema válido, schema inválido, schema ausente, tipos errados, enum inválido, campo extra ignorado

## Arquivos

- `foton_system/modules/shared/infrastructure/config/rag_schema.py` (novo) — schema JSON + validador
- `foton_system/modules/shared/infrastructure/config/config.py` (modificar) — adicionar properties `rag_*`
- `tests/unit/config/test_rag_schema.py` (novo)

## Estimativa

2h

## Dependências

- STORY-031 (definição da seção `rag` em settings.json)
