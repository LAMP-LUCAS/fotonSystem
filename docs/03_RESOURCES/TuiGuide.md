---
type: guide
domain: core
status: active
tags: [tui, terminal, productivity]
---
# 📟 Guia do Modo Terminal (TuiGuide)

Bem-vindo ao modo mais raiz e eficiente do **FOTON System**! O modo TUI (Terminal User Interface) foi criado para arquitetos que valorizam velocidade, precisão e automação.

---

## Paradigma Duplo

O FOTON System oferece duas interfaces sobre o mesmo domain layer:

| Interface | Para quem | Como iniciar |
|-----------|-----------|--------------|
| **TUI** (você está aqui) | Humanos via terminal | `foton --tui` |
| **MCP** (agentes de IA) | Claude, Gemini e outros LLMs | `foton --mcp` |

A TUI é ideal para operação manual e exploração interativa. Para automação por agentes de IA (RAG, watcher, batch), use o MCP — veja [[DocsMcp]].

---

## 💎 Design e Responsividade

A interface do Foton agora é **Dinâmica e Adaptável**. Graças ao motor `TUILayout`, o sistema detecta o tamanho da sua janela e ajusta o enquadramento automaticamente.

*   **Largura Inteligente:** O sistema opera entre 40 e 100 caracteres de largura, otimizando o espaço disponível.
*   **Bordas Perfeitas:** Mesmo usando Emojis ou cores, o sistema compensa a largura visual para manter o quadro sempre sólido.
*   **Limpeza Automática:** A tela é limpa a cada transição para manter o foco na tarefa atual.

---

## 🚀 Como Ativar

Existem duas formas de invocar o poder do terminal:

### 1. Via Linha de Comando (Temporário)

Se você quer apenas rodar uma vez sem janelas chatas:

```powershell
foton --tui
```

### 2. Via Configuração (Permanente)

No menu de **Configurações (Opção 5)**, você pode definir o `ui_mode` como `tui`. O sistema nunca mais abrirá uma janela do Windows para pedir uma pasta!

---

## 🎮 Como Jogar (Navegação)

Esqueça o mouse. No modo TUI, a interação é baseada em listas numeradas:

### 📁 Selecionando Pastas

Quando o sistema pedir uma pasta (ex: para gerar um documento):

1. Ele listará os diretórios atuais.
2. Digite o **Número** da pasta para entrar nela.
3. Digite `..` para subir um nível.
4. Digite `0` para selecionar o diretório atual onde você está.
5. Digite `q` para desistir (cancelar).

> [!DIDACTIC:TUI] Atalho de Navegação: Digite `..` para subir rapidamente na hierarquia de pastas. É muito mais rápido do que procurar o botão "voltar" em uma janela!

### 📄 Selecionando Arquivos

Igual às pastas, mas você escolhe o número do arquivo que deseja carregar.

---

## ⚡ Preenchimento Rápido (Form Filler)

> [!DIDACTIC:PRODUTIVIDADE] Velocidade Máxima: No preenchedor de fichas, aperte `ENTER` sem digitar nada para manter o valor atual e pular para o próximo campo.

No modo TUI, o preenchimento de documentos é otimizado para o teclado:
- **[N] / [ENTER]:** Próximo campo.
- **[P]:** Campo anterior.
- **[V]:** Visualizar o documento com realce de cores (Preview).
- **[S]:** Salvar as alterações.
- **[A]:** Salvar como (Crie uma nova versão sem perder a original).

> [!DIDACTIC:V1.2] Novidade v1.2: Use o comando `[A]` (Salvar Como) para criar revisões (R01, R02) dos seus documentos instantaneamente.

---

## 🧠 Por que usar TUI?

- **Velocidade:** Não precisa esperar o Windows carregar o diálogo de pastas.
- **Foco:** Sem janelas pulando na frente do seu código.
- **Resiliência:** Funciona até se o driver de vídeo do seu PC estiver de folga.
- **Minimalismo:** Apenas texto, cores e produtividade.

---

> "Com grandes terminais, vêm grandes responsabilidades." - *Anônimo da LAMP*

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Guia do Usuário: [[UserGuide]]
- Relatório de Testes: [[TestQualityReport]]
