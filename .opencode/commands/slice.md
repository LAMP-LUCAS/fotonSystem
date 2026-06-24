---
description: "Fatia uma Spec técnica em User Stories"
arguments:
  - name: spec_ref
    description: "Referência da Spec (ex: SPEC-CLIENTES-v1.0 ou caminho do arquivo)"
    required: true
---

# /slice — Passo 3: SPEC → STORIES (QUANDO / QUEM)

## Fluxo

1. **Leitura:** Carregue a Spec indicada.
2. **Fatiamento:** Quebre as regras da Spec em unidades de trabalho que caibam em uma Sprint (máximo ~8h cada).
3. **Rastreabilidade:** Cada Story deve conter links para:
   - O(s) RULE-ID(s) da Spec que implementa
   - O PRD/Épico de origem (se aplicável)
4. **Localização:** Salve em `.opencode/backlog/stories/STORY-NNN-descricao.md`.
5. **Sprint:** Adicione a(s) Story(s) à Sprint corrente em `.opencode/backlog/sprints/`.

## Regras

- Uma história NÃO entra na Sprint sem conter links válidos para a Spec.
- Critérios de Aceite devem ser derivados diretamente dos RULE-IDs.
- Estime em horas ou pontos pequenos (máx 8h ideal).
