# FOTON SYSTEM - CONTEXTO PARA AGENTES (LLM_CONTEXT)

> **Identidade do Sistema:** O Foton System é uma "Camada de Orquestração de Arquitetura" (Architecture Orchestration Layer). Ele não é apenas um gerador de documentos, mas um **Sistema Operacional para Escritórios de Arquitetura Autônomos**.

## 0. PROTOCOLO OBRIGATÓRIO
**ANTES DE QUALQUER AÇÃO, LEIA: [[LlmProtocol]]**
Você deve seguir rigorosamente a arquitetura PARA + Zettelkasten descrita no protocolo para manter a documentação coesa e evitar entropia.

## 1. O Problema que Resolvemos (Contexto do Usuário)
Arquitetos autônomos sofrem com a **fragmentação**.
*   Dados do cliente estão no Whatsapp.
*   Dados do projeto estão na cabeça do arquiteto.
*   Financeiro está numa planilha esquecida.
*   Documentos são feitos copiando e colando (gerando erros).

**O Foton resolve isso criando "Centros de Verdade" (Single Source of Truth) baseados em arquivos simples (Markdown) que vivem junto com os arquivos de projeto.**

## 2. Arquitetura do Sistema

O sistema segue uma arquitetura modular inspirada em **Hexagonal Architecture (Ports and Adapters)**, mas simplificada para scripts Python.

### Estrutura de Diretórios
*   /foton_system: Código fonte.
    *   /modules: Domínios do negócio.
        *   /documents: Geração de propostas e contratos.
        *   /clients: Gestão de dados de clientes (Planejado).
        *   /productivity: Ferramentas de foco (Pomodoro).
    *   /infrastructure: Adaptadores (Word, PowerPoint, Excel, Sistema de Arquivos).
    *   /interfaces: CLI e futuramente GUI/Web.

### Conceitos Chave

1.  **Centros de Verdade (INFO-*.md):**
    *   Arquivos de texto que contêm o estado atual do projeto.
    *   O Agente deve **LER** esses arquivos para entender o contexto antes de agir.
    *   O Agente deve **ESCREVER** nesses arquivos para salvar decisões.

2.  **Middlewares de Inteligência:**
    *   ormatting.py: Garante que números sejam formatados como moeda brasileira (R$).
    *   cub_service.py: Busca dados externos (CUB) automaticamente.

3.  **Pipeline de Geração:**
    *   Contexto (INFO) + Template (DOCX/PPTX) + Dados Variáveis = Documento Final.

## 3. Diretrizes para Agentes

Ao atuar neste repositório, você (Agente) deve agir como um **Gerente de Escritório Virtual**.

*   **Proatividade:** Se faltar um dado no INFO-CLIENTE, infira pelo contexto ou pergunte, mas não deixe o campo vazio.
*   **Segurança:** Nunca sobscreva um arquivo de dados existente sem verificar se ele já tem informações valiosas. Use versionamento (ex: ..._R01, ..._R02).
*   **Padrões de Tipagem:**
    *   Datas: Sempre por extenso (07 de Maio de 2026).
    *   Anos/Códigos/IDs: **OBRIGATÓRIO** usar aspas (ex: `@anoProjeto: "2026"`, `@numero: "001"`) para evitar que o parser formate como decimal (`2.026,00`).
    *   Valores Monetários: Sempre números puros com duas casas decimais (ex: `1500.50`) para cálculos. O sistema cuida do `R$`.
    *   Nomes de Arquivo: 02-COD_DOC_TIPO_VER_REV_NOME.ext.


## 4. Integração com GitHub

Este sistema é mantido em: https://github.com/LAMP-LUCAS/fotonSystem.
Ao sugerir melhorias de código, priorize:
1.  **Legibilidade:** Python limpo e tipado.
2.  **Desacoplamento:** Não misture lógica de apresentação (CLI) com regra de negócio.
3.  **Resiliência:** O sistema deve funcionar mesmo se a internet cair (com exceção de buscas externas como CUB).
