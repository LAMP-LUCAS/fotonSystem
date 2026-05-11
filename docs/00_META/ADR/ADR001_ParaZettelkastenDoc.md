---
type: adr
domain: core
status: accepted
date: 2026-05-11
---
# ADR001: Adoção do Modelo PARA + Zettelkasten para Documentação

## Status
Aceito

## Contexto
A documentação anterior do FOTON System estava dispersa, com links quebrados e sem uma estrutura clara de evolução. Isso dificultava tanto o uso por humanos quanto a navegação por agentes de IA, aumentando a entropia do repositório.

## Decisão
Adotar uma estrutura híbrida baseada em:
1.  **PARA (Projects, Areas, Resources, Archives):** Para categorizar o ciclo de vida da informação.
2.  **Zettelkasten:** Para criar um grafo de conhecimento interligado por links bi-direcionais (`[[link]]`) e metadados (Frontmatter YAML).

## Consequências
- **Positivas:** Maior rastreabilidade, facilidade de onboarding para IAs, histórico de sprints preservado.
- **Negativas:** Requer rigor na manutenção dos metadados e na localização dos arquivos.

---
## 🔗 Links Relacionados
- Índice de ADRs: [[Index]]
- Protocolo: [[LlmProtocol]]
