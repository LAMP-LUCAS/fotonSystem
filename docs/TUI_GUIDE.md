# 📟 Guia do Modo Terminal (TUI)

Bem-vindo ao modo mais raiz e eficiente do **FOTON System**! O modo TUI (Terminal User Interface) foi criado para quando você quer velocidade total ou está trabalhando em um ambiente sem suporte a janelas (como via SSH).

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

### 📄 Selecionando Arquivos

Igual às pastas, mas você escolhe o número do arquivo que deseja carregar.

---

## 🧠 Por que usar TUI?

- **Velocidade:** Não precisa esperar o Windows carregar o diálogo de pastas.
- **Foco:** Sem janelas pulando na frente do seu código.
- **Resiliência:** Funciona até se o driver de vídeo do seu PC estiver de folga.
- **Minimalismo:** Apenas texto, cores e produtividade.

---

> "Com grandes terminais, vêm grandes responsabilidades." - *Anônimo da LAMP*

🔗 [[README|Voltar ao Início]] | [[TestQualityReport|Ver Relatório de Testes]]
