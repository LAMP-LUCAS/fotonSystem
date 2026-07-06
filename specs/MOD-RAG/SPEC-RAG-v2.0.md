---
type: spec
domain: core
status: active
tags: [rag, pipeline, embeddings, multi-model]
---

# Spec: RAG Pipeline Inteligente — Multi-Modelo e Grapho de Inferência — v2.0

**Data:** 2026-07-03
**Versão:** 2.0
**Responsável:** Time Core
**Épico:** EPIC-004 — RAG Pipeline Inteligente

## 1. Problema

O motor RAG atual (v1.0) é monolítico: modelo de embedding hardcoded, pipeline de inferência fixo (embed → search → format), sem consciência de hardware, sem fallback, sem identidade nas coleções ChromaDB. Para evoluir para um sistema de produção que suporte múltiplos modelos (MiniLM, BGE-M3, futuros) e pipelines configuráveis (com rerank, sumarização, etc.), é necessária uma reestruturação arquitetural profunda.

## 2. Solução Proposta

Arquiteturar o RAG em 6 camadas independentes, cada uma com responsabilidade única e interface bem definida. O sistema passa de um modelo único hardcoded para um **grafo de inferência configurável** onde a topologia do pipeline é definida por configuração.

## 3. Regras

### 3.0 Herança da v1.0 (regras mantidas)

- **RULE-RAG-1.1 a 1.4** — Infraestrutura (Singleton, ChromaDB, modelo, circuit breaker) — **refatorado** para multi-instância
- **RULE-RAG-2.1 a 2.4** — Indexação (recursiva, chunking, metadados, batch) — mantidos
- **RULE-RAG-2.5** — Watcher reindexa automaticamente — mantido
- **RULE-RAG-3.1** — ~~Subprocess mode~~ — **removido** (obsoleto na v2.0 in-process; ver STORY-041)
- **RULE-RAG-3.2 a 3.4** — Consulta (score, resultado, fallback) — mantidos
- **RULE-RAG-4.1 a 4.3** — Filtros (cliente, tipo_doc, contexto) — mantidos
- **RULE-RAG-5.1 a 5.3** — Interface TUI (atalho g, formatação, indexação) — mantidos
- **RULE-RAG-6.1 a 6.2** — Diagnóstico + indexação seletiva — mantidos

### 3.1 Hardware Profiler (NOVO)

- **RULE-RAG-7.1 (NOVA):** `HardwareProfiler.detect()` retorna `HardwareProfile` com: `cpu_cores`, `ram_gb` (total e disponível), `has_cuda`, `cuda_version`, `has_mps`, `vram_gb`, `disk_free_gb` (no diretório de cache do modelo).
- **RULE-RAG-7.2 (NOVA):** `recommended_mode(profile)` → "cpu_safe" (RAM < 8GB), "cpu_standard" (8-16GB), "gpu" (CUDA/MPS disponível), "oom_risk" (RAM < 4GB).
- **RULE-RAG-7.3 (NOVA):** `validate_feasibility(model_id, profile)` → `FeasibilityReport` com `is_feasible: bool` e `warnings: List[str]`. Ex: "BGE-M3 requer 4.5GB RAM — apenas 3.2GB disponível".
- **RULE-RAG-7.4 (NOVA):** Profiler executa em < 100ms, sem blocking I/O pesado. Cache do resultado por 60 segundos.

### 3.2 Model Registry (NOVO)

- **RULE-RAG-8.1 (NOVA):** `ModelRegistry` é singleton com catálogo de modelos conhecidos. Cada entry contém: `id`, `name` (HuggingFace ID), `type` ("embedding" | "rerank"), `dimensions`, `ram_required_gb`, `disk_required_gb`, `requires_gpu`, `is_default`.
- **RULE-RAG-8.2 (NOVA):** `is_installed(model_id)` → verifica se o modelo existe no cache HuggingFace local (`~/.cache/huggingface/` ou `HF_HOME`).
- **RULE-RAG-8.3 (NOVA):** `available_models(hardware_profile)` → filtra por `ram_required` vs `ram_gb` disponível. Modelos que exigem GPU e não têm CUDA são sinalizados com `requires_gpu=True` + `gpu_available=False`.
- **RULE-RAG-8.4 (NOVA):** Registry é extensível via plugin: novos modelos podem ser adicionados por configuração sem alterar código.

### 3.3 Model Router (NOVO)

