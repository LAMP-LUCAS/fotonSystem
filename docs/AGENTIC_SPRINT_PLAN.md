# 🚀 FOTON System: Plano de Evolução Agêntica (v2)

<<<<<<< HEAD
Este documento estabelece a arquitetura para a transição do FOTON de um sistema de gestão para um **Ecossistema Agêntico** de alta performance, operando em três níveis de profundidade e mantendo a soberania do usuário.

## 🏗️ Níveis de Interação e Autonomia

O sistema é desenhado para operar em camadas. O Agente é livre para agir, mas sempre enraizado em procedimentos seguros.

| Nível | Nome | Papel da IA | Objetivo | Mecanismo |
| :--- | :--- | :--- | :--- | :--- |
| **0** | **Manual** | Inexistente | Soberania total do usuário. | O usuário executa scripts POP (`core/ops`) e gerencia os arquivos diretamente. |
| **1** | **Assistido** | Operadora | Automação de tarefas repetitivas. | A IA recebe ordens diretas e executa os scripts POP como "ferramentas" predefinidas. |
| **2** | **Autônomo** | Orquestradora | Resolução de objetivos complexos. | A IA entende o objetivo, consulta a memória e decide a melhor ação (usando ou não POPs). |

---

## 📅 Roadmap de Desenvolvimento (Sprint Agentic v2)

### A. Memória Semântica Local (RAG Local)

* **Tecnologia:** ChromaDB.
* **Função:** Criar um "Cérebro de Memória" que indexa arquivos `.md`, planilhas Excel e histórico de decisões.
* **Resultado:** Antes de qualquer ação, a IA pesquisa no histórico para entender o "tom", os "preços" e as "preferências" do escritório.

### B. Orquestração Multi-Agente

Dividiremos o sistema em agentes especialistas que colaboram entre si:

* **Agente de Vendas:** Foca em prospectar dados e gerar PPTX de propostas de alto impacto.
* **Agente Financeiro:** Monitora CSVs e avisa proativamente: *"Detectado atraso no Cliente X. Deseja preparar o e-mail de cobrança?"*
* **Agente de Organização:** O "Guardião" do manifesto. Garante que arquivos estejam nas pastas corretas (STR, HID, ELE, etc).

### C. Watcher Ativo (Proatividade)

* **Mecanismo:** Script em Python que monitora eventos do sistema de arquivos.
* **Exemplo:** Você salva um arquivo `projeto_v2.dwg` na pasta `ARQ`. O Agente detecta, valida o nome e pergunta: *"Notei uma nova versão. Devo atualizar o cronograma de entregas e notificar o cliente?"*

### D. LLM Local (Privacidade Nível AEC)

* **Integração:** Ollama (Llama 3 / Mistral).
* **Benefício:** Privacidade radical. Projetos e dados financeiros nunca saem da rede do escritório.

---

## 🛡️ Diretrizes do "Autonomous Orchestrator"

Embora o Agente no **Nível 2** tenha liberdade para "pensar" e atender o objetivo do usuário de forma criativa:

1. **Prioridade ROS:** Sempre que uma tarefa possa ser resolvida por um POP (`core/ops`), o Agente deve preferir este caminho para garantir padronização.
2. **Degradação Graciosa:** Se a lógica agêntica falhar, o sistema reverte para ferramentas simples (Nível 1). Se o MCP falhar, o usuário assume o controle total via scripts (Nível 0).
3. **Hibridismo:** O usuário pode intervir a qualquer momento. Se o Agente começar a organizar pastas, o usuário pode assumir a operação manualmente sem causar conflitos no banco de dados.

---

**Próximo Passo:** Implementação do diretório `foton_system/core/ops/` para consolidar o **Nível 1** e servir de fundação para o **Nível 2**.
=======
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
>>>>>>> bd7b97aaa2f383cac97855c4cb7eca8ddf31252a
