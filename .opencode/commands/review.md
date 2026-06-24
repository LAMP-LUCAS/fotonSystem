---
description: "Valida código implementado contra Specs e PRD"
arguments:
  - name: sprint_id
    description: "Identificador da sprint (ex: 2026-07-SPRINT-4)"
    required: true
---

# /review — Passo 5: VALIDAÇÃO

## Fluxo

1. **Leitura do Plano:** Leia o arquivo da sprint em `.opencode/backlog/sprints/{sprint_id}.md`. Para cada story concluída, leia o arquivo correspondente em `.opencode/backlog/stories/`.
2. **Vs. Spec (Análise Estática):** Para cada story concluída, verifique:
   - As constantes, validações e fluxos implementados correspondem exatamente aos RULE-IDs vinculados?
   - Há testes para cada Critério de Aceite?
   - A cobertura cobre caminhos felizes e exceções?
   - Identifique regras parcialmente implementadas ou ausentes.
3. **Vs. PRD:** Se o PRD define métricas de sucesso (ex: tempo de resposta < 2s):
   - Existem logs de performance?
   - Existem testes que comprovem a meta?
   - Sugira criação de métricas se ausentes.
4. **Relatório:** Gere `.opencode/reviews/{sprint_id}-REVIEW.md` com estrutura:
   - **Resumo:** Stories planejadas, concluídas e cobertura de spec
   - **Adesão às Specs:** Tabela Story × RULE × Status × Observação
   - **Métricas do PRD:** Tabela Métrica × Status × Evidência
   - **Recomendações:** Ações corretivas priorizadas

## Regras

- Se uma regra da Spec não foi implementada, a story NÃO pode ser considerada concluída.
- Se uma regra da Spec não tem teste correspondente, é uma violação.
- Se um teste existe mas a regra não está na Spec, a Spec precisa ser atualizada.
- Se o PRD mudou, sugira rodar `/translate` antes da próxima sprint.
- O relatório deve ser objetivo e acionável.
