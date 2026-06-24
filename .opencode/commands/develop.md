---
description: "Carrega a última sprint ativa, lista stories e pergunta qual iniciar"
arguments: []
---

# /develop — Entrada Tática: Sprint Corrente

## Fluxo

1. **Identificar Sprint Ativa:** Varra `.opencode/backlog/sprints/` e identifique a sprint mais recente com status `planning` ou `active` (ordenando por data de início decrescente).
2. **Listar Stories:** Exiba todas as stories da sprint em formato de tabela:
   - ID, descrição, estimativa, status, RULE-IDs vinculados
3. **Seleção:** Pergunte ao usuário qual story deseja desenvolver.
4. **Pré-carga:** Antes de iniciar, carregue automaticamente:
   - O arquivo completo da sprint
   - O arquivo da story selecionada
   - A(s) spec(s) vinculada(s) (parseie os RULE-IDs e localize os arquivos em `specs/`)
   - O `GLOSSARY.md`
5. **Plano:** Apresente um plano macro de implementação:
   - Arquivos que serão alterados
   - Dependências entre tarefas
   - Estratégia de testes
6. **Início:** Pergunte se prefere executar via `/feature` (TDD clássico) ou `/RL` (RalphLoop interativo com harness).

## Regras

- Se não houver sprint ativa, informe e sugira `/slice` para criar uma.
- Se não houver stories `ready`, sugere `/translate` ou `/slice` para popular o backlog.
- Se a sprint selecionada estiver com status `done`, avise e ofereça criar nova sprint.
- Atualize o status da story para `in_progress` após confirmação do usuário.
- Se houver stories `in_progress`, pergunte se deseja retomá-las em vez de iniciar uma nova.
