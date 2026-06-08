---
name: foton-documents
description: Geração inteligente de documentos de arquitetura — templates DOCX/PPTX, validação de variáveis, merge final
---

# Foton Skill: Documentos

Skill especializada em **geração de documentos** do Foton System.
Carregue esta skill quando a tarefa envolver criar contratos, propostas ou validar templates.

## Skills relacionadas

Este skill faz parte do ecossistema Foton. Consulte as demais conforme necessário:

| Skill | Quando usar |
|---|---|
| `foton-architecture` | Visão geral do sistema, primeiros passos |
| `foton-clients` | Cadastro e fichas de clientes (dados para documentos) |
| `foton-finance` | Registrar entradas/saídas, consultar financeiro |
| `foton-rag` | Buscar conhecimento em projetos passados |

## Ferramentas

| Ferramenta | Descrição |
|---|---|
| `listar_templates` | Catálogo de templates DOCX/PPTX disponíveis |
| `listar_documentos_cliente` | Arquivos já gerados para um cliente |
| `listar_arquivos_dados` | Arquivos .md/.txt de dados do cliente |
| `criar_arquivo_dados` | Arquivo de dados customizado a partir do template central |
| `validar_template` | Pré-voo: verifica variáveis faltantes no template |
| `gerar_documento` | Merge final: template + dados → DOCX/PPTX |
| `pipeline_emitir_documento` | **(Recomendado)** Pré-vôo completo antes de gerar |

## Workflow obrigatório

### Geração de documento (ciclo completo)
1. `listar_templates` — descobrir template adequado
2. `validar_template(cliente, template)` — verificar variáveis
3. `pipeline_emitir_documento(cliente, template)` — pré-vôo completo
4. **Corrigir** INFO files com variáveis faltantes (via `atualizar_ficha_cliente`)
5. `gerar_documento(cliente, template, dados_extras)` — gerar documento final

### Arquivos de dados
1. `listar_arquivos_dados(cliente)` — ver dados disponíveis
2. `criar_arquivo_dados(cliente, cod, descricao)` — criar novo conjunto

## Convenções

- **NUNCA** pule o `validar_template` — variáveis faltantes causam erros no merge
- **Case-insensitive**: `@CLIENTE` ≡ `@cliente`
- **dados_extras**: usar apenas valores escalares (str/int/float), máximo 50 chaves
- **POP Auditado**: geração de documento passa pelo sistema de auditoria
