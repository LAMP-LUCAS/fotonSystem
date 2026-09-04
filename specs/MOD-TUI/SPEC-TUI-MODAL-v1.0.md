# Spec: Interface Modal Vim+tmux

**Data:** 2026-07-06
**Versão:** 1.0
**Responsável:** Time Core
**Épico:** EPIC-013
**Componentes:** SPEC-UI-COMPONENTS.md, SPEC-UX-v1.x, TuiModalDesign.md

## 1. Problema

A TUI hierárquica atual (SPEC-UX-v1.2) resolve problemas de usabilidade, mas não de eficiência:
- Navegação excessiva para ações comuns (3-4 submenus por ação)
- Impossibilidade de visão simultânea (splits)
- Usuários avançados não têm atalhos diferenciais
- Não há composição de comandos

## 2. Solução Proposta

Adotar o paradigma de interface modal inspirado em Vim + tmux, com 4 modos (NORMAL, INSERT, VISUAL, COMANDO),
sistema de splits e barra de status modo-consciente.

### 2.1 Estratégia de Migração

A implementação é incremental em 3 fases:

| Fase | Foco | Stories | Esforço | Depende de |
|------|------|---------|---------|------------|
| 0 | Correção de regressões do EPIC-001 | STORY-042 a 047 | ~6h | -- |
| 1 | Modo NORMAL base (splits, navegação, `:`, `/`) | STORY-054, 055 | ~8h | Fase 0 |
| 2 | Modos INSERT e VISUAL | STORY-056, 057 | ~6h | Fase 1 |
| 3 | Polish, temas, compatibilidade | STORY-058 a 062 | ~4h | Fase 2 |

> **Importante:** A Fase 0 (correção de regressões) é executada no escopo do EPIC-001.
> As Fases 1-3 são o escopo do EPIC-013.

## 3. Regras de Negócio

### 3.1 Arquitetura do Sistema Modal (RULE-TUI-1.x)

- **RULE-TUI-1.1:** `ModalEngine` é a classe central que gerencia: modo atual, buffer ativo, splits, status bar, cmdline e message bar.
- **RULE-TUI-1.2:** `ModalEngine` DEVE ser inicializado com `settings.json` para carregar: `modal_enabled`, `modal_theme`, `modal_colors`, `modal_keybindings`.
- **RULE-TUI-1.3:** Se `modal_enabled: false`, o sistema DEVE carregar os handlers de menu hierárquico originais (fallback total).
- **RULE-TUI-1.4:** O modo padrão ao entrar no sistema DEVE ser NORMAL (se `modal_enabled: true`).
- **RULE-TUI-1.5:** `ModalEngine` DEVE expor: `current_mode`, `buffers[]`, `splits[]`, `active_buffer`, `active_split`.
- **RULE-TUI-1.6:** A inicialização do modal NÃO DEVE quebrar a suite de testes existente (1020+ testes).

### 3.2 Modo NORMAL (RULE-TUI-2.x)

- **RULE-TUI-2.1:** No modo NORMAL, teclas de navegação e comandos de tecla única são interpretados. Letras sem mapeamento são no-op.
- **RULE-TUI-2.2:** `j`/`k` movem o cursor para baixo/cima no buffer ativo. Funciona como setas para baixo/cima.
- **RULE-TUI-2.3:** `h`/`l` recolhem/expandem nós (se o buffer suportar tree view) ou movem para split esquerdo/direito.
- **RULE-TUI-2.4:** `gg` leva ao topo do buffer; `G` leva ao final.
- **RULE-TUI-2.5:** `Ctrl+d` move meia página para baixo; `Ctrl+u` move meia página para cima.
- **RULE-TUI-2.6:** `Enter` seleciona/ativa o item sob o cursor. O comportamento depende do tipo de buffer:
  - Lista de clientes → abre ficha do cliente
  - Item de menu → executa ação
  - Link → navega para o recurso
