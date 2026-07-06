---
status: "done"
sprint: "2026-SPRINT-9"
---

# STORY-034: TUI RAG Configuration

**Épico:** EPIC-004
**Spec:** `MOD-RAG/SPEC-RAG-v2.0.md`

## Descrição

Criar o menu de configuração de RAG na TUI, acessível via Configurações do Sistema (opção 7). O menu permite ao usuário visualizar o hardware detectado, escolher o modelo de embedding (MiniLM, BGE-M3, ou ambos), selecionar o tipo de pipeline (simple ou rerank), instalar modelos sob demanda com barra de progresso, e visualizar diagnóstico completo de todas as coleções ativas.

## Regras

- **RULE-RAG-7.3:** Exibir feasibility report — alertar se modelo escolhido pode travar a máquina.
- **RULE-RAG-9.4:** Exibir warnings do pipeline validator.
- **RULE-RAG-12.3:** Download com confirmação do usuário e verificação de disco.
- **RULE-RAG-12.4:** Barra de progresso em tempo real durante download.

## Critérios de Aceite

- [ ] Novo submenu "RAG / Modelo de Embedding" dentro de Configurações (opção 7)
- [ ] Exibe hardware detectado: CPU cores, RAM, GPU (se houver)
- [ ] Lista modelos disponíveis vs. instaláveis com tamanho de download
- [ ] Seleção de modo: MiniLM | BGE-M3 | Ambos (redundância)
- [ ] Ao trocar modo que exige download: confirmação + barra de progresso
- [ ] Opção "Re-indexar base para modelo ativo" com feedback de arquivos/chunks
- [ ] Exibe diagnóstico: chunks por coleção, status circuit breaker, última indexação
- [ ] Configuração persiste em settings.json (rag.embedding_mode)
- [ ] Ao trocar de modo, pergunta se deseja re-indexar agora ou depois
- [ ] Se hardware insuficiente para modo escolhido, exibe warning antes de aplicar
- [ ] Testes: navegação do menu, persistência, validação de hardware

## Arquivos

- `foton_system/interfaces/cli/menus_rag.py` (novo) — MenuConfigRagHandler
- `foton_system/interfaces/cli/menus_config.py` (extendido) — nova opção no menu settings
- `foton_system/interfaces/cli/menus.py` (extendido) — registrar novo handler em __init__
- `foton_system/modules/shared/infrastructure/config/config.py` — properties rag

## Estimativa

4h

## Dependências

- STORY-030 (Hardware Profiler) — exibir hardware detectado
- STORY-031 (VectorStoreManager) — diagnóstico multi-coleção
- STORY-032 (Download Manager) — download com progresso
- STORY-033 (Pipeline Nodes) — exibir tipo de pipeline ativo
