---
description: "Cria ou atualiza um PRD Épico em docs/prd/"
arguments:
  - name: contexto
    description: "Resumo da dor de stakeholder ou necessidade de negócio"
    required: true
---

# /epic — Passo 1: PRD (O QUÊ / POR QUÊ)

## Fluxo

1. **Problema:** Identifique a necessidade de negócio, stakeholders envolvidos e métricas de sucesso.
2. **Localização:** Crie/atualize o épico em `docs/prd/epics/EPIC-NNN-descricao.md` (ou em `docs/01_PROJECTS/` seguindo o método PARA).
3. **Regra:** NUNCA sugira tecnologia (React, PostgreSQL, etc.) no PRD. Foco exclusivo em problemas e métricas.
4. **Saída:** Arquivo markdown com:
   - **Métrica de Sucesso:** Como medimos que o problema foi resolvido?
   - **Dores:** O que motiva esta mudança?
   - **Critérios de Sucesso do Negócio:** Checkbox de resultados esperados.

## Regras

- O agente NUNCA sugere tecnologia no PRD.
- Toda feature deve nascer de um Épico ou de uma necessidade validada.
- Ao final, atualize `docs/01_PROJECTS/SPRINTS_INDEX.md` se aplicável.
