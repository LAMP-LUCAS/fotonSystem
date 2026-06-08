---
type: audit
domain: core
status: active
tags: [audit, architecture, resilience, security]
---

# Auditoria Completa — Foton System v1.2.0

**Data:** 2026-06-08
**Escopo:** Coerência, coesão, resiliência, robustez, usabilidade humana e agêntica

---

## Scorecard Geral

| Dimensão | Nota | Estado |
|---|---|---|
| **Coerência arquitetural** | 7/10 | Hexagonal consciente, mas entry points duais e ops bypassam DI |
| **Coesão dos módulos** | 7/10 | Finance impecável; Documents faz demais; ClientService tem 8 métodos mortos |
| **Resiliência** | 6/10 | 23 `except:` pelados corroem a confiança; circuit breaker sólido mas com 1 bug |
| **Robustez** | 7/10 | Graceful degradation no VectorStore, mas audit logger usa `print()` |
| **Usabilidade humana (TUI)** | 6/10 | Didática boa (tips contextuais!), mas placebos e bare excepts confundem |
| **Usabilidade agêntica (MCP)** | 7/10 | Docstrings excelentes, mas sem JSON estruturado, sem idempotência, sem paginação |
| **Vapor / Dead Code** | 5/10 | ~150 linhas de código morto ou placebo |

---

## 🔴 Críticos

### 1. `eval()` em 2 lugares — risco de segurança em sistema agêntico
- `document_service.py:380` — expressões `[calculo: ...]` viram `eval()` com regex frágil
- `form_session.py:130` — idem, no modelo do preenchedor de fichas
- **Impacto:** Um agente de IA injetando expressão maliciosa via template DOCX

### 2. Entry point `entry.py` não existe — documentação quebrada
- `DocsMcp.md:49` e `AGENTS.md` dizem `python -m foton_system.entry --mcp`
- O arquivo **nunca foi criado**

### 3. 23 `except:` pelados em produção
- `environment_porter.py:82,100,149` — capturam `KeyboardInterrupt`/`SystemExit`
- `menus.py:129,153,176,198,218,239,349,741,780` — 9 ocorrências
- `excel_client_repository.py:318,356` — máscara erros de integridade
- `op_doc_gen.py:35` — máscara `JSONDecodeError`
- `form_view.py:69`, `tui_form_filler_use_case.py:56`, `form_session.py:127,131`, `document_service.py:373`

### 4. Versão hardcoded como `1.0.0`
- `interfaces/cli/main.py:158` — `foton_system_v1.0.0.exe`
- `main.py:95` — `Version: 1.0.0`

### 5. Admin Launcher — off-by-one bug
- `admin_launcher.py:68` — `scripts[idx]` deveria ser `scripts[idx-1]`

### 6. Watcher "Desativar" é placebo
- `menus.py:796-798` — opção 2 existe, mas só printa "Desativado."

---

## 🟠 Alta Prioridade

### 7. Dois entry points competindo
- `main.py` — `safety_entry()` com detecção string-based
- `interfaces/cli/main.py` — `main()` com argparse legítimo

### 8. MCP bypassa factory em 2 tools
- `foton_mcp.py:312` — `cadastrar_cliente` importa `ClientService` diretamente
- `foton_mcp.py:422` — `criar_estrutura_servico` também

### 9. Menus sync não fazem loop
- `menus.py:384-398` e `421-435` — sem `while True`, input inválido sem retry

### 10. Domain importa infraestrutura
- `client_crud.py:10` — importa `PathManager` (infra) no domain layer
- `document_service.py:70` — idem

### 11. SyncService instancia `DocumentService(None, None)`
- `sync_service.py:25` — injeção nula de adapters

---

## 🟡 Média Prioridade

### 12. `listar_clientes` sem paginação
### 13. Tools sobrepostas: `cadastrar_cliente` vs `pipeline_novo_cliente`
### 14. Sem idempotência — retententativa cria duplicatas
### 15. Sem retorno JSON estruturado nas tools MCP
### 16. Sem validação JSON Schema do `settings.json`
### 17. `_log_tool_call` decorator vs tool body — dupla captura de ValueError
### 18. SyncService usa `INFO-CLIENTE.md` exato, resto do sistema usa glob `*INFO*.md`

---

## 🔵 Vapor / Dead Code

| Artefato | Linhas | Problema |
|---|---|---|
| `chat.py` | 32 | Explicitamente abandonado, mas ainda shipado |
| `client_service.py:93-118` | 25 | 8 métodos "backward compatibility" sem uso |
| `Config.enable_mcp` | 1 | Propriedade nunca lida |
| `EnvironmentPorter.get_form_filler()` | ~20 | Método nunca chamado |
| `TuiFormAdapter.open_form()` | 16 | Só printa "edite manualmente" |
| Watcher "Desativar" (`menus.py:796-798`) | 3 | Placebo |
| `foton_mcp.py:330` catch ValueError | 5 | Dead code (decorator já capturou) |
| `entry.py` | 0 | Referenciado em docs, nunca existiu |

---

## ✅ O Que Funciona Muito Bem

| Componente | Nota | Destaque |
|---|---|---|
| **Circuit Breaker** (vector_store.py) | 9/10 | 3 estados, configurável, graceful degradation |
| **TUI Layout** (tui_layout.py) | 9/10 | Adaptação dinâmica, emoji-aware, box-drawing limpo |
| **Environment Porter** | 9/10 | Detecção cross-platform impecável |
| **TipService** | 8/10 | Arquitetura didática — docs viram training material |
| **Ports/Adapters** (clients, finance) | 8/10 | Contratos limpos |
| **MCP Docs** (DocsMcp.md) | 8/10 | Mapping 32/32 tools, exemplos de prompt |
| **Path Traversal Security** | 9/10 | `Path(name).name` em todas as ferramentas |
| **Suite de Testes** | 7/10 | 339 testes, mocks fortes, 0% flaky |

---

## Recomendações em Ordem de Impacto

| # | Ação | Esforço | Impacto |
|---|---|---|---|
| 1 | Substituir `eval()` por parser seguro | 2h | 🔴 Segurança |
| 2 | Matar 23 bare `except:` | 1h | 🔴 Resiliência |
| 3 | Criar `entry.py` ou corrigir docs | 15min | 🔴 Documentação |
| 4 | Consertar versão hardcoded | 10min | 🔴 Precisão |
| 5 | Consertar off-by-one admin_launcher | 5min | 🔴 Bug |
| 6 | Remover ou implementar Watcher "Desativar" | 30min | 🟠 UX |
| 7 | Consolidar entry points | 2h | 🟠 Arquitetura |
| 8 | Remover dead code | 1h | 🟠 Manutenibilidade |
| 9 | Adicionar JSON Schema settings.json | 1h | 🟠 Robustez |
| 10 | Paginação + idempotência MCP | 4h | 🟠 UX Agêntica |
| 11 | Testes TipService + AuditLogger (0% hoje) | 2h | 🟡 Cobertura |

---

## Links

- Plano de ação: [[Sprint_Resiliencia/SprintPlan]]
- Sprint anterior: [[Sprint_DualInterface/SprintPlan]]
