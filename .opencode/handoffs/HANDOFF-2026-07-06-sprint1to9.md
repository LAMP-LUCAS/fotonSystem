# Relatório de Handoff — 2026-07-06

## 1. Conquistas da Sessão

- **EPIC-001 reaberto** como `active` (Fase 0) — 9 regressões catalogadas (R1-R9)
- **EPIC-013 criado** — PRD Interface Modal Vim+tmux (3 fases, métricas, riscos)
- **SPEC-UX-v1.0.md → v1.3** — RULE-UX-8.9 a 8.13
- **SPEC-UI-COMPONENTS.md (NOVA)** — catálogo 14 componentes com implementação Python
- **SPEC-TUI-MODAL-v1.0.md (NOVA)** — 8 áreas, ~55 RULE-IDs, SLAs de performance
- **TuiModalDesign.md (NOVO)** — conceitos perenes: 4 modos, splits, temas, keybindings, auto-detect split prefix
- **15 stories criadas:** STORY-042 a 047 (Fase 0) + STORY-054 a 062 (Fases 1-3)
- **Auto-detect split prefix:** dentro do tmux → Ctrl+b; fora → Ctrl+w; 3 camadas de decisão
- **`scripts/foton_tmux_setup.sh`** — configurador idempotente do tmux com backup
- **Reestruturação Git:** `feat/info-naming-patterns` → `archive/sprint-1to9` (preservada); `develop` criada; `feat/ui-ux-redesign` criada para novo trabalho
- **Handoff anterior** (GPU/CUDA, RAG) preservado em `.opencode/handoffs/HANDOFF-2026-07-06e.md`

## 2. Estado Atual dos Artefatos

