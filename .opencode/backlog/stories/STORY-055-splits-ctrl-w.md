---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-055: Sistema de splits (Ctrl+w)

**Épico:** EPIC-013 (Fase 1)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-3.x)
**Estimativa:** 4h

## Descrição

Implementar o sistema de splits da interface modal, inspirado no tmux, com prefixo `Ctrl+w`.
Cada split contém um buffer independente com scroll e cursor próprios.

## Regras Implementadas

- **RULE-TUI-3.1 a 3.16:** Todos os comandos de split (Ctrl+w s/v/w/h/j/k/l/H/J/K/L/q/o=+/-/</>)

## Funcionalidades

### Comandos Obrigatórios

| Atalho | Ação |
|--------|------|
| `Ctrl+w s` | Split horizontal |
| `Ctrl+w v` | Split vertical |
| `Ctrl+w w` | Ciclar entre splits |
| `Ctrl+w h/j/k/l` | Navegar para split na direção |
| `Ctrl+w H/J/K/L` | Mover split para extremo |
| `Ctrl+w q` | Fechar split atual |
| `Ctrl+w o` | Fechar todos exceto atual |
| `Ctrl+w =` | Equalizar tamanhos |
| `Ctrl+w + -` | Aumentar/diminuir altura |
| `Ctrl+w < >` | Aumentar/diminuir largura |

### Comportamento

- Cada split tem `Buffer` independente (scroll, cursor, conteúdo)
- Split ativo tem borda clara; inativos têm borda escura
- Mínimo 4 splits simultâneos
- Ao fechar o último split, volta ao estado de buffer único (não fecha o sistema)
- Divisão mínima: 20 colunas x 5 linhas por split
- Se terminal for < 80x24, splits são desabilitados com aviso

## Critérios de Aceite

- [ ] `Ctrl+w s` divide horizontalmente
- [ ] `Ctrl+w v` divide verticalmente  
- [ ] `Ctrl+w w` alterna foco entre splits (cíclico)
- [ ] `Ctrl+w h/j/k/l` navega para direção correta
- [ ] `Ctrl+w q` fecha split atual
- [ ] `Ctrl+w o` mantém apenas o atual
- [ ] `Ctrl+w =` equaliza tamanhos
- [ ] `Ctrl+w +/-` redimensiona altura; `Ctrl+w </>` redimensiona largura
- [ ] Split ativo tem borda clara; inativos têm borda escura
- [ ] Cada split mantém scroll independente
- [ ] 4+ splits simultâneos suportados
- [ ] Splits desabilitados em terminal < 80x24 com aviso
- [ ] Navegação entre splits < 100ms
- [ ] Testes: `test_split_create_horizontal`, `test_split_create_vertical`, `test_split_navigation`, `test_split_resize`, `test_split_close`, `test_split_min_terminal_size`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (ModalEngine + modo NORMAL)

## Estimativa

4h
