# LAMP System

**Sistema de Automação e Gestão para Arquitetura**

O LAMP é um sistema modular projetado para organizar clientes, serviços e documentos, utilizando uma arquitetura híbrida que combina a robustez de um banco de dados central com a flexibilidade de arquivos de texto distribuídos ("Centros de Verdade").

## 📚 Documentação
- **[Conceitos de Arquitetura](docs/concepts.md)**: Entenda a estrutura Hexagonal e Modular.
- **[Modelo de Dados](docs/DataModel.md)**: Mapeamento entre Banco de Dados e Arquivos.

## 🚀 Funcionalidades Principais

### 1. Gestão de Clientes e Serviços
- **Sincronização Bidirecional**: Mantenha suas pastas e banco de dados sempre alinhados.
- **Banco de Dados Distribuído**: Exporte e importe dados de clientes e serviços via arquivos Markdown (`INFO-*.md`) diretamente nas pastas.
- **Histórico de Alterações**: O sistema rastreia versões e revisões dos dados (ex: `R00`, `R01`).

### 2. Geração de Documentos (Propostas e Contratos)
- **Centros de Verdade**: O sistema utiliza arquivos `INFO-CLIENTE.md` e `INFO-SERVICO.md` como fonte primária de dados.
- **Herança de Dados**: Ao gerar um documento, os dados do cliente e do serviço são carregados automaticamente, evitando repetição.
- **Templates Flexíveis**: Suporte para templates `.docx` e `.pptx`.

### 3. Produtividade
- **Pomodoro Timer**: Cronômetro integrado com logs de sessão.
- **Timesheet**: Registro automático de horas trabalhadas vinculadas a clientes e serviços.

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.10+
- Dependências: `pip install -r requirements.txt`

### Configuração (`settings.json`)
O sistema cria automaticamente um arquivo `settings.json` na primeira execução. Você pode configurar:
- `base_pasta_clientes`: Caminho raiz onde ficam as pastas dos clientes.
- `base_dados`: Caminho para o arquivo Excel central (`baseDados.xlsx`).
- `templates_path`: Caminho para a pasta de templates (`KIT DOC`).

### Execução
Execute o arquivo `run_lamp.bat` ou via terminal:
```bash
python foton_system/main.py
```

## 📖 Guia de Uso

### 1. Clientes e Serviços
No menu principal, acesse **Gerenciar Clientes** ou **Gerenciar Serviços**.
- **Sincronizar Base (Pastas -> DB)**: Lê a estrutura de pastas e atualiza o Excel.
- **Sincronizar Pastas (DB -> Pastas)**: Cria pastas para clientes/serviços cadastrados no Excel.
- **Sincronizar Cadastro (DB <-> Arquivo)**:
    - **Exportar**: Cria arquivos `INFO-CLIENTE.md` e `INFO-SERVICO.md` nas pastas, com todos os dados do banco.
    - **Importar**: Lê os arquivos `INFO` e atualiza o banco de dados se houver mudanças.

### 2. Gerando Documentos
1.  Acesse **Documentos** -> **Gerar Proposta** ou **Contrato**.
2.  Selecione o Cliente e o Serviço.
3.  **Criar Novo Arquivo**: O sistema criará um arquivo `.md` enxuto (ex: `02-COD_DOC_PC_00_R00_PROPOSTA.md`).
4.  Preencha apenas os dados específicos do documento (ex: `@valorProposta`). Os dados do cliente e serviço serão puxados automaticamente dos arquivos `INFO`.
5.  Selecione o Template (`.docx` ou `.pptx`) e o documento será gerado.

### 3. Produtividade
1.  Acesse **Produtividade** -> **Iniciar Pomodoro**.
2.  (Opcional) Vincule a sessão a um Cliente/Serviço.
3.  Ao final, o tempo é registrado em `timesheet.csv`.

## 🏗️ Estrutura de Arquivos (Centros de Verdade)

O sistema prioriza a informação na seguinte ordem (último vence):
1.  **`INFO-CLIENTE.md`** (Pasta do Cliente): Dados cadastrais.
2.  **`INFO-SERVICO.md`** (Pasta do Serviço): Dados do projeto/obra.
3.  **`SEU_ARQUIVO_DE_DADOS.md`** (Específico): Dados da proposta/contrato.

---
Desenvolvido por Mundoaec.com
