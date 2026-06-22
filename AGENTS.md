# Foton System v1.4.0 — Guia do Agente

Sistema de gestão para escritório de arquitetura. Exposto via **MCP (35 ferramentas)**.

**Idioma obrigatório:** PT-BR. Todas as interações com o agente e o sistema em português brasileiro.

---

## Como conectar ao MCP

### Via executável compilado (recomendado)
```
"C:\Users\Lucas\AppData\Local\FotonSystem\bin\foton_system_v1.2.0.exe" --mcp
```

### Via Python (modo dev)
```bash
cd C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\fotonSystem
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
│   ├── mcp/foton_mcp.py         # 34 ferramentas MCP
│   └── cli/                     # CLI legado
└── infrastructure/
    └── dependency_manager.py    # AI Pack (torch, chromadb, etc.)
```

---

## 35 Ferramentas MCP (v1.4.0)

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

### 🔄 Sincronização (7)
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
cd C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\fotonSystem
python -m pytest           # 362 testes, zero regressão
python -m pytest -v -k "path_traversal"  # Testes de segurança
python -m pytest -v -k "circuit_breaker" # Testes de resiliência
```

---

## Links úteis

- Código: `C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\fotonSystem\`
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
