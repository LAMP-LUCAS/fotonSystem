---
description: "Implementa uma User Story seguindo TDD"
arguments:
  - name: story_id
    description: "ID da User Story (ex: STORY-001)"
    required: true
---

# /feature — Passo 4: EXECUÇÃO (CÓDIGO)

## Fluxo

### 1. Plano (antes de codificar)
- Leia a Story em `.opencode/backlog/stories/{story_id}.md`
- Carregue as Specs e RULE-IDs linkados
- Carregue o PRD/Épico de origem
- Descreva o plano de implementação com:
  - Arquivos que serão criados/modificados
  - Abordagem técnica
  - Casos de teste planejados

### 2. TDD (após aprovação do plano)
- Escreva os testes unitários baseados nos Critérios de Aceite
- RED: testes falham (ainda sem implementação)
- GREEN: implemente o código mínimo para passar
- REFACTOR: ajuste sem quebrar testes

### 3. Implementação
- Aplique código via patches incrementais (um patch por funcionalidade)
- Siga as convenções do `AGENTS.md`:
  - Código em inglês, comentários em português
  - Hexagonal Architecture (Ports & Adapters)
  - Nunca reescreva um arquivo inteiro

### 4. Rastreabilidade
- Commit com: `feat: descrição [STORY-XXX] [RULE-X.Y.Z]`

### 5. Handoff
- Ao final, gere relatório em `.opencode/handoffs/` usando o template
