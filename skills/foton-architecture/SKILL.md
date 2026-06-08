---
name: foton-architecture
description: Meta-skill do Foton System — visão geral da arquitetura, mapa de skills, filosofias e boas práticas transversais
---

# Foton Architecture System — Metaskill

**Esta é a skill raiz do ecossistema Foton.** Carregue-a para obter a visão geral do sistema. Para tarefas específicas, carregue a skill granular correspondente (cada uma contém ferramentas, workflows e convenções do seu domínio).

## Mapa de Skills

```
foton-architecture (esta) — visão geral, conceitos, boas práticas
├── foton-clients    → cadastro, fichas, serviços, pipelines
├── foton-documents  → templates, validação, geração de documentos
├── foton-finance    → entradas/saídas, saldos, dashboard
└── foton-rag        → indexação, busca semântica, ChromaDB
```

### Qual skill carregar?

| Situação | Skill |
|---|---|
| Primeiro contato com o sistema | `foton-architecture` |
| Cadastrar/consultar cliente | `foton-clients` |
| Gerar contrato ou proposta | `foton-documents` |
| Registrar ou consultar financeiro | `foton-finance` |
| Buscar conhecimento em projetos passados | `foton-rag` |
| Workflow que cruza domínios | Carregue as skills envolvidas |

## Filosofias do sistema

1. **Centro de Verdade**: cada cliente tem um `INFO-*.md`. Sempre leia antes de decidir.
2. **Pure Data**: valores numéricos como floats brutos (`1500.50`). Formatação é responsabilidade do motor.
3. **Organização Agnóstica**: o sistema busca contexto em toda a hierarquia de pastas.
4. **Segurança por padrão**: path traversal sanitizado, schema validation, circuit breaker.
5. **Auditabilidade**: operações críticas passam pelo sistema POP Auditado.

## Arquitetura

```
foton_system/
├── core/memory/vector_store.py   ChromaDB + circuit breaker
├── modules/                      clients, documents, finance, shared
├── interfaces/mcp/foton_mcp.py   32 ferramentas MCP
└── infrastructure/               dependency_manager, ai_pack
```

## Conexão MCP

```bash
# Executável compilado
"C:\Users\Lucas\AppData\Local\FotonSystem\bin\foton_system_v1.2.0.exe" --mcp

# Modo dev
python -m foton_system.entry --mcp
```

## Convenções transversais

- **Idioma**: PT-BR obrigatório
- **INFO-*.md**: Centro de Verdade — ler antes de agir sobre um cliente
- **POP Auditado**: criação de cliente, geração de documento, registro financeiro
- **Backup automático**: `.bak` antes de modificar fichas
- **Logs**: `%LOCALAPPDATA%\FotonSystem\foton_mcp.log` (rotação 5MB, 3 backups)
- **Testes**: `python -m pytest` — 262 testes, zero regressão
