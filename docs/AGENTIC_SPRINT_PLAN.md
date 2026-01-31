# 🚀 FOTON System: Plano de Evolução Agêntica (v2)

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
