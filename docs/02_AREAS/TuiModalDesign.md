# Design da Interface Modal Vim+tmux

**Data:** 2026-07-06
**Status:** Perene (conceitos de design, evolui com o sistema)
**Épico:** EPIC-013
**Spec:** SPEC-TUI-MODAL-v1.0.md

## 1. Filosofia

A interface modal do Foton System adota o paradigma Vim+tmux porque resolve 3 problemas fundamentais da TUI hierárquica atual:

1. **Custo de contexto:** No modelo atual, cada ação exige navegar até um submenu. No modelo modal, o recurso-alvo (cliente, serviço, documento) está sempre visível — navega-se *dentro* do dado, não *até* ele.
2. **Diferença iniciante vs expert:** Hoje ambos navegam igual. A interface modal oferece uma escada de proficiência: iniciantes usam setas + comandos óbvios (`Enter` para selecionar, `Esc` para voltar); experts usam composição (`/busca enter :e`).
3. **Composição:** Ações complexas são compostas de ações simples. Ex: `v j j j :g` = "selecione 3 itens e gere documento para eles".

## 2. Os 4 Modos

### 2.1 Modo NORMAL

**Ativado por:** `Esc` (a partir de qualquer modo), ou ao iniciar o sistema
**Status bar:** `[ NORMAL ]`
**O quê faz:** Navegação, busca, comando `:`

O usuário está sempre em NORMAL por padrão. Pode:
- Navegar entre lines/splits com `j`/`k`/`h`/`l`
- Buscar com `/`
- Executar comandos com `:`
- Mudar para INSERT com `i`, `a`, `o`
- Mudar para VISUAL com `v`

**Anti-padrão:** NORMAL não deve ter modo "inserção". Se o usuário precisa digitar texto, deve estar em INSERT.

### 2.2 Modo INSERT

**Ativado por:** `i` (insert no cursor), `a` (append após cursor), `o` (nova linha)
**Status bar:** `[ INSERT ]`
**O quê faz:** Entrada de dados textual

Regras:
- Para formulários com ≤ 10 campos: edição inline no próprio recurso
- Para > 10 campos: `:e [editor] [path]` (abre editor externo configurável)
- `Esc` retorna ao modo NORMAL
- Atalhos Vim clássicos: `Ctrl+w` para apagar palavra, `Ctrl+u` para apagar linha

### 2.3 Modo VISUAL

**Ativado por:** `v` (modo visual personagem), `V` (modo visual linha), `Ctrl+v` (modo visual bloco)
**Status bar:** `[ VISUAL ] 3 itens selecionados`
**O quê faz:** Seleção múltipla para ações batch

Regras:
- Navegação expande a seleção (`j`/`k` adiciona linhas)
- Ao pressionar `:`, o prompt mostra `:'<,'>` indicando range visual
- Comandos disponíveis: `:d` (excluir marcados), `:g` (gerar docs), `:e` (abrir em splits)
- Toda ação batch pede confirmação antes de executar

### 2.4 Modo COMANDO

**Ativado por:** `:` (a partir de NORMAL ou VISUAL)
**Status bar:** `[ COMANDO ]` (temporário, durante digitação)
**O quê faz:** Executa comandos textuais

Comandos padrão:
| Comando | Ação | Exemplo |
|---------|------|---------|
| `:e [path]` | Abrir recurso | `:e clientes/FULANO` |
| `:q` | Fechar split/voltar | `:q` |
| `:w` | Salvar alterações | `:w` |
| `:help` | Ajuda interna | `:help` |
| `:q!` | Fechar sem salvar | `:q!` |
| `:split [path]` | Split horizontal + abrir | `:split financeiro` |
| `:vsplit [path]` | Split vertical + abrir | `:vsplit documentos` |
| `:bd` | Fechar buffer atual | `:bd` |
| `:noh` | Limpar realce de busca | `:noh` |
| `:set [key]=[val]` | Configurar opção | `:set theme=dark` |

