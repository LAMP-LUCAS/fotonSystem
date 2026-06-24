---
description: "Traduz PRD → Spec Técnica com RULE-IDs"
arguments:
  - name: epic_ref
    description: "Referência do PRD/Épico (ex: EPIC-001 ou caminho do arquivo)"
    required: true
---

# /translate — Passo 2: PRD → SPEC (COMO)

## Fluxo

1. **Leitura:** Carregue o PRD/Épico indicado e o `GLOSSARY.md`.
2. **Tradução:** Converta cada requisito de negócio em regras técnicas com IDs únicos.
3. **IDs:** Cada regra recebe `RULE-<modulo>.<capitulo>.<sequencial>` (ex: `RULE-CLIENTES-4.2.1`).
4. **Localização:** Salve em `specs/MOD-<MODULO>/SPEC-<NOME>-v<versao>.md`.
5. **Saída:** Arquivo markdown com:
   - **Problema:** Contexto do PRD.
   - **Solução Proposta:** Abordagem técnica.
   - **Regras de Negócio (RULE-IDs):** Lista numerada de regras imutáveis.

## Regras

- A Spec é o "juiz final". Se uma regra não está na Spec, o código não é escrito.
- RULE-IDs devem ser únicos e imutáveis após publicação.
- Ao alterar uma regra, incremente a versão da Spec e registre no changelog.
- Atualize `docs/00_META/ADR/` se decisões arquiteturais forem tomadas.
