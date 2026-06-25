---
type: adr
domain: infrastructure
status: proposed
date: 2026-06-25
---

# ADR004: Arquitetura de Acesso Remoto e Integração Contínua

## Status

Proposto

## Contexto

O Foton System está restrito ao desktop do escritório, operando exclusivamente via TUI local e MCP via stdio. Isso limita o uso em situações críticas: profissionais em canteiro de obras não conseguem consultar dados, registrar ocorrências ou acessar documentos sem retornar ao escritório. Não há API pública documentada para integrar com ferramentas externas (ERP, CRM, contabilidade). O servidor MCP não opera em modo TCP/IP.

Esta decisão arquitetural substitui o EPIC-005 (anteriormente um PRD de épico), pois o escopo descrito é **infraestrutural e transversal** — um capacitador técnico para múltiplos épicos de negócio, não uma funcionalidade de valor isolado.

## Decisão

Adotar arquitetura de acesso remoto em 3 camadas, evoluindo progressivamente:

### Fase 1: MCP TCP/IP (imediatamente aplicável)
O servidor MCP deve suportar modo TCP/IP além do stdio atual, permitindo conexão remota de agentes de IA e clientes customizados. Autenticação por token de acesso.

### Fase 2: Modo Headless (curto prazo)
O sistema deve iniciar como serviço autônomo sem TUI, expondo apenas MCP (TCP/IP) e preparando terreno para API REST. Necessário para deploy em servidor e automações noturnas.

### Fase 3: API REST Documentada (médio prazo)
Interface programática REST com endpoints para as operações principais: consulta de clientes, serviços, documentos e financeiro. Documentação com exemplos em curl, Python e JavaScript.

### Não-Escopo (Fase Futura)
- Interface web completa (substitui a TUI) — não faz parte desta ADR
- Aplicativo mobile nativo — pode ser construído sobre a API REST futuramente

## Consequências

- **Positivas:**
  - Profissionais em campo podem consultar dados sem retornar ao escritório
  - Integração com outras ferramentas via API documentada
  - Automação de processos noturnos via modo headless
  - Agentes de IA podem operar remotamente via MCP TCP/IP

- **Negativas:**
  - Requer implementação de autenticação e autorização (token, rate limiting)
  - Aumento da superfície de ataque — segurança deve ser tratada desde a fase 1
  - Necessidade de documentação de API mantida em sincronia com o código
  - Modo headless requer reestruturação do ponto de entrada (`entry.py`)

## Rastreabilidade

Os requisitos originalmente listados no EPIC-005 são agora rastreados como:

| Requisito EPIC-005 | Onde é tratado |
|---|---|
| MCP TCP/IP remoto | ADR004 — Fase 1 |
| Modo headless | ADR004 — Fase 2 |
| API REST documentada | ADR004 — Fase 3 |
| Interface web mobile-first | Não-escopo (futuro) |
| Bridge Redmine | Não-escopo (futuro) |

## Links Relacionados

- ADR001: PARA + Zettelkasten
- EPIC-001: Usabilidade TUI
- EPIC-009: Conformidade e Segurança