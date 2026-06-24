# Spec: Módulo de Documentos

**Data:** 2026-06-24
**Versão:** 1.0
**Responsável:** Time Core

## 1. Problema
O escritório precisa gerar documentos profissionalizantes (contratos, propostas) a partir de templates DOCX/PPTX, com merge de dados dos clientes e variáveis dinâmicas.

## 2. Solução Proposta
Sistema de templates com engine de merge (variáveis `@tag` em DOCX/PPTX):
- Listagem de templates disponíveis
- Validação de variáveis (pré-voo)
- Geração do documento final
- Suporte a DOCX e PPTX
- Preenchimento interativo via TUIFormView

## 3. Regras de Negócio

### 3.1 Templates
- **RULE-DOCUMENTOS-1.1:** Templates ficam em `templates/` no diretório do sistema.
- **RULE-DOCUMENTOS-1.2:** Formatos suportados: `.docx` (Word) e `.pptx` (PowerPoint).
- **RULE-DOCUMENTOS-1.3:** Variáveis no template seguem formato `@NOMEVARIAVEL` (case-insensitive).
- **RULE-DOCUMENTOS-1.4:** `listar_templates` retorna todos os templates disponíveis com nome e descrição.

### 3.2 Validação
- **RULE-DOCUMENTOS-2.1:** `validar_template`: verificar se o template existe e listar variáveis faltantes no INFO do cliente.
- **RULE-DOCUMENTOS-2.2:** `dados_extras` é opcional, mas quando fornecido: deve ser dict plano (sem aninhamento), máx 50 chaves, valores string/int/float.
- **RULE-DOCUMENTOS-2.3:** Path traversal: `nome_template` é sanitizado com `Path(nome_template).name`.

### 3.3 Geração
- **RULE-DOCUMENTOS-3.1:** `gerar_documento`: merge template + dados do INFO-*.md + `dados_extras` → arquivo final.
- **RULE-DOCUMENTOS-3.2:** Documento gerado é salvo com prefixo `GERADO_` na pasta do cliente.
- **RULE-DOCUMENTOS-3.3:** `pipeline_emitir_documento`: pré-voo completo — valida template, verifica duplicidade, e só então executa o merge.
- **RULE-DOCUMENTOS-3.4:** Ao gerar documento, POP de auditoria é acionado.

### 3.4 Preenchimento Interativo
- **RULE-DOCUMENTOS-4.1:** `criar_arquivo_dados`: cria arquivo de dados customizado para um cliente via formulário interativo.
- **RULE-DOCUMENTOS-4.2:** TUIFormView: navegação campo-a-campo com comandos `n` (próximo), `p` (anterior), `v` (visualizar), `s` (salvar), `a` (abortar), `c` (confirmar).
- **RULE-DOCUMENTOS-4.3:** Campos calculados são exibidos com tag "CALC" e não podem ser editados.

## 4. Relações
- Port: `document_service_port.py`
- MCP tools: `listar_templates`, `listar_documentos_cliente`, `listar_arquivos_dados`, `criar_arquivo_dados`, `validar_template`, `gerar_documento`, `pipeline_emitir_documento`
