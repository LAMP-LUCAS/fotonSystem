# ADRs — Architecture Decision Records

Os ADRs (Recordações de Decisão Arquitetural) estão centralizados em:

**`docs/00_META/ADR/`**

Incluem:
- `ADR001_ParaZettelkastenDoc.md` — Adoção de PARA + Zettelkasten (accepted)
- `ADR002_PascalCaseNaming.md` — Padronização PascalCase (accepted)
- `ADR003_SandboxTestIsolation.md` — Isolamento de testes via Sandbox (proposed)

## Relação com Specs

Decisões arquiteturais (ADRs) **fundamentam** as regras técnicas (Specs):

- Um ADR pode gerar uma ou mais RULE-IDs
- Uma RULE-ID deve referenciar o ADR que a motivou
- Exemplo: `RULE-CLIENTES-3.1` (derivado de ADR002 — PascalCase)

## Para criar um novo ADR

Use o template em `docs/00_META/ADR/` e siga o formato:
- Título claro
- Status: proposed → accepted/rejected/deprecated
- Contexto e motivação
- Decisão
- Consequências
