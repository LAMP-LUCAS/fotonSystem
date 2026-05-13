# 🚀 FOTON System v1.2.0: Modularidade e Performance Extrema

### 🧠 A Revolução Silenciosa: Menos é Mais

A Versão 1.2.0 marca um salto qualitativo na arquitetura do FOTON System. Focamos em **performance, modularidade e experiência do usuário**, transformando o núcleo do sistema em algo leve e instantâneo.

---

### 1. Novo Terminal Rápido (TUI Form Filler) - ⚡ INSTANTÂNEO
Devido à lentidão observada em interfaces WebView no Windows, implementamos um **Preenchedor via Terminal de alta performance**.
- **Navegação Bidirecional:** Vá e volte entre as variáveis usando comandos simples ou apenas a tecla `ENTER`.
- **Cálculos Matemáticos Reais:** As fórmulas `[calculo: ...]` são processadas instantaneamente no terminal conforme você preenche os dados.
- **Resumo de Alterações:** Visualize um balanço de tudo que foi modificado antes de decidir salvar o arquivo.
- **Segurança:** O sistema agora cria automaticamente um backup `.bak` antes de qualquer salvamento.

### 2. Arquitetura de Plugins On-Demand (LITE vs FULL)
O FOTON agora possui um **DependencyManager** inteligente. 
- **Núcleo Leve:** O executável principal foi reduzido drasticamente. Bibliotecas pesadas (IA) são baixadas apenas se solicitadas.
- **Instalação Isolada:** Plugins são instalados em um ambiente virtual (`venv`) próprio em `%LOCALAPPDATA%`, mantendo o Windows limpo.

### 3. Interface Visual Moderna (WebView)
Mantivemos a interface visual sofisticada para quem prefere uma experiência gráfica, agora integrada ao backend via **WebViewBridge**.

### 4. Robustez do Instalador e Dependências
- **Resiliência:** O processo de instalação (Opção 7) agora lida com arquivos bloqueados pelo Windows/OneDrive sem travar.
- **Estabilidade:** Correção de bugs críticos de módulos ausentes (`PIL`, `pandas.plotting`, `jaraco`, `webview`).

---

### 🛠️ Como Atualizar

1. Baixe o novo `foton_system_v1.2.0.zip`.
2. Extraia os arquivos e execute o `foton_system_v1.2.0.exe`.
3. Escolha a **Opção [3]** para experimentar a velocidade do novo preenchedor TUI.

*Potencializando arquitetos com código leve e concreto inteligente.* 🏗️✨

---

**Changelog v1.2.0**:
- Implementação do `TerminalFormFiller` (TDD/DDD).
- Refatoração para suporte a plugins isolados via `DependencyManager`.
- Criação do `WebViewBridge` resiliente com fallback para Browser.
- Correção de resiliência no `InstallService`.
- Padronização de nomes de arquivos para PascalCase na documentação.
- Adição de testes unitários para a lógica de formulários.

---
**Baixar Agora**: [v1.2.0 Release Tag](https://github.com/LAMP-LUCAS/fotonSystem/releases/tag/v1.2.0)
