---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-057: Modo VISUAL — seleção e ações batch

**Épico:** EPIC-013 (Fase 2)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-5.x)
**Estimativa:** 3h

## Descrição

Implementar o modo VISUAL da interface modal, permitindo seleção múltipla de itens
e execução de ações batch (excluir, gerar documentos, abrir em splits, copiar).

## Regras Implementadas

- **RULE-TUI-5.1 a 5.8:** Modo VISUAL (seleção, comandos batch)

## Funcionalidades

### Ativação
- `v` → modo VISUAL (seleção por caractere)
- `V` → modo VISUAL (seleção por linha)
- `Ctrl+v` → modo VISUAL (seleção por bloco retangular)

### Navegação (expande seleção)
- `j`/`k` adiciona linhas à seleção
- `gg` seleciona do cursor ao topo
- `G` seleciona do cursor ao final
- `Ctrl+d`/`Ctrl+u` adiciona meia página

### Comandos Batch
| Comando | Ação | Comportamento |
|---------|------|---------------|
| `:d` | Excluir marcados | Confirmação S/N obrigatória |
| `:g` | Gerar documento | Abre wizard de template + confirmação |
| `:e` | Abrir em splits | Máx 4 splits; excede exibe aviso |
| `:y` | Copiar para clipboard | Copia para área de transferência interna |

### Confirmação
Toda ação batch exibe:
```
  Acao sera aplicada a N itens. Confirmar? (S/N): _
```

Após confirmação, `ProgressTracker` exibe progresso:
```
[3/10] Gerando documento...
[10/10] Documentos gerados com sucesso!
```

### Visual
- Itens selecionados em azul reverso
- Status bar: `[ VISUAL ] 3 itens selecionados`
- Cursor muda visualmente para indicar modo de seleção

## Critérios de Aceite

- [ ] `v`, `V`, `Ctrl+v` entram em modo VISUAL corretamente
- [ ] Navegação expande seleção
- [ ] `Esc` sai do modo VISUAL sem ação
- [ ] `:d` exclui itens selecionados com confirmação
- [ ] `:g` gera documentos com wizard de template
- [ ] `:e` abre itens em splits (máx 4)
- [ ] `:y` copia para clipboard interno
- [ ] Confirmação exibida antes de toda ação batch
- [ ] ProgressTracker mostra progresso durante ações batch
- [ ] Após execução, volta ao modo NORMAL
- [ ] Status bar mostra `[ VISUAL ] N itens selecionados`
- [ ] Testes: `test_visual_mode_enter_exit`, `test_visual_selection_expand`, `test_visual_batch_delete`, `test_visual_batch_generate`, `test_visual_batch_open_splits`, `test_visual_batch_copy`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (Modo NORMAL funcional)
- STORY-055 (Splits — obrigatório para `:e`)

## Estimativa

3h
