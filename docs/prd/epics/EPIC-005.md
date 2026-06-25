# EPIC-005: Arquitetura de Acesso e Integração Contínua

**Data:** 2026-06-25
**Status:** DEPRECATED — Substituído por ADR004

## Motivo da Deprecação

O escopo original do EPIC-005 foi reclassificado como **decisão arquitetural** (ADR), não como funcionalidade de negócio isolada. Os itens descritos aqui (MCP TCP/IP, modo headless, API REST) são **capacitadores técnicos transversais** que beneficiam múltiplos épicos de negócio, não um épico com valor de negócio próprio.

## Substituição

- **ADR004** (`docs/00_META/ADR/ADR004_RemoteAccessArchitecture.md`) — Define a estratégia de acesso remoto em 3 fases, com rastreabilidade de cada requisito original deste EPIC.
- Os requisitos de interface web mobile-first e bridge Redmine foram movidos para "Não-Escopo (Fase Futura)" na ADR.

## Requisitos Remanescentes

Os requisitos de integração com ferramentas externas (bridge Redmine) e interface web mobile-first permanecem como desejáveis não contemplados. Quando houver demanda de negócio clara, poderão ser reabertos como novo épico ou ADR complementar.