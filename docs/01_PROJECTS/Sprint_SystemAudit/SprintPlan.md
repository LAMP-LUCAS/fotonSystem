---
type: sprint
domain: core
status: active
tags: [audit, security, refactor, architecture, documentation]
---

# SPRINT: Auditoria Geral e Eliminação de Gaps

## Objetivo

Corrigir todos os gaps identificados na auditoria geral do Foton System v1.2.0, elevando o sistema para um patamar de maturidade onde segurança, coesão, resiliência, robustez e documentação estejam totalmente alinhados — sem passivos técnicos nem riscos de regressão.

## Contexto

Auditoria completa (Junho/2026) revelou nota **4.0/5.0** com gaps distribuídos em 8 eixos:

| Eixo | Nota | Principal Gap |
|------|------|---------------|
| Coesão | ⭐⭐⭐⭐⭐ | `client_service.py` (648 linhas) viola SRP |
| Coerência | ⭐⭐⭐⭐ | `modules/finance/` sem `__init__.py` |
| Segurança | ⭐⭐⭐ | Path traversal em `validar_template`, temp files acumulados |
| Documentação | ⭐⭐⭐⭐⭐ | `DocsMcp.md` desatualizado, sem CHANGELOG |
| Resiliência | ⭐⭐⭐⭐ | Sem log rotation, sem circuit breaker ChromaDB |
| Robustez | ⭐⭐⭐⭐ | Sem max length validation, sem schema para `dados_extras` |
| MCP Server | ⭐⭐⭐⭐ | 35 `except Exception` genéricos, sem request correlation ID |
| Skills/Agentes | ⭐⭐⭐⭐ | SKILL.md sem RAG/Watcher, sem `.opencode/` |

Documento de auditoria completo: `docs/04_ARCHIVES/DocumentationAudit.md`

---

## Fase 1 — Segurança (P0)

*Ação imediata — risco de path traversal e acúmulo de arquivos temporários.*

### 1.1 Fix path traversal em `validar_template`

**Local:** `foton_system/interfaces/mcp/foton_mcp.py:599`

**Problema:** `template_path = config.templates_path / nome_template` — se `nome_template` contiver `../`, o path escapa do diretório de templates, permitindo leitura de arquivos arbitrários.

**Solução:** Usar `Path(nome_template).name` para extrair apenas o nome base, ou validar que o path resolvido está contido em `config.templates_path` via `template_path.resolve().relative_to(config.templates_path.resolve())`.

**TDD:**
- [ ] Teste: `validar_template` com `nome_template="../../etc/passwd"` retorna erro de validação
- [ ] Teste: `validar_template` com `nome_template="template_valido.docx"` funciona normalmente
- [ ] Implementar sanitização com `Path(nome_template).name`
- [ ] Todos os 237 + novos testes verdes

### 1.2 Limpeza de arquivos temporários RAG

**Local:** `foton_system/interfaces/mcp/foton_mcp.py:705-740`

**Problema:** `_rag_run.py` e `_rag_error.txt` são escritos em `PathManager.get_app_data_dir() / "tmp"` e nunca removidos — acúmulo de lixo e potencial superfície de ataque.

**Solução:** Envolver escrita/leitura/exclusão em `try/finally` com `Path.unlink(missing_ok=True)`. Alternativamente, usar `tempfile.NamedTemporaryFile` com `delete=True`.

**TDD:**
- [ ] Teste: após executar `consultar_conhecimento`, verificar que `_rag_run.py` não existe mais
- [ ] Teste: após erro, `_rag_error.txt` existe (para debug) mas `_rag_run.py` foi limpo
- [ ] Implementar limpeza com `try/finally`
- [ ] Todos os testes verdes

### 1.3 Narrow `except Exception`

**Local:** `foton_system/interfaces/mcp/foton_mcp.py` (35 ocorrências) e `mcp_services.py` (7)

**Problema:** `except Exception` captura `KeyboardInterrupt` e `SystemExit`, impedindo shutdown gracioso do MCP. Também esconde erros inesperados que deveriam propagar.

**Solução:** Mapear cada tool e substituir `except Exception` por exceções específicas:
- `ValueError` para validação de entrada
- `FileNotFoundError`/`OSError` para operações de I/O
- `PermissionError` para arquivos/projetos travados
- Manter `except Exception` APENAS no wrapper mais externo de cada tool

**TDD:**
- [ ] Teste: cada tool com input inválido levanta `ValueError` (não `Exception`)
- [ ] Teste: cada tool com I/O failure levanta `OSError`
- [x] Refatorar todas as cláusulas `except` em `foton_mcp.py` e `mcp_services.py`
- [x] Todos os testes verdes (238/239 — 1 pre-existing, unrelated)

