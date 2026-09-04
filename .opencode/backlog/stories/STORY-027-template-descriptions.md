---
status: "done"
sprint: "2026-SPRINT-7"
---

# STORY-027: Sistema de Metadados e Descrição de Templates

**Épico:** EPIC-003
**Spec:** `MOD-DOCUMENTOS/SPEC-DOCUMENTOS-v1.1.md`

## Descrição

Implementar o sistema de descrição de templates exigido pela **RULE-DOC-1.4** ("`listar_templates` retorna todos os templates disponíveis com nome e descrição"). Atualmente `list_templates()` retorna apenas nomes de arquivo. Criar um sistema de metadados sidecar via `templates_index.json` para armazenar descrição, categoria e tags de cada template, e expor essas informações no MCP e TUI.

## Regras

- **RULE-DOC-1.4:** `listar_templates` retorna nome **e descrição** de cada template
- A implementação deve ser backward-compatible: sem `templates_index.json`, o comportamento atual (só nomes) é mantido
- O schema deve permitir futuras extensões (categoria, tags, versão, autor)

## Critérios de Aceite

### G1 — Schema e Criação do Index
- [ ] Arquivo `templates_index.json` criado no diretório de templates (`caminho_templates`)
- [ ] Schema contém por entry: `filename`, `description`, `category` (opcional), `tags` (opcional), `version` (opcional)
- [ ] Script `build_templates_index.py` (ou similar) para gerar/atualizar o index automaticamente, escaneando o diretório e permitindo edição manual das descrições
- [ ] `templates_index.json` versionado no repositório (ou ignorado via .gitignore se gerado localmente — decidir)

### G2 — Carregamento no Código
- [ ] `DocumentService.list_templates()` carrega `templates_index.json` e retorna lista de `TemplateInfo(filename, description, category, tags)` ou similar
- [ ] Se `templates_index.json` não existir, fallback para comportamento legado (só nomes de arquivo)
- [ ] Cache do index em memória (recarregar se arquivo mudar ou a cada N segundos)

### G3 — Exposição no MCP
- [ ] MCP tool `listar_templates` exibe descrição ao lado do nome do template
- [ ] Formato: `📄 {filename} — {description}` ou similar
- [ ] Filtro por categoria via parâmetro opcional `categoria`

### G4 — Exposição no TUI
- [ ] Menu "Documentos" mostra descrição dos templates ao listar
- [ ] Opção "Detalhes do Template" exibe metadados completos (filename, descrição, categoria, tags)

### G5 — Testes
- [ ] Teste: `list_templates` com `templates_index.json` retorna descrições
- [ ] Teste: `list_templates` sem index fallback para lista simples
- [ ] Teste: index com campo ausente (ex: sem `description`) não quebra
- [ ] Teste: MCP `listar_templates` exibe descrição no formato esperado
- [ ] Teste: cache invalida ao modificar arquivo

## Arquivos Afetados

- `foton_system/modules/documents/application/use_cases/document_service.py` — `list_templates()`, `TemplateInfo`
- `foton_system/modules/documents/domain/models/template_info.py` (novo) — dataclass `TemplateInfo`
- `foton_system/interfaces/mcp/foton_mcp.py` — `listar_templates` tool com descrição
- `foton_system/interfaces/cli/menus_docs.py` — exibição de descrição no TUI
- `scripts/build_templates_index.py` (novo) — gerador do index
- `ADM/KIT DOC/templates_index.json` (novo) — arquivo de metadados

## Riscos

- **Manutenção do index:** Descrições precisam ser mantidas manualmente quando novos templates são adicionados. Mitigação: script `build_templates_index.py` detecta templates sem entrada no index e emite warning.
- **Performance:** Carregar JSON a cada `list_templates()` é leve (< 1ms para 50 entries), mas cache em memória evita I/O repetido.
- **Encoding:** Nomes de templates podem ter acentos e caracteres especiais (ex: `02-COD_DOC_PC_00_R00_PROPOSTA_ANTEPROJETO.pptx`). Garantir UTF-8.

## Definição de Pronto (DoD)

- [ ] `templates_index.json` criado e populado com todos os templates existentes
- [ ] `list_templates()` retorna `TemplateInfo` com filename + description
- [ ] MCP `listar_templates` exibe descrições
- [ ] Fallback compatível se index ausente
- [ ] Testes para index presente, ausente e corrompido
- [ ] `python -m pytest` — zero regressão
- [ ] Commits com `[STORY-027]`

## Dependências

- Independente de STORY-026 (podem ser executadas em paralelo)

## Estimativa

4h
