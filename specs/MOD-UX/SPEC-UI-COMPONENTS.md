# Spec: Catálogo de Padrões de Componentes de Interface (TUI)

**Data:** 2026-07-06
**Versão:** 1.0
**Responsável:** Time Core
**Épico:** EPIC-001, EPIC-013
**Spec relacionada:** SPEC-UX-v1.x, SPEC-TUI-MODAL-v1.0

## 1. Propósito

Definir um catálogo único de padrões visuais e comportamentais para todos os componentes da TUI.
Este documento é o árbitro final para dúvidas de implementação: se dois menus divergem, o padrão
aqui descrito prevalece.

## 2. Convenções Gerais

### 2.1 Codificação de caracteres

- **Toda string de interface DEVE ser ASCII-safe** (não usar `\N{...}`, emojis ou caracteres Unicode que possam quebrar em cp1252)
- Para ícones, usar alternativas ASCII: `[!]` (aviso), `[X]` (erro), `[v]` (sucesso), `[>]` (progresso), `[*]` (destaque)
- Acentos são permitidos e recomendados (cp1252 suporta acentos do português)

### 2.2 Strings

- Todo label DEVE estar em português brasileiro (RULE-UX-4.1)
- Usar **f-strings** exclusivamente (proibido `.format()` em novos código; migrar `.format()` existente)
- Strings longas (> 80 chars) DEVEM ser quebradas com parênteses implícitos ou `\`

### 2.3 Funções de utilidade (DRY)

```python
# ui_components.py

def print_breadcrumb(path: list[str]) -> None:
    """Exibe breadcrumb centralizado. Ex: '  Clientes > Servicos > Proposta  '"""
    text = " > ".join(path)
    print(f"\n  {'=' * (len(text) + 4)}")
    print(f"  {text}")
    print(f"  {'=' * (len(text) + 4)}\n")

def print_header(title: str, subtitle: str = "") -> None:
    """Exibe cabeçalho padronizado com linha dupla."""
    print(f"\n{'=' * 60}")
    print(f"  {title.upper()}")
    if subtitle:
        print(f"  {subtitle}")
    print(f"{'=' * 60}")

def print_section(label: str) -> None:
    """Exibe separador de seção (ex: '--- Cadastro ---')."""
    print(f"\n--- {label} ---")

def confirm_action(prompt: str, dangerous: bool = False) -> bool:
    """
    Padrão único de confirmação.
    Retorna True se o usuário confirmar.
    dangerous=True exibe marcador visual [!].
    """
    marker = " [!] " if dangerous else " "
    resposta = input(f"{marker}{prompt} (S/N): ").upper().strip()
    return resposta == 'S'

def paginate(items: list[str], page_size: int = 10) -> None:
    """Exibe itens paginados com 'Pressione Enter para continuar...'."""
    for i in range(0, len(items), page_size):
        for item in items[i:i + page_size]:
            print(item)
        if i + page_size < len(items):
            input("\nPressione Enter para continuar...")

def format_error_with_suggestion(error: Exception) -> str:
    """
    Retorna mensagem de erro + sugestão contextualizada por tipo.
    Uso obrigatório em todos os `except:`.
    """
    suggestions = {
        FileNotFoundError: "Verifique o caminho do arquivo ou settings.json",
        PermissionError: "Feche programas que estejam usando o arquivo e tente novamente",
        ConnectionError: "Verifique sua conexão de rede",
        TimeoutError: "O servidor não respondeu a tempo. Tente novamente",
        KeyError: "Configuração ausente. Verifique settings.json",
        json.JSONDecodeError: "Arquivo JSON inválido. Verifique a formatação",
    }
    suggestion = ""
    for exc_type, msg in suggestions.items():
        if isinstance(error, exc_type):
            suggestion = msg
            break
    if not suggestion:
        suggestion = "Caso o erro persista, contate o suporte"
    return f"[X] {type(error).__name__}: {error}\n    Sugestao: {suggestion}"

class ProgressTracker:
    """Feedback visual para operações batch."""

    def __init__(self, total: int, label: str = "Processando"):
        self.total = total
        self.current = 0
        self.label = label

    def advance(self, item_name: str = "") -> None:
        self.current += 1
        item = f" {item_name}" if item_name else ""
        print(f"\r[{self.current}/{self.total}] {self.label}{item}...", end="")

    def finish(self) -> None:
        print(f"\r[{self.total}/{self.total}] {self.label} concluido!")
```

## 3. Componentes

### 3.1 Título de Tela (Header)

```
============================================================
  GESTAO DE CLIENTES
  Selecione uma opcao abaixo
============================================================
```

**Implementação:** `print_header(title, subtitle)`

### 3.2 Breadcrumb

```
  =========================
  Clientes > Servicos
  =========================
```

**Implementação:** `print_breadcrumb(path)`

**Regras:**
- Centralizado (2 espaços antes/linha dupla)
- Presente em TODAS as telas exceto menu principal
- Caminho completo desde a raiz (ex: `Clientes > Financeiro`)

### 3.3 Menu de Opções

```
--- Cadastro ---
1. Novo Cliente

--- Manutencao ---
2. Listar Todos os Clientes
3. Buscar Cliente
4. Ler Ficha

--- Servicos ---
5. Gerenciar Servicos

--- Perigo ---
6. Remover Cliente
```

**Regras:**
- Subgrupos separados por `--- label ---`
- Opções numeradas sequencialmente (1, 2, 3...)
- Grupo "Perigo" sempre por último
- Nenhuma opção destrutiva fora do grupo Perigo

### 3.4 Diálogo de Confirmação

```
  Remover o cliente FULANO DE TAL?
  Esta acao nao pode ser desfeita. (S/N): _
