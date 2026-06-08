---
type: sprint
domain: core
status: draft
tags: [tui, mcp, refactor, dual-interface, documentation]
---

# SPRINT: Interface Dual (TUI + MCP)

## Objetivo

Corrigir bugs críticos da TUI, eliminar ~300 linhas de lógica duplicada entre os wrappers MCP e os domain services, documentar explicitamente os dois paradigmas de operação (humano via TUI vs agente via MCP), e adicionar suporte a `--tui` no entry point real para permitir inicialização direta da interface textual.

## Contexto

Auditoria de arquitetura (Junho/2026) revelou que o Foton System possui **três interfaces** coexistindo sobre o mesmo domain layer:

| Interface | Linhas | Público | Estado |
|-----------|--------|---------|--------|
| TUI (Textual) | 1.772 | Humanos via terminal | Ativo — 2 bugs confirmados |
| MCP (Model Context Protocol) | ~1.400 + 3 resources | Agentes de IA | Ativo — ~300 linhas duplicadas |
| WebView | 843 (HTML+JS) | Humanos via navegador | Ativo |

O **problema central** é que as interfaces MCP reimplementam lógica que já existe nos domain services (`client_service.py`, `finance_service.py`) em vez de delegar, criando risco de divergência e manutenção dobrada. Simultaneamente, a TUI tem dois bugs que a impedem de funcionar em Linux/Mac e em cenários de servidor headless.

---

## Fase 1 — Correção de Bugs da TUI (P0)

*Ação imediata — bugs confirmados que afetam a execução da interface textual.*

### 1.1 SystemProfile não importado

**Local:** `foton_system/interfaces/cli/menus.py:306`

**Problema:** `self.porter.profile == SystemProfile.SERVER_HEADLESS` referencia `SystemProfile` que nunca foi importado. O arquivo importa `get_porter` (linha 12) de `environment_porter.py`, mas `SystemProfile` (definido como `class SystemProfile(Enum)` no mesmo módulo) não está na cláusula `from`.

**Solução:** Adicionar `SystemProfile` à importação existente:
```python
from foton_system.modules.shared.infrastructure.services.environment_porter import get_porter, SystemProfile
```

**TDD:**
- [ ] Teste: `MenuSystem` com perfil `SERVER_HEADLESS` não lança `NameError`
- [ ] Teste: Importação de `SystemProfile` de `environment_porter` funciona
- [ ] Implementar correção (1 linha alterada)
- [ ] Todos os 262 testes verdes

### 1.2 `os.startfile` Windows-only

**Local:** `foton_system/interfaces/cli/menus.py:480`

**Problema:** `os.startfile(config.workspace_path)` é exclusivo do Windows. No Linux/Mac lança `AttributeError: module 'os' has no attribute 'startfile'`. O `try/except` genérico captura mas não oferece alternativa.

**Solução:** Usar `subprocess.run` com comando apropriado por plataforma:
- Windows: `os.startfile(path)` (comportamento nativo)
- Linux: `xdg-open {path}`
- Mac: `open {path}`

```python
import sys
import subprocess

if sys.platform == 'win32':
    os.startfile(path)
elif sys.platform == 'darwin':
    subprocess.run(['open', str(path)])
else:
    subprocess.run(['xdg-open', str(path)])
```

**TDD:**
- [ ] Teste: `open_folder` não lança `AttributeError` em Linux simulado
- [ ] Teste: `open_folder` não lança `AttributeError` em Mac simulado
- [ ] Teste: `open_folder` funciona no Windows real
- [ ] Implementar correção com `subprocess.run` + `sys.platform`
- [ ] Todos os 262 testes verdes

---

## Fase 2 — Eliminação de Duplicação MCP ↔ Domain (P1)

*Centralizar lógica nos domain services; MCP wrappers viram fachadas finas.*

### 2.1 MCPClientService — delegar para ClientService

**Local:** `foton_system/interfaces/mcp/mcp_services.py` (~linhas 110-280)