### 1.4 Schema validation para `dados_extras`

**Local:** `foton_system/interfaces/mcp/foton_mcp.py` (tools `gerar_documento`, `pipeline_emitir_documento`)

**Problema:** `dados_extras: dict = {}` aceita qualquer dict sem validação de schema — valores aninhados, tipos inválidos, cardinalidade excessiva.

**Solução:** Validar que:
- `dados_extras` é plano (sem dicts/listas aninhadas)
- Todas as chaves são strings (max 50 keys)
- Todos os valores são `str`, `int`, ou `float`
- Rejeitar com `ValueError` + mensagem descritiva

**TDD:**
- [ ] Teste: `dados_extras` com dict aninhado rejeitado
- [ ] Teste: `dados_extras` com 51+ chaves rejeitado
- [ ] Teste: `dados_extras` válido processado normalmente
- [x] Implementar `_validate_dados_extras()` como helper
- [x] Todos os testes verdes (238/239 — 1 pre-existing, unrelated)

---

## Fase 2 — Arquitetura e Coesão (P1)

*Refinamento estrutural para escalabilidade e manutenibilidade.*

### 2.1 Fatorar `client_service.py`

**Local:** `foton_system/modules/clients/application/use_cases/client_service.py` (648 linhas)

**Problema:** Único arquivo contém validação, normalização, CRUD e busca — viola SRP. Dificulta testes e manutenção.

**Solução:** Quebrar em 3 arquivos no mesmo diretório:
- `client_validation.py` — `normalize_client_name()` + validações de input
- `client_crud.py` — `create_client()` + `update_client()` + `delete_client()`
- `client_query.py` — `find_client()` + `list_service_nodes()` + `resolve_client_path()` + busca fuzzy
- `client_service.py` vira fachada que importa e delega

**TDD:**
- [x] Extrair métodos sem alterar assinatura
- [x] Testes existentes continuam passando (refatoração segura)
- [x] Import paths preservados — facade mantém compatibilidade total
- [x] Todos os 239 testes verdes

### 2.2 Adicionar `__init__.py` nos módulos faltantes

**Local:**
- `foton_system/modules/finance/` — sem `__init__.py` (não é pacote Python válido)
- `foton_system/modules/documents/infrastructure/adapters/` — sem `__init__.py`

**Solução:** Criar `__init__.py` com imports públicos:

```python
# modules/finance/__init__.py
from .application.use_cases.finance_service import FinanceService
from .application.ports.finance_repository_port import FinanceRepositoryPort
from .infrastructure.repositories.csv_finance_repository import CSVFinanceRepository

__all__ = ["FinanceService", "FinanceRepositoryPort", "CSVFinanceRepository"]
```

**TDD:**
- [ ] Teste: `from foton_system.modules.finance import FinanceService` funciona
- [x] `__init__.py` criado em `modules/finance/` + 5 subdiretórios
- [x] Todos os 239 testes verdes

### 2.3 Unificar diretórios de scripts

**Local:** `scripts/migrate_client_structure.py` (raiz) vs `foton_system/scripts/` (13 scripts)

**Problema:** Script de migração está solto na raiz enquanto todos os outros scripts estão dentro do pacote.

**Solução:**
- Mover `scripts/migrate_client_structure.py` → `foton_system/scripts/migrate_client_structure.py`
- Atualizar imports internos se houver
- Criar atalho opcional na raiz (`.bat` ou symlink) para não quebrar workflows manuais

**TDD:**
- [x] `python -m foton_system.scripts.migrate_client_structure` funciona
- [x] Old path `scripts/migrate_client_structure.py` mantido com `.bat` wrapper
- [x] Caminho `parents[1]` atualizado para `parents[2]`
- [x] Todos os 239 testes verdes

---

## Fase 3 — Resiliência e Robustez (P2)

*Garantir que o sistema se recupera de falhas graciosamente e resiste a inputs maliciosos ou inesperados.*

### 3.1 Max length validation

**Local:** `foton_system/interfaces/mcp/foton_mcp.py` (todas as 32 tools com parâmetros string)

**Problema:** Nomes de cliente, queries RAG, descrições financeiras, etc. podem ser arbitrariamente longos, causando estouro de buffer em logs, paths do Windows (MAX_PATH=260), ou lentidão no ChromaDB.

**Solução:** Adicionar decorator ou helper `_validate_str(value, field_name, max_length)` que trunca com aviso ou rejeita com `ValueError`:

| Campo | Max Length |
|-------|-----------|
| `nome` (cliente/serviço) | 200 |
| `apelido` | 100 |
| `pergunta` (RAG query) | 5000 |
| `descricao` (financeiro) | 500 |
| `conteudo` (ficha cliente) | 50000 |
| `cod` (arquivo dados) | 50 |

**TDD:**
- [ ] Teste: nome com 201 chars rejeitado
- [ ] Teste: RAG query com 5001 chars rejeitada
- [ ] Teste: nome com 200 chars aceito
- [ ] Implementar `_validate_str()` e aplicar em todas as tools
- [ ] Todos os testes verdes

### 3.2 Log rotation

**Local:** `foton_system/interfaces/mcp/foton_mcp.py` (logger setup, ~linha 80)

**Problema:** `FileHandler` sem rotação — `foton_mcp.log` cresce indefinidamente.

**Solução:** Substituir por `RotatingFileHandler(maxBytes=5*1024*1024, backupCount=3)`.

**TDD:**
- [ ] Teste: após escrever >5MB de log, arquivo é rotacionado
- [ ] Implementar `RotatingFileHandler`
- [ ] Todos os testes verdes

### 3.3 Request correlation ID

**Local:** `foton_system/interfaces/mcp/foton_mcp.py` (logger + todas as tools)

**Problema:** Logs não têm ID de correlação — impossível rastrear uma chamada de tool do começo ao fim.

**Solução:** Adicionar decorator `_log_tool_call` que:
1. Gera `uuid4()` no início de cada tool
2. Loga entrada com `[req-{id}] Tool called: {nome}`
3. Loga saída com `[req-{id}] Tool completed: {nome}` (ou erro)
4. Inclui `request_id` no logger adapter

**TDD:**
- [ ] Teste: log contém request ID no formato `[req-{uuid}]`
- [ ] Teste: request ID é único por chamada
- [ ] Implementar decorator `_log_tool_call`
- [ ] Todos os testes verdes

### 3.4 Circuit breaker para ChromaDB

**Local:** `foton_system/core/memory/vector_store.py`

**Problema:** Se ChromaDB falha (processo externo, banco corrompido), toda consulta RAG falha ruidosamente — sem backoff.

**Solução:** Implementar circuit breaker simples no `VectorStore`:
- Se 3 consultas consecutivas lançarem exceção, entrar em estado `OPEN` por 60s
- Em `OPEN`, retornar `{"status": "UNAVAILABLE", "message": "Knowledge base temporarily unavailable"}`
- Após 60s, transição para `HALF_OPEN`: 1 consulta teste
- Se sucesso, `CLOSED`; se falha, volta para `OPEN` por mais 60s

**TDD:**
- [ ] Teste: 3 falhas seguidas → circuit OPEN
- [ ] Teste: em OPEN, consulta retorna unavailable sem tentar ChromaDB
- [ ] Teste: após 60s (mock time), HALF_OPEN → CLOSED se sucesso
- [ ] Implementar `CircuitBreaker` class
- [ ] Todos os testes verdes

### 3.5 Atualizar DocsMcp.md

**Local:** `docs/03_RESOURCES/DocsMcp.md` (54 linhas)

**Problema:** Lista ferramentas desatualizadas ou com nomes antigos (ex: `cadastrar_cliente_func` renomeado). Faltam `consultar_auditoria`, `verificar_atualizacao`, `importar_dados_servicos`, `pipeline_novo_cliente`, `pipeline_emitir_documento`.

**Solução:** Sincronizar a documentação com o código gerando a lista de tools a partir das docstrings de `foton_mcp.py`. Ou, para maintenance zero, adicionar tool `docs_mcp()` que retorna a documentação atualizada automaticamente.

- [ ] Mapear todas as 32 tools com suas docstrings atuais
- [ ] Reescrever `DocsMcp.md` com a lista completa e exemplos de uso
- [ ] Verificar links para outras docs (McpGuide, QuickReference)

### 3.6 Testes para path traversal

**Local:** `tests/unit/`

**Problema:** Nenhum teste cobre cenários de path traversal malicioso.

**Solução:** Adicionar test cases específicos para cada tool que aceita nomes de arquivos ou pastas:

- [ ] Teste: `validar_template` com `../../etc/passwd` → erro
- [ ] Teste: `criar_estrutura_servico` com nome `../../../windows` → sanitizado para `WINDOWS`
- [ ] Teste: `cadastrar_cliente` com nome `../../evil` → sanitizado para `EVIL`
- [ ] Teste: `ler_ficha_cliente` com `..\..\..\secret` → erro
- [ ] Todos os 237+ testes verdes