```

```
[!] Excluir permanentemente o servico REFORMA?
  Esta acao e irreversivel. (S/N): _
```

**Implementação:** `confirm_action(prompt, dangerous=False)`

**Regras:**
- Sempre usar `.upper().strip()` na resposta
- `dangerous=True` para operações irreversíveis
- Usar "Esta ação não pode ser desfeita" para ações normais
- Usar "Esta ação é irreversível" para ações destrutivas
- O prompt deve ser claro sobre o que será feito

### 3.5 Paginação

```
  1. FULANO DE TAL (FUL) - Ativo
  2. BELTRANO DA SILVA (BEL) - Ativo
  3. SICRANO PEREIRA (SIC) - Ativo
  4. MARIA SOUZA (MAS) - Ativo
  5. JOAO PEDRO (JPE) - Ativo
  6. ANA LUCIA (ALU) - Ativo
  7. CARLOS EDUARDO (CED) - Ativo
  8. PATRICIA LIMA (PLI) - Ativo
  9. ROBERTO ALVES (RAL) - Ativo
  10. FERNANDA COSTA (FCO) - Ativo
  Pressione Enter para continuar...
  11. GUSTAVO HENRIQUE (GHE) - Ativo
```

**Implementação:** `paginate(items, page_size=10)`

### 3.6 Indicador de Progresso

```
[3/10] Processando CLIENTE...
[10/10] Processando concluido!
```

**Implementação:** `ProgressTracker(total, label)`
**Técnica:** `\r` (carriage return) para atualizar na mesma linha

### 3.7 Mensagem de Erro com Sugestão

```
[X] FileNotFoundError: settings.json nao encontrado
    Sugestao: Verifique o caminho do arquivo ou settings.json
```

**Implementação:** `format_error_with_suggestion(error)`
**Uso obrigatório:** Em todo `except:` de handler de menu

### 3.8 Lista de Resultados de Busca

```
  Resultados para "fulano":
  [1] FULANO DE TAL - fulano@email.com - 12.345.678/0001-90
  [2] FULANA DE SOUZA - fulana@email.com - 98.765.432/0001-10

  Selecione o numero ou Enter para voltar: _
```

**Regras:**
- Resultados numerados com `[n]`
- Exibir: nome, email e NIF
- Enter sem número volta para tela anterior
- Seleção navega diretamente para o recurso

### 3.9 Entrada de Formulário

```
  --- Novo Cliente ---

  Nome: ________________________________
  Apelido: _____________________________
  NIF: ________________________________
  Email: ______________________________
  Telefone: ____________________________

  Comandos: /s (salvar)  /c (cancelar)  /n (proximo)
  Comando ou Valor: _
```

**Regras:**
- Prompt "Comando ou Valor" (RULE-UX-6.1)
- Comandos prefixados com `/` (RULE-UX-6.2)
- Rodapé de comandos sempre visível (RULE-UX-6.3)

### 3.10 Status Bar (Interface Modal)

```
┌──────────────────────────────────────────────────────────┐
│  FOTON SYSTEM — [ NORMAL ]  cliente: FULANO     15:30   │
└──────────────────────────────────────────────────────────┘
```

**Modos:**
| Modo | Status | Cor |
|------|--------|-----|
| NORMAL | `[ NORMAL ]` | Cyan reverso |
| INSERT | `[ INSERT ]` | Verde reverso |
| VISUAL | `[ VISUAL ] N itens` | Azul reverso |
| COMANDO | `[ COMANDO ]` | Amarelo reverso |

### 3.11 Split Separator (Interface Modal)

```
┌──────────────────────────────┬───────────────────────────┐
│                              │                           │
│  split ativo (foco)         │  split inativo            │
│                              │                           │
└──────────────────────────────┴───────────────────────────┘
```

O split com foco tem borda clara; splits inativos têm borda escura.

### 3.12 Command Line (Interface Modal)

```
  :e clientes/FULANO _
```

- Sempre na penúltima linha (acima da message bar)
- Prefixo `:` automático ao entrar no modo COMANDO
- `Tab` para autocomplete de caminhos
- `Enter` para executar
- `Esc` para cancelar (volta ao modo NORMAL)

### 3.13 Search Bar (Interface Modal)

```
  /fulano _
```

- Acionada por `/` no modo NORMAL
- `Enter` para buscar, `n`/`N` para navegar matches
- `Esc` para limpar realce e sair

### 3.14 Message Bar (Interface Modal)

```
  "fulano" — 3 matches em 2 arquivos    n/N para navegar
```

- Última linha (sempre visível)
- Mensagens de resultado, erro, notificação
- Expira após 5 segundos ou ao próximo comando

## 4. Contrato de Telas

Toda tela/handler DEVE seguir este contrato:

```python
def nome_da_tela() -> None:
    """Breve descrição do que a tela faz."""
    print_breadcrumb(["Raiz", "SubMenu"])
    print_header("Título", "Subtítulo opcional")
    try:
        # ... lógica da tela ...
    except (FileNotFoundError, PermissionError, KeyError, Exception) as e:
        print(format_error_with_suggestion(e))
        input("\nPressione Enter para continuar...")
```

## 5. Histórico de Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2026-07-06 | Catálogo inicial (14 componentes, 3 utilidades, contrato de telas) |