- **RULE-RAG-9.1 (NOVA):** `ModelRouter.resolve(config, hardware, registry)` → lista de modelos ativos conforme modo `"minilm" | "bgem3" | "dual"`.
- **RULE-RAG-9.2 (NOVA):** Se modo `"dual"`, retorna `[modelo_primario, modelo_secundario]`. Ordem determina prioridade no merge.
- **RULE-RAG-9.3 (NOVA):** Se modelo primário não está instalado, tenta fallback configurado. Se nenhum fallback, gera erro com sugestão de instalação.
- **RULE-RAG-9.4 (NOVA):** `validate_pipeline_feasibility(config, hardware)` → `List[Warning]`. Ex: "Dual mode requer 8GB RAM — você tem 6GB. Considere modo single."
- **RULE-RAG-9.5 (NOVA):** Fallback automático em runtime: se `VectorStoreInstance.query()` falha (circuit breaker OPEN), router redireciona para próxima instância disponível.

### 3.4 Vector Store Manager (REFATORADO)

- **RULE-RAG-10.1 (NOVA):** `VectorStoreManager` substitui o Singleton `VectorStore`. Gerencia um dicionário de `{model_tag: VectorStoreInstance}`.
- **RULE-RAG-10.2 (NOVA):** `VectorStoreInstance` é a antiga `VectorStore` refatorada: contém `client` (ChromaDB), `embedder` (SentenceTransformer), `collection`, `breaker`.
- **RULE-RAG-10.3 (NOVA):** Cada coleção ChromaDB é nomeada como `foton_{model_tag}_{dimensions}d`. Metadata da coleção: `{model_name, model_tag, dimensions, created_at}`.
- **RULE-RAG-10.4 (NOVA):** `VectorStoreManager.query()` consulta todas as instâncias ativas. Em modo dual, faz merge dos resultados intercalando por score decrescente, removendo duplicatas (pelo chunk ID).
- **RULE-RAG-10.5 (NOVA):** `VectorStoreManager.add_documents()` indexa em TODAS as instâncias ativas. Cada instância gera seus próprios embeddings com seu modelo.
- **RULE-RAG-10.6 (NOVA):** `VectorStoreManager.diagnostic()` agrega diagnóstico de todas as instâncias: `{mode, stores: {tag: {total_chunks, cb_status, ultima_indexacao}}}`.
- **RULE-RAG-10.7 (NOVA):** Backward compatibility: se config `rag` ausente, `VectorStoreManager` opera em modo `"minilm"` com a coleção `foton_minilm_384d` (ou migra da legada `foton_knowledge_base` via STORY-035).

### 3.5 Pipeline Node System (NOVO)

- **RULE-RAG-11.1 (NOVA):** `PipelineNode(ABC)` — interface abstrata para todos os nós do pipeline. Contém: `name: str`, `input_keys: List[str]`, `output_keys: List[str]`, `async execute(context: ProcessContext) → ProcessContext`.
- **RULE-RAG-11.2 (NOVA):** `ProcessContext` é um dict progressivo: cada nó recebe o contexto enriquecido pelos nós anteriores. Contém `query`, `embeddings`, `raw_results`, `scored_results`, `formatted_output`.
- **RULE-RAG-11.3 (NOVA):** `RagPipeline` executa uma lista ordenada de `PipelineNode`. `RagPipeline.run(initial_context)` → chama `node.execute()` sequencialmente, passando o contexto.
- **RULE-RAG-11.4 (NOVA):** Nós padrão do sistema:
  - `EmbedNode`: gera embedding da query usando o modelo ativo
  - `SearchNode`: busca na(s) coleção(ões) via `VectorStoreManager`
  - `RerankNode`: reordena top-K resultados usando cross-encoder (ex: `BAAI/bge-reranker-v2-m3`)
  - `FormatNode`: monta saída com score, fonte, contexto e marcadores visuais
- **RULE-RAG-11.5 (NOVA):** Pipeline é configurável via `settings.json`:
  ```json
  {
    "rag": {
      "pipeline": {
        "type": "simple",
        "nodes": ["embed", "search", "format"]
      }
    }
  }
  ```
  Para rerank: `"type": "rerank", "nodes": ["embed", "search", "rerank", "format"]`
- **RULE-RAG-11.6 (NOVA):** Futuramente: pipeline customizado via JSON array, permitindo topologia arbitrária.

### 3.6 Download Manager (NOVO)