---

## Fase 4 — Documentação e Skills (P3)

*Aprimorar suporte a agentes de IA e fluidez de onboarding.*

### 4.1 Atualizar SKILL.md com RAG + Watcher

**Local:** `skills/foton-architecture/SKILL.md` (47 linhas)

**Problema:** SKILL.md cobre 4 workflows (cliente, informações, documentos, financeiro) mas não menciona RAG (`consultar_conhecimento`/`indexar_conhecimento`) nem Watcher (proatividade).

**Solução:** Adicionar 2 workflows:

**Workflow 5 — Knowledge Base (RAG):**
```
5. Knowledge Management:
   a) Index: `indexar_conhecimento(pasta_alvo="")` para popular a base vetorial
   b) Query: `consultar_conhecimento(pergunta="...")` para busca semântica
   c) Best practice: Indexar após cada alteração em INFO files
```

**Workflow 6 — Watcher (Proatividade):**
```
6. Watcher Mode:
   a) Ativar: iniciar com `--watcher` para monitoramento de alterações
   b) Reage automaticamente a: criação/modificação de INFO files
   c) Dispara: `indexar_conhecimento` automaticamente após alterações
```

- [ ] Atualizar `skills/foton-architecture/SKILL.md`
- [ ] Verificar que `configurar_agente` tool copia o SKILL.md corretamente

### 4.2 Criar CHANGELOG.md

**Local:** `CHANGELOG.md` (raiz)

**Problema:** Não existe changelog consolidado — releases estão espalhadas em `docs/04_ARCHIVES/releases/`.

**Solução:** Criar `CHANGELOG.md` em formato Keep a Changelog, agregando:

```markdown
# Changelog

## [1.2.0] - 2026-05
### Added
- TUI 2.0 responsive layout
- DNA unification (info-Template.md)
- DependencyManager for on-demand AI pack installation
- TipService with didactic notifications
- Sandbox mode for safe testing

## [1.1.0] - 2026-04
### Added
- MCP protocol with 21 tools
- RAG semantic memory (chromadb)
- Sentinel/Watcher proactive mode
- Intelligent document pipelines
```

- [ ] Criar `CHANGELOG.md` na raiz
- [ ] Manter releases futuras atualizando este arquivo

### 4.3 Adicionar .opencode/ no repositório

**Local:** `.opencode/` (raiz)

**Problema:** Não existe configuração opencode para agentes — todo onboarding é manual via `configurar_agente`.

**Solução:** Criar estrutura `.opencode/` com:

```
.opencode/
├── opencode.json          # Referencia o skill foton-architecture
└── agents.json            # Define agente padrão para o repositório
```

**`opencode.json`:**
```json
{
  "skills": [
    "skills/foton-architecture/SKILL.md"
  ]
}
```

**`agents.json`:**
```json
{
  "default": "foton-architecture",
  "agents": {
    "foton-architecture": {
      "description": "Gerencia projetos de arquitetura, documentos e RAG",
      "skill": "skills/foton-architecture/SKILL.md"
    }
  }
}
```

- [ ] Criar `.opencode/opencode.json`
- [ ] Criar `.opencode/agents.json`
- [ ] Verificar que opencode reconhece a configuração

### 4.4 Skills granulares por domínio

**Local:** `skills/` (raiz)

**Problema:** Um único SKILL.md genérico — agentes recebem instruções sobre domínios que não vão usar.

**Solução:** Criar skills menores e focadas:

| Skill | Workflows | Público |
|-------|-----------|---------|
| `foton-clients/SKILL.md` | Onboarding, fichas, serviços | Agentes de cadastro |
| `foton-documents/SKILL.md` | Templates, validação, geração | Agentes documentais |
| `foton-finance/SKILL.md` | Entradas, extratos, BI | Agentes financeiros |
| `foton-rag/SKILL.md` | Indexar, consultar, watcher | Agentes de memória |

- [ ] Criar `skills/foton-clients/SKILL.md`
- [ ] Criar `skills/foton-documents/SKILL.md`
- [ ] Criar `skills/foton-finance/SKILL.md`
- [ ] Criar `skills/foton-rag/SKILL.md`
- [ ] Atualizar `foton-architecture/SKILL.md` para delegar para os skills granulares

---

## Fase 5 — Backlog Técnico (Contínuo)

*Melhorias sem prazo fixo que elevam a qualidade do código sem quebrar compatibilidade.*

### 5.1 Type hints completos

