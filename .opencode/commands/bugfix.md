---
description: "Corrige um bug com rastreabilidade"
arguments:
  - name: issue_id
    description: "Identificador da issue/bug (ex: #123, BUG-045)"
    required: true
  - name: descricao
    description: "Descrição do bug (comportamento esperado vs atual, passos para reproduzir)"
    required: false
---

# /bugfix — Correção de Bug

## Fluxo

1. **Diagnóstico:** Analise o bug reportado em `{issue_id}`. Identifique o comportamento atual vs esperado e a causa raiz no código.
2. **Apresentação:** Mostre um breve diagnóstico e o plano de correção antes de implementar.
3. **Teste de Regressão:** Escreva um teste unitário que REPRODUZA o bug (RED — deve falhar no estado atual).
4. **Correção:** Implemente a correção mínima (GREEN). Se afetar mais de 3 arquivos, PARE e peça aprovação.
5. **Regressão:** Execute o suite completo de testes.
6. **Rastreabilidade:** Commit com `fix: {descrição} [{issue_id}]`.
7. **Documentação:** Atualize docstrings das funções alteradas. Se a correção revelar regra não documentada, sugira `/translate`.

## Regras

- Sempre comece com o teste que expõe o bug.
- Se o bug revelar uma regra não documentada na Spec, atualize a Spec via `/translate`.
- Se o bug for crítico (dados corrompidos, crash), pause e sinalize prioridade máxima.
- Commits devem referenciar a issue: `fix: [descrição] ({issue_id})`.
