---
type: plan
domain: core
status: active
tags: [agentic, roadmap, future]
---
# 🚀 FOTON System: Plano de Evolução Agêntica (v2) (AgenticSprintPlan)

Este documento estabelece a arquitetura para a transição do FOTON de um sistema de gestão para um **Ecossistema Agêntico** de alta performance, operando em três níveis de profundidade.

## 🏗️ Níveis de Interação e Autonomia

| Nível | Nome | Papel da IA | Objetivo | Mecanismo |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Manual** | Inexistente | Soberania total do usuário. | Scripts POP (`core/ops`) executados manualmente. |
| **1** | **Assistido** | Operadora | Automação de tarefas. | IA executa POPs como ferramentas via MCP. |
| **2** | **Autônomo** | Orquestradora | Resolução de objetivos. | IA usa RAG e lógica própria para decidir ações. |

---

## 📅 Roadmap Detalhado: Sprint 2 - Memória Semântica (RAG)

O objetivo desta sprint é dar "consciência" ao sistema sobre os dados dispersos nas pastas de clientes.

### Passo 1: Infraestrutura de Vetores (Core Memory)

- **Ação:** Instalação do `chromadb`.
- **Implementação:** Criar `foton_system/core/memory/vector_store.py`.
- **Detalhe:** Configurar a persistência local em `%LOCALAPPDATA%/FotonSystem/memory_db`.

### Passo 2: O Pipeline de Ingestão (The Harvester)

- **Ação:** Criar um script `core/ops/op_index_knowledge.py`.
- **Funcionamento:**
    1. Varre `base_pasta_clientes` em busca de arquivos `.md`.
    2. Divide os textos em fragmentos semânticos.
    3. Gera representações matemáticas (embeddings) e salva no banco.
- **Redundância:** Pode ser disparado via CLI `python -m foton_system.core.ops.op_index_knowledge`.

### Passo 3: Ferramenta de Recuperação (Knowledge Retrieval)

- **Ação:** Criar a ferramenta `consultar_conhecimento(query)` no servidor MCP.
- **Lógica:** A IA busca no banco vetorial e recebe o contexto exato do que foi feito em projetos anteriores.

---

## 📅 Roadmap Futuro: Sprints 3 e 4

### Sprint 3: Watcher e Proatividade

- Monitoramento em tempo real de arquivos.
- Agentes que perguntam em vez de esperar ordens.

### Sprint 4: LLM Local (Ollama)

- Integração com Llama 3 para privacidade total offline.

---

## 🛡️ Diretrizes de Segurança e Resiliência

1. **Prioridade ROS:** Sempre preferir POPs (`core/ops`) para ações.
2. **Escaping de Paths:** Todas as saídas de configuração devem usar strings seguras para JSON (Escape de barras `\\`).
3. **Privacidade AEC:** Dados sensíveis de arquitetura nunca saem da máquina do usuário.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Contexto: [[LlmContext]]
- Protocolo: [[LlmProtocol]]