**Local:**
- `foton_system/modules/shared/infrastructure/config/config.py` (93 linhas)
- `foton_system/modules/documents/domain/models/form_session.py` (120 linhas)
- `foton_system/modules/productivity/pomodoro.py` (134 linhas)
- adapters (browser, webview, tui, linux, windows, null)

**Problema:** Módulos sem type hints — IDE e type checkers (mypy/pyright) não conseguem validar.

**Solução:** Adicionar type hints em todos os parâmetros e retornos.

- [ ] `config.py` completo
- [ ] `form_session.py` completo
- [ ] `pomodoro.py` completo
- [ ] Todos os adapters
- [ ] Verificar com `mypy --strict` (ou pyright)

### 5.2 Docstrings em módulos sem cobertura

**Local:**
- `foton_system/core/watcher/handlers.py`
- `foton_system/core/watcher/service.py`
- `foton_system/modules/productivity/pomodoro.py`
- Adapters (browser_form_adapter, tui_form_adapter, etc.)

**Problema:** Módulos funcionais sem docstrings — difícil para novos contribuidores (humanos ou IA) entenderem o propósito.

**Solução:** Adicionar docstrings no formato Google-style ou NumPy-style, consistentes com o resto do código.

- [ ] `watcher/handlers.py` — docstrings em todas as classes e métodos
- [ ] `watcher/service.py` — docstrings em todas as classes e métodos
- [ ] `pomodoro.py` — docstrings em todas as classes e métodos
- [ ] Adapters — docstrings mínimas (1 linha) em cada classe

### 5.3 MCP Resources (Opcional)

**Local:** `foton_system/interfaces/mcp/foton_mcp.py`

**Problema:** Servidor MCP expõe apenas tools — sem resources ou prompts. O protocolo MCP suporta expor arquivos como resources, o que enriqueceria a integração.

**Solução:** Implementar `@mcp.resource()` para:
- `foton://clientes/{nome}/INFO` — conteúdo do INFO-CLIENTE.md
- `foton://clientes/{nome}/servicos` — lista de serviços
- `foton://financeiro/resumo` — resumo financeiro geral

**Benefício:** Agentes poderiam "ler" arquivos como resources em vez de chamar tools.

- [ ] Implementar resource handler para INFO files
- [ ] Implementar resource handler para listagem de serviços
- [ ] Verificar com cliente MCP (opencode, Claude Desktop)

### 5.4 Benchmark de inicialização

**Local:** `foton_system/main.py`

**Problema:** Sem métricas de performance — não sabemos se uma mudança torna o bootstrap mais lento.

**Solução:** Adicionar timer no `safety_entry()` que loga tempo de cada etapa:

```python
import time
_start = time.perf_counter()
# ... bootstrap ...
_elapsed = time.perf_counter() - _start
_logger.info(f"Bootstrap completed in {_elapsed:.2f}s")
```

- [ ] Adicionar timer no bootstrap
- [ ] Logar tempo total e por etapa
- [ ] Estabelecer baseline (tempo atual)

---

## Critérios de Aceitação da Sprint

- [ ] **Fase 1:** Zero path traversal risks, temp files limpos, `except` narrowed, `dados_extras` validado
- [x] **Fase 2:** `client_service.py` fatorado em 3 arquivos + facade, `__init__.py` em módulos faltantes, scripts unificados
- [ ] **Fase 3:** Max length validation em todas as tools, log rotation, request correlation ID, circuit breaker para ChromaDB, `DocsMcp.md` atualizado, testes de path traversal adicionados
- [ ] **Fase 4:** SKILL.md com RAG+Watcher, CHANGELOG.md criado, `.opencode/` configurado, skills granulares criados
- [ ] **Fase 5:** Type hints completos, docstrings adicionadas, resources MCP (opcional), benchmark de inicialização
- [ ] **Regressão zero:** 237+ testes passando SEMPRE após cada fase

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Fatoração de `client_service.py` quebra imports | Média | Alto | CI/CD com suite completa antes do merge |
| Narrow `except` descobre erro escondido | Média | Médio | Testes exaustivos em modo MCP real |
| Circuit breaker ChromaDB mascara problema real | Baixa | Médio | Log detalhado no OPEN com alerta |
| Skills granulares desatualizam rápido | Alta | Baixo | Manter SKILL.md principal como source of truth |

---

## Links Relacionados

- Documentação de auditoria: [[DocumentationAudit]]
- Guia do MCP: [[McpGuide]]
- Protocolo para Agentes: [[LlmProtocol]]
- Contexto do Sistema: [[LlmContext]]
- Arquitetura: [[Concepts]]
- Plano de evolução agêntica: [[AgenticSprintPlan]]
