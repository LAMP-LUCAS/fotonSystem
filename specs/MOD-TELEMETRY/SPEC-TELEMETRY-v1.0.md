# SPEC-TELEMETRY-v1.0 — Telemetria e Observabilidade

**Data:** 2026-06-28
**Versão:** 1.0
**Épico:** EPIC-012
**Responsável:** Time Core

## 1. Problema

O Foton System não possui visibilidade sobre uso e performance. Não é possível saber quais funcionalidades são utilizadas, com que frequência, duração ou taxa de sucesso. Métricas do EPIC-002 (redução de 40% em sincronização) não podem ser validadas sem dados reais. A pesquisa NPS existe mas não carrega contexto de uso do respondente.

## 2. Solução Proposta

Três camadas de observabilidade local-first:

1. **Session Tracking** — toda execução do sistema inicia uma sessão com UUID, interface detectada (TUI/MCP) e timestamp. Contadores de sessão e operação são persistidos entre execuções.
2. **Operation Tracking** — toda operação de feature (CRUD, sync, documento, financeiro, conhecimento, NPS) é automaticamente instrumentada com timestamp, duração, sucesso/falha e metadados contextuais.
3. **Export** — o usuário pode gerar um arquivo autocontido com seus dados de telemetria + NPS para compartilhar com o time de desenvolvimento, sem infraestrutura de recebimento.

Nenhum dado sai da máquina sem ação explícita do usuário (LGPD art. 7º).

## 3. Regras de Negócio (RULE-IDs)

### 3.1 Session Tracking

- **RULE-TELEMETRY-1.1:** O bootstrap do sistema deve iniciar uma nova sessão a cada execução de `main.py`. A sessão deve conter: `session_id` (UUID), `timestamp_inicio`, `interface` (detectada automaticamente: `"TUI"` se CLI interativa, `"MCP"` se via servidor MCP), `contador_operacoes` (incrementado a cada operação). O arquivo de sessão deve ser persistido em `session.json` no diretório de configuração do usuário.
- **RULE-TELEMETRY-1.2:** O session.json deve conter contadores monotônicos e imutáveis: `total_sessoes_all_time` (incrementado a cada execução), `total_operacoes_all_time` (acumulado entre sessões), `primeiro_uso` (timestamp ISO da primeira execução detectada). Estes valores NUNCA devem ser decrementados ou resetados.

### 3.2 Operation Tracking

- **RULE-TELEMETRY-1.3:** Toda operação de feature deve ser instrumentada registrando em `operation_log.jsonl`: `timestamp`, `session_id`, `interface`, `operacao` (string única e estável), `sucesso` (bool), `duracao_ms` (float), `metadados` (dict opcional com dados contextuais como `quantidade_clientes`, `quantidade_servicos`, `direcao_sync`, etc.). O registro deve ser escrito de forma atômica (append síncrono ao final do arquivo).
- **RULE-TELEMETRY-1.4:** O arquivo `operation_log.jsonl` deve ter rotação automática: máximo 10MB. Ao atingir o limite, os registros mais antigos devem ser truncados (remove do início até que o arquivo fique abaixo de 8MB). A rotação deve ser silenciosa — não pode interromper a operação em andamento.

### 3.3 Export

- **RULE-TELEMETRY-1.5:** O menu Configurações deve conter a opção "Exportar Dados de Uso" que gera um arquivo autocontido contendo: (a) resumo da sessão atual em formato legível, (b) dados do NPS com evolução histórica, (c) dados brutos de telemetria das operações. O arquivo deve ser salvo na área de trabalho do usuário. O sistema deve exibir a instrução: "Envie o arquivo para contato@mundoaec.com".

## 4. Critérios de Aceite Técnicos

| RULE | Critério de Aceite |
|------|-------------------|
| 1.1 | Executar `main.py` → `session.json` criado com UUID, interface detectada, contador zerado |
| 1.1 | Rodar via MCP → interface = `"MCP"`. Rodar via CLI → interface = `"TUI"` |
| 1.2 | Segunda execução → `total_sessoes_all_time` = 2, `primeiro_uso` mantém data original |
| 1.3 | Decorator `@track_operation("nome")` → registro em `operation_log.jsonl` com todos os campos |
| 1.3 | Operação que levanta exceção → `sucesso: false`, `duracao_ms` preenchido |
| 1.4 | Preencher 10MB+ de log → arquivo truncado para ≤8MB, sem erro |
| 1.5 | Opção "Exportar Dados de Uso" no menu Config → gera arquivo na Área de Trabalho |

## 5. Restrições e Limitações

- LGPD: NENHUMA requisição HTTP deve ser feita pelas rotas de telemetria ou NPS. Todo dado é local-first.
- A rotação do operation_log.jsonl (RULE-TELEMETRY-1.4) é lossy — dados antigos são perdidos. O usuário que quiser histórico completo deve exportar periodicamente.
- O NPS e sua evolução continuam sendo regidos pela SPEC-UX (RULE-UX-9.1 e RULE-UX-9.2). Esta spec cobre apenas a infraestrutura de telemetria subjacente.
- A exportação (RULE-TELEMETRY-1.5) gera arquivo local. O envio para contato@mundoaec.com é responsabilidade do usuário.