## 3. Splits e Layout

Inspirado no Neovim, com prefixo adaptável para evitar conflito com tmux.

### 3.1 Detecção Automática de Prefixo

O Foton detecta automaticamente se está rodando dentro de uma sessão tmux
(variável de ambiente `$TMUX`) e ajusta o prefixo de splits:

| Ambiente | Prefixo automático | Razão |
|----------|:------------------:|-------|
| Dentro do tmux | `Ctrl+b` | tmux usa `Ctrl+b` como prefixo padrão alternativo |
| Fora do tmux | `Ctrl+w` | Padrão Neovim, sem conflito |
| settings.json explícito | O que o usuário definir | Sobrescreve a detecção |

### 3.2 Camadas de Decisão (precedência)

```
1. settings.json "modal_split_prefix" (se definido)
   ↓ se não
2. Auto-detect: os.environ.get("TMUX") → Ctrl+b ou Ctrl+w
   ↓ se não
3. Fallback padrão: Ctrl+w (Neovim standard)
```

Se `modal_split_prefix_auto: false` em settings.json, o auto-detect é desligado
e o valor literal de `modal_split_prefix` é usado (ou o fallback se não definido).

### 3.3 Script de Configuração do tmux

Fornecemos o script `scripts/foton_tmux_setup.sh` que configura o tmux para
usar `Ctrl+b` como prefixo, liberando `Ctrl+w` para o Foton (quem preferir
manter o prefixo tmux original pode desabilitar o auto-detect e usar `Ctrl+b`
no Foton — a escolha é do usuário).

### 3.4 Comandos de Split (prefixo configurável)

O prefixo é denotado como `{SPLIT}` nos atalhos abaixo. Por default:
- `Ctrl+w` fora do tmux
- `Ctrl+b` dentro do tmux

### Comandos de Split

`{SPLIT}` = prefixo ativo (auto-detectado ou configurado).

| Atalho | Ação |
|--------|------|
| `{SPLIT} s` | Split horizontal (divide o painel atual ao meio na horizontal) |
| `{SPLIT} v` | Split vertical (divide o painel atual ao meio na vertical) |
| `{SPLIT} w` | Alternar entre splits (ciclo) |
| `{SPLIT} h/j/k/l` | Navegar para split na direção |
| `{SPLIT} H/J/K/L` | Mover split para direção extrema |
| `{SPLIT} q` | Fechar split atual |
| `{SPLIT} o` | Fechar todos os outros splits (deixar só o atual) |
| `{SPLIT} =` | Equalizar tamanho de todos os splits |
| `{SPLIT} +/-` | Aumentar/diminuir altura do split atual |
| `{SPLIT} </>` | Aumentar/diminuir largura do split atual |

### Layout Padrão

```
┌─────────────────────────────────────────────────────────┐
│  FOTON SYSTEM — [ NORMAL ]  cliente: FULANO    15:30   │ ← status bar
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Conteúdo do recurso ativo]                            │
│                                                         │
│  ─────────────────────────────────────────────────      │
│                                                         │
│  [Segundo split se houver]                              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  :e clientes/FULANO                                     │ ← cmdline
├─────────────────────────────────────────────────────────┤
│  "fulano" — 3 matches  n/N para navegar     (1/3)      │ ← message bar
└─────────────────────────────────────────────────────────┘
```

### No-breakpad (telas de erro/diagnóstico)

```
┌──────────────────────────────────────────────────────┐
│  FOTON SYSTEM — [ NORMAL ]           DIAGNÓSTICO     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ⚠ FileNotFoundError: settings.json não encontrado   │
│                                                      │
│  Sugestão: Verifique se o arquivo settings.json      │
│  existe em C:\Users\...\FotonSystem\config\          │
│                                                      │
│  Pressione Enter para continuar...                   │
└──────────────────────────────────────────────────────┘
```

