# PRD — Product Requirements Document (Índice)

Este diretório contém os PRDs (Épicos) do repositório, organizados por IDs sequenciais.
A partir de junho/2026, o índice inclui matriz de interdependência entre épicos e o mapa de jornada do cliente (EPIC-000).

## Como este diretório é usado

- `docs/prd/epics/` — Épicos individuais (EPIC-000, EPIC-001, EPIC-002, etc.)
- `docs/prd/00-index.md` — Este arquivo, serve como sumário, ponto de entrada e matriz de interdependência

## Épicos Registrados

| ID | Título | Data | Status |
|---|---|---|---|---|
| EPIC-000 | Jornada do Cliente AECD — Ciclo de Vida Completo | 2026-06-25 | draft |
| EPIC-001 | Usabilidade da Interface TUI e Navegação | 2026-06-24 | **completed** |
| EPIC-002 | Domínio, CRUD e Pipeline de Sincronização | 2026-06-25 | active |
| EPIC-003 | Automação Comercial e Geração de Documentos | 2026-06-25 | draft |
| EPIC-004 | RAG Pipeline Inteligente — Multi-Modelo e Grapho de Inferência | 2026-07-02 | **active** |
| ~~EPIC-005~~ | ~~Arquitetura de Acesso e Integração Contínua~~ | 2026-06-25 | **deprecated** → ADR004 |
| EPIC-006 | Inteligência Financeira por Projeto | 2026-06-25 | draft |
| EPIC-007 | Controle de Cronograma e Marcos de Obra | 2026-06-25 | draft |
| EPIC-008 | Gestão de Suprimentos e Compras | 2026-06-25 | draft |
| EPIC-009 | Conformidade, Rastreabilidade e Perenidade | 2026-06-25 | draft |
| EPIC-010 | Diário de Obra e Atas de Reunião | 2026-06-25 | draft |
| EPIC-011 | Controle de Qualidade e Inspeção | 2026-06-25 | draft |
| EPIC-012 | Observabilidade e Telemetria de Uso | 2026-06-28 | draft |

## Matriz de Interdependência entre Épicos

A matriz abaixo documenta quais épicos dependem de quais. Leia-se: **linha** depende de **coluna**.

```
             │ EPIC  EPIC  EPIC  EPIC  EPIC  EPIC  EPIC  EPIC  EPIC  EPIC  EPIC  EPIC
             │ 000   001   002   003   004   006   007   008   009   010   011   012
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-000    │  –    UX    DOM   DOC    –    FIN   CRON   –    CONF   –     –     –
 (Jornada)   │              CRUD                                  (legal)
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-001    │  –     –     –     –     –     –     –     –     –     –     –     –
 (UX TUI)    │
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-002    │  –    UX     –     –     –     –     –     –     –     –     –     –
 (Domínio)   │        (feito)
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-003    │  –    UX    DOM    –     –     –     –     –     –     –     –     –
 (Documentos)│
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-004    │  –    UX    DOM    –     –     –     –     –     –     –     –     –
 (RAG)       │              CRUD
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-006    │  –    UX    DOM    –     –     –     –     –     –     –     –     –
 (Financeiro)│              CRUD
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-007    │  –    UX    DOM    –     –     –     –     –     –     –     –     –
 (Cronograma)│              CRUD
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-008    │  –    UX    DOM    –     –    FIN   CRON   –     –     –     –     –
 (Suprimentos)│             CRUD         (preço) (prazo)
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-009    │  –    UX    DOM    –     –     –     –     –     –     –     –     –
 (Conformid.)│              CRUD
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-010    │  –    UX    DOM    DOC    –     –    CRON   –     –     –     –     –
 (Diário+Atas)│             CRUD   (expt)
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-011    │  –    UX    DOM    –     –     –    CRON   –     –   DIAR   –     –
 (Qualidade) │              CRUD                (bloq)         (dados)
─────────────┼─────────────────────────────────────────────────────────────────────────
 EPIC-012    │  –     –    MET    –     –     –     –     –     –     –     –     –
 (Telemetria)│           (dados)
```

### Legenda

