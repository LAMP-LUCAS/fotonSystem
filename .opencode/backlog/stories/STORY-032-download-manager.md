---
status: "done"
sprint: "2026-SPRINT-9"
---

# STORY-032: Download Manager — Instalação Sob Demanda

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Implementar o Download Manager para baixar modelos do HuggingFace Hub sob demanda, com progress callback para feedback visual na TUI e verificação de espaço em disco antes do download.

## Regras

- **RULE-RAG-12.1:** `DownloadManager.ensure_model(model_id, progress_callback)` → baixa se não instalado.
- **RULE-RAG-12.2:** `progress_callback(bytes_downloaded, total_bytes)` para barra de progresso na TUI.
- **RULE-RAG-12.3:** Verifica espaço em disco antes de baixar. Aborta se insuficiente.
- **RULE-RAG-12.4:** Em modo MCP: download síncrono com logs. Em TUI: barra de progresso.
- **RULE-RAG-12.5:** Cache em HF_HOME, reutilização automática.

## Critérios de Aceite

- [ ] `ensure_model("paraphrase-multilingual-MiniLM-L12-v2")` detecta que já está instalado e retorna imediatamente
- [ ] `ensure_model("BAAI/bge-m3", progress_callback)` baixa o modelo e chama callback com progresso
- [ ] Download aborta com erro claro se disco insuficiente (testado com mock de disk_free_gb)
- [ ] Progress callback recebe bytes_downloaded e total_bytes em intervalos regulares
- [ ] Em modo MCP, download é síncrono sem callback (apenas logs)
- [ ] Modelo já em HF_HOME é reutilizado sem download
- [ ] Testes: download sucesso, download abortado, já instalado, disco insuficiente

## Arquivos

- `foton_system/core/rag/download_manager.py` (novo)

## Estimativa

4h

## Dependências

- STORY-030 (Hardware Profiler) — para `disk_free_gb`
- Pode ser implementado em paralelo com STORY-031
