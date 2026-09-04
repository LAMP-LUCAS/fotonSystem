---
type: guide
domain: rag
status: active
tags: [rag, documentation, index]
---

# Documentação RAG — FOTON System

> **RAG** (Retrieval-Augmented Generation) é o módulo de memória semântica do escritório. Ele permite buscar conhecimento em projetos passados usando linguagem natural.

## Guias

| Guia | Público | O que cobre |
|------|---------|-------------|
| [USER_GUIDE.md](USER_GUIDE.md) | Usuários finais | Operação diária, modos, diagnóstico, troubleshooting |
| [DEVELOPER.md](DEVELOPER.md) | Desenvolvedores | Arquitetura, pipeline nodes, extensão, testes |

## Pré-requisitos

- FOTON System v1.4.0 ou superior
- `sentence-transformers` e `chromadb` (incluídos no AI Pack)

## Navegação Rápida

- **Acessar o RAG:** Menu Principal → Opção 7 (Configurações) → RAG
- **Diagnóstico:** Visualiza hardware, modelo ativo, coleções e status
- **Benchmarks:** `pytest benchmarks/rag_benchmark.py -v --benchmark`
- **Testes:** `pytest tests/integration/test_rag_pipeline_e2e.py -v`
