---
type: concept
domain: core
status: active
tags: [meta, dictionary, ddd, terms]
---
# 📖 Dicionário de Domínios e Termos (Dictionary)

Este documento serve como a **Ubiquitous Language** (DDD) do FOTON System. Aqui definimos o que cada termo significa para garantir que Humanos e IAs falem a mesma língua.

## 🏛️ Termos de Arquitetura

- **Centro de Verdade (Center of Truth):** Arquivo `.md` (INFO-CLIENTE, INFO-SERVICO) que detém a autoridade sobre os dados de um projeto. A partir da v1.4.0, o nome segue um pattern configurável.
- **Placeholder:** Token `{nome}` dentro de um pattern de arquivo INFO que é substituído por um valor real. Ex: `{codCliente}` → `JOS01`.
- **Pattern (InfoPattern):** Template de nome de arquivo com placeholders, configurado em `settings.json` sob `info_file_patterns`. Ex: `INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md`.
- **Glob Pattern:** Versão de busca onde placeholders são substituídos por `*`. Gerado automaticamente pelo `to_glob()`.
- **Conformance Checker:** Auditoria automatizada (MCP + classe) que verifica se todos os clientes/serviços seguem o pattern configurado.
- **RalphLoop:** Ciclo agêntico de "Pesquisa -> Plano -> Ação -> Validação".
- **Hexagonal Architecture:** Padrão que isola a lógica de negócio (Core) de implementações externas (Adapters).
- **Zettelkasten + PARA:** Sistema de organização de notas interligadas por grafos e esferas de responsabilidade.

## 👥 Termos de Negócio (Escritório)

- **Cliente:** Pessoa ou entidade que contrata os serviços de arquitetura.
- **Serviço (Service):** Um sub-projeto ou demanda específica vinculada a um cliente (ex: Projeto Executivo, Consultoria).
- **Template:** Modelo de documento (Word/PowerPoint) com variáveis `@tags`.
- **CUB (Custo Unitário Básico):** Índice usado para estimativas de custos de construção.

## 🤖 Termos Técnicos

- **MCP (Model Context Protocol):** Protocolo de comunicação entre o Foton e Assistentes de IA.
- **TUI (Terminal User Interface):** Interface de navegação via teclado no terminal.
- **Frontmatter:** Bloco de metadados YAML no início dos arquivos Markdown.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Protocolo: [[LlmProtocol]]
- Contexto LLM: [[LlmContext]]
