---
type: plan
domain: core
status: active
tags: [sprint, architecture, refactor, cross-platform]
---
# 🏃‍♂️ Sprint Plan: Arquitetura Agnóstica (OS/Environment)

## 🎯 Objetivo
Transformar o **FOTON System** em um sistema verdadeiramente cross-platform e multi-ambiente. O sistema deve rodar perfeitamente como um microsserviço (Docker/Ubuntu Server) ou como uma aplicação Desktop rica (Windows/Mac), ativando ou ocultando recursos dinamicamente através do padrão Adapter e de um "Porteiro" de ambiente, sem falhas de importação (`ImportError`).

## 🛠️ Especificações Técnicas (Specs)

### Fase 1: O Porteiro (Environment Porter)
Criar um módulo central que identifica as capacidades reais do ambiente de execução.
*   **Arquivo:** `foton_system/modules/shared/infrastructure/services/environment_porter.py`
*   **Lógica:**
    *   Detectar SO (`os.name`, `platform.system()`).
    *   Detectar GUI (presença de  DISPLAY e existência de socket X11 /tmp/.X11-unix/X0 ou execução no Windows/Mac Desktop).
    *   Detectar Docker (`os.path.exists('/.dockerenv')` /.dockerenv, /.dockerinit, e variáveis como DOCKER_HOST).
    *   Detectar MCP (`--mcp` via `sys.argv`).
*   **Perfis Mapeados (SystemProfile):** `SERVER_HEADLESS`, `DESKTOP_GUI`, `DESKTOP_WSL`, DESKTOP_TUI`.
*   **Método Chave:** `can_use_feature(feature_name: str) -> bool` (ex: can_use_native_dialogs validando presença do zenity).

### Fase 2: Menus Dinâmicos e Condicionais
Refatorar a CLI para usar uma estrutura de dados de roteamento baseada em `SystemProfile`.
*   **Arquivo:** `foton_system/interfaces/cli/menus.py`
*   **Lógica:**
    *   O `MenuSystem` deve injetar o `EnvironmentPorter`.
    *   Substituir os menus "hardcoded" por dicionários/listas mapeados.
    *   Ocultar automaticamente a opção de "Preencher Ficha (Interface)" se `can_use_feature("webview")` for `False`.
    *   Ocultar opções de "Criar Atalhos" se `can_use_feature("shortcuts")` for `False`.

### Fase 3: Padrões Adapter ("Porta dos Fundos")
Isolar e encapsular bibliotecas problemáticas (pywin32, pywebview, tkinter). Nenhuma dessas libs deve ser importada no escopo global.

1.  **IFormInterface (Web/GUI):**
    *   *Abstract:* Interface para captura rica de dados.
    *   *Adapters:* 
	    * `WebViewFormFiller` (Tenta abrir o  `webview`. Falha capturada faz fallback elegante para o Browser.), 
	    * `BrowserFormFiller` (Usa webbrowser nativo do Python sendo o fallback)
	    * `TuiFormFiller` (modo terminal).
    *   *Desacoplamento:* O import do `webview` fica apenas dentro do `WebViewFormFiller`.
2.  **IFileSelector (Buscas/Caminhos):**
    *   *Abstract:* Diálogos para salvar/abrir.
    *   *Adapters:*
		* `CrossFileDialogSelector` (diálogos nativos limpos, ex: usando a lib leve `crossfiledialog` se adicionada e condicional se GUI disponível e zenity/kdialog presentes ou fallback pra tkinter encapsulado localmente)
		* `TuiFileSelector` (terminal fallback absoluto).
3.  **ISystemIntegrator (SO):**
    *   *Abstract:* Integrações específicas do SO (atalhos, registro).
    *   *Adapters:* 
		* WindowsIntegrator: Cria atalhos com winshell.
		* LinuxIntegrator: Cria atalhos .desktop em ~/.local/share/applications/ usando xdg-desktop-menu.
		* NullIntegrator: Ignora a integração (para Server/Docker). 
### Fase 4: Gestão Otimizada de Dependências e Build Multi-OS
O sistema de dependências não deve punir instalações servidoras com "lixo" gráfico.

1.  **Requirements Modulares:**
    *   `requirements-core.txt`: `pandas`, `python-docx`, `python-pptx`, `mcp`, `chromadb`, etc.
    *   `requirements-desktop.txt`: `pywebview`, `pythonnet`, `pywin32` (instalado on-demand ou durante o build de desktop).
2.  **Estratégia de Build (`build.py`):**
    *   Refatorar o pipeline para aceitar flags `--target=linux-server`, `--target=windows-desktop`.
	*  Opção de Pipelines duplos: Target Server (limpo) e Target Desktop (com hooks e hidden-imports explícitos como webview, winshell, crossfiledialog). 
	*   Configurar o `PyInstaller` para empacotar apenas o necessário para cada target, criando bundles independentes em `dist/`.
    *   No Linux, usar script Bash nativo ou empacotamento `.tar.gz`.

## 📦 Checklist de Execução

- [ ] Criar o `EnvironmentPorter` (Fase 1).
- [ ] Criar estrutura de `requirements-*.txt` dividida (Fase 4).
- [ ] Implementar interfaces e classes Adapter para SO (`ISystemIntegrator`) e Forms (`IFormInterface`) (Fase 3).
- [ ] Refatorar os adapters UI (`IFileSelector` e provedores de UI) (Fase 3).
- [ ] Refatorar o `MenuSystem` para usar o Porteiro dinamicamente (Fase 2).
- [ ] Ajustar o `build.py` para suportar cross-platform e dependências condicionais (Fase 4).
- [ ] Executar suite de testes para garantir que quebras de import (`ImportError`) não afetem o core.

---
## 🔗 Links Relacionados
- Meta: [[LlmProtocol]]
- Arquitetura: [[LlmContext]]
