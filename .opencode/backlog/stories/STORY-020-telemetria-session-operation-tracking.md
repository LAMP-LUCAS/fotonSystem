---
status: "done"
sprint: "2026-SPRINT-6"
---

# STORY-020: Telemetria — Session + Operation Tracking

**Épico:** EPIC-012
**Spec:** `MOD-TELEMETRY/SPEC-TELEMETRY-v1.0.md`

## Descrição

Implementar as duas primeiras camadas de observabilidade local-first: rastreamento de sessão (cada execução do sistema gera uma sessão com UUID e interface detectada) e rastreamento de operações (toda feature instrumentada com timestamp, duração, sucesso/falha e metadados). Os dados persistem em `session.json` e `operation_log.jsonl` no diretório de configuração do usuário, com rotação automática de 10MB.

## Regras Implementadas

- **RULE-TELEMETRY-1.1:** Session tracking no bootstrap de main.py
- **RULE-TELEMETRY-1.2:** Contadores monotônicos (total_sessoes, total_operacoes, primeiro_uso)
- **RULE-TELEMETRY-1.3:** Decorator @track_operation para instrumentação de features
- **RULE-TELEMETRY-1.4:** Rotação automática do operation_log.jsonl (10MB max)

## Critérios de Aceite

- [ ] `core/ops/session_tracker.py` — SessionState com UUID, timestamp_inicio, interface (TUI|MCP), contador_operacoes
- [ ] `session.json` criado/persistido no diretório de configuração do usuário
- [ ] Segunda execução → `total_sessoes_all_time` incrementa, `primeiro_uso` mantido
- [ ] `core/ops/operation_tracker.py` — decorator `@track_operation(nome)` que registra timestamp, session_id, interface, operacao, sucesso, duracao_ms, metadados
- [ ] Operação com exceção → registro com `sucesso: false`, duração preenchida
- [ ] Rotação: operation_log.jsonl atinge 10MB → trunca para ≤8MB sem erro
- [ ] Todas as ~20 operações de feature instrumentadas com o decorator
- [ ] 706+/706+ testes passando (zero regressão)

## Estimativa

5h

## Débito Técnico

N/A