- **RULE-TUI-2.7:** `Space` alterna fold/expansão de seções no buffer.
- **RULE-TUI-2.8:** `Esc` limpa seleção atual ou realce de busca. Se já limpo, permanece em NORMAL.
- **RULE-TUI-2.9:** `i` entra em modo INSERT (cursor na posição atual).
- **RULE-TUI-2.10:** `a` entra em modo INSERT (cursor após posição atual).
- **RULE-TUI-2.11:** `o` abre nova linha abaixo do cursor e entra em modo INSERT.
- **RULE-TUI-2.12:** `v` entra em modo VISUAL (seleção por caractere).
- **RULE-TUI-2.13:** `V` entra em modo VISUAL (seleção por linha).
- **RULE-TUI-2.14:** `Ctrl+v` entra em modo VISUAL (seleção por bloco retangular).
- **RULE-TUI-2.15:** `n` navega para próximo match de busca; `N` navega para match anterior.
- **RULE-TUI-2.16:** `/` abre a search bar na cmdline. Após digitar e pressionar Enter, resultados são realçados no buffer.
- **RULE-TUI-2.17:** `:` abre a linha de comando. Após digitar e pressionar Enter, o comando é executado.
- **RULE-TUI-2.18:** A barra de status DEVE exibir: modo atual, nome do buffer ativo, número de linhas, hora atual.
- **RULE-TUI-2.19:** A message bar DEVE exibir feedback de ações (resultado, erro, notificação) por no máximo 5 segundos ou até o próximo comando.
- **RULE-TUI-2.20:** Status bar e message bar NÃO DEVEM consumir linhas do conteúdo do buffer.

### 3.3 Splits (RULE-TUI-3.x)

O prefixo de splits é variável conforme o ambiente, denotado como `{SPLIT}`.

- **RULE-TUI-3.1:** Todos os comandos de split usam o prefixo ativo `{SPLIT}` seguido de uma tecla.
- **RULE-TUI-3.2:** `{SPLIT} s` divide o split atual horizontalmente (split acima/abaixo).
- **RULE-TUI-3.3:** `{SPLIT} v` divide o split atual verticalmente (split esquerda/direita).
- **RULE-TUI-3.4:** `{SPLIT} w` alterna o foco entre splits (ordem cíclica).
- **RULE-TUI-3.5:** `{SPLIT} h/j/k/l` navega o foco para o split na direção indicada.
- **RULE-TUI-3.6:** `{SPLIT} H/J/K/L` move o split atual para a posição extrema na direção indicada.
- **RULE-TUI-3.7:** `{SPLIT} q` fecha o split atual. Se for o último split, volta ao estado de split único (não fecha o sistema).
- **RULE-TUI-3.8:** `{SPLIT} o` fecha todos os splits exceto o atual (deixar apenas o atual).
- **RULE-TUI-3.9:** `{SPLIT} =` equaliza o tamanho de todos os splits.
- **RULE-TUI-3.10:** `{SPLIT} +` aumenta altura do split atual em 1 linha; `{SPLIT} -` diminui.
- **RULE-TUI-3.11:** `{SPLIT} >` aumenta largura do split atual em 1 coluna; `{SPLIT} <` diminui.
- **RULE-TUI-3.12:** O sistema DEVE suportar no mínimo 4 splits simultâneos.
- **RULE-TUI-3.13:** O split ativo DEVE ter borda clara; splits inativos DEVEM ter borda escura.
- **RULE-TUI-3.14:** Em terminais que não suportam bordas, usar caracteres ASCII: `-` e `|`.
- **RULE-TUI-3.15:** Cada split contém um buffer independente com seu próprio scroll e cursor.
- **RULE-TUI-3.16:** Navegação entre splits DEVE levar < 100ms.

### 3.3a Determinação Automática do Prefixo de Split (RULE-TUI-3a.x)