## 4. Hierarquia de Navegação (vs modelo atual)

Na interface modal, não há "menus". Há **recursos** e **comandos**.

| Ação | Hoje (hierárquico) | Amanhã (modal) |
|------|-------------------|-----------------|
| Abrir ficha do Fulano | Menu → Clientes → Buscar → Digitar "Fulano" → Enter → Opção "Ler Ficha" | `:e fulano` ou `/fulano Enter` |
| Ver financeiro do Fulano | (volta) → Menu → Financeiro → Buscar Cliente → Fulano | `:vsplit financeiro/fulano` |
| Gerar proposta | (volta) → Documentos → Gerar → Proposta → Fulano | `:e propostas/fulano` |
| Busca global | (menu) → Opção 4 → Digitar termo | `/termo` |
| 3 ações em série | 3× navegar até o cliente | `:e fulano \| :vsplit financeiro/fulano \| :e propostas/fulano` |

## 5. Temas e Cores

### Tema Padrão (Escuro)

| Elemento | Cor | Uso |
|----------|-----|-----|
| Fundo | Preto (bg) | Painel principal |
| Texto normal | Branco (fg) | Conteúdo |
| Status bar | Cyan reverso | Modo + contexto |
| Cmdline | Amarelo (fg) | Linha de comando |
| Busca realce | Amarelo reverso | Matches de `/busca` |
| Seleção VISUAL | Azul reverso | Itens selecionados |
| Split separador | Cinza escuro | Linha divisória entre splits |
| Modo atual | Bold | Na status bar |
| Erro | Vermelho | Mensagens de erro |
| Aviso | Amarelo | Avisos |
| Sucesso | Verde | Confirmações |

### Configuração

```json
{
  "modal_theme": "dark",
  "modal_colors": {
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
  }
}
```

Temas pré-definidos em `modal_themes.json`: `dark`, `light`, `high_contrast`.

## 6. Keybindings Padrão

O prefixo de splits (`{SPLIT}`) é determinado pelo auto-detect (ver §3.1-3.2).
A subseção `ctrl_w` no JSON usa a tecla real (ex: se prefixo = `Ctrl+b`,
a seção é `ctrl_b` em runtime, mas o padrão documentado é `ctrl_w`).

Armazenados em `settings.json` → `modal_keybindings`:

```json
{
  "modal_keybindings": {
    "normal": {
      "j": "cursor_down",
      "k": "cursor_up",
      "h": "collapse_or_left",
      "l": "expand_or_right",
      "gg": "go_to_top",
      "G": "go_to_bottom",
      "Ctrl+d": "page_down_half",
      "Ctrl+u": "page_up_half",
      "i": "enter_insert_mode",
      "a": "enter_insert_mode_after",
      "o": "open_new_line",
      "v": "enter_visual_mode",
      "V": "enter_visual_line_mode",
      "Ctrl+v": "enter_visual_block_mode",
      "/": "enter_search_mode",
      ":": "enter_command_mode",
      "n": "next_search_match",
      "N": "prev_search_match",
      "Enter": "select_or_activate",
      "Esc": "clear_or_leave_mode",
      "Space": "toggle_fold"
    },
    // A chave real (ctrl_w, ctrl_b, etc.) é determinada pelo prefixo ativo
    // O JSON sempre usa "ctrl_w" como chave; o ModalEngine traduz para o prefixo real
    "ctrl_w": {
      "s": "split_horizontal",
      "v": "split_vertical",
      "w": "cycle_splits",
      "h": "focus_left",
      "j": "focus_down",
      "k": "focus_up",
      "l": "focus_right",
      "H": "swap_left",
      "J": "swap_down",
      "K": "swap_up",
      "L": "swap_right",
      "q": "close_split",
      "o": "only_this_split",
      "=": "equalize_splits",
      "+": "increase_height",
      "-": "decrease_height",
      "<": "decrease_width",
      ">": "increase_width"
    }
  }
}
```

