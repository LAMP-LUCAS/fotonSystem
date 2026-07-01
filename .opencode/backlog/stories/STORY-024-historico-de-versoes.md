---
status: "ready"
sprint: "2026-SPRINT-7"
---

# STORY-024: Histórico de Versões

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Descrição

Implementar sistema de histórico versionado de documentos gerados. Substituir o `history.log` textual por `historico_documentos.jsonl` na pasta do cliente. Criar MCP tool para consulta e opção TUI no menu Documentos. Suporte a regeneração preservando versão anterior.

## Regras

- **RULE-DOC-3.6 (nova):** Todo documento gerado é registrado em `historico_documentos.jsonl` na pasta do cliente, com campos: `data_hora`, `tipo_template`, `nome_arquivo`, `status` (sucesso/erro), `versao`, `versao_anterior` (se regeneração), `cliente`.

## Critérios de Aceite

- [ ] `DocumentService._log_generation()` escreve no formato JSONL em vez de history.log
- [ ] JSONL com campos obrigatórios: data_hora (ISO 8601), tipo_template, nome_arquivo, status, versao, cliente
- [ ] Regeneração de documento: versão anterior renomeada com sufixo `_v1`, nova salva como `_v2`, registro com `versao_anterior`
- [ ] MCP tool `historico_documentos(cliente, limite=10)` retorna lista de entradas
- [ ] TUI: opção "Histórico de Documentos" no menu Documentos exibe tabela com data/tipo/status
- [ ] Tratamento de erro: se JSONL não existir → lista vazia, não quebra
- [ ] Testes: criação na primeira geração, append em múltiplas gerações, versionamento na regeneração, MCP tool retorna entradas

## Arquivos Afetados

- `foton_system/modules/documents/application/use_cases/document_service.py` — `_log_generation()` upgrade para JSONL + versionamento
- `foton_system/interfaces/mcp/foton_mcp.py` — nova tool `historico_documentos`
- `foton_system/interfaces/tui/menus/menus_docs.py` — opção "Histórico de Documentos"

## Estimativa

4h

## Dependências

Nenhuma — **independente**, pode ser executada em paralelo com STORY-022