- **RULE-TUI-3a.1:** `{SPLIT}` é determinado na inicialização do `ModalEngine` pela função `_detect_split_prefix()`.
- **RULE-TUI-3a.2:** `_detect_split_prefix()` DEVE consultar `os.environ.get("TMUX")`. Se retornar string não vazia, o ambiente está dentro do tmux.
- **RULE-TUI-3a.3:** Dentro do tmux, o prefixo automático DEVE ser `Ctrl+b` (alternativa oficial do tmux, sem conflito).
- **RULE-TUI-3a.4:** Fora do tmux, o prefixo automático DEVE ser `Ctrl+w` (padrão Neovim).
- **RULE-TUI-3a.5:** O settings.json DEVE suportar `modal_split_prefix` (str, opcional). Se definido, sobrescreve o auto-detect.
- **RULE-TUI-3a.6:** O settings.json DEVE suportar `modal_split_prefix_auto` (bool, default: true). Se `false`, o auto-detect é desligado e usa-se o valor de `modal_split_prefix` ou o fallback `Ctrl+w`.
- **RULE-TUI-3a.7:** A precedência é: `settings.json modal_split_prefix` (se definido) → auto-detect (se ativado) → fallback `Ctrl+w`.
- **RULE-TUI-3a.8:** O prefixo ativo DEVE ser exposto no help (`:help`) e na message bar durante comandos de split.
- **RULE-TUI-3a.9:** O script `scripts/foton_tmux_setup.sh` DEVE ser fornecido para configurar o tmux com prefixo `Ctrl+b` (idempotente, com backup automático).

### 3.4 Modo INSERT (RULE-TUI-4.x)

- **RULE-TUI-4.1:** No modo INSERT, toda tecla imprimível é inserida como texto no buffer.
- **RULE-TUI-4.2:** `Esc` sai do modo INSERT e volta ao NORMAL.
- **RULE-TUI-4.3:** `Enter` quebra a linha no cursor.
- **RULE-TUI-4.4:** `Backspace` apaga caractere anterior ao cursor.
- **RULE-TUI-4.5:** `Delete` apaga caractere sob o cursor.
- **RULE-TUI-4.6:** `Ctrl+w` apaga palavra anterior ao cursor.
- **RULE-TUI-4.7:** `Ctrl+u` apaga tudo do cursor até o início da linha.
- **RULE-TUI-4.8:** Para buffers com ≤ 10 campos editáveis, a edição DEVE ser inline (no próprio buffer).
- **RULE-TUI-4.9:** Para buffers com > 10 campos, o modo INSERT DEVE oferecer `:e [editor] [path]` para edição externa. O editor padrão é configurável em `settings.json` → `modal_external_editor` (default: notepad no Windows, vim no Linux/Mac).
- **RULE-TUI-4.10:** Ao salvar com `:w`, o buffer DEVE ser validado antes de persistir. Se inválido, erro na message bar e permanece em INSERT.
- **RULE-TUI-4.11:** A status bar DEVE mostrar `[ INSERT ]` em verde reverso durante o modo INSERT.

### 3.5 Modo VISUAL (RULE-TUI-5.x)

- **RULE-TUI-5.1:** No modo VISUAL, navegação (j/k, gg/G, Ctrl+d/u) EXPANDE a seleção.
- **RULE-TUI-5.2:** A status bar DEVE mostrar `[ VISUAL ] N itens selecionados` em azul reverso, onde N é o número de itens/lines selecionados.
- **RULE-TUI-5.3:** `Esc` sai do modo VISUAL sem executar ação (volta ao NORMAL).
- **RULE-TUI-5.4:** Ao pressionar `:` no modo VISUAL, o cmdline deve prefixar com `:'<,'>` indicando range visual.
- **RULE-TUI-5.5:** Comandos disponíveis no modo VISUAL:
  - `:d` → Excluir itens selecionados (com confirmação S/N)
  - `:g` → Gerar documento para itens selecionados (abre wizard de template)
  - `:e` → Abrir cada item selecionado em um novo split (máx. 4)
  - `:y` → Copiar itens selecionados para área de transferência interna
- **RULE-TUI-5.6:** Toda ação batch (`:d`, `:g`, `:e`, `:y`) DEVE exibir confirmação antes de executar: `"Acao sera aplicada a N itens. Confirmar? (S/N): "`
- **RULE-TUI-5.7:** Comandos batch DEVEM usar `ProgressTracker` para feedback visual.
- **RULE-TUI-5.8:** Após execução do comando, o modo VISUAL é desativado (volta ao NORMAL).

### 3.6 Linha de Comando (RULE-TUI-6.x)

