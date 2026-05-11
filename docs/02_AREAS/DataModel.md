---
type: concept
domain: core
status: active
tags: [datamodel, schema, database]
---
# Modelo de Dados & Centros de Verdade (DataModel)

Este documento define o modelo de dados para o [**FOTON System**](../../README.md), mapeando a Base de Dados Central (`baseDados.xlsx`) para os Centros de Verdade Distribuídos (arquivos `INFO-*.md`) e as variáveis de geração de documentos.

## Visão Geral

O sistema utiliza uma **Arquitetura de Dados Híbrida**:

1.  **Base de Dados Central (`baseDados.xlsx`):** O sistema de registro para dados estruturados, usado para listagem, filtragem e relatórios.
2.  **Centros de Verdade (`INFO-*.md`):** Arquivos mestres distribuídos localizados nas pastas de Clientes e Serviços. Estes são a **fonte primária** para a geração de documentos.

## 1. Clientes (`baseClientes` <-> `INFO-CLIENTE.md`)

... (rest of the table) ...

## 3. Fluxo de Geração de Documentos

Ao gerar um documento (ex: Proposta), o sistema:

1.  **Localiza o Contexto:** Encontra as pastas pai de Cliente e Serviço.
2.  **Carrega a Verdade do Cliente:** Lê `INFO-CLIENTE.md`.
3.  **Carrega a Verdade do Serviço:** Lê `INFO-SERVICO.md` (sobrescreve dados do Cliente se houver colisões).
4.  **Carrega Dados do Documento:** Lê o arquivo `.md` específico do documento (sobrescreve todos).
5.  **Gera:** Substitui as variáveis no template `.docx` ou `.pptx`.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Pipelines: [[Pipelines]]
- Guia do Usuário: [[UserGuide]]

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
