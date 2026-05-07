# SPRINT: Desenvolvimento do Modo Sandbox (RalphLoop)

## 🎯 Objetivo
Implementar um ambiente volátil e seguro que permita aos usuários e agentes de IA explorarem as funcionalidades do Foton System sem afetar os dados reais de produção (OneDrive).

## 🛠️ Arquitetura Proposta
- **Ativação:** Via flag CLI `--sandbox` ou variável de ambiente `FOTON_SANDBOX=1`.
- **Isolamento:** Redirecionamento de todos os caminhos do `PathManager` para uma pasta temporária do SO.
- **Seeding:** Cópia automática de dados mínimos (templates de exemplo, clientes fictícios) para o ambiente temporário.
- **Feedback:** Alertas visuais na TUI e metadados no MCP/info_sistema.

## 📋 Backlog de Tarefas (RalphLoop)

### Fase 1: Fundação e TDD (Vermelho)
- [x] Criar teste unitário para `PathManager` validando redirecionamento em modo Sandbox. `test_path_manager_sandbox.py`
- [x] Criar teste de integração para o ciclo de vida do Sandbox (Início -> Redirecionamento -> Limpeza).

### Fase 2: Implementação (Verde)
- [x] Modificar `PathManager` para suportar estado global `SANDBOX_MODE`.
- [x] Implementar `SandboxService` para gerenciar a criação e limpeza do diretório temporário.
- [x] Implementar lógica de "Seeding" (Cópia de recursos básicos).

### Fase 3: Refatoração e Feedback (Azul)
- [x] Atualizar `info_sistema` para reportar o modo ativo.
- [x] Garantir que logs também sejam redirecionados no sandbox.

---

## 🚀 Progresso Atual
- [x] Base limpa (Git verificado)
- [x] Documento de Sprint criado
- [x] Fase 1: Fundação e TDD (Vermelho -> Verde)
- [x] Fase 2: SandboxService e Seeding (Implementado)
- [x] Fase 3: Refatoração e Feedback (Concluído)
- [x] Todos os 132 testes passando (Regressão zero)
