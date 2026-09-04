# Contribuindo — Foton System

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.10+ |
| Testes | pytest |
| CLI | Rich (TUI) + Typer |
| MCP | `mcp` SDK (Python) |
| RAG | ChromaDB + sentence-transformers |
| Documentos | python-docx, python-pptximage |

## Setup local

```bash
# 1. Clone
git clone <repo-url>
cd fotonSystem

# 2. Dependências
pip install -r requirements.txt

# 3. Testes
python -m pytest
```

## Estrutura do repositório

```
/
├── foton_system/        # Código-fonte principal
├── specs/               # Regras técnicas (RULE-IDs)
├── docs/                # PRDs, ADRs, guias
├── .opencode/           # Sprints, Stories, Comandos, Handoffs
├── tests/               # Testes unitários
├── scripts/             # Build, deploy
├── installer/           # Inno Setup
├── AGENTS.md            # Guia para CodeAssistants
├── DEVELOPMENT_GUIDE.md # Metodologia de desenvolvimento
├── GLOSSARY.md          # Linguagem ubíqua
└── CONTRIBUTING.md      # Este arquivo
```

## Primeira contribuição (passo a passo)

```
1. Leia DEVELOPMENT_GUIDE.md — entenda as 3 camadas
2. Leia AGENTS.md — entenda os comandos do framework
3. Consulte GLOSSARY.md — familiarize-se com os termos
4. Execute /start — veja o backlog atual
5. Escolha uma story em status "ready"
6. Execute /feature STORY-XXX — implemente com TDD
7. Execute /handoff — gere relatório ao finalizar
```

## Convenções de código

- **Código:** inglês (nomes de classes, funções, variáveis)
- **Comentários:** português (explicação do "porquê")
- **Arquitetura:** Hexagonal (Ports & Adapters)
- **Testes:** pytest, um arquivo por módulo
- **Commits:** `tipo: descrição [STORY-XXX] [RULE-X.Y.Z]`
  - `feat:` nova funcionalidade
  - `fix:` correção de bug
  - `refactor:` refatoração sem mudança de comportamento
  - `docs:` documentação
  - `test:` testes

## Onde encontrar cada coisa

| Precisa de... | Vá em... |
|---------------|----------|
| Regra de negócio exata | `specs/MOD-*/SPEC-*.md` (busque pelo RULE-ID) |
| Contexto de uma funcionalidade | `docs/prd/epics/EPIC-*.md` |
| O que fazer agora | `.opencode/backlog/stories/` |
| Decisão arquitetural | `docs/00_META/ADR/` |
| Guia do usuário | `docs/02_GUIDES/` |
| Instalação | `AGENTS.md` (seção Instalação) |

## Dúvidas?

Abra uma issue ou consulte o dicionário de domínio em `docs/00_META/Dictionary.md`.
