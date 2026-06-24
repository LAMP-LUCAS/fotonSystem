# Camada Estratégica — Specs Técnicas

Esta pasta contém as **Specs Técnicas** do sistema. Cada Spec é a "lei" que o código deve seguir.

## Convenções

### Estrutura de ID
`RULE-<MODULO>-<CAPITULO>.<SEQUENCIAL>`

Exemplo: `RULE-CLIENTES-4.2.1`

### Ciclo de vida
1. **Proposal:** Spec é criada via `/translate` a partir de um PRD.
2. **Active:** Spec vigente, código deve honrar todas as RULE-IDs.
3. **Deprecated:** Spec substituída por versão mais nova.
4. **Archived:** Spec histórica, mantida para rastreabilidade.

### Versionamento
- `SPEC-<NOME>-v1.0.md` → versão inicial
- `SPEC-<NOME>-v1.1.md` → regras adicionadas/modificadas
- Mantenha `CHANGELOG.md` atualizado com as mudanças de Spec

### Conteúdo mínimo de uma Spec
```markdown
# Spec: <Nome do Módulo>
**Data:** YYYY-MM-DD
**Versão:** X.Y

## 1. Problema
[Contexto de negócio]

## 2. Solução Proposta
[Abordagem técnica]

## 3. Regras de Negócio
- **RULE-XXX-1.1:** [Regra imutável]
- **RULE-XXX-1.2:** [Regra imutável]
```

## Relação com outras camadas

| Camada | Pasta | Propósito |
|--------|-------|-----------|
| Diretiva | `docs/` | PRDs, ADRs, conceitos, manuais |
| **Estratégica** | **`specs/`** | **Regras técnicas rastreáveis** |
| Tática | `.opencode/` | Sprints, stories, handoffs |

## Módulos atuais

| Spec | Cobre |
|------|-------|
| `MOD-CLIENTES/SPEC-CLIENTES-v1.0.md` | CRUD de clientes, soft delete, info files, services, conformance |
| `MOD-FINANCEIRO/SPEC-FINANCEIRO-v1.0.md` | Entradas financeiras, saldos, tipos |
| `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.0.md` | Templates, validação, geração de documentos |
| `MOD-SYNC/SPEC-SYNC-v1.0.md` | Sincronização DB ↔ filesystem, direções, pipeline |
