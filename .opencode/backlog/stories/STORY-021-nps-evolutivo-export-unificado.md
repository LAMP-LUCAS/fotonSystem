---
status: "done"
sprint: "2026-SPRINT-6"
---

# STORY-021: NPS Evolutivo + Export Unificado

**Épico:** EPIC-012, EPIC-001
**Spec:** `MOD-UX/SPEC-UX-v1.2.md`, `MOD-TELEMETRY/SPEC-TELEMETRY-v1.0.md`

## Descrição

Expandir a pesquisa NPS existente com campos de contexto (comentário opcional, session_count, operation_count, interface, session_id), exibição de evolução temporal com tendência, e exportação unificada para email (gera .zip local com relatório NPS + telemetria + sessão). Adicionar opção "Exportar Dados de Uso" no menu Configurações.

**Dependência:** Requer STORY-020 (session_tracker para obter session_count/operation_count, operation_log.jsonl para compor o .zip).

## Regras Implementadas

- **RULE-UX-9.1:** NPS expandido (nota + classificação + comentário + contexto automático + tendência visual + tabela histórica)
- **RULE-UX-9.2:** Exportação para email (arquivo .zip local, sem envio automático)
- **RULE-TELEMETRY-1.5:** Opção "Exportar Dados de Uso" no menu Configurações

## Critérios de Aceite

- [ ] Formulário NPS coleta nota 0-10 + comentário opcional (textarea)
- [ ] Registro em nps_responses.jsonl inclui: timestamp, nota, classificacao, comentario, session_count, operation_count, session_id, interface
- [ ] Após resposta: exibe nota atual com classificação, média histórica, tendência visual (📈📉➡️) e tabela das últimas 5 respostas
- [ ] Opção "Exportar para Email" no pós-NPS gera .zip na Área de Trabalho
- [ ] .zip contém: relatório NPS.md legível, operation_log.jsonl, session.json
- [ ] Instrução exibida: "Envie o arquivo para contato@mundoaec.com"
- [ ] "Exportar Dados de Uso" no menu Configurações (fora do fluxo NPS)
- [ ] Nenhuma requisição HTTP feita — dado 100% local
- [ ] 706+/706+ testes passando (zero regressão)

## Estimativa

4h

## Débito Técnico

N/A
