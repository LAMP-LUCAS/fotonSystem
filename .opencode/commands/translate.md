---
description: "Traduz PRD → Spec Técnica com RULE-IDs"
arguments:
  - name: epic_id
    description: "Identificador do épico a ser traduzido (ex: EPIC-001)"
    required: true
  - name: modulo
    description: "Nome do módulo no formato MOD-XXXX (ex: MOD-CLIENTES)"
    required: true
  - name: spec_version
    description: "Versão da spec (ex: v1.0, v1.2)"
    required: false
---

# /translate — Passo 2: PRD → SPEC (COMO)

## Fluxo

1. **Leitura:** Carregue o PRD/Épico em `docs/prd/epics/{epic_id}.md` e o `GLOSSARY.md`.
2. **Spec Existente?:** Se a spec já existir em `specs/{modulo}/SPEC-{epic_id}-{spec_version}.md`, leia-a para preservar regras existentes.
3. **Tradução:** Converta cada requisito de negócio em regras técnicas com IDs únicos.
4. **IDs:** Cada regra recebe `RULE-<modulo>.<capitulo>.<sequencial>` (ex: `RULE-CLIENTES-4.2.1`).
5. **Localização:** Salve em `specs/{modulo}/SPEC-{epic_id}-{spec_version}.md`.
6. **Saída:** Arquivo markdown com:
   - **Problema:** Contexto do PRD.
   - **Solução Proposta:** Abordagem técnica de alto nível (sem código).
   - **Regras de Negócio (RULE-IDs):** Lista numerada de regras atômicas e testáveis.
   - **Critérios de Aceite Técnicos:** Vinculados às RULES.
   - **Restrições e Limitações:** Dependências conhecidas.

## Regras

- A Spec é o "juiz final". Se uma regra não está na Spec, o código não é escrito.
- Cada parágrafo de dor do PRD deve gerar pelo menos uma RULE.
- RULE-IDs devem ser únicos, imutáveis, e no formato `RULE-{capitulo}.{secao}.{sequencial}`.
- Se uma regra já existir na spec atual, mantenha seu ID original e atualize apenas a descrição.
- **NUNCA** invente regras que não tenham lastro no PRD.
- Ao alterar uma regra, incremente a versão da Spec e registre no changelog.
- Atualize `docs/00_META/ADR/` se decisões arquiteturais forem tomadas.
