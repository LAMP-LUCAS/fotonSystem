---
type: plan
domain: core
status: active
tags: [sprint, refactor, documentation]
---
# 🎯 Plano de Sprint: Refatoração da Documentação (PARA + Zettelkasten)

## 📋 Escopo
Migrar toda a documentação dispersa em `docs/` para a nova estrutura baseada em grafos e interlinks, focando em usabilidade para Agentes LLM.

## ✅ Checklist de Execução
- [x] Criar estrutura de diretórios PARA.
- [x] Criar `LlmProtocol.md` (Guia de Orientação).
- [x] Criar `Index.md` (Mapa de Conteúdo).
- [x] Atualizar `README.md` com links para a nova estrutura.
- [x] Atualizar `LlmContext.md` com referências ao protocolo.
- [x] Mover arquivos para `02_AREAS/` (Conceitos e Domínios).
- [x] Mover arquivos para `03_RESOURCES/` (Manuais e Guias).
- [x] Mover arquivos para `01_PROJECTS/` (Planos de Trabalho).
- [x] Mover arquivos para `04_ARCHIVES/` (Histórico e Releases).
- [x] Adicionar Frontmatter em todos os arquivos migrados.
- [x] Padronizar nomenclatura para `PascalCase.md`.
- [x] Corrigir interlinks e adicionar rodapés de navegação.

## 📐 Especificações Técnicas (Specs)
- **Estrutura de Link:** Sempre usar `[[NomeDoArquivo]]`.
- **Frontmatter:** Mínimo de `type`, `domain`, `status`, `tags`.
- **Organização:** Seguir estritamente o método PARA.

---
## 🔗 Links Relacionados
- Protocolo: [[LlmProtocol]]
- Índice: [[Index]]
