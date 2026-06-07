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

## 3. Guia de Ferramentas (32 ferramentas)

### 📂 Pilar: Clientes

- `listar_clientes`: Lista todos os projetos (ignora pastas de sistema).
- `cadastrar_cliente`: Cria a estrutura de pastas e o `INFO-CLIENTE.md`.
- `ler_ficha_cliente`: Lê o contexto do projeto (Centro de Verdade).
- `atualizar_ficha_cliente`: Adiciona notas de reunião ou decisões técnicas.
- `listar_servicos_cliente`: Lista sub-projetos (ex: Arq, Interiores).
- `criar_estrutura_servico`: Cria estrutura de pastas para um novo serviço dentro de um cliente.

### 💵 Pilar: Financeiro & BI

- `registrar_financeiro`: Adiciona entradas/saídas no `FINANCEIRO.csv` do cliente.
- `consultar_financeiro`: Resumo de saldo/receita do cliente específico.
- `resumo_financeiro_geral`: Dashboard executivo de todo o escritório.

### 📄 Pilar: Documentos

- `listar_templates`: Mostra o catálogo de contratos e propostas.
- `listar_documentos_cliente`: Lista arquivos gerados e arquivos técnicos.
- `listar_arquivos_dados`: Lista arquivos de dados (`.md`, `.txt`) disponíveis para um cliente.
- `criar_arquivo_dados`: Cria um arquivo de dados personalizado a partir do template centralizado.
- `validar_template`: Check "pré-voo" para ver se faltam variáveis.
- `gerar_documento`: Faz o merge final do template com os dados.

### 🔄 Pilar: Sincronização & Sistema

- `info_sistema`: Diagnóstico de saúde do MCP e caminhos ativos.
- `sincronizar_base`: Atualiza o Excel a partir dos arquivos `.md`.
- `sincronizar_clientes`: Descobre pastas novas criadas manualmente e adiciona ao DB.
- `sincronizar_pastas_clientes`: Cria pastas de clientes a partir de entradas no DB (direção inversa).
- `sincronizar_pastas_servicos`: Cria pastas de serviços a partir de entradas no DB.
- `exportar_dados_clientes`: Exporta dados do DB para arquivos `.md` nas pastas dos clientes.
- `exportar_dados_servicos`: Exporta dados de serviços do DB para arquivos `.md`.
- `importar_dados_servicos`: Importa dados de serviços de arquivos `.md` de volta ao DB.
- `configurar_agente`: Instala formalmente o Skill Foton Architecture no CLI.

### 🧠 Pilar: Memória (RAG)

- `consultar_conhecimento`: Busca semântica em projetos passados.
- `indexar_conhecimento`: Treina a memória da IA com novos arquivos.

### 🚀 Pilar: Pipelines Inteligentes

- `pipeline_novo_cliente`: Check de duplicata + Criação + Verificação.
- `pipeline_emitir_documento`: Validação completa + Relatório de erros antes de gerar.

### 🏗️ Pilar: Infraestrutura

- `consultar_cub`: Retorna o CUB (Custo Unitário Básico) de referência do mês.
- `verificar_atualizacao`: Verifica se há nova versão do Foton System no GitHub.
- `consultar_auditoria`: Mostra eventos recentes de auditoria (operações POP).
- `ping`: Verifica se o servidor MCP está responsivo.

---

## 3.1 Segurança (Fase 1 — Implemented)

As seguintes melhorias de segurança foram aplicadas na Fase 1 da Sprint de Auditoria:

- **Path traversal prevention**: `validar_template` sanitiza `nome_template` com `Path(nome_template).name` antes de construir o caminho — impede escapes como `../../etc/passwd`.
- **Temp file cleanup**: Subprocessos RAG usam `tempfile.mkdtemp()` + `shutil.rmtree()` em `finally` — sem acúmulo de `_rag_run.py` ou `_rag_error.txt`.
- **Exception narrowing**: Todas as 32 tools têm cláusulas `except` específicas (`ValueError`, `OSError`, `PermissionError`, `ConnectionError`) antes do `except Exception` genérico — sem risco de capturar `KeyboardInterrupt` ou `SystemExit`.
- **dados_extras schema validation**: `_validate_dados_extras()` rejeita dicts aninhados, chaves não-string, cardinalidade >50, valores não escalares.

---

## 4. Como Utilizar (Exemplos de Prompts)

**Para começar o dia:**
> "Quais são meus clientes ativos e como está a saúde financeira geral do escritório?"

**Para criar um cliente novo:**
> "Crie um novo cliente chamado Silva Residência. O nif é 123..." (O MCP usará o pipeline para evitar duplicados).

**Para gerar um contrato:**
> "Valide se temos todos os dados para o contrato de projeto do cliente Santos e, se sim, gere o documento."

**Para verificar integridade do sistema:**
> "Faça um ping no sistema e me mostre o status atual."
