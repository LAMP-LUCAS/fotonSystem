# Guia de Uso: FOTON MCP 🚀

O **FOTON MCP** é o servidor que permite que Inteligências Artificiais (como Claude Desktop, Cursor ou ChatGPT) interajam diretamente com o sistema Foton para gerenciar seu escritório.

## 1. Instalação e Requisitos

### Pré-requisitos

* **Python 3.10+**
* **Claude Desktop** ou **Cursor IDE** (ou qualquer cliente compatível com MCP)

### Passo 1: Instalar dependências

No terminal da pasta do projeto, execute:

```bash
pip install mcp fastmcp pandas openpyxl python-docx python-pptx
```

### Passo 2: Localizar o script

O servidor MCP está em:
`foton_system/interfaces/mcp/foton_mcp.py`

---

## 2. Configuração nos LLMs

### No Claude Desktop

1. Abra o arquivo de configuração do Claude (`%APPDATA%/Claude/claude_desktop_config.json` no Windows).
2. Adicione o FOTON na lista de `mcpServers`:

```json
{
  "mcpServers": {
    "foton": {
      "command": "python",
      "args": ["Caminho/Absoluto/Para/fotonSystem/foton_system/interfaces/mcp/foton_mcp.py"]
    }
  }
}
```

3. Reinicie o Claude. Um ícone de martelo (tools) aparecerá.

### No Cursor (IDE)

1. Vá em **Settings > Cursor Settings > Features > MCP**.
2. Clique em **+ Add New MCP Server**.
3. Escolha o tipo `command` e cole:
   `python "Caminho/Absoluto/Para/foton_system/interfaces/mcp/foton_mcp.py"`
4. Pronto! O Cursor agora tem acesso às ferramentas do Foton.

---

## 3. Comandos e Utilização

Você não precisa digitar comandos específicos. Basta pedir para a IA em linguagem natural:

* *"Registre uma entrada de R$ 500 para o cliente João Silva referente a consultoria"*
* *"Qual é o saldo atual do cliente Maria?"*
* *"Gere uma proposta para o cliente João usando o template de anteprojeto"*
* *"Sincronize meu dashboard do Excel"*

---

## 4. Segurança

* O servidor roda localmente.
* A IA só tem acesso às ferramentas definidas no arquivo `foton_mcp.py`.
* Sempre valide documentos gerados antes de enviar ao cliente.
