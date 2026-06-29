# Foton System v1.4.0 — Guia do Agente

Sistema de gestão para escritório de arquitetura.

**Idioma obrigatório:** PT-BR. Todas as interações em português brasileiro.

---

## Framework de Desenvolvimento (SSOT + Rastreabilidade)

O repositório segue uma metodologia de 3 camadas documentada em `DEVELOPMENT_GUIDE.md`:

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| **Diretiva** | `docs/` (PARA) | PRDs, ADRs, conceitos, manuais |
| **Estratégica** | `specs/` | Regras técnicas com `RULE-IDs` rastreáveis |
| **Tática** | `.opencode/` | Sprints, Stories, Handoffs, Comandos |

### Comandos disponíveis

| Comando | Função | Tipo |
|---------|--------|------|
| `/epic EPIC-XXX "contexto"` | Cria/atualiza PRD Épico | **Estratégico** |
| `/translate EPIC-XXX MOD-NOME` | PRD → Spec Técnica com RULE-IDs | **Estratégico** |
| `/slice MOD-X/SPEC-Y-v1 2026-SPRINT-N` | Spec → User Stories para uma sprint | **Planejamento** |
| `/start` | Lista todas sprints/stories pendentes e pergunta qual iniciar | **Tático** |
| `/develop` | Carrega última sprint ativa, lista stories, pergunta qual iniciar | **Tático** |
| `/feature STORY-XXX` | Executa Story com TDD | **Operacional** |
| `/RL STORY-XXX` | Sessão RalphLoop interativa com harness | **Operacional** |
| `/bugfix #123` | Corrige bug com teste e rastreabilidade | **Operacional** |
| `/review 2026-SPRINT-N` | Valida código vs Spec e PRD | **Validação** |
| `/handoff` | Gera relatório de passagem de contexto | **Handoff** |

### Convenções do Framework
- **Commits** devem referenciar `[STORY-XXX]` e `[RULE-X.Y.Z]`
- **Handoff** obrigatório ao final de cada sessão via `/handoff` (template em `.opencode/templates/HANDOFF_TEMPLATE.md`)
- **GLOSSARY.md** na raiz define a Linguagem Ubíqua (fonte: `docs/00_META/Dictionary.md`)

---

## Estratégia RalphLoop (Contexto Atômico)

RalphLoop é o padrão de execução atômica do framework. Para qualquer tarefa que envolva mais de 2 arquivos ou mais de 50 linhas de código novo, o agente DEVE operar em loops atômicos:

```
┌─────────────────────────────────────────────────────┐
│                    RALPHLOOP                         │
├─────────────────────────────────────────────────────┤
│ 1. LOAD  → Carregar APENAS os arquivos necessários  │
│ 2. PLAN  → Descrever em ≤3 frases o que será feito  │
│ 3. CODE  → Gerar código via patch/diff              │
│ 4. TEST  → Executar testes (RED → GREEN)            │
│ 5. SAVE  → Confirmar conclusão, limpar contexto     │
└─────────────────────────────────────────────────────┘
```

**Regras:**
- **LOAD mínimo:** Nunca carregue um arquivo inteiro se apenas uma função será alterada. Use `grep` + `read` com `offset`/`limit`.
- **PLAN obrigatório:** Antes de cada CODE, descreva o plano. O usuário pode aprovar ou ajustar.
- **TEST primeiro:** Escreva o teste (RED), depois implemente (GREEN). Sem exceções.
- **SAVE explícito:** Confirme a conclusão antes de avançar. Descarte arquivos carregados.
- **Rastreabilidade:** Cada patch deve conter `// @story: STORY-XXX` e `// @rule: RULE-X.Y.Z`.
- **Benefício:** Reduz consumo de tokens em 40-60% mantendo contexto focado.

> O comando `/RL STORY-XXX` orquestra este fluxo interativamente. O harness automatizado (com limpeza total de memória) é executado via script externo.

### Primeira Interação (fluxo recomendado)

```
/start                    # Ver backlog, escolher sprint/story
/develop                  # ou: atalho direto para sprint ativa
/feature STORY-XXX        # ou /RL STORY-XXX — implementar
/handoff                  # gerar relatório ao finalizar sessão
```

---

## Links úteis

