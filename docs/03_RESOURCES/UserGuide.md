---
type: guide
domain: core
status: active
tags: [user, manual, guide]
---
# 📐 Guia do Usuário - FOTON System (UserGuide)

> **Seu braço direito no escritório de arquitetura.**

Bem-vindo ao FOTON! Este guia foi feito para você dominar o sistema em menos de 10 minutos e começar a economizar horas do seu dia.        

---

## 🚀 Início Rápido

> **Novo no FOTON?** Veja também: [[DeploymentGuide|Guia de Instalação Completo]]

### Instalação

Baixe e instale o `foton_system_vX.X.X.exe`. Pronto! O sistema já vem com tudo que precisa.

### Primeiro Acesso

Abrindo o terminal ou clicando no ícone do **FotonSystem**:

```powershell
foton
```

Você pode escolher entre duas interfaces:

1. **Modo Visual (GUI)**: Janelas padrão do Windows (Padrão).
2. **Modo Turbo (TUI)**: Navegação ultra-rápida via teclado. ([[TuiGuide|Aprenda aqui]])

Na primeira execução, o sistema cria automaticamente suas pastas de trabalho:

| Pasta | Localização | O que guarda |
|-------|-------------|--------------|
| 📁 **Dados do Sistema** | `%LOCALAPPDATA%\FotonSystem` | Configurações, logs |
| 📂 **Projetos** | `Documentos\FotonProjects` | Suas pastas de clientes |
| 📄 **Templates** | `Documentos\FotonTemplates` | Modelos de propostas |

> [!TIP]
> Use `foton --info` para ver exatamente onde cada coisa está salva no seu PC.

---

## 🏠 Um Dia na Vida com o FOTON

Vamos simular um dia típico no escritório:

### ☀️ Manhã: Novo Cliente Apareceu

1. Vá em **Gerenciar Clientes** > **Cadastrar Novo**
2. Preencha: Nome, endereço, contato
3. O FOTON cria a pasta automaticamente em `FotonProjects/REF_NomeCliente`

### 🌤️ Tarde: Hora de Enviar Proposta

1. Vá em **Documentos** > **Gerar Proposta (PPTX)**
2. Escolha o cliente (Navegue pelas pastas ou digite o número na TUI)
3. Selecione o template "Proposta Comercial"
4. **Mágica:** O sistema puxa nome, endereço e dados do cliente automaticamente!
5. Pronto! Arquivo gerado na pasta do cliente.

### 🌙 Noite: Registrar Pagamento

1. Vá em **Gerenciar Serviços** > **Financeiro**
2. Ou peça para a IA: *"Registre uma entrada de R$ 5.000 para o cliente Silva"*

> [!IMPORTANT]
> Você precisa ter o **Claude Desktop** ou **Cursor** para usar comandos de voz/texto com IA.

---

## 🛡️ Segurança e Experimentação (Modo Sandbox)

> [!DIDACTIC:SANDBOX] Segurança em Primeiro Lugar: Use o modo Sandbox (`--sandbox`) para treinar novos funcionários ou testar mudanças estruturais sem risco de corromper os dados reais do escritório.

O FOTON possui um **Ambiente Isolado** para quando você quer testar novas funcionalidades ou treinar sem medo de errar.

- **Como Ativar:** Execute `foton --sandbox`.
- **O que acontece:** O sistema cria uma pasta temporária e copia arquivos básicos. Todas as alterações feitas em modo sandbox são **descartadas** ao fechar o programa.
- **Uso Ideal:** Testar novos templates ou scripts de automação.

---

## 🎓 Aprendizado Contextual (TipService)

> [!DIDACTIC:GERAL] Foton é Didático: Observe o rodapé da TUI. O sistema exibe dicas extraídas diretamente destes manuais para ajudar você a dominar o fluxo de trabalho enquanto executa as tarefas.

Não se preocupe em decorar todos os comandos. O Foton utiliza o **TipService** para mostrar dicas úteis baseadas no que você está fazendo:
- Se estiver preenchendo uma proposta, ele dará dicas de formatação.
- Se estiver no financeiro, ele lembrará sobre o CUB.
- Se estiver navegando em pastas, ele dará atalhos de produtividade.

---

## 🧩 Como a Mágica Acontece (Pipelines)

O FOTON usa um sistema inteligente de "Centros de Verdade" para nunca perder dados.

### 📊 Sincronização Automática

