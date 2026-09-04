---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-058: Temas configuráveis

**Épico:** EPIC-013 (Fase 3)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-8.1, 8.2, 8.6, 8.9)
**Estimativa:** 1h

## Descrição

Implementar 3 temas pré-definidos (dark, light, high_contrast) e permitir
configuração de cores via settings.json e `:set theme=<name>` em tempo real.

## Regras Implementadas

- **RULE-TUI-8.1:** `modal_theme` em settings.json (dark|light|high_contrast)
- **RULE-TUI-8.2:** `modal_colors` com chaves específicas
- **RULE-TUI-8.6:** Aplicação em tempo real via `:set`
- **RULE-TUI-8.9:** `modal_themes.json` em `foton_system/interfaces/modal/themes/`

## Estrutura

```
foton_system/interfaces/modal/themes/
├── __init__.py       # Carrega temas, Theme class
├── base.py           # Classe Theme (namedtuple ou dataclass)
├── themes.json       # Pré-definições: dark, light, high_contrast
```

### `themes.json`
```json
{
  "dark": {
    "bg": "black",
    "fg": "white",
    "status": "cyan",
    "cmdline": "yellow",
    "search_highlight": "yellow",
    "visual_select": "blue",
    "split_separator": "bright_black",
    "error": "red",
    "warning": "yellow",
    "success": "green"
  },
  "light": {
    "bg": "white",
    "fg": "black",
    ...
  },
  "high_contrast": {
    "bg": "black",
    "fg": "white",
    ...
  }
}
```

## Critérios de Aceite

- [ ] 3 temas pré-definidos em `themes.json`: dark, light, high_contrast
- [ ] `:set theme=light` aplica tema em tempo real (sem restart)
- [ ] Temas inválidos exibem erro na message bar
- [ ] Cores personalizadas via `settings.json → modal_colors` sobrescrevem tema
- [ ] Testes: `test_themes_loaded`, `test_theme_switch_realtime`, `test_theme_invalid`, `test_custom_colors_override`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (ModalEngine)

## Estimativa

1h
