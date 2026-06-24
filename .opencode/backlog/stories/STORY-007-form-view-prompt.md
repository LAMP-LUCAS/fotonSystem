---
status: "ready"
sprint: "2026-07-SPRINT-4"
estimativa: "1h"
---

# STORY-007: Prompt Não-Ambíguo no Formulário Interativo

**Spec:** [RULE-UX-6.1](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-6.2](specs/MOD-UX/SPEC-UX-v1.0.md), [RULE-UX-6.3](specs/MOD-UX/SPEC-UX-v1.0.md)
**Tipo:** Melhoria (UX)

## Descrição
O prompt do `TUIFormView` é `">> Ação ou Novo Valor: "`, que conflita comandos de navegação (`n`, `p`, `v`, `s`, `a`, `c`) com valores literais. Se um campo precisa do valor "n", o usuário não consegue digitá-lo. Solução: prefixar comandos com `/` (ex: `/n`, `/p`, `/s`) e mudar o prompt para `">> Valor (/n prox, /p ant, /v ver, /s salvar): "`.

## Critérios de Aceite
- [ ] Comandos de navegação prefixados com `/` (`/n`, `/p`, `/v`, `/s`, `/a`, `/c`)
- [ ] Comandos sem `/` são tratados como valor literal do campo
- [ ] Prompt alterado para algo como `">> Valor (ou /n prox, /p ant, /v ver, /s salvar): "`
- [ ] Rodapé de comandos atualizado para mostrar `/n`, `/p`, etc.
- [ ] Comandos antigos sem `/` continuam funcionando (backward compat) ou são removidos com aviso
- [ ] Testes do form_view atualizados

## Arquivos
- `foton_system/interfaces/cli/views/form_view.py` (run_loop, _draw)
