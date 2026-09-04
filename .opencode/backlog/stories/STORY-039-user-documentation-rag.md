---
status: "completed"
sprint: "2026-SPRINT-9"
---

# STORY-039: Documentação de Usuário do RAG Multi-Modelo

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Criar documentação em português para o usuário final e para desenvolvedores sobre as novas capacidades RAG v2.0. O guia do usuário cobre como trocar de modelo, interpretar diagnóstico e resolver problemas comuns. O guia do desenvolvedor cobre arquitetura, plugin de modelos e nós de pipeline customizados.

## Critérios de Aceite

### `docs/rag/USER_GUIDE.md`

- [ ] Explica o que é o RAG e para que serve (linguagem não-técnica)
- [ ] Como acessar: Menu Principal → Opção 7 (Configurações) → RAG
- [ ] Modos de operação: MiniLM (leve/rápido), BGE-M3 (preciso/pesado), Dual (redundância)
- [ ] Recomendação por perfil de hardware (< 8GB RAM → MiniLM, 8-16GB → BGE-M3, > 16GB → Dual)
- [ ] Como instalar/baixar um modelo com barra de progresso
- [ ] O que significa cada campo no diagnóstico (coleção, modelo, dimensões, chunks, CB)
- [ ] Troubleshooting: "Modelo não encontrado", "Memória insuficiente", "Download falhou", "Slow query"

### `docs/rag/DEVELOPER.md`

- [ ] Diagrama de arquitetura das 6 camadas (ASCII ou Mermaid)
- [ ] Como adicionar um novo modelo ao Registry via settings.json
- [ ] Como criar um nó de pipeline customizado (implementar PipelineNode)
- [ ] Como registrar um nó customizado no RagPipeline
- [ ] Como rodar os benchmarks: `python -m pytest benchmarks/rag_benchmark.py -v --benchmark`
- [ ] Como rodar testes de integração: `python -m pytest tests/integration/test_rag_pipeline_e2e.py -v`

## Arquivos

- `docs/rag/USER_GUIDE.md` (novo)
- `docs/rag/DEVELOPER.md` (novo)
- `docs/rag/README.md` (novo, índice do diretório)

## Estimativa

2h

## Dependências

- STORY-030 (Hardware Profiler) — para recomendações por hardware
- STORY-032 (Download Manager) — para guia de download
- STORY-034 (TUI RAG Configuration) — para telas documentadas
- STORY-038 (Performance Benchmarking) — para seção "Como rodar benchmarks"
