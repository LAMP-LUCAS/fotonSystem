---
description: "Cria ou atualiza um PRD Épico em docs/prd/"
arguments:
  - name: epic_id
    description: "Identificador do épico (ex: EPIC-003)"
    required: true
  - name: contexto
    description: "Resumo da dor de stakeholder ou necessidade de negócio"
    required: true
---

# /epic — Passo 1: PRD (O QUÊ / POR QUÊ)

## Fluxo

1. **Problema:** Identifique a necessidade de negócio, stakeholders envolvidos e métricas de sucesso a partir do `{contexto}` fornecido.
2. **Épico Existente?:** Leia `docs/prd/epics/{epic_id}.md` se já existir — neste caso, atualize mantendo o que for relevante.
3. **Localização:** Crie/atualize o épico em `docs/prd/epics/{epic_id}.md`.
4. **Índice:** Atualize `docs/prd/00-index.md` adicionando referência ao novo épico.
5. **Regra:** NUNCA sugira tecnologia (React, PostgreSQL, etc.) no PRD. Foco exclusivo em problemas e métricas.
6. **Saída:** Arquivo markdown com:
   - **Título curto e descritivo**
   - **Data,** Stakeholders, Métrica de Sucesso, Dor Atual
   - **Critérios de Sucesso do Negócio:** Checkbox de resultados esperados.

## Regras

- O agente NUNCA sugere tecnologia no PRD.
- Toda feature deve nascer de um Épico ou de uma necessidade validada.
- Métricas devem ser quantificáveis (tempo, percentual, valor monetário).
- Use termos do `GLOSSARY.md` sempre que possível.
- Se algo não estiver claro no contexto, pergunte antes de gerar o arquivo.