## 7. Configuração de Split Prefix no `settings.json`

```json
{
  "modal_split_prefix": "Ctrl+b",       // força prefixo específico (opcional)
  "modal_split_prefix_auto": true,       // false desliga auto-detect
  "modal_keybindings": {
    "ctrl_w": {
      ...
    }
  }
}
```

| Chave | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `modal_split_prefix` | `str` | `undefined` | Prefixo explícito (ex: `Ctrl+b`, `Ctrl+w`, `Ctrl+\`). Se definido, o auto-detect é ignorado. |
| `modal_split_prefix_auto` | `bool` | `true` | Se `true`, detecta `$TMUX` e ajusta prefixo. Se `false`, usa o valor literal de `modal_split_prefix` ou o fallback `Ctrl+w`. |

### Comportamento Completo

| `modal_split_prefix` | `modal_split_prefix_auto` | `$TMUX` | Prefixo Ativo |
|----------------------|:------------------------:|:-------:|:-------------:|
| `undefined` | `true` (default) | set | `Ctrl+b` |
| `undefined` | `true` (default) | unset | `Ctrl+w` |
| `undefined` | `false` | qualquer | `Ctrl+w` (fallback) |
| `"Ctrl+b"` | qualquer | qualquer | `Ctrl+b` |
| `"Ctrl+w"` | qualquer | qualquer | `Ctrl+w` |
| `"Ctrl+\\"` | qualquer | qualquer | `Ctrl+\` |

## 8. Compatibilidade Retroativa

A Fase 3 implementa modo de compatibilidade que restaura os menus hierárquicos originais:

```json
{
  "modal_enabled": true     // false → TUI clássica
}
```

Quando `modal_enabled: false`:
- Todo o código modal é ignorado
- O sistema carrega os handlers de menu originais (menus_clients, menus_finance, etc.)
- Nenhuma funcionalidade é perdida

## 9. Script de Configuração do tmux

O script `scripts/foton_tmux_setup.sh` configura o tmux para usar `Ctrl+b`
como prefixo, liberando `Ctrl+w` para o Foton (ou para o Neovim do usuário).

### Uso

```bash
# Dentro do WSL ou Linux/Mac
bash scripts/foton_tmux_setup.sh

# O script:
# 1. Faz backup de ~/.tmux.conf → ~/.tmux.conf.foton_backup_<date>
# 2. Verifica se "set -g prefix C-b" já existe
# 3. Se não: adiciona as 3 linhas no início do arquivo
# 4. Cria ~/.tmux.conf se não existir
# 5. Exibe instrução: "tmux source-file ~/.tmux.conf" ou reiniciar tmux
```

### Conteúdo Injetado

```tmux
# === Foton System: prefixo ajustado para evitar conflito ===
set -g prefix C-b
unbind C-w
bind C-b send-prefix
# ==============================================================
```

### Idempotência

O script é idempotente: se executado múltiplas vezes, não duplica as linhas
(verifica se o marcador `# === Foton System` já existe no arquivo).

## 10. Glossário de Termos Modais

| Termo | Definição |
|-------|-----------|
| **Modo** | Estado da interface que define como teclas são interpretadas |
| **NORMAL** | Modo padrão: navegação, busca, comando |
| **INSERT** | Modo de entrada de dados textual |
| **VISUAL** | Modo de seleção múltipla para ações batch |
| **COMANDO** | Modo de linha de comando (`:`) |
| **Split** | Subdivisão da tela em painéis independentes |
| **Buffer** | Dado carregado em memória sendo visualizado/editado |
| **Status bar** | Linha superior com modo + contexto do buffer ativo |
| **Cmdline** | Linha de entrada de comandos `:` |
| **Message bar** | Linha inferior com mensagens, resultados de busca |
| **Modo de compatibilidade** | Fallback para menus hierárquicos originais |