> **Quer entender os detalhes técnicos?** Veja [[Pipelines#Sincronização|Como o Pipeline Funciona]]

```
Suas Pastas  ←→  Banco de Dados (Excel)  ←→  Arquivos INFO-*.md
```

- **Pastas → Excel:** Criou uma pasta manualmente? O sistema atualiza o Excel.
- **Excel → Pastas:** Cadastrou em massa no Excel? O sistema cria as pastas.

### 📝 Arquivos INFO (O Coração do Sistema)

> **Entenda a estrutura completa:** [[DataModel|Modelo de Dados]]

Cada pasta de cliente tem um arquivo `INFO-CLIENTE.md` com todos os dados:

```markdown
@nomeCliente: João Silva
@cpf: 123.456.789-00
@endereco: Rua das Flores, 123
@telefone: (11) 99999-9999
```

> [!TIP]
> Você pode editar esses arquivos diretamente pelo VS Code ou Bloco de Notas. O FOTON respeita suas mudanças!

### 📄 Geração de Documentos

Quando você gera uma proposta, o sistema:

1. Lê o `INFO-CLIENTE.md` para pegar dados base
2. Lê o `INFO-SERVICO.md` se for um serviço específico
3. Mescla tudo e substitui no template
4. Salva o documento final na pasta

---

## 📟 Modo Turbo (Terminal / TUI)

> **Quer velocidade máxima?**

Se você prefere não tirar a mão do teclado ou está acessando remotamente, o FOTON tem um modo especial.

- **Ativar:** Inicie com `foton --tui` ou mude nas Configurações.
- **Como usar:** Navegue usando números (`1`, `2`, `3`) em vez do mouse.
- **Guia Completo:** [[TuiGuide|Leia o manual do Modo Turbo]]

---

## 🤖 Integração com IA (MCP)

> **Guia completo:** [[McpGuide|Configuração MCP em 2 Minutos]]

O FOTON pode ser controlado por comandos de voz/texto via Claude ou Cursor.

### Configuração Automática

```powershell
foton --mcp-config
```

Copie o JSON gerado e cole no arquivo de configuração do seu assistente:

- **Claude Desktop:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Cursor:** Settings > Features > MCP

### Exemplos de Comandos

Depois de configurar, basta pedir:

- *"Qual o saldo do cliente Silva?"*
- *"Gere uma proposta para o cliente Maria usando o template comercial"*
- *"Registre uma despesa de R$ 200 para material de escritório"*

> [!NOTE]
> O servidor MCP demora ~15 segundos para iniciar na primeira vez. Isso é normal.

---

## ⚙️ Configurações e Ferramentas Admin

Acesse via **Configurações do Sistema** no menu principal.

### Ferramentas Disponíveis

| Ferramenta | O que faz |
|------------|-----------|
| **Diagnóstico** | Verifica integridade do sistema e gera relatório |
| **Correção em Lote** | Adiciona campos novos em todos os arquivos INFO |
| **Schema Manager** | Renomeia ou mescla variáveis no sistema inteiro |
| **Abrir Pasta do Sistema** | Abre o diretório de dados do FOTON |

---

## 📋 Referência Rápida de Comandos

| Comando | O que faz |
|---------|-----------|
| `foton` | Abre o menu principal |
| `foton --info` | Mostra caminhos do sistema |
| `foton --version` | Mostra versão instalada |
| `foton --mcp-config` | Gera configuração para Claude/Cursor |
| `foton --reset-config` | Reseta configurações para o padrão |

---

## 💡 Dicas & Truques

> [!TIP]
> **Edição Rápida:** Clique com botão direito em qualquer pasta de cliente e abra o `INFO-CLIENTE.md` com seu editor favorito.

> [!TIP]
> **Backup Automático:** O sistema faz backup do Excel antes de operações críticas in `reports/`.

> [!TIP]
> **Pomodoro Integrado:** Use o timer em **Produtividade** para rastrear horas por projeto.

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError" ao rodar

Use o comando completo:

```powershell
python foton_system/interfaces/cli/main.py
```

Ou configure o `PYTHONPATH` antes de rodar.

### MCP não conecta

1. Verifique se o JSON está correto com `foton --mcp-config`
2. Reinicie o Claude/Cursor
3. Aguarde ~15 segundos para o servidor iniciar

### Mudei algo e o sistema não vê

Execute uma **Sincronização** em Gerenciar Clientes para atualizar o banco de dados.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Pipelines: [[Pipelines]]
- Integração IA: [[McpGuide]]
- Arquitetura: [[Concepts]]

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.**

🔗 [LAMP Arquitetura](https://github.com/LAMP-LUCAS/fotonSystem) | 🌍 [Mundo AEC](https://www.mundoaec.com)
