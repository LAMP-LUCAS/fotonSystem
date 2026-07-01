---
status: "done"
sprint: "2026-SPRINT-7"
---

# STORY-023: Engine de Fórmulas Extraída + Hardening

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Descrição

Extrair a lógica de resolução de fórmulas `[calculo: ...]` do `DocumentService` para um módulo dedicado `FormulaEngine`. Adicionar tratamento explícito de NaN/Infinity como erro. Implementar relatório de fórmulas aplicadas. Harmonizar as duas implementações paralelas atuais (DocumentService vs FormSession).

## Regras

- **RULE-DOC-4.1 (existente):** Fórmulas seguem formato `[calculo: expressao]` com operadores `+`, `-`, `*`, `/`, `()`, e referências a `@VARIAVEIS`. *(extrair para módulo dedicado)*
- **RULE-DOC-4.2 (existente):** Pré-processamento: substituição de `@VAR` por valores numéricos, validação de tipos, cálculo. Falha gera relatório. *(extrair para módulo dedicado)*
- **RULE-DOC-4.3 (upgrade):** NaN/Infinity são tratados como erro e bloqueiam a geração (hoje `safe_eval` retorna 0.0 silenciosamente em div/0).
- **RULE-DOC-4.4 (nova):** Relatório de fórmulas: lista de fórmulas aplicadas com expressão, resultado e status (OK/ERRO).

## Critérios de Aceite

- [ ] `core/ops/formula_engine.py` criado com classe `FormulaEngine` contendo `resolve(replacements) → dict` e `report() → list[FormulaResult]`
- [ ] `DocumentService._resolve_operations` delegada para `FormulaEngine`
- [ ] `FormSession._evaluate` harmonizada com `FormulaEngine` (mesmo parser, mesmo safe_eval)
- [ ] `safe_math.py` atualizado: divisão por zero → levanta `FormulaError` (em vez de retornar 0.0)
- [ ] NaN/Infinity detectados pós-eval e reportados como erro
- [ ] `FormulaEngine.report()` retorna lista com `{var, expressao, resultado, status}`
- [ ] Testes: extração mantém comportamento, NaN/Infinity erro explícito, report estrutura, dependência circular, número BR

## Arquivos Afetados

- `foton_system/core/ops/formula_engine.py` — **novo** módulo
- `foton_system/modules/shared/domain/services/safe_math.py` — upgrade div/0 → erro
- `foton_system/modules/documents/application/use_cases/document_service.py` — delegar para FormulaEngine
- `foton_system/modules/documents/domain/models/form_session.py` — harmonizar _evaluate

## Estimativa

5h

## Dependências

- STORY-022 (fraca — prefere a pré-validação existente para testar integração, mas pode ser feita em paralelo)
