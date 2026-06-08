---
type: sprint
domain: core
status: draft
tags: [resilience, security, refactor, vapor, documentation]
---

# SPRINT: Resiliência e Robustez (Fase 1)

## Objetivo

Eliminar 23 bare `except:` blocks, substituir `eval()` por parser seguro, remover ~150 linhas de código morto/vapor, corrigir bugs de entrada de usuário, e consolidar entry points duais.

---

## Contexto

Auditoria completa (2026-06-08) — ver [[AuditoriaJun2026]]

| Problema | Gravidade | Ocorrências |
|---|---|---|
| `eval()` sem sandbox em produção | 🔴 Segurança | 2 (document_service.py, form_session.py) |
| Bare `except:` blocks | 🔴 Resiliência | 23 em 10 arquivos |
| Entry point `entry.py` não existe | 🔴 Docs | 1 (DocsMcp.md + AGENTS.md) |
| Versão hardcoded `1.0.0` | 🔴 Precisão | 2 (main.py, cli/main.py) |
| Admin launcher off-by-one | 🔴 Bug | 1 (admin_launcher.py:68) |
| Watcher "Desativar" placebo | 🟠 UX | 1 (menus.py:796-798) |
| Vapor / dead code | 🟠 Manutenção | ~150 linhas em 6 arquivos |
| MCP bypassa factory | 🟠 Arquitetura | 2 tools (foton_mcp.py:312,422) |
| SyncService null DI | 🟠 Robustez | 1 (sync_service.py:25) |
| Domain importa infra | 🟠 Coesão | 2 (client_crud.py, document_service.py) |
| 2 entry points competindo | 🟠 Arquitetura | main.py vs interfaces/cli/main.py |
| Sem JSON Schema no settings.json | 🟠 Robustez | 1 (config.py) |
| Circuit breaker `_last_failure_time` não reseta | 🟡 Precisão | 1 (vector_store.py:75) |

---

## Fase 1 — Segurança: `eval()` → Parser Seguro (P0)

*Substituir `eval()` por expressões aritméticas seguras sem risco de injeção.*

### 1.1 Criar `safe_math.py` — parser aritmético à la shunting-yard

**Local:** `foton_system/modules/shared/domain/services/safe_math.py` (novo)

**Solução:** Implementar avaliador aritmético com:
- Parser shunting-yard (operadores: `+`, `-`, `*`, `/`, `(`, `)`, `.`)
- Sem acesso a `__builtins__`, sem `__import__`, sem strings
- Suporte a números decimais (`,` → `.` para padrão BR)
- Suporte a `%` (percentual: `100%` → `1.0`)
- Limite de profundidade de expressão (ex: 50 tokens)
- Erro claro para expressões inválidas

```python
# API de exemplo
def safe_eval(expression: str) -> float:
    """Avalia expressão aritmética segura. raises ValueError se inválida."""
```

**TDD:**
- [ ] Teste: `safe_eval("2 + 3")` → `5.0`
- [ ] Teste: `safe_eval("(10 + 20) * 3")` → `90.0`
- [ ] Teste: `safe_eval("__import__('os')")` → `ValueError`
- [ ] Teste: `safe_eval("10 / 0")` → trata divisão por zero (retorna 0 ou raise)
- [ ] Teste: `safe_eval("10% + 20%")` → `0.3` (percentuais)
- [ ] Teste: `safe_eval("")` → `0.0`
- [ ] Teste: `safe_eval("1 + 'string'")` → `ValueError`
- [ ] Implementar `safe_math.py`
- [ ] Todos os 264+ testes verdes

### 1.2 Substituir `eval()` em `document_service.py`

**Local:** `document_service.py:375-381`

**Ação:** Trocar `eval(expression)` por `safe_eval(expression)`.

- [ ] Teste: DocumentService com `[calculo: 2+3]` retorna `5.00`
- [ ] Teste: DocumentService com `[calculo: __import__('os')]` retorna `---` (placeholder)
- [ ] Implementar substituição
- [ ] Todos os 264+ testes verdes

### 1.3 Substituir `eval()` em `form_session.py`

**Local:** `form_session.py:130`

**Ação:** Trocar `eval(safe_expr, {"__builtins__": {}}, {})` por `safe_eval(safe_expr)`.

- [ ] Teste: `FormSession._evaluate("2+3", {})` → `5.0`
- [ ] Teste: `FormSession._evaluate("@total * 0.1", {"total": "1000"})` → `100.0`
- [ ] Implementar substituição
- [ ] Todos os 264+ testes verdes

---

## Fase 2 — Resiliência: Eliminar Bare `except:` Blocks (P0)