- **RULE-TUI-6.1:** A linha de comando (`:`) aparece na penúltima linha da tela (acima da message bar).
- **RULE-TUI-6.2:** `:` é automaticamente prefixado ao entrar no modo COMANDO.
- **RULE-TUI-6.3:** `Enter` executa o comando; `Esc` cancela (volta ao NORMAL sem ação).
- **RULE-TUI-6.4:** `Tab` DEVE oferecer autocomplete de caminhos de recursos (clientes, serviços, documentos).
- **RULE-TUI-6.5:** Comandos padrão obrigatórios:
  | Comando | Ação |
  |---------|------|
  | `:e [path]` | Abrir recurso no split atual |
  | `:q` | Fechar split atual (ou voltar se split único) |
  | `:q!` | Fechar split atual sem salvar |
  | `:w` | Salvar buffer atual |
  | `:help` | Abrir ajuda interna |
  | `:split [path]` | Split horizontal + abrir recurso |
  | `:vsplit [path]` | Split vertical + abrir recurso |
  | `:bd` | Fechar buffer atual (fecha o split) |
  | `:noh` | Limpar realce de busca |
  | `:set [key]=[val]` | Configurar opção em tempo real |
- **RULE-TUI-6.6:** Comandos desconhecidos DEVEM exibir `"[X] Comando desconhecido: :<cmd>. Use :help para ajuda"` na message bar.
- **RULE-TUI-6.7:** `:e` sem argumento abre o seletor de recursos (navegável com j/k).
- **RULE-TUI-6.8:** `:help` DEVE abrir um buffer de ajuda no split atual com: lista de modos, comandos `:` disponíveis, keybindings padrão, exemplo de composição.
- **RULE-TUI-6.9:** `:set` com key inválida DEVE exibir erro na message bar. `:set` sem argumentos DEVE listar configurações atuais.

### 3.7 Busca (RULE-TUI-7.x)

- **RULE-TUI-7.1:** `/<termo>` busca texto em todos os buffers abertos. Resultados são realçados.
- **RULE-TUI-7.2:** A busca é case-insensitive.
- **RULE-TUI-7.3:** `n` navega para o próximo match; `N` navega para o match anterior.
- **RULE-TUI-7.4:** `Esc` limpa o realce de busca (equivale a `:noh`).
- **RULE-TUI-7.5:** Se nenhum match for encontrado, exibir `"[X] Nenhum resultado para <termo>"` na message bar.
- **RULE-TUI-7.6:** A message bar DEVE mostrar `"<termo> — N matches em M arquivos    n/N para navegar"`.
- **RULE-TUI-7.7:** `/` sem termo (vazio) repete a última busca.

### 3.8 Temas e Configuração (RULE-TUI-8.x)

- **RULE-TUI-8.1:** `settings.json` DEVE conter a seção `modal_theme` com `dark`, `light` ou `high_contrast`. Default: `dark`.
- **RULE-TUI-8.2:** `settings.json` DEVE conter a seção `modal_colors` com as chaves: `bg`, `fg`, `status`, `cmdline`, `search_highlight`, `visual_select`, `split_separator`, `error`, `warning`, `success`. Default: conforme TuiModalDesign.md §5.
- **RULE-TUI-8.3:** `settings.json` DEVE conter a seção `modal_keybindings` com subseções `normal` e `ctrl_w`. Default: conforme TuiModalDesign.md §6.
- **RULE-TUI-8.4:** `settings.json` DEVE conter `modal_enabled` (bool, default: false). Quando false, o sistema opera em modo de compatibilidade (TUI hierárquica original).
- **RULE-TUI-8.5:** `settings.json` DEVE conter `modal_external_editor` (string, default: `notepad` no Windows, `vim` no Linux/Mac).
- **RULE-TUI-8.6:** A alteração de `modal_theme` ou `modal_colors` DEVE ser aplicada em tempo real (sem restart) via `:set theme=light`.
- **RULE-TUI-8.7:** O sistema DEVE vir com 3 temas pré-definidos (`dark`, `light`, `high_contrast`) em `modal_themes.json`.
- **RULE-TUI-8.8:** O modo de compatibilidade (`modal_enabled: false`) DEVE restaurar COMPLETAMENTE o comportamento da TUI hierárquica, incluindo todos os atalhos (RULE-UX-1.x), breadcrumbs (RULE-UX-1.1), paginação (RULE-UX-2.x) e confirmações (RULE-UX-5.x).
- **RULE-TUI-8.9:** `modal_themes.json` DEVE ficar em `foton_system/interfaces/modal/themes/` e ser carregado na inicialização do `ModalEngine`.
- **RULE-TUI-8.10:** A message bar NÃO DEVE conter informações críticas que desaparecem — toda ação DEVE ser confirmada visualmente antes de sumir.
- **RULE-TUI-8.11:** Os testes da interface modal DEVEM estar em `tests/test_modal/` e NÃO DEVEM interferir nos testes existentes.
- **RULE-TUI-8.12:** A cobertura de testes da interface modal DEVE ser ≥ 80% nas primeiras 2 semanas após a Fase 1.
- **RULE-TUI-8.13:** `settings.json` DEVE conter `modal_split_prefix` (str, opcional) e `modal_split_prefix_auto` (bool, default: true) conforme especificado em RULE-TUI-3a.5/3a.6.

