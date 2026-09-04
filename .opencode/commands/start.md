---
description: "Lista todas as sprints e stories pendentes e pergunta qual iniciar"
arguments: []
---

# /start — Entrada Tática: Visão Geral do Backlog

## Fluxo

1. **Listar Sprints:** Varra `.opencode/backlog/sprints/` e liste todas as sprints encontradas com seus respectivos status (planning, active, done).
2. **Listar Stories:** Para cada sprint, liste as stories com status `ready` ou `in_progress`.
3. **Seleção:** Pergunte ao usuário qual sprint/story deseja iniciar.
4. **Carga de Contexto:** Ao selecionar uma story, carregue:
   - O arquivo da sprint
   - O arquivo da story
   - A(s) spec(s) vinculada(s) via RULE-IDs
   - O `GLOSSARY.md`
5. **Início:** Apresente um resumo do escopo e pergunte se deseja iniciar com `/feature {story_id}` ou com `/RL {story_id}`.

## Regras

- Se não houver sprints, informe que o backlog está vazio e sugira `/epic` ou `/translate`.
- Se houver múltiplas sprints, apresente como lista numerada para o usuário escolher.
- Se houver stories `in_progress`, destaque-as com prioridade.
- Após a seleção, sugira explicitamente o próximo comando (`/feature` ou `/RL`).
- Atualize o status da story para `in_progress` ao confirmar o início.