*23 blocos `except:` sem tipo especificado devem virar `except SpecificError:` com logging.*

### 2.1 `environment_porter.py` — 3 bare excepts

**Local:** `environment_porter.py:82,100,149`

**Solução:** Substituir `except:` por `except (IOError, OSError):` nas 3 ocorrências.

- [ ] Teste: Docker detection não lança exceção em Windows (monkeypatch)
- [ ] Teste: WSL detection não lança exceção em ambiente não-WSL
- [ ] Substituir bare excepts
- [ ] Todos os 264+ testes verdes

### 2.2 `menus.py` — 9 bare excepts (display_*_menu tips)

**Local:** `menus.py:129,153,176,198,218,239,349,741,780`

**Solução:** Substituir por `except Exception:` com `logger.warning()`. Cada menu continua funcionando sem tips.

- [ ] Teste: Menu exibe sem tips quando TipService lança exceção
- [ ] Substituir 9 bare excepts por `except Exception: logger.warning(...)`
- [ ] Todos os 264+ testes verdes

### 2.3 `excel_client_repository.py` — 2 bare excepts

**Local:** `excel_client_repository.py:318,356`

**Solução:** Substituir por `except (PermissionError, OSError, ValueError): logger.error(...)`.

- [ ] Teste: Erro de permissão no save loga e relança
- [ ] Substituir 2 bare excepts
- [ ] Todos os 264+ testes verdes

### 2.4 Demais bare excepts (6 ocorrências)

| Arquivo | Linha | Solução |
|---|---|---|
| `op_doc_gen.py` | 35 | `except (json.JSONDecodeError, TypeError):` |
| `form_view.py` | 69 | `except Exception: logger.warning(...)` |
| `tui_form_filler_use_case.py` | 56 | `except (IOError, OSError): logger.warning(...)` |
| `form_session.py` | 127, 131 | `except (ValueError, TypeError):` — já é float coercion |
| `document_service.py` | 373 | `except (ValueError, TypeError): logger.warning(...)` |

- [ ] Substituir 6 bare excepts com tipos específicos
- [ ] Todos os 264+ testes verdes

---

## Fase 3 — Bugs e Placebos (P0)

### 3.1 Versão hardcoded `1.0.0` → `__version__`

**Local:** `interfaces/cli/main.py:158`, `main.py:95`

**Solução:** Importar `__version__` de `foton_system/__init__.py` e usar dinamicamente.

- [ ] Teste: `main.py` fatal error mostra versão real `1.2.0`
- [ ] Teste: `cli/main.py` gera caminho com versão real
- [ ] Implementar `from foton_system import __version__` em ambos
- [ ] Todos os 264+ testes verdes

### 3.2 Admin launcher off-by-one

**Local:** `admin_launcher.py:63-68`

**Solução:** Mudar para `if 1 <= idx <= len(scripts): selected = scripts[idx - 1]`.

- [ ] Teste: Selecionar primeiro script funciona
- [ ] Teste: Selecionar último script funciona
- [ ] Teste: Input zero retorna
- [ ] Teste: Input fora do range mostra erro
- [ ] Implementar correção
- [ ] Todos os 264+ testes verdes

### 3.3 Watcher "Desativar" — implementar stop real

**Local:** `menus.py:796-798`

**Solução:** Armazenar `watcher` como `self._watcher` e implementar stop.

- [ ] Teste: Ativar watcher, desativar watcher — `watcher.stop()` é chamado
- [ ] Teste: Desativar sem watcher ativo mostra warning (não erro)
- [ ] Implementar correção
- [ ] Todos os 264+ testes verdes

### 3.4 Circuit breaker: resetar `_last_failure_time` no CLOSED

**Local:** `vector_store.py:75`

**Solução:** Adicionar `self._last_failure_time = 0.0` na transição CLOSED.

- [ ] Teste: Após probe bem-sucedido, `_last_failure_time` é 0
- [ ] Teste: Próxima falha após recovery funciona corretamente
- [ ] Implementar 1 linha
- [ ] Todos os 264+ testes verdes

---

## Fase 4 — Vapor / Dead Code (P1)

### 4.1 Arquivar `chat.py`

**Local:** `foton_system/interfaces/cli/chat.py`

**Ação:** Mover para `docs/04_ARCHIVES/chat.py` com nota de arquivamento.

- [ ] Mover para `scripts/archive/chat.py` ou `docs/04_ARCHIVES/`
- [ ] Verificar que nenhum import referencia `chat.py`
- [ ] Testes continuam passando

### 4.2 Remover backward-compat methods mortos

**Local:** `client_service.py:93-118`

