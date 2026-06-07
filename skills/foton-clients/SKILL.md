---
name: foton-clients
description: Gerenciamento de clientes e serviços do escritório de arquitetura — cadastro, fichas, centros de verdade, estrutura de serviços
---

# Foton Skill: Clientes

Skill especializada em **gestão de clientes e serviços** do Foton System.
Carregue esta skill quando a tarefa envolver criar, consultar ou modificar dados de clientes.

## Skills relacionadas

Este skill faz parte do ecossistema Foton. Consulte as demais conforme necessário:

| Skill | Quando usar |
|---|---|
| `foton-architecture` | Visão geral do sistema, primeiros passos |
| `foton-documents` | Gerar contratos, propostas, validar templates |
| `foton-finance` | Registrar entradas/saídas, consultar financeiro |
| `foton-rag` | Buscar conhecimento em projetos passados |

## Ferramentas

| Ferramenta | Descrição |
|---|---|
| `listar_clientes` | Lista todos os projetos (ignora pastas de sistema) |
| `cadastrar_cliente` | Cria estrutura de pastas + INFO-CLIENTE.md |
| `pipeline_novo_cliente` | **(Recomendado)** Check de duplicata + criação + verificação |
| `ler_ficha_cliente` | Lê o Centro de Verdade (INFO-*.md) — mandatório antes de agir |
| `atualizar_ficha_cliente` | Adiciona notas de reunião ou decisões técnicas (com .bak) |
| `listar_servicos_cliente` | Lista sub-projetos de um cliente |
| `criar_estrutura_servico` | Cria pastas DOC/ADM/OP para novo serviço |

## Workflows

### Onboarding de cliente
1. `listar_clientes` — verificar duplicatas
2. `pipeline_novo_cliente(nome, ...)` — criar com segurança
3. `ler_ficha_cliente` — confirmar criação
4. `atualizar_ficha_cliente` — complementar dados iniciais

### Gestão de serviços
1. `listar_servicos_cliente` — ver serviços existentes
2. `criar_estrutura_servico` — novo serviço
3. `ler_ficha_cliente` — atualizar centro de verdade

## Convenções

- **INFO-*.md** é o Centro de Verdade — SEMPRE leia antes de modificar
- **Idioma**: PT-BR obrigatório
- **Backup automático**: `.bak` antes de alterar fichas
- **POP Auditado**: criação de cliente passa pelo sistema de auditoria
