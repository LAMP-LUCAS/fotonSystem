---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-059: Keybindings configuráveis

**Épico:** EPIC-013 (Fase 3)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-8.3)
**Estimativa:** 1h

## Descrição

Permitir que keybindings sejam configurados via `settings.json → modal_keybindings`.
Isso resolve o risco de conflito com tmux nativo e permite que cada usuário
personalize os atalhos.

## Regras Implementadas

- **RULE-TUI-8.3:** `modal_keybindings` em settings.json com subseções `normal` e `ctrl_w`

## Funcionalidades

### Formato

```json
{
  "modal_keybindings": {
    "normal": {
      "j": "cursor_down",
      "k": "cursor_up",
      "Ctrl+j": "cursor_down_5",  // custom: desce 5 linhas
      "Ctrl+k": "cursor_up_5"     // custom: sobe 5 linhas
    },
    "ctrl_w": {
      "s": "split_horizontal",
      "v": "split_vertical",
      "|": "split_vertical_right"  // custom: tmux-like
    }
  }
}
```

### Comportamento

- Keybindings não configurados usam o padrão (TuiModalDesign.md §6)
- Se uma tecla não é reconhecida, exibe aviso e usa default
- Validação na inicialização: teclas conflitantes são reportadas
- `:help` mostra keybindings atuais (padrão + customizações)

## Critérios de Aceite

- [ ] `modal_keybindings` lido de settings.json na inicialização
- [ ] Subseções `normal` e `ctrl_w` suportadas
- [ ] Teclas não configuradas usam default
- [ ] Validação de conflitos na inicialização
- [ ] `:help` mostra keybindings atuais
- [ ] Testes: `test_keybindings_load`, `test_keybindings_default_fallback`, `test_keybindings_conflict_detection`, `test_keybindings_help`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (ModalEngine)

## Estimativa

1h
