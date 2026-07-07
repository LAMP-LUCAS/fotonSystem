---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-061: `:help` interno e documentação de bordo

**Épico:** EPIC-013 (Fase 3)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-6.8)
**Estimativa:** 0.5h

## Descrição

Implementar o sistema de ajuda interna (`:help`) que abre um buffer de documentação
completa sobre modos, comandos, keybindings e exemplos de composição.

## Regras Implementadas

- **RULE-TUI-6.8:** `:help` abre buffer de ajuda com cobertura completa

## Conteúdo do `:help`

```
============================================================
  FOTON SYSTEM — HELP
============================================================

1. Modos
   NORMAL   — Navegacao, busca (/), comando (:)
   INSERT   — Edicao de texto (i, a, o)
   VISUAL   — Selecao multipla (v, V, Ctrl+v)
   COMANDO  — Linha de comando (:)

2. Comandos :
   :e [path]     Abrir recurso (ex: :e cliente/FULANO)
   :q            Fechar split / voltar
   :q!           Fechar sem salvar
   :w            Salvar alteracoes
   :help         Esta ajuda
   :split [path] Split horizontal + abrir
   :vsplit [path] Split vertical + abrir
   :bd           Fechar buffer
   :noh          Limpar realce de busca
   :set [k]=[v]  Configurar (ex: :set theme=dark)

3. Navegacao (Modo NORMAL)
   j/k           Cima/baixo
   h/l           Esquerda/direita (ou tree fold/unfold)
   gg/G          Topo/final do buffer
   Ctrl+d/u      Meia pagina
   /texto        Buscar
   n/N           Proximo/anterior match

4. Splits (Ctrl+w)
   s/v           Split horizontal/vertical
   w             Ciclar splits
   h/j/k/l       Navegar direcao
   q             Fechar split
   o             So este split
   =             Equalizar

5. Modo INSERT
   i/a/o         Entrar (cursor/append/nova linha)
   Esc           Voltar ao NORMAL
   Ctrl+w        Apagar palavra
   Ctrl+u        Apagar linha

6. Modo VISUAL
   v/V/Ctrl+v    Ativar visual
   j/k           Expandir selecao
   :d            Excluir selecionados
   :g            Gerar docs selecionados
   :e            Abrir selecionados em splits
   :y            Copiar selecionados

7. Exemplos de Composicao
   :e fulano               → Abrir ficha do Fulano
   :vsplit financeiro      → Abrir financeiro ao lado
   /relatorio n n :e       → Buscar, navegar, abrir
   v j j j :g              → Selecionar 3 e gerar docs
```

## Critérios de Aceite

- [ ] `:help` abre buffer no split atual
- [ ] Ajuda cobre: modos, comandos `:`, navegação, splits, INSERT, VISUAL, exemplos
- [ ] Navegação normal (j/k, gg/G, /busca) funciona dentro do buffer de ajuda
- [ ] `:q` fecha o buffer de ajuda
- [ ] Testes: `test_help_buffer_content`, `test_help_buffer_navigation`, `test_help_buffer_close`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (Modo NORMAL funcional)

## Estimativa

0.5h
