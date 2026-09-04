---
description: "Estrutura de sessão RalphLoop interativa com harness de limpeza de memória"
arguments:
  - name: story_id
    description: "ID da User Story (ex: STORY-001)"
    required: true
---

# /RL — Sessão RalphLoop Interativa

## O que é o RalphLoop

RalphLoop é um padrão de execução atômica que divide o trabalho em micro-ciclos LOAD→PLAN→CODE→TEST→SAVE. Cada ciclo opera com contexto mínimo, reduzindo consumo de tokens em 40-60% e mantendo o foco em uma única transformação por vez.

**Atenção:** Este comando não executa o RalphLoop automatizado (que roda via script harness externo com limpeza total de memória). Ele cria a **estrutura interativa** para que o agente e o usuário percorram juntos cada ciclo.

## Fluxo

### Fase 1: Setup da Sessão
1. **Leitura:** Carregue a story em `.opencode/backlog/stories/{story_id}.md`.
2. **Mapeamento:** Identifique todas as tarefas técnicas da story.
3. **Plano Macro:** Apresente a sequência de ciclos atômicos planejados.
4. **Harness:** Informe que o contexto será resetado ao final de cada ciclo (LOAD fresco).

### Fase 2: Loop Atômico (repetir para cada tarefa)
```
┌─────────────────────────────────────────────────┐
│                 CICLO RALPHLOOP                  │
├─────────────────────────────────────────────────┤
│ 1. LOAD  → Carrega APENAS arquivos necessários  │
│ 2. PLAN  → Descreve em ≤3 frases o que fará     │
│ 3. CODE  → Gera código via patch/diff           │
│ 4. TEST  → Executa testes, confirma verde       │
│ 5. SAVE  → Persiste, prepara próximo ciclo      │
└─────────────────────────────────────────────────┘
```

### Fase 3: Cleanup
1. Ao final de todos os ciclos, execute `python -m pytest` completo.
2. Sugira gerar handoff via `/handoff`.
3. Se houver pendências, registre em `.opencode/handoffs/`.

## Regras do RalphLoop Interativo

- **LOAD mínimo:** Nunca carregue um arquivo inteiro se apenas uma função será alterada. Use `grep` + `read` com `offset`/`limit`.
- **PLAN obrigatório:** Antes de cada CODE, descreva o plano em até 3 frases. O usuário pode aprovar ou ajustar.
- **TEST primeiro:** Escreva o teste (RED), depois implemente (GREEN). Sem exceções.
- **SAVE explícito:** Confirme a conclusão de cada micro-tarefa antes de avançar.
- **Limpeza de contexto:** Ao final de cada ciclo, descarte arquivos carregados que não serão mais necessários.
- **Rastreabilidade:** Cada patch deve conter `// @story: {story_id}` e `// @rule: RULE-X.Y.Z`.
- **Commit:** Ao final de todos os ciclos, commit com `feat: descrição [{story_id}] [RULE-X.Y.Z]`.

## Comportamento em caso de desvio

- Se encontrar lacuna na Spec, PARE e sugira `/translate`.
- Se uma tarefa exigir alterar mais de 3 arquivos, PARE e peça aprovação.
- Se um teste falhar inesperadamente, PARE, diagnostique e corrija antes de seguir.
