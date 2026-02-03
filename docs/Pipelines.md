# 🔄 Pipelines do Sistema FOTON

> **Como a mágica acontece por trás das cortinas.**

← [[README|Voltar ao Início]] | [[UserGuide|Guia do Usuário]] | [[concepts|Arquitetura]] →

Este documento explica os fluxos de dados do FOTON de forma visual e simplificada.

> **Quer entender a teoria por trás?** Veja [[concepts|Conceitos de Arquitetura]]

---

## 1. Sincronização Cliente/Serviço

### Para Humanos 🧠

> **Detalhes técnicos em:** [[DataModel#Estrutura de Diretórios|Modelo de Dados]]

> Você cria uma pasta no Windows → O FOTON atualiza o Excel automaticamente.
> Você cadastra no Excel → O FOTON cria a pasta automaticamente.

### Diagrama Técnico

```mermaid
flowchart LR
    subgraph FS["📁 Pastas Windows"]
        CF[Pastas de Clientes]
        SF[Pastas de Serviços]
    end

    subgraph DB["📊 Banco Central"]
        XLSX[baseDados.xlsx]
    end

    CF -->|"Sync Base"| XLSX
    SF -->|"Sync Base"| XLSX
    XLSX -->|"Sync Folders"| CF
    XLSX -->|"Sync Folders"| SF
```

---

## 2. Centros de Verdade (INFO Files)

### Para Humanos 🧠

> **Veja a estrutura completa:** [[DataModel|Modelo de Dados]]
> **Aprenda a usar:** [[UserGuide#Arquivos INFO|Guia do Usuário]]

> Cada cliente tem um "cartão de visita digital" chamado `INFO-CLIENTE.md`.
> Você pode editar esse arquivo no Bloco de Notas, e o FOTON respeita.
> Quando você altera no Excel, o sistema atualiza o arquivo. E vice-versa.

### Diagrama Técnico

```mermaid
flowchart TD
    subgraph DB["📊 Banco Central"]
        Rows[Linhas do Excel]
    end

    subgraph Files["📝 Arquivos Distribuídos"]
        InfoC[INFO-CLIENTE.md]
        InfoS[INFO-SERVICO.md]
    end

    Rows -->|"Exportar"| InfoC
    Rows -->|"Exportar"| InfoS
    InfoC -->|"Importar"| Rows
    InfoS -->|"Importar"| Rows
```

---

## 3. Geração de Documentos

### Para Humanos 🧠

> **Entenda a lógica:** [[concepts#Context-Aware Engine|Conceitos de Arquitetura]]
> **Tutorial prático:** [[UserGuide#Geração de Documentos|Guia do Usuário]]

> Quando você pede uma proposta, o FOTON:
>
> 1. Pega os dados do cliente (nome, endereço, CPF)
> 2. Pega os dados do serviço (tipo de projeto, área)
> 3. Junta tudo como um sanduíche 🥪
> 4. Substitui as variáveis no template
> 5. Salva o documento pronto na pasta

### Diagrama Técnico

```mermaid
flowchart TD
    subgraph Inputs["📥 Fontes de Dados"]
        L1[INFO-CLIENTE.md]
        L2[INFO-SERVICO.md]
        L3[Dados do Documento]
        TPL["📄 Template"]
    end

    subgraph Engine["⚙️ Motor de Contexto"]
        Merge["Mesclar Dados"]
        Math["Resolver Fórmulas"]
        Render["Renderizar"]
    end

    L1 --> Merge
    L2 --> Merge
    L3 --> Merge
    Merge --> Math
    Math --> Render
    TPL --> Render
    Render --> Output["📄 Documento Final"]
```

> [!TIP]
> O dado mais específico sempre vence. Se o cliente tem `@cidade: SP` e o serviço tem `@cidade: RJ`, o documento usará `RJ`.

---

## 4. Ferramentas Administrativas

### 4.1 Gerenciador de Schema

#### Para Humanos 🧠

> **Aprenda a usar:** [[UserGuide#Schema Manager|Guia do Usuário]]

> Você quer renomear `@obs` para `@observacoes`?
> O Schema Manager faz isso em TODO o sistema de uma vez: Excel, arquivos INFO, tudo!

```mermaid
flowchart LR
    Schema[schema.json] --> Manager[Schema Manager]
    Manager -->|"Renomear"| Excel[baseDados.xlsx]
    Manager -->|"Renomear"| Files[INFO-*.md]
```

### 4.2 Diagnóstico do Sistema

#### Para Humanos 🧠

> **Entenda quando usar:** [[UserGuide#Diagnóstico|Guia do Usuário]]

> O sistema está estranho? Rode o diagnóstico.
> Ele verifica tudo e gera um relatório em `reports/`.

```mermaid
flowchart TD
    Start["🔍 Iniciar Diagnóstico"] --> CheckFiles
    CheckFiles["Verificar Arquivos"] --> LoadDB
    LoadDB["Carregar Excel"] --> Scan
    Scan["Escanear Pastas"] --> Report["📋 Gerar Relatório"]
```

### 4.3 Correção em Lote

#### Para Humanos 🧠

> **Tutorial:** [[UserGuide#Correção em Lote|Guia do Usuário]]

> Adicionou um campo novo no template? Use a correção em lote.
> O sistema adiciona esse campo em TODOS os arquivos INFO automaticamente.

---

## 📚 Documentação Relacionada

- [[UserGuide|📖 Guia do Usuário]] - Como usar cada funcionalidade
- [[DataModel|📊 Modelo de Dados]] - Estrutura de arquivos e DB
- [[concepts|🏗️ Arquitetura]] - Clean Architecture e Hexagonal
- [[mcp_guide|🤖 Integração IA]] - Como a IA se conecta aos pipelines

---

## 🎯 Resumo Visual

```mermaid
flowchart TB
    subgraph User["👤 Usuário"]
        Pasta["Cria Pasta"]
        Excel["Edita Excel"]
        Info["Edita INFO.md"]
    end

    subgraph FOTON["🤖 FOTON"]
        Sync["Sincronização"]
        DocGen["Gerador de Docs"]
        Admin["Ferramentas Admin"]
    end

    subgraph Output["📤 Saídas"]
        Doc["Propostas/Contratos"]
        Report["Relatórios"]
    end

    Pasta --> Sync
    Excel --> Sync
    Info --> Sync
    Sync --> DocGen
    DocGen --> Doc
    Admin --> Report
```

---

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.**

🔗 [LAMP Arquitetura](https://github.com/LAMP-LUCAS/fotonSystem) | 🌍 [Mundo AEC](https://www.mundoaec.com)