- Código: `.\fotonSystem\`
- Metodologia: `DEVELOPMENT_GUIDE.md`
- Docs MCP: `docs/03_RESOURCES/DocsMcp.md`
- Plano de auditoria: `docs/01_PROJECTS/Sprint_SystemAudit/SprintPlan.md`
- Installer Inno Setup: `installer/foton_setup.iss`
- Skills:
  - `skills/foton-architecture/SKILL.md` — Metaskill (visão geral)
  - `skills/foton-clients/SKILL.md` — Clientes e serviços
  - `skills/foton-documents/SKILL.md` — Documentos e templates
  - `skills/foton-finance/SKILL.md` — Financeiro
  - `skills/foton-rag/SKILL.md` — RAG e memória semântica

---

## Como conectar ao MCP

### Via executável compilado (recomendado)
```
"C:\Users\Lucas\AppData\Local\FotonSystem\bin\foton_system_v1.2.0.exe" --mcp
```

### Via Python (modo dev)
```bash
cd fotonSystem
python -m foton_system.entry --mcp
```

---

## Arquitetura

```
foton_system/
├── core/
│   ├── memory/vector_store.py   # ChromaDB + circuit breaker
│   └── ops/                     # Operações POP auditadas
├── modules/
│   ├── clients/                 # CRUD, validação, query
│   ├── documents/               # Templates, geração DOCX/PPTX
│   ├── finance/                 # Financeiro por cliente
│   └── shared/                  # Config, PathManager, bootstrap
├── interfaces/
│   ├── mcp/foton_mcp.py         # 37 ferramentas MCP
│   └── cli/                     # CLI legado
└── infrastructure/
    └── dependency_manager.py    # AI Pack (torch, chromadb, etc.)
```

---

## 41 Ferramentas MCP (v1.4.0)

### 📂 Clientes (6)
| Ferramenta | Descrição |
|---|---|
| `listar_clientes` | Lista projetos (ignora pastas de sistema) |
| `cadastrar_cliente` | Cria estrutura de pastas + INFO-CLIENTE.md |
| `ler_ficha_cliente` | Lê o Centro de Verdade (INFO-*.md) |
| `atualizar_ficha_cliente` | Adiciona notas de reunião (com .bak) |
| `listar_servicos_cliente` | Lista sub-projetos |
| `criar_estrutura_servico` | Cria estrutura DOC/ADM/OP |

### 💵 Financeiro (3)
| Ferramenta | Descrição |
|---|---|
| `registrar_financeiro` | Entrada/saída no CSV do cliente |
| `consultar_financeiro` | Saldo e extrato do cliente |
| `resumo_financeiro_geral` | Dashboard do escritório |

### 📄 Documentos (6)
| Ferramenta | Descrição |
|---|---|
| `listar_templates` | Catálogo de contratos/propostas |
| `listar_documentos_cliente` | Arquivos gerados por cliente |
| `listar_arquivos_dados` | Arquivos .md/.txt de dados |
| `criar_arquivo_dados` | Arquivo de dados customizado |
| `validar_template` | Pré-voo de variáveis do template |
| `gerar_documento` | Merge template + dados → DOCX/PPTX |

### 🔄 Sincronização (8)
| Ferramenta | Descrição |
|---|---|
| `info_sistema` | Diagnóstico do sistema |
| `sincronizar_base` | Atualiza Excel mestre |
| `sincronizar_clientes` | Descobre pastas novas → DB |
| `sincronizar_pastas_clientes` | DB → pastas (direção inversa) |
| `sincronizar_pastas_servicos` | DB → pastas de serviços |
| `exportar_dados_clientes` | DB → .md nas pastas |
| `exportar_dados_servicos` | DB → .md de serviços |
| `importar_dados_servicos` | .md → DB |
| `importar_dados_clientes` | INFO files → DB |

### 🧠 RAG (2)
| Ferramenta | Descrição |
|---|---|
| `indexar_conhecimento` | Indexa arquivos no ChromaDB |
| `consultar_conhecimento` | Busca semântica em projetos passados |

### 🚀 Pipelines (2)
| Ferramenta | Descrição |
|---|---|
| `pipeline_novo_cliente` | Duplicate check + criação + verificação |
| `pipeline_emitir_documento` | Pré-vôo completo antes de gerar |

### 🏗️ Infraestrutura (5)
| Ferramenta | Descrição |
|---|---|
| `ping` | Health check do servidor |
| `consultar_cub` | CUB do mês (SINDUSCON-GO) |
| `verificar_atualizacao` | Check de nova versão no GitHub |
| `consultar_auditoria` | Eventos POP auditados |
| `configurar_agente` | Instala skill no CLI |

### ✅ Conformidade e Códigos (v1.4.0+)
| Ferramenta | Descrição |
|---|---|
| `verificar_conformidade_clientes` | Audita pastas e nomes de INFO files contra o pattern |
| `corrigir_conformidade` | Aplica correção sugerida para item não conforme (inclui criação de INFO files) |
| `preencher_codigos_faltantes` | Preenche CodCliente/CodServico NaN no banco de dados |
| `validar_codigos_servicos` | Valida todos os CodServico (ausentes, placeholders, formato, duplicatas) |
| `corrigir_codigos_servicos` | Corrige automaticamente códigos de serviço inválidos |

---

## Épicos do Sistema (v2 — reestruturado)

| ID | Título | Status | Spec |
|---|---|---|---|
| EPIC-000 | Jornada do Cliente AECD (transversal) | draft | — |
| EPIC-001 | Usabilidade TUI e Navegação | **completed** | SPEC-UX-v1.1 |
| EPIC-002 | Domínio, CRUD e Sincronização | active | SPEC-DOMAIN-CRUD-v1.1 + SPEC-SYNC-v1.0 |
| EPIC-003 | Automação Comercial e Documentos | draft | SPEC-DOCUMENTOS-v1.1 |
| EPIC-004 | Recuperação Inteligente (RAG) | draft | — |
| ~~EPIC-005~~ | ~~Arquitetura de Acesso~~ | **deprecated → ADR004** | — |
| EPIC-006 | Inteligência Financeira | draft | SPEC-FINANCEIRO-v2.0 |
| EPIC-007 | Cronograma e Marcos de Obra | draft | — |
| EPIC-008 | Suprimentos e Compras | draft | — |
| EPIC-009 | Conformidade e Perenidade | draft | — |
| EPIC-010 | Diário de Obra e Atas de Reunião | draft | — |
| EPIC-011 | Controle de Qualidade e Inspeção | draft | — |

---

## Workflows

### 1. Cliente (ciclo completo)
```
listar_clientes → pipeline_novo_cliente → ler_ficha_cliente
→ atualizar_ficha_cliente (se necessário)
```

### 2. Documento
```
listar_templates → validar_template → pipeline_emitir_documento
→ gerar_documento
```

### 3. Financeiro
```
consultar_financeiro → registrar_financeiro → resumo_financeiro_geral
```

### 4. RAG (memória semântica)
```
indexar_conhecimento → consultar_conhecimento
```
*Indexar após cada alteração em INFO files para manter a base atualizada.*

---

## Convenções

- **INFO-*.md** é o Centro de Verdade — sempre ler antes de agir sobre um cliente. O nome do arquivo segue o pattern configurável via `info_file_patterns` em `settings.json` (v1.4.0+)
- **POP Auditado**: operações críticas (criar cliente, gerar documento, registrar financeiro) passam pelo sistema de auditoria
- **Backup automático**: `.bak` antes de modificar fichas
- **Segurança**: path traversal sanitizado com `Path(nome).name`, circuit breaker no ChromaDB (3 falhas → OPEN 60s)
- **Logs**: `%LOCALAPPDATA%\FotonSystem\foton_mcp.log` com rotação (5MB, 3 backups)

---

## Testes

```bash
cd fotonSystem
python -m pytest           # 452 testes, zero regressão
python -m pytest -v -k "path_traversal"  # Testes de segurança
python -m pytest -v -k "circuit_breaker" # Testes de resiliência
```

---

## Instalação e Distribuição

### 2 formas de instalar

| Método | Quando usar | Descrição |
|---|---|---|
| **Inno Setup** | Distribuição para usuários | Instalador .exe profissional (recomendado) |
| **Menu Opção 7** | Teste local do build | Instala via `install_service.py` |

### Fluxo de instalação (Inno Setup — recomendado)

```powershell
# 1. Build
python foton_system/scripts/build.py --type lite

