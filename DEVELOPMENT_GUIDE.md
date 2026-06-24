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
│   ├── commands/        → /feature, /review, /slice...
│   ├── backlog/         → Sprints + Stories
│   └── handoffs/        → Relatórios de sessão
│                         → Estabilidade: BAIXA (churn diário)
│                         → Público: IA, dev no dia-a-dia
```

## Fluxo de 5 Passos

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  /epic   │ →  │/translate│ →  │  /slice  │ →  │ /feature │ →  │ /review  │
│  (PRD)   │    │(PRD→Spec)│    │(Spec→St )│    │(TDD+Code)│    │(Validate)│
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Passo 1: `/epic` — Descoberta Estratégica
- Define problema de negócio, métricas de sucesso, personas
- **Proibido** sugerir tecnologia
- Saída: PRD em `docs/` (PARA)

### Passo 2: `/translate` — PRD → Spec
- Traduz necessidades em regras técnicas com `RULE-IDs`
- Saída: Spec em `specs/MOD-*/`

### Passo 3: `/slice` — Spec → Stories
- Fatia regras em unidades de trabalho (máx 8h)
- Cada Story linka RULE-IDs da Spec
- Saída: Story em `.opencode/backlog/stories/`

### Passo 4: `/feature` — Execução (TDD)
- Plano → Testes (RED) → Código (GREEN) → Refactor
- Commit com `[STORY-XXX] [RULE-X.Y.Z]`
- Saída: Código + testes + handoff

### Passo 5: `/review` — Validação
- Verifica código vs Spec e PRD
- Gera relatório de conformidade

## Comandos Rápidos

| Ação | Comando |
|------|---------|
| Nova funcionalidade | `/feature STORY-XXX` |
| Corrigir bug | `/bugfix "descrição"` |
| Planejar sprint | `/slice SPEC-XXX` |
| Validar entrega | `/review` |
| Passagem de contexto | Preencher `HANDOFF_TEMPLATE.md` |
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
- **RalphLoop:** Pesquisa → Plano → Ação → Validação
