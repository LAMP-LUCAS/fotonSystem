---
description: "Fatia uma Spec técnica em User Stories para uma sprint"
arguments:
  - name: spec_file
    description: "Caminho relativo da spec (ex: MOD-CLIENTES/SPEC-EPIC-003-v1.0)"
    required: true
  - name: sprint_id
    description: "Identificador da sprint (ex: 2026-07-SPRINT-4)"
    required: true
---

# /slice — Passo 3: SPEC → STORIES (QUANDO / QUEM)

## Fluxo

1. **Leitura:** Carregue a Spec em `specs/{spec_file}.md`, o PRD/Épico vinculado, e o `GLOSSARY.md`.
2. **Fatiamento:** Agrupe as regras da Spec em unidades de trabalho coesas (máx 5 RULE-IDs por story, ~8h cada).
3. **Rastreabilidade:** Cada Story DEVE conter links para:
   - O(s) RULE-ID(s) da Spec que implementa
   - O PRD/Épico de origem
4. **Localização:** Salve cada story em `.opencode/backlog/stories/STORY-NNN-descricao.md` com frontmatter contendo `status: "ready"`, `sprint: {sprint_id}`.
5. **Arquivo da Sprint:** Crie/atualize `.opencode/backlog/sprints/{sprint_id}.md` listando todas as stories com IDs, descrições, estimativas e RULE-IDs.

## Regras

- Stories devem ser **independentes** sempre que possível (evitar dependências entre stories).
- Uma história NÃO entra na Sprint sem conter links válidos para a Spec e PRD.
- Critérios de Aceite devem ser derivados diretamente dos RULE-IDs.
- Estime em horas (máx 8h ideal por story).
- A numeração segue o padrão `STORY-{sequencial de 3 dígitos}`.
- Reporte ao final: quantas stories geradas e percentual de cobertura da spec.
