---
type: concept
domain: core
status: draft
tags: [modal, tui, vim, tmux, navigation, ux]
---

# EPIC-013: Interface Modal (Vim+tmux)

**Data:** 2026-07-06
**Stakeholders:** Equipe do escritório (usuários avançados da TUI), Time Core (implementação)
**Métrica de Sucesso:** Redução de 50% no tempo médio de navegação para ações comuns vs TUI hierárquica

## Dor Atual

A interface TUI atual é estritamente hierárquica (menu → submenu → ação → volta). Isso gera:

- **Fricção narrativa:** Para executar 3 ações em clientes diferentes, o usuário navega 3× o mesmo caminho
- **Custo de contexto:** Cada submenu exige releitura das opções — não há posicionamento persistente
- **Ausência de composição:** Não é possível encadear comandos (ex: "buscar CLIENTE-X e abrir ficha")
- **Barreira de escala:** Usuários avançados não têm atalhos — todos navegam igual (iniciantes e experts)
- **Split ausente:** Não há visão simultânea de duas telas (ex: ficha do cliente + financeiro lado a lado)
- **Feedback passivo:** O sistema espera input sem sinalizar estado — o usuário nunca sabe "o que posso fazer agora"

A interface modal resolve esses problemas adotando o paradigma **Vim + tmux**, onde o usuário está sempre em um modo ativo, com comandos de tecla única e splits gerenciáveis.

## Visão Geral

Migrar progressivamente de menus hierárquicos para uma interface modal inspirada em Vim + tmux:

```
┌─────────────────────────────────────────────────────────┐
│  FOTON SYSTEM — [NORMAL]  cliente: FULANO v           │ ← status bar
├────────────────────────────┬────────────────────────────┤
│  INFO-CLIENTE              │  FINANCEIRO                │ ← split horizontal
│  Nome: FULANO DE TAL      │  Saldo: R$ 15.000,00      │
│  NIF: 12.345.678/0001-90  │  Última: 05/07 - R$ 3.000 │
│  Tel: (62) 99999-0000     │                            │
│                           │                            │
│  :e servicos              │  :q                        │ ← command line
└────────────────────────────┴────────────────────────────┘
```

### Filosofia

| Princípio | Descrição |
|-----------|-----------|
| **Modos explícitos** | Toda ação tem um modo (NORMAL, INSERT, VISUAL, COMANDO). O usuário sabe em que modo está. |
| **Tecla única** | Comandos frequentes são uma tecla só (navegação, ações) |
| **Composição** | Comandos podem ser encadeados (`/busca enter :e` — busca e abre ficha) |
| **Splits visíveis** | Múltiplas visões simultâneas sem perder contexto |
| **Sem hierarquia fixa** | O usuário decide o que vê, não o menu |

## Fases

### Fase 0 — Correção de Regressões (EPIC-001)

Antes de evoluir, o EPIC-001 precisa ser estabilizado. As 9 regressões identificadas (R1-R9) são pré-requisito para qualquer mudança modal.

**Stories:** STORY-042 a STORY-047 (6 stories, ~6h)
**Spec:** SPEC-UX-v1.1 (RULE-UX-8.9 a 8.12)

### Fase 1 — Modo Normal Base (~8h)

Núcleo da interface modal: modo NORMAL funcional com splits, navegação e linha de comando.

**Features:**
- Modo NORMAL como modo padrão ao entrar no sistema
- Status bar modo-consciente: `[NORMAL]`, `[INSERT]`, `[VISUAL]`, `[COMANDO]`
- Navegação por tecla única: `j/k` (cima/baixo), `h/l` (expandir/retrair), `Ctrl+d/u` (meia página), `gg`/`G` (topo/fim)
- Sistema de splits: `Ctrl+w s` (split horizontal), `Ctrl+w v` (split vertical), `Ctrl+w w` (alternar), `Ctrl+w q` (fechar)
- Linha de comando `:`: `:e [caminho]` (abrir recurso), `:q` (fechar split/voltar), `:w` (salvar), `:help`
- Busca `/`: busca full-text com realce e navegação `n`/`N`
- Display unificado de dados em vez de menus hierárquicos

**Stories:** STORY-054 e STORY-055 (2 stories)
**Spec:** SPEC-TUI-MODAL-v1.0 (RULE-TUI-1.x, 2.x)

### Fase 2 — Modos Insert e Visual (~6h)