- **Specs Ativas:**
  - `specs/MOD-UX/SPEC-UX-v1.0.md` (v1.3)
  - `specs/MOD-UX/SPEC-UI-COMPONENTS.md` (v1.0 — NOVA)
  - `specs/MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (v1.0 — NOVA)
- **Epics Afetados:**
  - `docs/prd/epics/EPIC-001.md` — reaberto (active, Fase 0)
  - `docs/prd/epics/EPIC-013.md` — NOVO (draft)
- **Docs Perenes:**
  - `docs/02_AREAS/TuiModalDesign.md` — NOVO
- **Stories Concluídas:** Nenhuma (sessão só de documentação/planejamento)
- **Stories em Andamento:** Nenhuma
- **Stories Pendentes (15):**

| Story | Título | Épico | Esforço |
|-------|--------|-------|:-------:|
| STORY-042 | Resolver conflito atalho `g` | EPIC-001 (F0) | 1h |
| STORY-043 | Unificar UI RAG em `menus_rag.py` | EPIC-001 (F0) | 1h |
| STORY-044 | Conformidade UX `menus_rag.py` | EPIC-001 (F0) | 1h |
| STORY-045 | Corrigir emojis Unicode cp1252 | EPIC-001 (F0) | 1h |
| STORY-046 | Breadcrumb telas de diagnóstico | EPIC-001 (F0) | 1h |
| STORY-047 | Refatorar `__getattr__` MenuSystem | EPIC-001 (F0) | 1h |
| STORY-054 | ModalEngine + modo NORMAL | EPIC-013 (F1) | 4h |
| STORY-055 | Splits Ctrl+w | EPIC-013 (F1) | 4h |
| STORY-056 | Modo INSERT inline | EPIC-013 (F2) | 3h |
| STORY-057 | Modo VISUAL batch | EPIC-013 (F2) | 3h |
| STORY-058 | Temas configuráveis | EPIC-013 (F3) | 1h |
| STORY-059 | Keybindings configuráveis | EPIC-013 (F3) | 1h |
| STORY-060 | Modo de compatibilidade | EPIC-013 (F3) | 1h |
| STORY-061 | `:help` interno | EPIC-013 (F3) | 0.5h |
| STORY-062 | Testes E2E modal | EPIC-013 (F3) | 0.5h |

## 3. Estado do Código

- `foton_system/interfaces/cli/menus.py` — `__getattr__` frágil em MenuSystem (STORY-047)
- `foton_system/interfaces/cli/menus_rag.py` — 4 violações UX (STORY-044), UI duplicada (STORY-043)
- `foton_system/interfaces/cli/menus_config.py` — emojis cp1252 (STORY-045), UI RAG duplicada (STORY-043)
- `foton_system/interfaces/cli/menus_docs.py` — emojis cp1252 (STORY-045)
- `foton_system/interfaces/cli/menus.py` (dispatch) — conflito atalho `g` (STORY-042)
- `specs/MOD-RAG/SPEC-RAG-v1.0.md` — precisa atualizar RULE-RAG-8.4 (STORY-042)
- Nenhum arquivo de código foi alterado nesta sessão (apenas documentação)

## 4. Próximos Passos (To-Do)

1. **STORY-042** — Resolver conflito atalho `g` (global_search vs rag_query)
2. **STORY-043** — Unificar UI de indexação/consulta em `menus_rag.py`
3. **STORY-044** — Corrigir conformidade UX de `menus_rag.py` (error suggestions, PT-BR, f-strings, breadcrumb)
4. **STORY-045** — Substituir emojis por ASCII-safe em `menus_config.py` e `menus_docs.py`
5. **STORY-046** — Garantir breadcrumb em todas as telas de diagnóstico
6. **STORY-047** — Refatorar `__getattr__` para dispatch explícito com type hints
7. **STORY-054 a 062** — Implementação da interface modal (Fases 1-3)
8. Após cada story: `python -m pytest` — zero regressão obrigatório

## 5. Bloqueios e Decisões

- **Decisões tomadas:**
  - **Épicos:** EPIC-001 reaberto (Fase 0 — correções); EPIC-013 novo (Fases 1-3 — modal)
  - **Sprint única** (~25h total), ordem numérica (042→047→054→062)
  - **Split prefix:** auto-detect (`$TMUX` → Ctrl+b; fora → Ctrl+w); 3 camadas (settings > auto > fallback)
  - **Config:** `modal_split_prefix` + `modal_split_prefix_auto` em settings.json
  - **Script:** `foton_tmux_setup.sh` — idempotente, backup automático
  - **Emojis:** substituídos por `[+]`, `[-]`, `[=]` (ASCII-safe)
  - **f-strings obrigatórias:** `.format()` proibido em novos códigos
  - **Error handling:** `format_error_with_suggestion()` obrigatório em todo `except:`
  - **Renderização:** stdlib `curses` como backend primário
- **Bloqueios:** Nenhum
- **⚠️ Pendência:** validar se `upgrade_torch_to_cuda()` foi executado pelo usuário (não foi nesta sessão)

## 6. Contexto da Conversa (Resumo para Próximo Agente)

Esta sessão foi de **planejamento e documentação**. Partimos da completude do EPIC-004 (RAG) e identificamos 9 regressões TUI introduzidas durante o desenvolvimento do RAG. Criamos a documentação completa para a **reforma da interface**: Fase 0 corrige as regressões no EPIC-001, Fases 1-3 implementam a interface modal Vim+tmux no EPIC-013.

**Reestruturamos o Git por completo:**
- Branch legada `feat/info-naming-patterns` → `archive/sprint-1to9` (64 commits preservados)
- `develop` criada apontando para o mesmo HEAD (796c89f)
- `feat/ui-ux-redesign` criada como branch de trabalho (ativa atualmente)

**15 stories prontas para execução**, ordem numérica. Toda implementação de código (não documentação) começa agora. O handoff anterior (GPU/CUDA) está em `.opencode/handoffs/HANDOFF-2026-07-06e.md` — a instalação CUDA no VENP do AI Pack não foi executada pelo usuário.

## 7. Estrutura de Branches

```
main ──────── b847b04 (InfoNaming — congelado)
                 
archive/sprint-1to9 ── 796c89f (intocável, consulta futura)
   │
develop ──────────────── 796c89f (linha de integração)
   │
feat/ui-ux-redesign ──── 796c89f (★ ATIVA — todo trabalho novo aqui)
```