**Problema:** `MCPClientService` reimplementa:
- `list_clients()` — itera diretórios manualmente em vez de usar `ClientService`
- `resolve_client_path()` — réplica de `ClientService.resolve_client_path()`
- `read_client_info()` — réplica de `ClientService._read_file_content()`
- `update_client_info()` — réplica de `ClientService._write_formatted_file_content()`

**Solução:** Substituir implementações internas por delegação ao `ClientService` injetado. `MCPClientService` deve receber `ClientService` no construtor e chamar seus métodos.

**TDD:**
- [ ] Teste: `MCPClientService.list_clients()` retorna mesmo resultado que `ClientService`
- [ ] Teste: `MCPClientService.resolve_client_path()` delega corretamente
- [ ] Teste: `MCPClientService.read_client_info()` delega corretamente
- [ ] Teste: `MCPClientService.update_client_info()` delega corretamente
- [ ] Teste: Nenhuma tool MCP existente muda de comportamento
- [ ] Remover métodos duplicados de `MCPClientService` (~100 linhas)
- [ ] Todos os 262 testes verdes

### 2.2 MCPFinanceService — delegar para FinanceService

**Local:** `foton_system/interfaces/mcp/mcp_services.py` (~linhas 285-410)

**Problema:** `MCPFinanceService` reimplementa:
- `get_firm_summary()` — agrega dados financeiros manualmente em vez de usar `FinanceService.get_summary()` por cliente

**Solução:** `get_firm_summary()` deve iterar clientes via `ClientService.list_clients()` e agregar via `FinanceService.get_summary()` para cada cliente.

**TDD:**
- [ ] Teste: `MCPFinanceService.get_firm_summary()` retorna mesma estrutura que implementação atual
- [ ] Teste: Agregação usa `FinanceService.get_summary()` internamente (mock)
- [ ] Remover lógica de agregação manual (~80 linhas)
- [ ] Todos os 262 testes verdes

### 2.3 Verificar MCPDocumentService

**Local:** `foton_system/interfaces/mcp/mcp_services.py` (~linhas 413-614)

**Problema:** Possível duplicação com `DocumentService` para `list_templates()`, `validate_template()`, `generate_document()`.

**Ação:**
- [ ] Auditar `MCPDocumentService` em busca de lógica duplicada
- [ ] Se encontrada, delegar para `DocumentService` seguindo mesmo padrão
- [ ] Todos os 262 testes verdes

---

## Fase 3 — Documentação dos Dois Paradigmas (P2)

*Documentar explicitamente como humanos (TUI) e agentes (MCP) interagem com o sistema.*

### 3.1 Atualizar DocsMcp.md com seção TUI

**Local:** `docs/03_RESOURCES/DocsMcp.md`

**Ação:** Adicionar seção "Para humanos (TUI)" que explica:
- Como iniciar a TUI (`python -m foton_system.main` ou `--tui`)
- Que a TUI oferece os mesmos workflows (clientes, documentos, financeiro)
- Limitações da TUI vs MCP (sem RAG, sem watcher)

**TDD:**
- [ ] Revisar `DocsMcp.md` existente
- [ ] Adicionar seção de paradigma humano (TUI)
- [ ] Verificar links para outras documentações

### 3.2 Atualizar TuiGuide.md com seção MCP

**Local:** `docs/03_RESOURCES/TuiGuide.md`

**Ação:** Adicionar seção "Para agentes (MCP)" que explica:
- Que o mesmo sistema pode ser operado via MCP
- Como conectar (`--mcp`)
- Lista de ferramentas disponíveis (link para DocsMcp.md)

**TDD:**
- [ ] Revisar `TuiGuide.md` existente
- [ ] Adicionar seção de paradigma agente (MCP)
- [ ] Verificar links para outras documentações

### 3.3 Atualizar Concepts.md com camada MCP

**Local:** `docs/02_AREAS/Concepts.md`

**Problema:** Diagrama de arquitetura omite a camada MCP — mostra apenas TUI + WebView sobre domain.

**Solução:** Atualizar diagrama para incluir MCP como terceira interface:

```
[TUI (CLI)]  [WebView]  [MCP (Agentes)]
        \         |         /
         \        |        /
          Domain Services
          (ClientService,
           FinanceService,
           DocumentService)
                |
         Infrastructure
    (CSV, Excel, ChromaDB, etc.)
```

