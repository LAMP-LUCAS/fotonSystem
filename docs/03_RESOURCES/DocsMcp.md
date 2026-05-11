# Documentação FOTON MCP — Secretário Virtual Inteligente

## 1. Conceitos Fundamentais

O **FOTON MCP** transforma o sistema legado de arquitetura em um assistente de IA capaz de operar o escritório. Ele se baseia em dois pilares:

### A. Centros de Verdade (Single Source of Truth)

Cada cliente possui um arquivo `INFO-*.md`. Este arquivo é a **única fonte de verdade** para a IA. Antes de qualquer ação (gerar contrato, registrar financeiro), o MCP lê este arquivo para obter contexto.

### B. O Secretário Virtual LLM

O MCP não é apenas um conjunto de ferramentas; é um protocolo que permite que o Claude ou Gemini (via cursor/desktop app) hajam como um secretário:

- **Pró-atividade**: Ele sugere correções ou preenchimentos.
- **Segurança**: Nunca sobrescreve dados sem backup (`.bak`).
- **Auditabilidade**: Operações críticas usam o `OpContext` (POP Auditado).

---

## 2. Configuração

O MCP respeita as configurações globais do FotonSystem definidas em:
`%LOCALAPPDATA%\FotonSystem\bin\_internal\foton_system\config\settings.json`

### Caminhos Críticos

- `caminho_pastaClientes`: Onde estão os arquivos dos clientes (OneDrive/Dropbox).
- `caminho_templates`: Onde ficam os arquivos `.docx` e `.pptx` (KIT DOC).
- `caminho_baseDados`: O Excel mestre que o MCP sincroniza.

---

## 3. Guia de Ferramentas (21 ferramentas)

### 📂 Pilar: Clientes

- `listar_clientes`: Lista todos os projetos (ignora pastas de sistema).
- `cadastrar_cliente`: Cria a estrutura de pastas e o `INFO-CLIENTE.md`.
- `ler_ficha_cliente`: Lê o contexto do projeto (Centro de Verdade).
- `atualizar_ficha_cliente`: Adiciona notas de reunião ou decisões técnicas.
- `listar_servicos_cliente`: Lista sub-projetos (ex: Arq, Interiores).

### 💵 Pilar: Financeiro & BI

- `registrar_financeiro`: Adiciona entradas/saídas no `FINANCEIRO.csv` do cliente.
- `consultar_financeiro`: Resumo de saldo/receita do cliente específico.
- `resumo_financeiro_geral`: Dashboard executivo de todo o escritório.

### 📄 Pilar: Documentos

- `listar_templates`: Mostra o catálogo de contratos e propostas.
- `listar_documentos_cliente`: Lista arquivos gerados e arquivos técnicos.
- `validar_template`: Check "pré-voo" para ver se faltam variáveis.
- `gerar_documento`: Faz o merge final do template com os dados.

### 🔄 Pilar: Sincronização & Sistema

- `info_sistema`: Diagnóstico de saúde do MCP e caminhos ativos.
- `sincronizar_base`: Atualiza o Excel a partir dos arquivos `.md`.
- `sincronizar_clientes`: Descobre pastas novas criadas manualmente.
- `exportar_fichas`: Puxa dados do DB para os arquivos `.md`.

### 🧠 Pilar: Memória (RAG)

- `consultar_conhecimento`: Busca semântica em projetos passados.
- `indexar_conhecimento`: Treina a memória da IA com novos arquivos.

### 🚀 Pilar: Pipelines Inteligentes

- `pipeline_novo_cliente`: Check de duplicata + Criação + Verificação.
- `pipeline_emitir_documento`: Validação completa + Relatório de erros antes de gerar.

---

## 4. Como Utilizar (Exemplos de Prompts)

**Para começar o dia:**
> "Quais são meus clientes ativos e como está a saúde financeira geral do escritório?"

**Para criar um cliente novo:**
> "Crie um novo cliente chamado Silva Residência. O nif é 123..." (O MCP usará o pipeline para evitar duplicados).

**Para gerar um contrato:**
> "Valide se temos todos os dados para o contrato de projeto do cliente Santos e, se sim, gere o documento."
