# 🚀 FOTON System v1.3.2: Hotfix - Instalation Windows

Esta atualização de patch traz melhorias críticas de **resiliência e agnosticismo de sistema operacional**, tornando o **FOTON System** plenamente compatível com ambientes de servidor (**Headless**), VPS, homeServers e Containers Docker.

A arquitetura foi refinada para garantir que o sistema funcione de forma estável mesmo em ambientes sem interface gráfica (Linux/Windows Server), garantindo que as ferramentas de automação e o protocolo MCP operem sem interrupções.

### 🛡️ Destaques de Resiliência
    **Suporte Headless Nativo:** O sistema agora detecta automaticamente a ausência de um servidor de display (GUI) e degrada graciosamente para interfaces de terminal (TUI) ou modo servidor, evitando crashes.
    **Modo Daemon (`--watcher`):** Introduzida a possibilidade de rodar o Monitor de Arquivos (Sentinel) em background como um processo daemon autônomo.
    **Agnosticismo de Terminal:** Substituição de comandos de sistema (`cls`, `clear`) por sequências de escape ANSI universais, eliminando mensagens de erro em logs de servidores Linux.
    **Isolamento de Dependências:** Removidos imports de top-level do Windows (como `winsound`), permitindo a inicialização limpa em qualquer distribuição Linux.

### ✨ Novidades e Melhorias
    **Flag `--version`:** Adicionada para permitir auditorias rápidas e verificação de integridade via CLI.
    **Detecção Inteligente de GUI:** Melhoria na detecção de sessões interativas no Windows (RDP/Console vs Serviços), garantindo o comportamento correto em Windows Server Core.
    **Proteção de Input:** O ponto de entrada fatal agora é imune a falhas de `EOFError`, garantindo logs limpos em pipelines de automação.
    **Fallback de Áudio:** Substituição automática do aviso sonoro do Pomodoro por um Bell ANSI (`\a`) em ambientes sem placa de som.

### 🛠️ Como usar os novos modos
Para rodar o sistema no seu **homeServer** ou **VPS**:
  Iniciar o servidor de monitoramento em background
  python -m foton_system.entry --watcher

  Verificar a versão instalada
  python -m foton_system.entry --version

  Usar como servidor MCP para agentes (estritamente headless)
  python -m foton_system.entry --mcp


 ### 📊 Qualidade
    **Testes:** 100% de aprovação na suíte de **302 testes unitários e de integração**.
    **Estabilidade:** Zero crashes reportados em ambientes Linux Headless simulados.

 ---
 **Desenvolvido para Arquitetos que buscam produtividade em qualquer lugar.**
 Saiba mais em [Mundo AEC](https://www.mundoaec.com) | [GitHub](https://github.com/LAMP-LUCAS/fotonSystem)