**Ação:** Verificar com grep se algum caller usa esses métodos. Se não, remover.

- [ ] Grep para cada método — confirmar zero callers
- [ ] Remover 8 métodos
- [ ] Todos os 264+ testes verdes

### 4.3 Remover dead config `enable_mcp`

**Local:** `bootstrap_service.py:96`, `settings.json`

**Ação:** Remover a chave do bootstrap e do settings.json.

- [ ] Remover `enable_mcp` do bootstrap defaults
- [ ] Remover do settings.json (se presente)
- [ ] Testes continuam passando

### 4.4 Remover `EnvironmentPorter.get_form_filler()` se não usado

**Local:** `environment_porter.py:187-205`

**Ação:** Verificar callers. Se órfão, remover junto com adapters não referenciados.

- [ ] Grep para `get_form_filler` — confirmar zero callers
- [ ] Grep para adapters de form — remover se órfãos
- [ ] Remover métodos e adapters órfãos
- [ ] Todos os 264+ testes verdes

### 4.5 Remover catch ValueError morto em tools MCP

**Local:** `foton_mcp.py` (corpo de tools com `except ValueError`)

**Problema:** O decorator `_log_tool_call` já captura `ValueError` e retorna antes.

- [ ] Identificar todas as tools com `except ValueError` no corpo
- [ ] Remover dead except blocks
- [ ] Todos os 264+ testes verdes

---

## Fase 5 — Arquitetura e Coesão (P1)

### 5.1 Criar `entry.py` ou corrigir docs

**Problema:** `DocsMcp.md:48` e `AGENTS.md` documentam `python -m foton_system.entry --mcp`.

**Opção A (recomendada):** Criar `foton_system/entry.py`:
```python
from foton_system.main import safety_entry

if __name__ == "__main__":
    safety_entry()
```

**Opção B:** Corrigir documentação.

- [ ] Criar `entry.py` OU corrigir DocsMcp.md + AGENTS.md
- [ ] Teste: `python -m foton_system.entry --mcp` funciona (via subprocess mock)
- [ ] Teste: `python -m foton_system.entry --tui` funciona

### 5.2 Consolidar entry points

**Solução:** `cli/main.py` delega para `main.py:safety_entry()` nos modos MCP e TUI.

- [ ] Teste: `cli/main.py --mcp` inicia MCP server
- [ ] Teste: `cli/main.py --tui` redireciona para safety_entry
- [ ] Teste: `cli/main.py --info` funciona como antes
- [ ] Implementar delegação
- [ ] Todos os 264+ testes verdes

### 5.3 MCP tools: usar factory em vez de import direto

**Local:** `foton_mcp.py:312` (cadastrar_cliente), `foton_mcp.py:422` (criar_estrutura_servico)

**Solução:** Substituir import direto por `_get_factory().get_client_service()`.

- [ ] Teste: tools usam a mesma instância de ClientService
- [ ] Implementar
- [ ] Todos os 264+ testes verdes

### 5.4 SyncService: corrigir `DocumentService(None, None)`

**Local:** `sync_service.py:25`

**Solução:** Aceitar `DocumentService` como dependência injetada ou criar método de classe.

- [ ] Teste: SyncService aceita DocumentService injetado
- [ ] Teste: SyncService funciona sem (herdado)
- [ ] Implementar
- [ ] Todos os 264+ testes verdes

### 5.5 Domain não importa infraestrutura

**Local:** `client_crud.py:10`, `document_service.py:70`

**Solução:** Passar `info_template_path: str` como parâmetro, não resolver via `PathManager`.

- [ ] Teste: funções recebem path como parâmetro
- [ ] Remover `import PathManager` do domain
- [ ] Atualizar callers
- [ ] Todos os 264+ testes verdes

---

## Fase 6 — Robustez e UX (P2)

### 6.1 JSON Schema para `settings.json`

**Local:** `config.py` (após `_load_settings`)

- [ ] Teste: settings.json com `ignored_folders: "string"` → usa default
- [ ] Teste: settings.json com `caminho_pastaClientes: 123` → usa default
- [ ] Teste: settings.json válido → carrega normalmente
- [ ] Implementar validação
- [ ] Todos os 264+ testes verdes

### 6.2 Menus sync com loop

**Local:** `menus.py:384-398, 421-435`

- [ ] Teste: Input inválido no sync menu → mostra erro e pede de novo
- [ ] Teste: Input '0' → retorna
- [ ] Implementar `while True`
- [ ] Todos os 264+ testes verdes

### 6.3 `--reset-config` recria config imediatamente

**Local:** `interfaces/cli/main.py:227-233`