**Features:**
- Modo INSERT (`i`): entrada de dados inline no recurso ativo. Para formulários < 10 campos, edição inline. Para > 10 campos, abre `:e [editor] [path]`.
- Modo VISUAL (`v`): seleção múltipla de itens com ações batch: `:d` (delete marcados), `:g` (gerar documento para marcados), `:e` (abrir marcados em novos splits)
- Comandos batch com confirmação antes da execução
- Indicador `[VISUAL] 3 itens selecionados` na status bar

**Stories:** STORY-056 e STORY-057 (2 stories)
**Spec:** SPEC-TUI-MODAL-v1.0 (RULE-TUI-3.x, 4.x, 5.x)

### Fase 3 — Polish e Configuração (~4h)

**Features:**
- Tema escuro com cores configuráveis (via `settings.json`: `modal_theme`, `modal_colors`)
- Keybindings configuráveis (via `settings.json`: `modal_keybindings`)
- Modo de compatibilidade (fallback para menus hierárquicos para usuários que preferirem)
- Documentação de bordo (`:help` interno + man page)
- Testes E2E da interface modal

**Stories:** STORY-058 a STORY-062 (5 stories)
**Spec:** SPEC-TUI-MODAL-v1.0 (RULE-TUI-6.x, 7.x, 8.x)

## Critérios de Sucesso

- [ ] Fase 0: 9 regressões corrigidas, zero pre-existing test failures
- [ ] Fase 1: Modo NORMAL funcional com splits e linha de comando `:`
- [ ] Fase 1: Status bar modo-consciente visível em tempo real
- [ ] Fase 2: Edição inline funcional no modo INSERT
- [ ] Fase 2: Seleção batch funcional no modo VISUAL
- [ ] Fase 2: Comandos batch com confirmação antes da execução
- [ ] Fase 3: Temas configuráveis aplicados sem refresh
- [ ] Fase 3: Keybindings customizáveis via settings.json
- [ ] Fase 3: Modo de compatibilidade (fallback menus hierárquicos)
- [ ] Fase 3: `:help` interno cobre todos os comandos e modos
- [ ] Zero regressão na suite de testes existente (1020+ testes)
- [ ] Navegação entre splits < 200ms (qualquer ação)
- [ ] Carga da interface modal < 500ms

## Métricas

| Métrica | Atual (TUI) | Alvo (Modal) |
|---------|-------------|--------------|
| Tempo médio para abrir ficha de cliente | ~12s (3 navegações) | < 5s (1 comando) |
| Ações por minuto (usuário avançado) | 3-4 | 8-12 |
| Toques por ação comum | 8-15 | 2-5 |
| Splits simultâneos | 0 (navegação linear) | 2-4 |
| Curva de aprendizado (expert) | 0 (igual iniciante) | ~30min (atalhos) |
| **NPS usabilidade interna** | ≥ 7 (atual) | ≥ 9 |

## Dependências

- **EPIC-001 (Fase 0):** Correção de regressões é pré-requisito obrigatório
- **SPEC-TUI-MODAL-v1.0:** Deve estar finalizada antes do início da Fase 1
- **Menus modulares (RULE-UX-8.1):** `menus_clients.py`, `menus_finance.py`, `menus_docs.py`, `menus_config.py` já separados
- **Sem dependência externa:** Toda implementação é stdlib Python (curses via `tui_layout.py` já existente, ou `rich` se necessário)

## Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|:-----------:|:-------:|-----------|
| Usuários resistentes à mudança de paradigma | Alta | Médio | Modo de compatibilidade (Fase 3) |
| Complexidade de splits em terminais Windows | Média | Alto | Testar em cmd.exe e Windows Terminal; fallback para sem splits |
| Regressões na suite de 1020+ testes | Média | Alto | CI obrigatório; Fase 0 garante base estável |
| Curva de aprendizado íngreme | Alta | Baixo | `:help` interno + cheatsheet + documentação |
| Conflito de atalhos com tmux nativo | Baixa | Baixo | Auto-detect: dentro do tmux usa Ctrl+b, fora usa Ctrl+w. Script foton_tmux_setup.sh configura tmux para Ctrl+b. Prefixo configurável via settings.json. Três camadas de fallback. |

## Histórico

| Data | Evento |
|------|--------|
| 2026-07-06 | EPIC-013 criado com escopo de interface modal Vim+tmux |
| 2026-07-06 | Fase 0 (regressões) delegada ao EPIC-001; EPIC-013 inicia na Fase 1 |

## Especificações Técnicas

- SPEC-TUI-MODAL-v1.0 (8 áreas, ~40 RULE-IDs)
- SPEC-UX-v1.1 (compatibilidade com novos RULE-IDs)
- TuiModalDesign.md (conceitos perenes de design modal)
- SPEC-UI-COMPONENTS.md (catálogo de padrões visuais)
