---
type: plan
domain: architecture
status: active
tags: [audit, architecture, hardening, roadmap, quality]
---

# Plano Estratégico de Hardening e Evolução Arquitetural

**Data:** 2026-09-04  
**Origem:** Auditoria Profunda do Foton System (v1.4.0 / v1.4.1)  
**Objetivo:** Estruturar a remediação das debilidades identificadas no Radar Dimensional em 3 momentos bem definidos, separando claramente a higiene tática, o saneamento arquitetural e a evolução funcional de novos épicos.

---

## Estrutura dos 3 Momentos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MOMENTO 1: HIGIENE IMEDIATA                                                │
│ • Restauração de settings.json (eliminar contaminação de caminhos temporários)│
│ • Sincronização do AGENTS.md (catalogar as 47 MCP tools e 1.061 testes)      │
│ • Remoção de artefatos residuais de debug na raiz (_debug_bisect.py, etc.)  │
│ • Validação de zero regressão com a suite completa de testes                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MOMENTO 2: SPRINT DE HARDENING & DESACOPLAMENTO (Pré-EPIC-006)              │
│ • Quebra dos 5 ciclos de importação entre módulos                           │
│ • Inversão de dependência: desacoplar tui_form_filler_use_case via Port     │
│ • Expurgar código morto em sync_service.py e consolidar em pipeline_sync.py │
│ • Fatiar o God File foton_mcp.py (1.846 linhas) em sub-roteadores modulares │
│ • Desacoplar client_crud.py (1.023 linhas), isolando geradores e templates   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ MOMENTO 3: EXECUÇÃO DOS MARCOS ESTRATÉGICOS DE PRODUTO                      │
│ 1. Conclusão da Sprint 9 (RAG v2.0: benchmarks e testes de integração E2E)   │
│ 2. Desenvolvimento do EPIC-006 (Inteligência Financeira v2.0 com lucrativ.) │
│ 3. Implementação do EPIC-013 (Interface Modal TUI Vim+tmux)                 │
│ 4. Transição de baseDados.xlsx para SQLite como SSOT relacional transacional│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detalhamento das Ações

### Momento 1: Higiene Imediata
- **Arquivo `settings.json`:** Restaurar os caminhos reais de produção do escritório (`CLIENTES`, `BASE/Modelos de Documentos`, `%LOCALAPPDATA%/FotonSystem/baseDados.xlsx`), eliminando a poluição de diretórios temporários gerados por testes.
- **Governança `AGENTS.md`:** Atualizar a contagem e a catalogação das 47 ferramentas MCP expostas em [foton_mcp.py](file:///c:/Users/Lucas/OneDrive/LAMP_ARQUITETURA/fotonSystem/foton_system/interfaces/mcp/foton_mcp.py), formalizando as 6 ferramentas ausentes na documentação (`remover_cliente`, `restaurar_cliente`, `remover_servico`, `restaurar_servico`, `atualizar_servico`, `pipeline_sincronizacao`). Atualizar a contagem da suite para 1.061 testes.
- **Higiene do Repositório:** Excluir do versionamento e do disco scripts efêmeros de depuração (`_debug_bisect.py`, `check_paths.py`, `test_tk.py`, `validate_foton_ai.py`, `grep_jsonschema.txt`, `stderr.txt`, `test_*.txt`).
- **Validação:** Executar a suite de testes garantindo integridade absoluta do ambiente.

### Momento 2: Sprint de Hardening & Desacoplamento (Sprint Técnica)
*Executada antes de iniciar o desenvolvimento das features do EPIC-006 (Financeiro v2.0).*
- **Ciclos de Dependência:**
  - `core.memory ↔ core.rag`: Mover tipos e contratos compartilhados para `core/rag/domain` ou desacoplar via injeção.
  - `core.ops ↔ modules.documents`: Desacoplar `op_doc_gen.py` de `document_service.py` via porta de serviço.
  - `interfaces.cli ↔ modules.documents`: Eliminar a importação direta de `TUIFormView` dentro de `tui_form_filler_use_case.py`, aplicando a interface [FormInterfacePort](file:///c:/Users/Lucas/OneDrive/LAMP_ARQUITETURA/fotonSystem/foton_system/modules/shared/application/ports/form_interface_port.py).
  - `interfaces.cli ↔ scripts` e `modules.documents ↔ modules.shared`: Reorganizar pontos de entrada utilitários.
- **Decomposição Modular de `foton_mcp.py`:** Dividir o arquivo de 1.846 linhas em sub-módulos coesos por domínio:
  - `interfaces/mcp/routers/clients_router.py`
  - `interfaces/mcp/routers/documents_router.py`
  - `interfaces/mcp/routers/finance_router.py`
  - `interfaces/mcp/routers/rag_router.py`
  - `interfaces/mcp/routers/system_router.py`
  Mantendo `foton_mcp.py` como um agregador de rotas de <200 linhas.
- **Eliminação de Código Morto:** Deletar `modules/sync/sync_service.py` e consolidar todas as referências no pipeline moderno [pipeline_sync.py](file:///c:/Users/Lucas/OneDrive/LAMP_ARQUITETURA/fotonSystem/foton_system/modules/clients/application/use_cases/pipeline_sync.py).

### Momento 3: Execução dos Marcos Estratégicos
- **Passo 1 (Sprint 9 — RAG v2.0):** Fechar as 6 stories pendentes (STORY-036 a 041), com testes E2E, benchmarks e telemetria de queries.
- **Passo 2 (EPIC-006 — Financeiro v2.0):** Implementar as 17 regras da [SPEC-FINANCEIRO-v2.0.md](file:///c:/Users/Lucas/OneDrive/LAMP_ARQUITETURA/fotonSystem/specs/MOD-FINANCEIRO/SPEC-FINANCEIRO-v2.0.md) (lucratividade por serviço, projeção de caixa, alertas de estouro e conciliação).
- **Passo 3 (EPIC-013 — TUI Modal):** Implementar o paradigma Vim+tmux sobre os menus estabilizados na Fase 0.
- **Passo 4 (Migração para SQLite):** Migrar a persistência relacional do Excel para SQLite local, eliminando locks concorrentes e garantindo integridade ACID.