- [ ] Teste: `--reset-config` → settings.json existe com defaults
- [ ] Implementar
- [ ] Todos os 264+ testes verdes

### 6.4 `webview_bridge.py`: corrigir `PathManager.get_app_dir()`

**Local:** `webview_bridge.py:57,85`

- [ ] Teste: webview_bridge encontra HTML path sem AttributeError
- [ ] Implementar
- [ ] Todos os 264+ testes verdes

---

## Fase 7 — Qualidade Agêntica (P2)

### 7.1 Criar `views/__init__.py`

**Local:** `foton_system/interfaces/cli/views/`

- [ ] Criar `views/__init__.py` vazio
- [ ] Testes continuam passando

### 7.2 Paginação em `listar_clientes`

**Local:** `foton_mcp.py` (tool `listar_clientes`)

- [ ] Teste: `listar_clientes(limite=2)` retorna máximo 2
- [ ] Implementar `clients[:limite]`
- [ ] Todos os 264+ testes verdes

### 7.3 Idempotência em `pipeline_novo_cliente`

**Local:** `pipeline_novo_cliente` tool

- [ ] Teste: Criar cliente com NIF existente → erro
- [ ] Teste: Criar cliente com nome existente → erro
- [ ] Implementar verificação extra
- [ ] Todos os 264+ testes verdes

---

## Fase 8 — Cobertura de Testes (P2)

### 8.1 Testes para TipService (0% hoje)

**Local:** `tests/unit/test_tip_service.py` (novo)

- [ ] `get_tip(context)` retorna string quando há tips
- [ ] `get_tip(context)` retorna string vazia quando contexto não existe
- [ ] `get_tip(context)` não lança exceção quando docs_dir não existe
- [ ] Indexação de tips de arquivos .md com `[!DIDACTIC:CONTEXT]`
- [ ] Indexação ignora arquivos não .md

### 8.2 Testes para AuditLogger (0% hoje)

**Local:** `tests/unit/test_audit_logger.py` (novo)

- [ ] `log_event` escreve linha JSONL
- [ ] `get_events` retorna lista de eventos
- [ ] AuditLogger não lança exceção em caso de permissão negada
- [ ] Log rotate funciona

---

## Critérios de Aceitação

- [x] **Fase 1:** `eval()` substituído por `safe_eval()` em document_service.py e form_session.py
- [x] **Fase 2:** Zero bare `except:` na produção (23 eliminados)
- [x] **Fase 3:** Versão dinâmica, admin launcher corrigido, watcher funcional, circuit breaker correto
- [x] **Fase 4:** Vapor removido (~70 linhas); chat.py arquivado; dead config/methods removidos
- [x] **Fase 5:** Entry points consolidados; MCP usa factory; SyncService usa DI; domain sem infra
- [x] **Fase 6:** JSON Schema no config; sync menus com loop; `--reset-config` funcional
- [x] **Fase 7:** `__init__.py` criado; paginação no listar_clientes; idempotência reforçada
- [x] **Fase 8:** TipService e AuditLogger com cobertura de testes
- [x] **Regressão zero:** 302 testes passando (293 → 302 baseline)

---

## Cronograma Estimado

| Fase | Descrição | Esforço | Depende de |
|------|-----------|---------|------------|
| 1 | `safe_eval()` + substituições | 4h | Nenhuma |
| 2 | 23 bare excepts | 2h | Nenhuma |
| 3 | Bugs e placebos | 2h | Nenhuma |
| 4 | Vapor removal | 2h | Nenhuma |
| 5 | Arquitetura | 4h | Fase 4 (limpeza) |
| 6 | Robustez | 2h | Nenhuma |
| 7 | Qualidade agêntica | 2h | Nenhuma |
| 8 | Testes | 3h | Fase 1, 2 (código novo) |
| **Total** | | **~21h** | |

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| `safe_eval()` não cobre edge case de expressão real | Média | Alto | Testes com exemplos reais de templates DOCX existentes |
| Remover método "backward compat" quebra caller não detectada | Baixa | Alto | Grep completo + testes de integração antes de remover |
| Consolidar entry points quebra fluxo de inicialização | Média | Alto | Testes de subprocess simulando `--mcp`, `--tui`, `--sandbox` |
| `PathManager.get_app_dir()` não tem equivalente direto | Média | Médio | Verificar métodos existentes em PathManager antes de codificar |

---

## Links Relacionados

- Sprint anterior: [[Sprint_DualInterface/SprintPlan]]
- Auditoria original: [[AuditoriaJun2026]]
- Guia do MCP: [[DocsMcp]]
- Guia da TUI: [[TuiGuide]]
