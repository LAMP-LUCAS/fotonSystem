# Spec: Módulo RAG — Recuperação Inteligente de Conhecimento — v1.0

**Data:** 2026-07-02
**Versão:** 1.0
**Responsável:** Time Core
**Épico:** EPIC-004 — Recuperação Inteligente (RAG)

## 1. Problema

O Foton System possui um motor de busca semântica (ChromaDB + sentence-transformers) funcional, mas subutilizado: não há filtro por cliente ou tipo de documento, resultados não mostram contexto ao redor do match, não há diagnóstico de integridade do índice, e a TUI não expõe busca dedicada.

## 2. Solução Proposta

Evoluir o RAG de MVP técnico para ferramenta de uso diário: filtros de busca, contexto enriquecido nos resultados, diagnóstico de integridade e indexação seletiva.

## 3. Regras

### 3.1 Infraestrutura (já implementado)
- **RULE-RAG-1.1:** `VectorStore` é Singleton que gerencia `ChromaDB PersistentClient`. Apenas uma instância do modelo de embedding em memória.
- **RULE-RAG-1.2:** Coleção padrão `foton_knowledge_base` com espaço de busca `cosine`. Persistência em `{config_dir}/memory_db`.
- **RULE-RAG-1.3:** Modelo de embedding: `paraphrase-multilingual-MiniLM-L12-v2` (otimizado PT-BR).
- **RULE-RAG-1.4:** Circuit breaker: 3 falhas consecutivas → OPEN por 60s → HALF_OPEN → probe. Graceful degradation: falha retorna resposta vazia, nunca crash.

### 3.2 Indexação (já implementado)
- **RULE-RAG-2.1:** `OpIndexKnowledge` varre recursivamente arquivos `*.md` e `*.txt` na pasta de clientes. Aceita `target_path` opcional para indexação seletiva.
- **RULE-RAG-2.2:** Chunking header-aware: seções Markdown (`#`, `##`, etc.) viram chunks individuais. Sub-chunking com overlap de 50 caracteres se chunk > 500 chars.
- **RULE-RAG-2.3:** Metadados obrigatórios por chunk: `source` (path absoluto), `filename`, `hash` (MD5), `chunk_index`.
- **RULE-RAG-2.4:** Batch upsert de 100 documentos por vez no ChromaDB.
- **RULE-RAG-2.5:** `Watcher` reindexa automaticamente ao criar/modificar arquivos `.md`/`.txt`. Debounce de 2 segundos.

### 3.3 Consulta (já implementado)
- **RULE-RAG-3.1:** `consultar_conhecimento(pergunta)` — busca semântica via MCP. Retorna até 5 resultados. Suporta modo frozen (subprocess) e modo nativo.
- **RULE-RAG-3.2:** Score de similaridade = `1 - distancia_cosseno`. Retornado como percentual.
- **RULE-RAG-3.3:** Resultados incluem: texto do documento, `source` (path do arquivo), `score` (0-1).
- **RULE-RAG-3.4:** Se ChromaDB indisponível (circuit breaker OPEN), retorna mensagem clara "Nenhum conhecimento relevante encontrado."

### 3.4 Filtros e Contexto (NOVO v1.0)
- **RULE-RAG-4.1 (NOVA):** `consultar_conhecimento` aceita parâmetro opcional `cliente` — filtra resultados para chunks cujo `source` contenha o nome da pasta do cliente.
- **RULE-RAG-4.2 (NOVA):** `consultar_conhecimento` aceita parâmetro opcional `tipo_doc` — filtra por tipo de arquivo (ex: `INFO`, `dados`, `proposta`). O filtro opera sobre o `filename` do metadado.
- **RULE-RAG-4.3 (NOVA):** Resultados exibem trecho de contexto: 100 caracteres antes e depois do trecho mais relevante de cada chunk, delimitado por marcadores visuais.

### 3.5 Interface e Diagnóstico (NOVO v1.0)
- **RULE-RAG-5.1 (REVISADO):** TUI: atalho `g` no menu principal pertence à SPEC-UX (RULE-UX-8.9) e dispara exclusivamente `global_search` (busca global por clientes). A consulta semântica RAG é acessível via submenu (Configurações > RAG > Consultar Conhecimento).
- **RULE-RAG-5.2:** TUI: resultado da consulta exibido com formatação: `[Score: XX%] Fonte: caminho/arquivo.md`, seguido do trecho com contexto.
- **RULE-RAG-5.3:** Indexação manual disponível na TUI com feedback de progresso (arquivos escaneados, chunks criados).
- **RULE-RAG-6.1 (NOVA):** Ferramenta de diagnóstico: `diagnostico_conhecimento` — retorna total de chunks, status do circuit breaker (CLOSED/OPEN), última indexação.
- **RULE-RAG-6.2 (NOVA):** `indexar_conhecimento` aceita parâmetro `cliente` para re-indexação seletiva (apenas um cliente, não o acervo inteiro).

## 4. Relações

- Port: `KnowledgeStoreProtocol` (em `mcp_services.py`)
- MCP tools existentes: `indexar_conhecimento`, `consultar_conhecimento`
- Novas MCP tools (propostas): `diagnostico_conhecimento`

## 5. Changelog

| Versão | Data | Mudanças |
|--------|------|----------|
| v1.0 | 2026-07-02 | Versão inicial — regras 1.1 a 6.2 |
