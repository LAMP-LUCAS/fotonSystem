---
type: concept
domain: core
status: active
tags: [rag, pipeline, embeddings, semantic-search]
---

# EPIC-004: RAG Pipeline Inteligente — Arquitetura Multi-Modelo e Grapho de Inferência

**Data:** 2026-07-02 (v2.0 — revisão estrutural)
**Stakeholders:** Equipe do escritório (todos os usuários), Time Core (manutenção), Arquiteto de IA
**Métrica de Sucesso:** Qualquer consulta RAG retorna resultado relevante em ≤3s, usando o melhor modelo disponível sem comprometer a máquina do usuário

## Dor Atual

O motor RAG atual (MiniLM + ChromaDB) é um MVP funcional, mas sua arquitetura monolítica impede evolução:

- **Modelo único hardcoded:** `paraphrase-multilingual-MiniLM-L12-v2` fixo em `vector_store.py:24`. Trocar de modelo exige alteração de código fonte.
- **Sem consciência de hardware:** O sistema não sabe se o usuário tem GPU, quanta RAM está disponível, ou se o download de 2.2 GB (BGE-M3) vai travar a máquina.
- **Sem pipeline configurável:** A sequência "embed → search → format" é fixa. Não há como inserir rerank, expansão de query, ou sumarização sem reescrever o fluxo inteiro.
- **Coleção sem identidade:** A coleção ChromaDB (`foton_knowledge_base`) não carrega metadados sobre qual modelo a gerou — impossível saber se uma coleção é compatível com o modelo ativo.
- **Download sem feedback:** Baixar modelos via `SentenceTransformer` é silencioso. O usuário não vê progresso e pode achar que o sistema travou.
- **Zero tolerância a fallback:** Se o modelo primário falha, não há fallback automático para um modelo mais leve.

## Solução Proposta

Arquiteturar o RAG como um **grafo de inferência configurável**, onde cada etapa (embed, search, rerank, format) é um **nó independente** e a topologia do pipeline é definida por configuração, não por código.

### Camadas do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CONFIG (settings.json)                    │
│  rag.pipeline.type = "simple" | "rerank" | "custom"         │
│  rag.pipeline.nodes = ["embed","search","format"]            │
│  rag.models.primary = "minilm" | "bgem3"                    │
│  rag.models.fallback = ["minilm"]                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 HARDWARE PROFILER                            │
│  Detecta: CPU cores, RAM total, CUDA, MPS, VRAM,            │
│  espaço em disco disponível, temperatura (futuro)            │
│  Saída: {ram_gb, has_cuda, vram_gb, recommended_mode,       │
│          warnings: ["RAM < 8GB — modo seguro ativado"]}      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  MODEL REGISTRY                              │
│  Catálogo de modelos conhecidos (embedding + rerank)         │
│  Cada entry: {id, name, dims, ram_required, disk_required,   │
│               requires_gpu, is_installed(), download_size}    │
│  Filtragem: available_models(hardware) → modelos viáveis     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   MODEL ROUTER                               │
│  resolve(config, hardware, registry) → [modelos ativos]      │
│  Valida: modo dual precisa ≥8GB RAM? Modelo precisa GPU?     │
│  Fallback: se primário não instalado → tenta fallback        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│               VECTOR STORE MANAGER                           │
│  Gerencia N instâncias de VectorStoreInstance                │
│  Cada instância: {collection_name, embedder, breaker}        │
│  Coleção nomeada: "foton_{model_tag}_{dims}d"                │
│  Metadata da coleção: model_name, dimensions, created_at     │
│  Operações: query, add_documents, delete, count, diagnostic  │
│  Modo dual: consulta paralela + merge por score              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                  RAG PIPELINE (Node Graph)                   │
│                                                              │
│  PipelineNode(ABC):                                          │
│    .name → identificador do nó                               │
│    .input_schema / .output_schema → validação                │
│    .execute(context) → ProcessContext                        │
│                                                              │
│  Nós padrão:                                                 │
│    EmbedNode   → gera embedding da query                     │
│    SearchNode  → busca na(s) coleção(ões) ativas             │
│    RerankNode  → reordena resultados por cross-encoder       │
│    FormatNode  → formata saída com contexto + score          │
│                                                              │
│  Pipeline = ordered list of PipelineNode                     │
│  Context = dict progressivo (cada nó enriquece)              │
└──────────────────────────────────────────────────────────────┘
```

## Critérios de Sucesso do Negócio

- [ ] Usuário pode escolher entre MiniLM (leve, rápido) e BGE-M3 (preciso) via TUI, sem editar código
- [ ] Sistema detecta hardware e alerta se modelo escolhido pode causar travamento
- [ ] Download de modelos tem barra de progresso na TUI e confirmação do usuário
- [ ] Modo "redundância total" indexa em ambos os modelos e consulta em paralelo com merge
- [ ] Fallback automático: se modelo primário falha, usa secundário sem perder a consulta
- [ ] Cada coleção ChromaDB armazena metadata do modelo que a gerou — impossível consultar com modelo errado
- [ ] Pipeline de inferência é configurável: "simple" (embed→search→format) ou "rerank" (embed→search→rerank→format)
- [ ] Futuramente: pipeline customizado via JSON (topologia do grafo definida em config)
- [ ] Zero regressão em funcionalidades existentes (consulta MCP, TUI, indexação)

## Métricas

- Tempo de consulta RAG ≤ 3s no modo MiniLM, ≤ 5s no modo BGE-M3 (CPU)
- Download de modelos com feedback visível em tempo real
- 100% das coleções ChromaDB com metadata de modelo (rastreabilidade total)
- Zero crashes por falta de RAM — hardware profiler bloqueia modelos inviáveis
- NPS do módulo RAG ≥ 8 (pesquisa pós-implementação)
  - **Primeira coleta:** 2026-07-06 (STORY-041)
  - **Periodicidade:** Semestral
  - **Template:** `.opencode/templates/NPS_RAG.md`

## Dependências

| Este épico depende de | Para fornecer |
|---|---|
| STORY-029 (filtros + contexto + diagnóstico) | Base de consulta atual |
| STORY-030 a STORY-041 (v2.0 pipeline multi-modelo) | 12 stories de implementação |
| INFRA: `sentence-transformers` + `chromadb` | Já resolvido pelo AI Pack |
| INFRA: `torch` (CUDA opcional) | GPU acceleration via hardware profiler |

## Histórico

| Data | Evento |
|------|--------|
| 2026-06-25 | EPIC-004 criado (v1 — MVP RAG) |
| 2026-07-02 | EPIC-004 revisado para v2.0 — arquitetura multi-modelo + pipeline node graph |
| 2026-07-03 | Implementado: STORY-028 (SPEC), STORY-029 (filtros + contexto + diagnóstico) |
| 2026-07-05 | Planejamento v2.0 completo: 12 stories (STORY-030 a STORY-041), SPEC-RAG-v2.0, SprintPlan revisado |
| 2026-07-06 | STORY-041: Template NPS criado, `primeira_coleta_nps` registrada |