# 2. Compilar instalador (abrir installer/foton_setup.iss no Inno Setup)
#    Ou via CLI:
iscc installer/foton_setup.iss

# 3. Distribuir dist/FotonSystem_Setup_v1.xxx.exe
```

### Fluxo de instalação local (Menu Opção 7)

```
Usuário escolhe opção 7 (Instalação / Atalhos)
  ↓
install() copia o .exe para %LOCALAPPDATA%/FotonSystem/bin/  (sempre OK)
  ↓
Tenta copiar _internal/ diretamente (funciona em modo Python source)
  ├── OK       → atalhos + config inline, "Instalação realizada!"
  └── LOCKED   → deploy de script nativo, retorna KILL_SWITCH
                    ↓
Menu exibe: "Feche o programa para concluir" → os._exit(0)
                    ↓
Script nativo (shell do SO):
  1. taskkill (Win) / pkill (Unix)  → mata TODAS as instâncias do Foton
  2. rmdir (Win) / rm (Unix)        → deleta _internal destino (agora unlocked)
  3. xcopy (Win) / cp (Unix)        → copia _internal
  4. Cria .first_run marker
  5. start (Win) / nohup (Unix)     → reabre o EXE de AppData
  6. Auto-delete do script
                    ↓
main.py detecta .first_run → atalhos + config → deleta marcador
```

### Primeira execução pós-instalação

Quando o EXE instalado inicia pela primeira vez, `main.py._first_run_setup()`:
1. Detecta o marcador `.first_run` no `bin_dir`
2. Cria atalhos via `porter.get_integrator()` (abstração cross-platform)
3. Inicializa config via `BootstrapService.initialize()`
4. Remove o marcador (execução única)

### Estratégia cross-platform

O instalador usa templates de shell script nativo para evitar dependências:

| SO | Script | Matar processo | Copiar | Atalhos |
|---|---|---|---|---|
| Windows | `.bat` | `taskkill /f /im` | `xcopy` | `main.py` first-run |
| Linux | `.sh` | `pkill -f` | `cp -r` | `main.py` first-run |
| macOS | `.sh` | `pkill -f` | `cp -r` | `main.py` first-run |

A camada Python (`install_service.py`) detecta `sys.platform` e gera o script apropriado — a lógica é idêntica, apenas a sintaxe do shell muda.
