---
description: "Valida código implementado contra Specs e PRD"
arguments: []
---

# /review — Passo 5: VALIDAÇÃO

## Fluxo

1. **Escopo:** Identifique todas as Stories da Sprint corrente em `.opencode/backlog/sprints/`.
2. **Vs. Spec:** Para cada Story, verifique:
   - As constantes, validações e fluxos implementados correspondem aos RULE-IDs?
   - Há testes para cada Critério de Aceite?
   - A cobertura cobre os caminhos felizes e as exceções?
3. **Vs. PRD:** Se o PRD define métricas de sucesso (ex: tempo de resposta), verifique:
   - Existem logs de performance?
   - Existem testes que comprovem a meta?
4. **Relatório:** Gere em `docs/01_PROJECTS/` ou `.opencode/handoffs/`:
   - Regras da Spec violadas ou ausentes
   - Métricas do PRD sem cobertura
   - Sugestões de melhoria

## Regras

- Se uma regra da Spec não tem teste correspondente, é uma violação.
- Se um teste existe mas a regra não está na Spec, a Spec precisa ser atualizada.
- Se houver desvios gere relatório e atualize a Spec antes de prosseguir.