- **RULE-RAG-12.1 (NOVA):** `DownloadManager.ensure_model(model_id, progress_callback)` → baixa o modelo do HuggingFace Hub se não estiver instalado. Retorna `DownloadReport` com `{success, model_path, download_size_mb, elapsed_seconds}`.
- **RULE-RAG-12.2 (NOVA):** `progress_callback(bytes_downloaded, total_bytes)` — chamado durante o download para alimentar barra de progresso na TUI.
- **RULE-RAG-12.3 (NOVA):** Antes de baixar, verifica espaço em disco (`HardwareProfiler.disk_free_gb` >= `model.disk_required_gb`). Se insuficiente, aborta com erro claro.
- **RULE-RAG-12.4 (NOVA):** Em modo MCP (sem TUI), download é síncrono com logs periódicos. Em modo TUI, barra de progresso é atualizada em tempo real.
- **RULE-RAG-12.5 (NOVA):** Cache de modelos baixados em `HF_HOME` (~/.cache/huggingface). Reutilização automática se já instalado.

## 4. Arquivos do Sistema

### Core — Camada de Domínio do RAG

| Arquivo | Responsabilidade |
|---------|-----------------|
| `foton_system/core/rag/hardware_profiler.py` | Detecção de hardware (CPU, RAM, GPU) |
| `foton_system/core/rag/model_registry.py` | Catálogo de modelos conhecidos |
| `foton_system/core/rag/model_router.py` | Roteamento: config + hardware → modelos ativos |
| `foton_system/core/rag/download_manager.py` | Download sob demanda com progress callback |
| `foton_system/core/rag/pipeline.py` | Orquestrador do pipeline de inferência |
| `foton_system/core/rag/nodes/__init__.py` | Pacote de nós do pipeline |
| `foton_system/core/rag/nodes/embed_node.py` | Nó de embedding |
| `foton_system/core/rag/nodes/search_node.py` | Nó de busca vetorial |
| `foton_system/core/rag/nodes/rerank_node.py` | Nó de rerank (cross-encoder) |
| `foton_system/core/rag/nodes/format_node.py` | Nó de formatação de saída |
| `foton_system/core/rag/migration.py` | Migração de coleções legadas |
| `foton_system/core/memory/vector_store.py` | **Refatorado:** VectorStoreInstance + VectorStoreManager |

### Config

| Arquivo | Mudança |
|---------|---------|
| `foton_system/modules/shared/infrastructure/config/config.py` | Adicionar seção `rag` ao schema + properties |

### Interface

| Arquivo | Mudança |
|---------|---------|
| `foton_system/interfaces/cli/menus_rag.py` | **Novo:** Menu de configuração RAG |
| `foton_system/interfaces/cli/menus_config.py` | Estender com opção para submenu RAG |
| `foton_system/interfaces/mcp/foton_mcp.py` | `diagnostico_conhecimento` expandido multi-modelo |

## 5. Pipeline de Dados — Fluxo Completo

```
QUERY
  │
  ▼
[EmbedNode] ──────────────────────────────────────────────┐
  │ Gera embedding da query usando modelo ativo            │
  ▼                                                        │
[SearchNode]                                               │
  │ Busca em coleção(ões) ativas via ChromaDB              │
  │ Modo single: 1 consulta                                │
  │ Modo dual: 2 consultas paralelas + merge               │
  ▼                                                        │
[RerankNode] ←── opcional (se pipeline = "rerank")         │
  │ Reordena top-K com cross-encoder                       │
  ▼                                                        │
[FormatNode]                                               │
  │ Monta saída: [Score: XX%] — Fonte: path + contexto    │
  │ Aplica marcadores >>>...<<<                            │
  ▼                                                        │
OUTPUT                                                     │
                                                           │
Para CADA indexação:                                       │
  [Indexador] → EmbedNode (DOC) → SearchNode (add)        │
  → repete para cada modelo ativo                          │
```

## 6. Relações

- Depende de: `VectorStoreInstance` (ChromaDB + SentenceTransformer)
- Consome: `Config` (seção `rag`)
- Exposto via: MCP tools (`consultar_conhecimento`, `indexar_conhecimento`, `diagnostico_conhecimento`)
- Consumido por: TUI (menus RAG), CLI (comandos diretos)

## 7. Changelog

| Versão | Data | Mudanças |
|--------|------|----------|
| v2.0 | 2026-07-03 | Arquitetura multi-modelo: Hardware Profiler, Model Registry, Router, Pipeline Nodes, Download Manager, VectorStoreManager |
| v1.0 | 2026-07-02 | Versão inicial — regras 1.1 a 6.2 (MVP RAG) |
