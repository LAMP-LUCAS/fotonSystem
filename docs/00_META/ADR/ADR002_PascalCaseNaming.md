---
type: adr
domain: core
status: accepted
date: 2026-05-11
---
# ADR002: Padronização de Nomenclatura PascalCase para Documentos

## Status
Aceito

## Contexto
Arquivos Markdown na pasta `docs/` seguiam múltiplos padrões (snake_case, UPPER_CASE, camelCase), o que gerava inconsistências nos links bi-direcionais e dificultava a predição de caminhos por scripts e IAs.

## Decisão
Padronizar todos os nomes de arquivos de documentação para **PascalCase** (ex: `UserGuide.md`).
Pastas meta e de projeto mantêm o prefixo numérico ou descritivo em snake_case para ordenação no sistema de arquivos.

## Consequências
- **Positivas:** Coesão visual, links previsíveis, conformidade com padrões de "Wikis" modernas.
- **Negativas:** Necessidade de renomear arquivos existentes e atualizar todas as referências internas.

---
## 🔗 Links Relacionados
- Protocolo: [[LlmProtocol]]
- Índice: [[Index]]
