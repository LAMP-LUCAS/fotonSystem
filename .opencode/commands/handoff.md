---
description: "Gera relatório de passagem de contexto para continuidade do trabalho"
arguments: []
---

# /handoff — Relatório de Handoff

## Fluxo

1. **Análise da Sessão:** Revise tudo o que foi feito nesta sessão (commits, arquivos alterados, decisões tomadas, stories trabalhadas).
2. **Identifique Pendências:** O que ficou incompleto, bloqueado ou precisa de decisão.
3. **Preencha o Template:** Gere o relatório seguindo a estrutura abaixo.
4. **Salve em:** `.opencode/handoffs/HANDOFF-{YYYY-MM-DD}.md`.
5. **Instrua o usuário:** Sugira copiar o conteúdo para o board ou iniciar a próxima sessão com "Continue a partir deste handoff".

## Estrutura do Relatório

```markdown
# Relatório de Handoff — {YYYY-MM-DD}

## 1. Conquistas da Sessão
- [Lista de tarefas concluídas, commits realizados, patches aplicados]

## 2. Estado Atual dos Artefatos
- **Specs Ativas:** [Lista com versões]
- **Stories Concluídas:** [Lista]
- **Stories em Andamento:** [Lista com % de progresso]

## 3. Estado do Código
- `[arquivo]`: [status atual, pendências]
- `[arquivo]`: [status atual, pendências]

## 4. Próximos Passos (To-Do)
1. [Ação concreta e priorizada]
2. [Ação concreta e priorizada]

## 5. Bloqueios e Decisões
- **Decisão:** [Decisão tomada e justificativa]
- **Bloqueio:** [Impedimento e ação necessária]

## 6. Contexto da Conversa (Resumo para Próximo Agente)
[Parágrafo conciso que permita a outro agente continuar o trabalho sem reler todo o histórico]
```

## Regras

- O relatório DEVE permitir que outro agente continue o trabalho sem reler o histórico da sessão.
- Se houver stories em andamento, inclua o status exato de cada tarefa técnica.
- Se houver decisões pendentes, destaque-as com `⚠️`.
- Atualize a(s) story(s) afetadas para o status atual (`in_progress`, `done`, `blocked`).
- Atualize o arquivo da sprint se o status de alguma story mudou.
