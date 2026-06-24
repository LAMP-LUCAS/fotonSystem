---
description: "Corrige um bug com rastreabilidade"
arguments:
  - name: descricao
    description: "Descrição do bug (comportamento esperado vs atual, passos para reproduzir)"
    required: true
---

# /bugfix — Correção de Bug

## Fluxo

1. **Reprodução:** Identifique o comportamento atual vs esperado.
2. **Causa Raiz:** Encontre a origem no código.
3. **Teste:** Escreva um teste que reproduza o bug (RED).
4. **Correção:** Implemente a correção mínima (GREEN).
5. **Regressão:** Execute o suite completo de testes.
6. **Rastreabilidade:** Commit com `fix: descrição [BUG-XXX]`.

## Regras

- Sempre comece com o teste que expõe o bug.
- Se o bug revelar uma regra não documentada na Spec, atualize a Spec via `/translate`.
- Se o bug for crítico (dados corrompidos, crash), pause e sinalize prioridade máxima.
