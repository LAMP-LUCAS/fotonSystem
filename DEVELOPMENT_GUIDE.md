# Guia de Desenvolvimento — Foton System

## Arquitetura do Repositório (3 Camadas)

```
/ (raiz)
├── docs/              🎯 DIRETIVA    — O QUÊ / POR QUÊ
│   └── (PARA method)    → PRDs, ADRs, guias, conceitos
│                         → Estabilidade: ALTA
│                         → Público: stakeholders, usuários
│
├── specs/             🧭 ESTRATÉGICA — COMO (REGRAS)
│   └── MOD-*/SPEC-*    → RULE-IDs rastreáveis
│                         → Estabilidade: MÉDIA
│                         → Público: tech lead, devs, revisores
│
├── .opencode/         🔧 TÁTICA      — QUANDO / QUEM
│   ├── commands/        → /epic, /feature, /review, /handoff...
│   ├── backlog/         → Sprints + Stories
│   ├── handoffs/        → Relatórios de sessão
│   └── reviews/         → Relatórios de validação
│                         → Estabilidade: BAIXA (churn diário)
│                         → Público: IA, dev no dia-a-dia
```

## Fluxo de Desenvolvimento

```
┌──────────┐   ┌──────────┐   ┌──────────┐
│  /epic   │ → │/translate│ → │  /slice  │   ← ESTRATÉGICO
│  (PRD)   │   │(PRD→Spec)│   │(Spec→St) │
└──────────┘   └──────────┘   └──────────┘
                                    │
                                    ▼
                              ┌──────────┐
                         ┌─── │ /start   │ ← TÁTICO: visão geral
                         │   │ /develop │ ← TÁTICO: sprint ativa
                         │   └──────────┘
                         │         │
                         │         ▼
┌──────────┐             │   ┌──────────┐   ┌──────────┐
│ /bugfix  │ ← atalho ───┤   │ /feature │   │   /RL    │ ← OPERACIONAL
│ (#issue) │             │   │ (TDD)    │   │(RalphLp) │
└──────────┘             │   └──────────┘   └──────────┘
                         │         │              │
                         │         ▼              ▼
                         │     ┌──────────┐
                         └──── │ /handoff │ ← HANDOFF: fim de sessão
                               └──────────┘
                                     │
                                     ▼
                               ┌──────────┐
                               │ /review  │ ← VALIDAÇÃO: fim de sprint
                               │(Vs Spec) │
                               └──────────┘
```

### Passo 1: `/epic` — Descoberta Estratégica
- Define problema de negócio, métricas de sucesso, personas
- **Proibido** sugerir tecnologia
- Saída: PRD em `docs/prd/epics/EPIC-NNN.md`

### Passo 2: `/translate` — PRD → Spec
- Traduz necessidades em regras técnicas com `RULE-IDs`
- Saída: Spec em `specs/MOD-*/SPEC-NOME-vX.Y.md`

### Passo 3: `/slice` — Spec → Stories
- Fatia regras em unidades de trabalho (máx 5 RULES, ~8h cada)
- Cada Story linka RULE-IDs da Spec e o PRD de origem
- Saída: Stories em `.opencode/backlog/stories/` + sprint em `.opencode/backlog/sprints/`

### Passo 4a: `/start` — Visão Geral do Backlog
- Lista **todas** as sprints e stories pendentes
- Usuário escolhe qual sprint/story iniciar

### Passo 4b: `/develop` — Sprint Corrente
- Carrega a última sprint ativa automaticamente
- Lista stories e sugere qual iniciar
- Pré-carrega specs e RULE-IDs vinculados

### Passo 5a: `/feature` — Execução (TDD)
- Plano → Testes (RED) → Código (GREEN) → Refactor
- Commit com `[STORY-XXX] [RULE-X.Y.Z]`
- Saída: Código + testes + handoff

### Passo 5b: `/RL` — RalphLoop Interativo
- Execução atômica em ciclos LOAD→PLAN→CODE→TEST→SAVE
- Cada ciclo opera com contexto mínimo
- Harness externo com limpeza total de memória

### Atalho: `/bugfix` — Correção de Bugs
- Diagnóstico → Teste (RED) → Correção (GREEN) → Regressão
- Commit referenciando issue: `fix: descrição (#123)`

### Passo 6: `/handoff` — Passagem de Contexto
- Gera relatório em `.opencode/handoffs/HANDOFF-{data}.md`
- Obrigatório ao final de cada sessão
- Permite que outro agente continue sem reler o histórico

### Passo 7: `/review` — Validação de Sprint
- Verifica código implementado vs Spec e PRD
- Gera relatório em `.opencode/reviews/{sprint_id}-REVIEW.md`

## Comandos Rápidos

| Ação | Comando |
|------|---------|
| Ver backlog completo | `/start` |
| Iniciar sprint ativa | `/develop` |
| Nova funcionalidade | `/feature STORY-XXX` |
| RalphLoop interativo | `/RL STORY-XXX` |
| Corrigir bug | `/bugfix #123` |
| Planejar sprint | `/slice MOD-X/SPEC-Y 2026-SPRINT-N` |
| Validar entrega | `/review 2026-SPRINT-N` |
| Passagem de contexto | `/handoff` |
| Continuar sessão | Colar último handoff + "Continue daqui" |

## Regras de Convivência

| Isto... | ...fica em |
|---------|------------|
| "O que o sistema faz?" | `docs/` (guias, manuais) |
| "Por que decidimos assim?" | `docs/00_META/ADR/` |
| "Qual a regra de negócio exata?" | `specs/` (RULE-ID) |
| "O que vou fazer hoje?" | `.opencode/backlog/stories/` |
| "O que foi feito?" | `.opencode/handoffs/` |
| "Como conectar ao MCP?" | `AGENTS.md` |
| "Qual o termo correto?" | `GLOSSARY.md` |

## Glossário do Framework

- **RULE-ID:** Identificador único de regra de negócio (`RULE-CLIENTES-4.2.1`)
- **Spec:** Documento técnico com regras rastreáveis
- **Story:** Unidade de trabalho com critérios de aceite
- **Handoff:** Relatório de passagem de contexto entre sessões
- **RalphLoop:** Ciclo atômico LOAD→PLAN→CODE→TEST→SAVE
