# Spec: Módulo de Documentos — v1.1

**Data:** 2026-06-25
**Versão:** 1.1
**Responsável:** Time Core
**Alterações:** Adicionadas regras de pré-visualização, placeholders zero, geração em lote, histórico de versões, e engine de fórmulas com validação explícita.

## 1. Problema (v1.1)

A engine de documentos existe e é funcional, mas o usuário não confia nela para uso diário: placeholders não resolvidos geram `"---"` ou `"None"` no documento final, fórmulas de cálculo quebram silenciosamente, não há pré-visualização antes da geração, não há histórico de versões, e cada documento exige operação individual.

## 2. Solução Proposta (v1.1)

Evolução da engine de documentos com camada de confiança:

1. **Pré-validação rigorosa:** Antes de gerar, verificar todas as variáveis do template contra dados disponíveis. Relatório explícito de variáveis resolvidas, não encontradas e fórmulas aplicadas.
2. **Engine de fórmulas com validação:** Fórmulas `[calculo: @area * @cub]` são pré-processadas com substituição de placeholders e validação de tipos. Falha de cálculo interrompe a geração com relatório de erro.
3. **Geração em lote:** Comando único para gerar proposta + contrato + anexo simultaneamente.
4. **Histórico de versões:** Documentos gerados são registrados na ficha do cliente com data, tipo e status. Regeneração preserva versão anterior.
5. **Nomenclatura padronizada:** Documentos gerados nomeados como `CLIENTE_SERVICO_TIPO_DATA.ext`.

## 3. Regras de Negócio

### 3.1 Templates (mantido da v1.0)
- **RULE-DOCUMENTOS-1.1:** Templates ficam em `templates/` no diretório do sistema.
- **RULE-DOCUMENTOS-1.2:** Formatos suportados: `.docx` (Word) e `.pptx` (PowerPoint).
- **RULE-DOCUMENTOS-1.3:** Variáveis no template seguem formato `@NOMEVARIAVEL` (case-insensitive).
- **RULE-DOCUMENTOS-1.4:** `listar_templates` retorna todos os templates disponíveis com nome e descrição.

### 3.2 Validação (atualizado v1.1)
- **RULE-DOCUMENTOS-2.1:** `validar_template` agora gera relatório completo com: variáveis resolvidas (verde), variáveis não encontradas (vermelho), fórmulas validadas, e alerta se alguma variável do INFO tem valor `None` ou `"---"`.
- **RULE-DOCUMENTOS-2.2:** `dados_extras` é opcional, mas quando fornecido: deve ser dict plano (sem aninhamento), máx 50 chaves, valores string/int/float.
- **RULE-DOCUMENTOS-2.3:** Path traversal: `nome_template` é sanitizado com `Path(nome_template).name`.
- **RULE-DOCUMENTOS-2.4 (NOVA):** Pré-validação obrigatória: `gerar_documento` executa `validar_template` internamente. Se houver variáveis não resolvidas ou fórmulas com erro, a geração é **bloqueada** e o relatório de erros é exibido.
- **RULE-DOCUMENTOS-2.5 (NOVA):** Placeholder zero: nenhum `@VAR` pode chegar ao documento final como `"None"`, `"---"` ou string vazia. Toda variável não resolvida gera erro explícito antes da geração.

### 3.3 Geração (atualizado v1.1)
- **RULE-DOCUMENTOS-3.1:** `gerar_documento`: merge template + dados do INFO-*.md + `dados_extras` → arquivo final.
- **RULE-DOCUMENTOS-3.2:** Documento gerado é salvo com prefixo `GERADO_` na pasta do cliente, seguindo padrão `CLIENTE_SERVICO_TIPO_DATA.ext`.
- **RULE-DOCUMENTOS-3.3:** `pipeline_emitir_documento`: pré-voo completo — valida template, verifica duplicidade, e só então executa o merge.
- **RULE-DOCUMENTOS-3.4:** Ao gerar documento, POP de auditoria é acionado.
- **RULE-DOCUMENTOS-3.5 (NOVA):** Geração em lote: `gerar_documentos_lote` aceita lista de pares (template, dados_extras) e gera todos em uma operação. O pré-voo (validar_template) é executado para cada item antes de gerar qualquer um.
- **RULE-DOCUMENTOS-3.6 (NOVA):** Histórico: todo documento gerado é registrado em `historico_documentos.json` na pasta do cliente, com campos: data_hora, tipo_template, nome_arquivo, status (sucesso/erro), versao_anterior (se regeneração).

### 3.4 Engine de Fórmulas (NOVO v1.1)
- **RULE-DOCUMENTOS-4.1 (NOVA):** Fórmulas seguem formato `[calculo: expressao]` onde expressao pode conter operadores `+`, `-`, `*`, `/`, `()`, e referências a `@VARIAVEIS`.
- **RULE-DOCUMENTOS-4.2 (NOVA):** Toda fórmula é pré-processada: substituição de `@VAR` por valores numéricos, validação de tipos (não numérico → erro), e cálculo. Falha em qualquer etapa gera relatório de erro antes da geração.
- **RULE-DOCUMENTOS-4.3 (NOVA):** Fórmulas com resultado `NaN` ou `Infinity` são tratadas como erro e bloqueiam a geração.
- **RULE-DOCUMENTOS-4.4 (NOVA):** Relatório de fórmulas: ao final do cálculo, exibir lista de fórmulas aplicadas com variável de entrada, resultado e status (OK/ERRO).

### 3.5 Preenchimento Interativo (mantido da v1.0)
- **RULE-DOCUMENTOS-5.1:** `criar_arquivo_dados`: cria arquivo de dados customizado para um cliente via formulário interativo.
- **RULE-DOCUMENTOS-5.2:** TUIFormView: navegação campo-a-campo com comandos `n` (próximo), `p` (anterior), `v` (visualizar), `s` (salvar), `a` (abortar), `c` (confirmar).
- **RULE-DOCUMENTOS-5.3:** Campos calculados são exibidos com tag "CALC" e não podem ser editados.

## 4. Relações
- Port: `document_service_port.py`
- MCP tools: `listar_templates`, `listar_documentos_cliente`, `listar_arquivos_dados`, `criar_arquivo_dados`, `validar_template`, `gerar_documento`, `pipeline_emitir_documento`
- Novas MCP tools (propostas): `gerar_documentos_lote`, `historico_documentos`

## 5. Changelog

| Versão | Data | Mudanças |
|---|---|---|
| v1.0 | 2026-06-24 | Versão inicial |
| v1.1 | 2026-06-25 | Adicionado RULE-DOCUMENTOS-2.4, 2.5, 3.5, 3.6, 4.1-4.4 |