## 4. Composição de Comandos (Exemplos)

Demonstração de como comandos simples se compõem em workflows:

| Workflow | Sequência | Fase |
|----------|-----------|------|
| Abrir ficha do Fulano | `/fulano Enter` ou `:e fulano` | 1 |
| Ver ficha + financeiro do Fulano | `:e fulano` → `Ctrl+w v` → `:e financeiro/fulano` | 1 |
| Excluir 3 clientes inativos | `v j j v :d S Enter` | 2 |
| Gerar proposta para 2 serviços | `V j v :g Enter` → seleciona template → `S Enter` | 2 |
| Mudar tema para light | `:set theme=light Enter` | 3 |
| Mapa completo de teclas | `:help Enter` → `g` (keybindings) | 3 |

## 5. Estrutura de Diretórios

```
foton_system/
└── interfaces/
    └── modal/
        ├── __init__.py
        ├── engine.py              # ModalEngine (classe central)
        ├── modes.py               # Modo NORMAL, INSERT, VISUAL, COMANDO
        ├── keybindings.py         # Mapa de teclas → ações
        ├── splits.py              # Gerenciamento de splits
        ├── buffer.py              # Buffer (dado carregado)
        ├── cmdline.py             # Linha de comando (:)
        ├── search.py              # Busca (/)
        ├── themes/
        │   ├── __init__.py
        │   ├── base.py            # Classe Theme
        │   └── themes.json        # dark, light, high_contrast
        ├── ui.py                  # Status bar, message bar, rendering
        └── compatibility.py       # Fallback para menus hierárquicos
```

## 6. Especificações Técnicas

### 6.1 Renderização

- Usar stdlib `curses` (cross-platform Windows/Linux/Mac) como backend de renderização
- Alternativa: `rich` (se curses apresentar problemas em terminais Windows antigos)
- Fallback: `print()` com ANSI codes para terminais que não suportam curses

### 6.2 Performance

| Operação | SLA | Medição |
|----------|-----|---------|
| Navegação entre splits | < 100ms | time.time() |
| Carga da interface modal | < 500ms | time.time() |
| Renderização de buffer 1000 linhas | < 200ms | time.time() |
| Busca em buffers abertos | < 500ms | time.time() |
| Comando `:` (abrir recurso) | < 300ms | time.time() |

### 6.3 Tratamento de Erros

- Todo `except` no código modal DEVE usar `format_error_with_suggestion()` (SPEC-UI-COMPONENTS.md §2.3)
- Erros de renderização (terminal muito pequeno, encoding) DEVEM ter fallback gracejoso
- Se o terminal for < 80x24, exibir aviso na message bar e operar em modo simplificado

## 7. Relações

- Código: `foton_system/interfaces/modal/` (nova)
- Specs relacionadas: `SPEC-UX-v1.x.md`, `SPEC-UI-COMPONENTS.md`
- Design: `TuiModalDesign.md` (conceitos perenes)
- Épicos: `EPIC-001` (Fase 0), `EPIC-013` (Fases 1-3)
- ADRs: (a definir)

## 8. Histórico de Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2026-07-06 | Versão inicial: 8 áreas, ~50 RULE-IDs, estrutura de diretórios, SLAs de performance |
| 1.0 | 2026-07-06 | RULE-TUI-3a.1~3a.9 adicionadas: prefixo de split automático (Ctrl+b dentro do tmux, Ctrl+w fora), modal_split_prefix/modal_split_prefix_auto, script foton_tmux_setup.sh. RULE-TUI-8.13 adicionada. Atualização sem numeração (doc fix). |