| Sigla | Significado |
|---|---|
| UX | EPIC-001 (TUI e navegação) |
| DOM CRUD | EPIC-002 (entidades, domínio, sincronização) |
| DOC | EPIC-003 (geração de documentos) |
| RAG | EPIC-004 (busca semântica) |
| FIN | EPIC-006 (dados financeiros) |
| CRON | EPIC-007 (cronograma e marcos) |
| SUPR | EPIC-008 (suprimentos e compras) |
| CONF | EPIC-009 (conformidade legal) |
| DIAR | EPIC-010 (diário de obra) |
| QUAL | EPIC-011 (qualidade) |
| MET | EPIC-012 (telemetria e observabilidade) |

## Pipeline de Jornada do Cliente AECD

O fluxo completo de um cliente no escritório, indicando quais épicos atuam em cada etapa:

```
Prospecção ──► EPIC-003 (proposta)
    │
    ▼
Proposta ──► EPIC-003 (contrato) ◄── EPIC-004 (RAG: consultar projetos similares)
    │
    ▼
Contrato ──► EPIC-002 (cadastro + serviços)
    │
    ▼
Serviços ──► EPIC-007 (cronograma) ──► EPIC-008 (compras)
    │                                       │
    │                                       ▼
    ├──► EPIC-010 (diário de obra) ──► EPIC-011 (qualidade/inspeção)
    │                                       │
    ▼                                       ▼
Execução ──► EPIC-006 (financeiro: medição + faturamento)
    │
    ▼
Entrega ──► EPIC-009 (dossiê + backup + conformidade)
    │
    ▼
Pós-obra ──► EPIC-004 (RAG: indexar aprendizado)
              EPIC-010 (atas de reunião de lições aprendidas)
```

## Mapa de Maturidade

| ID | PRD | Spec técnica | Stories | Código | Maturidade |
|---|---|---|---|---|---|---|
| EPIC-000 | ✅ draft | ❌ | ❌ | ❌ | 0% |
| EPIC-001 | ✅ completed | ✅ SPEC-UX-v1.0 (30 RULEs) | ✅ 11/11 | ✅ | 100% |
| EPIC-002 | ✅ active | ✅ SPEC-DOMAIN-CRUD-v1.1 (17 RULEs) + SPEC-SYNC-v1.0 (10 RULEs) | ✅ 9/9 | ✅ | 100% |
| EPIC-003 | ✅ draft | ✅ SPEC-DOCUMENTOS-v1.1 (atualizada, 18 RULEs) | ❌ | ⚠️ | 25% |
| EPIC-004 | ✅ draft | ❌ | ❌ | ❌ | 10% |
| ~~EPIC-005~~ | ❌ deprecated | ❌ → ADR004 | ❌ | ❌ | – |
| EPIC-006 | ✅ draft | ✅ SPEC-FINANCEIRO-v2.0 (atualizada, 22 RULEs) | ❌ | ⚠️ (básico existe) | 15% |
| EPIC-007 | ✅ draft | ❌ | ❌ | ❌ | 0% |
| EPIC-008 | ✅ draft | ❌ | ❌ | ❌ | 0% |
| EPIC-009 | ✅ draft | ❌ | ❌ | ❌ | 5% |
| EPIC-010 | ✅ draft | ❌ | ❌ | ❌ | 0% |
| EPIC-011 | ✅ draft | ❌ | ❌ | ❌ | 0% |
| EPIC-012 | ✅ draft | ✅ SPEC-TELEMETRY-v1.0 (5 RULEs) | ✅ 2/2 | ✅ | 50% |

**Maturidade geral do sistema como ERP AECD: ~20%** (ponderado pelo escopo total de 12 épicos)

## Regras

- Todo épico deve ter um ID único (EPIC-NNN) e ser listado aqui.
- Épicos descrevem apenas problemas, dores e métricas de negócio — NUNCA tecnologia.
- A transição de Épico → Especificação Técnica é feita via `/translate`.
- **EPIC-000** é transversal e orquestra a jornada do cliente — não substitui épicos específicos.
- **EPIC-005** foi deprecado e substituído pela ADR004 (`docs/00_META/ADR/ADR004_RemoteAccessArchitecture.md`).
- A matriz de interdependência deve ser atualizada sempre que um novo épico for criado ou o escopo de um épico existente for alterado.

## ADRs Relacionadas

| ADR | Título | Status |
|---|---|---|
| ADR001 | PARA + Zettelkasten para Documentação | accepted |
| ADR002 | Padronização de Nomenclatura PascalCase | accepted |
| ADR003 | Isolamento de Testes via Modo Sandbox | proposed |
| **ADR004** | **Arquitetura de Acesso Remoto e Integração Contínua** | **proposed** |