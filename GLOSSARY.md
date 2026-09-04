# GLOSSÁRIO DE DOMÍNIO (Ubiquitous Language)

> Fonte primária: `docs/00_META/Dictionary.md`. Este arquivo é um atalho na raiz para consulta rápida por agentes de IA.

## 🏛️ Termos de Arquitetura

- **Centro de Verdade (Center of Truth):** Arquivo `.md` (INFO-CLIENTE, INFO-SERVICO) que detém a autoridade sobre os dados de um projeto. Nome segue um pattern configurável.
- **Placeholder:** Token `{nome}` dentro de um pattern de arquivo INFO substituído por valor real. Ex: `{codCliente}` → `JOS01`.
- **Pattern (InfoPattern):** Template de nome de arquivo com placeholders, configurado em `settings.json` sob `info_file_patterns`.
- **Pasta Oculta:** Diretório com nome iniciado por `.`. Ignorado em varreduras de pastas.
- **Conformance Checker:** Auditoria que verifica se todos os clientes/serviços seguem o pattern configurado.
- **RalphLoop:** Ciclo agêntico de Pesquisa → Plano → Ação → Validação.
- **Hexagonal Architecture:** Padrão que isola lógica de negócio (Core) de implementações externas (Adapters).
- **Zettelkasten + PARA:** Sistema de organização de notas interligadas por grafos e esferas de responsabilidade.

## 👥 Termos de Negócio (Escritório)

- **Cliente:** Pessoa ou entidade que contrata serviços de arquitetura.
- **Serviço (Service):** Sub-projeto vinculado a um cliente (ex: Projeto Executivo).
- **Template:** Modelo de documento (Word/PowerPoint) com variáveis `@tags`.
- **CUB (Custo Unitário Básico):** Índice para estimativas de custos de construção.

## 🤖 Termos Técnicos

- **MCP (Model Context Protocol):** Protocolo de comunicação entre Foton e Assistentes de IA.
- **TUI (Terminal User Interface):** Interface de navegação via teclado no terminal.
- **POP (Procedimento Operacional Padrão):** Operação auditada (criar cliente, gerar documento, registrar financeiro).

---

## 🔗 Referência cruzada

- `docs/00_META/Dictionary.md` — Versão completa com exemplos e contexto.
- `docs/00_META/ADR/` — Decisões arquiteturais.
- `specs/` — Regras técnicas rastreáveis (RULE-IDs).