**TDD:**
- [ ] Atualizar diagrama em `Concepts.md`
- [ ] Adicionar nota sobre dual-paradigma

### 3.4 Arquivar QuickReference.md

**Local:** `docs/03_RESOURCES/QuickReference.md`

**Problema:** Documento é inteiramente TUI-legado — comandos e atalhos que não refletem a arquitetura atual.

**Solução:** Mover para `docs/04_ARCHIVES/QuickReference.md` com nota de arquivamento.

- [ ] Mover `QuickReference.md` para `docs/04_ARCHIVES/`
- [ ] Adicionar nota: "Arquivado — reflete TUI legado. Ver TuiGuide.md + DocsMcp.md"

---

## Fase 4 — Flag --tui no Entry Point (P2)

*Permitir inicialização direta da TUI sem passar pelo menu CLI intermediário.*

### 4.1 Adicionar --tui em safety_entry()

**Local:** `foton_system/main.py:42-80`

**Problema:** `safety_entry()` intercepta `--mcp` e `--sandbox` mas não `--tui`. A flag existe no parser secundário de `interfaces/cli/main.py` mas é inalcançável diretamente via `python -m foton_system.main`.

**Solução:** Adicionar detecção de `--tui` em `safety_entry()`, posicionada após `--sandbox` e antes de `--mcp`:

```python
# ── TUI MODE ──
if "--tui" in sys.argv:
    # Remove --tui dos args para não conflitar com argparse do CLI
    sys.argv = [a for a in sys.argv if a != "--tui"]
```

**TDD:**
- [ ] Teste: `safety_entry()` com `--tui` inicia CLI sem erro
- [ ] Teste: `--tui` é removido de `sys.argv` antes de chegar no argparse
- [ ] Teste: `safety_entry()` sem flags continua funcionando (default CLI)
- [ ] Implementar filtro de `--tui` em `safety_entry()`
- [ ] Todos os 262 testes verdes

### 4.2 Sinalizar chat.py como abandoned

**Local:** `foton_system/interfaces/cli/chat.py`

**Problema:** Arquivo de 31 linhas com `status: abandoned` e referência a `run_gen.py` que não existe. Não é chamado por nenhum código ativo.

**Solução:** Manter como está — já documentado como abandoned. Adicionar comentário no topo indicando data da desativação.

- [ ] Adicionar comentário: `# Abandoned since v1.2.0 (Jun/2026) — see main.py for entry points`

---

## Critérios de Aceitação da Sprint

- [ ] **Fase 1:** TUI funciona sem `NameError` em servidor headless; `os.startfile` substituído por `subprocess.run` multiplataforma
- [ ] **Fase 2:** `MCPClientService` e `MCPFinanceService` delegam para domain services; ~200 linhas de duplicação eliminadas; 0 mudanças de comportamento nas tools MCP
- [ ] **Fase 3:** `DocsMcp.md`, `TuiGuide.md` e `Concepts.md` atualizados com ambos os paradigmas; `QuickReference.md` arquivado
- [ ] **Fase 4:** `python -m foton_system.main --tui` funciona; `chat.py` sinalizado
- [ ] **Regressão zero:** 262 testes passando SEMPRE após cada fase

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Delegação MCP altera comportamento de tools existentes | Média | Alto | Testes de integração comparando output antes/depois |
| `sys.argv` filter quebra outro componente | Baixa | Alto | Teste unitário capturando `sys.argv` antes/depois |
| Documentação fica desatualizada rápido | Alta | Baixo | Foco em docs curtas e precisas; links diretos ao código |
| Duplicação não detectada em MCPDocumentService | Média | Médio | Auditoria completa dos ~200 lines restantes |

---

## Links Relacionados

- Guia do MCP: [[DocsMcp]]
- Guia da TUI: [[TuiGuide]]
- Arquitetura do sistema: [[Concepts]]
- Referência rápida (arquivado): [[QuickReference]]
- Protocolo para Agentes: [[LlmProtocol]]
- Plano de auditoria anterior: [[Sprint_SystemAudit/SprintPlan]]
