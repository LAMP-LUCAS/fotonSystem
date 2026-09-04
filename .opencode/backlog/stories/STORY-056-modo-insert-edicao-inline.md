---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-056: Modo INSERT — edição inline

**Épico:** EPIC-013 (Fase 2)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-4.x)
**Estimativa:** 3h

## Descrição

Implementar o modo INSERT da interface modal, permitindo edição de dados inline no buffer ativo.
Para formulários pequenos (≤ 10 campos), edição direta; para formulários grandes, delega para editor externo.

## Regras Implementadas

- **RULE-TUI-4.1 a 4.11:** Modo INSERT (entrada de dados, inline/external, validação)

## Funcionalidades

### Ativação
- `i` → INSERT no cursor
- `a` → INSERT após cursor
- `o` → nova linha + INSERT

### Teclas em INSERT
- Toda tecla imprimível → insere texto
- `Enter` → quebra linha
- `Backspace` → apaga anterior
- `Delete` → apaga sob cursor
- `Ctrl+w` → apaga palavra anterior
- `Ctrl+u` → apaga até início da linha
- `Esc` → volta ao NORMAL

### Inline vs External

| Critério | Comportamento |
|----------|---------------|
| ≤ 10 campos editáveis | Edição inline no buffer |
| > 10 campos | `:e [editor] [path]` (editor configurável) |
| Editor default (Win) | `notepad` |
| Editor default (Linux/Mac) | `vim` |
| Config | `settings.json → modal_external_editor` |

### Validação
- Ao salvar (`:w`), buffer é validado antes de persistir
- Se inválido, erro na message bar e permanece em INSERT
- Validação usa as mesmas funções de validação dos handlers existentes

## Critérios de Aceite

- [ ] `i`, `a`, `o` entram em modo INSERT nas posições corretas
- [ ] Teclas imprimíveis inserem texto
- [ ] `Enter` quebra linha
- [ ] `Backspace` e `Delete` funcionam
- [ ] `Ctrl+w` apaga palavra anterior
- [ ] `Ctrl+u` apaga até início da linha
- [ ] `Esc` retorna ao NORMAL
- [ ] ≤ 10 campos: edição inline funcional
- [ ] > 10 campos: `:e` abre editor externo
- [ ] Validação ao salvar com `:w`
- [ ] Status bar mostra `[ INSERT ]` em verde reverso
- [ ] Testes: `test_insert_mode_enter_exit`, `test_insert_text`, `test_insert_special_keys`, `test_insert_external_editor`, `test_insert_validation`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (Modo NORMAL funcional)
- STORY-055 (Splits — opcional, mas desejável para testar edição em split)

## Estimativa

3h
