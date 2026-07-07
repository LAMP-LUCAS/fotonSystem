---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-054: ModalEngine — classe central e modo NORMAL base

**Épico:** EPIC-013 (Fase 1)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-1.x, 2.x, 6.x, 7.x)
**Estimativa:** 4h

## Descrição

Implementar o núcleo da interface modal: `ModalEngine`, modo NORMAL funcional (navegação
`j/k/h/l/gg/G/Ctrl+d/Ctrl+u`), busca `/` e linha de comando `:` com comandos básicos.

## Regras Implementadas

- **RULE-TUI-1.1 a 1.6:** ModalEngine (classe central, initialização, fallback)
- **RULE-TUI-2.1 a 2.20:** Modo NORMAL (navegação, busca, comando)
- **RULE-TUI-6.1 a 6.9:** Linha de comando `:` 
- **RULE-TUI-7.1 a 7.7:** Busca `/`

## Estrutura de Arquivos

```
foton_system/interfaces/modal/
├── __init__.py
├── engine.py          # ModalEngine
├── modes.py           # Enum Mode + lógica de transição
├── buffer.py          # Buffer (dado carregado)
├── cmdline.py         # Linha de comando (:)
├── search.py          # Busca (/)
├── ui.py              # Status bar, message bar
└── compatibility.py   # Fallback
```

## Critérios de Aceite

- [ ] ModalEngine inicializa com settings.json (lê `modal_enabled`, `modal_theme`, etc.)
- [ ] Se `modal_enabled: false`, fallback total para menus hierárquicos
- [ ] Modo NORMAL é o modo padrão ao entrar
- [ ] `j`/`k` movem cursor para baixo/cima
- [ ] `h`/`l` navegam entre elementos (tree expand/retract ou split direction)
- [ ] `gg` e `G` navegam para topo/final do buffer
- [ ] `Ctrl+d`/`Ctrl+u` movem meia página
- [ ] `Enter` ativa item sob cursor
- [ ] `/` abre search bar; Enter executa; `n`/`N` navega matches
- [ ] `:` abre cmdline; comandos `:e`, `:q`, `:w`, `:help` funcionam
- [ ] `:help` abre buffer de ajuda
- [ ] `:e [path]` abre recurso (cliente, serviço, documento)
- [ ] Status bar exibe modo + contexto
- [ ] Message bar exibe feedback
- [ ] Tab autocomplete em `:e` e `/`
- [ ] Carga da interface modal < 500ms
- [ ] Renderização de buffer 1000 linhas < 200ms
- [ ] Testes: `test_modal_engine_init`, `test_normal_mode_navigation`, `test_search`, `test_cmdline`
- [ ] Zero regressão na suite existente (1020+ testes)

## Dependências

- Fase 0 completa (STORY-042 a 047)

## Estimativa

4h
