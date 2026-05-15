---
type: guide
domain: core
status: active
tags: [mcp, ai, integration]
---
# 🤖 Guia de Integração MCP - FOTON System (McpGuide)

> **Deixe a IA trabalhar por você.**

O **FOTON MCP** conecta seu escritório a assistentes de IA como Claude Desktop, Cursor e outros clientes compatíveis com o Model Context Protocol.

> **Quer entender como funciona?** Veja [[AiIntegrationReport|Relatório de Integração IA]]

---

## 🚀 Configuração em 2 Minutos

### Passo 1: Gerar Configuração

No terminal, execute:

```powershell
foton --mcp-config
```

O sistema gera o JSON pronto para copiar:

```json
{
  "mcpServers": {
    "foton": {
      "command": "python",
      "args": ["C:\\...\\foton_mcp.py"]
    }
  }
}
```

### Passo 2: Colar no Assistente

O comando `foton --mcp-config` detecta automaticamente se você está usando o código-fonte ou o executável instalado e gera o JSON correto. 

**Se estiver usando o executável:**

```json
"foton": {
  "command": "C:\\Users\\...\\foton_system_v1.2.0.exe",
  "args": ["--mcp"]
}
```

**Se estiver desenvolvendo (Python):**

```json
"foton": {
  "command": "python",
  "args": ["C:\\...\\foton_mcp.py"]
}
```

#### Para Claude Desktop

1. Abra `%APPDATA%\Claude\claude_desktop_config.json`
2. Cole o JSON gerado pelo comando.
3. Reinicie o Claude.

#### Para Cursor IDE

1. Vá em **Settings** > **Features** > **MCP**
2. Clique em **+ Add New MCP Server**
3. Type: `command`
4. Cole o comando e argumentos fornecidos pelo `foton --mcp-config`.

---

## 💬 Comandos Disponíveis

Depois de configurar, basta pedir em linguagem natural:

### 💵 Financeiro

| Comando | O que faz |
|---------|-----------|
| *"Qual o saldo do cliente Silva?"* | Consulta o resumo financeiro |
| *"Registre entrada de R$ 5.000 para João"* | Registra pagamento recebido |
| *"Registre despesa de R$ 200 para material"* | Registra saída de caixa |

### 📄 Documentos

| Comando | O que faz |
|---------|-----------|
| *"Liste os templates disponíveis"* | Mostra PPTX e DOCX cadastrados |
| *"Gere proposta para Maria usando template comercial"* | Cria documento com dados do cliente |

### 🧠 Memória (RAG)

| Comando | O que faz |
|---------|-----------|
| *"O que sabemos sobre projetos residenciais?"* | Busca na base de conhecimento |
| *"Qual foi a última decisão sobre acabamentos?"* | Pesquisa histórico de documentos |

---

## ⚠️ Solução de Problemas

### MCP não inicia

> [!NOTE]
> O servidor demora ~15 segundos para iniciar na primeira vez. Isso é normal devido às dependências carregadas.

### JSON inválido

Use sempre `foton --mcp-config` para gerar o JSON correto. Não edite manualmente!

### Erro de caminho

Verifique se o Python está no PATH do sistema:

```powershell
python --version
```

Se não funcionar, reinstale o Python marcando "Add to PATH".

---

## 🔒 Segurança

- O servidor roda **localmente** no seu computador
- A IA só acessa ferramentas definidas no `foton_mcp.py`
- Nenhum dado é enviado para servidores externos
- Sempre valide documentos gerados antes de enviar ao cliente

---

## 📋 Referência Técnica

### Arquivo do Servidor

```
foton_system/interfaces/mcp/foton_mcp.py
```

### Ferramentas Expostas

| Tool | Descrição |
|------|-----------|
| `registrar_financeiro` | Registra entrada/saída financeira |
| `consultar_financeiro` | Consulta saldo e resumo |
| `listar_templates` | Lista templates PPTX/DOCX |
| `gerar_documento` | Gera documento a partir de template |
| `consultar_conhecimento` | Pesquisa na base de memória (RAG) |

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Guia do Usuário: [[UserGuide]]
- Relatório de IA: [[AiIntegrationReport]]
