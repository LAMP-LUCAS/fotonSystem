---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-060: Modo de compatibilidade (fallback menus hierárquicos)

**Épico:** EPIC-013 (Fase 3)
**Spec:** `MOD-TUI/SPEC-TUI-MODAL-v1.0.md` (RULE-TUI-1.3, 8.4, 8.8)
**Estimativa:** 1h

## Descrição

Implementar o modo de compatibilidade que restaura a TUI hierárquica original quando
`modal_enabled: false` em settings.json. Isso garante que usuários que preferem
o modelo antigo não percam funcionalidade.

## Regras Implementadas

- **RULE-TUI-1.3:** Se `modal_enabled: false`, fallback total
- **RULE-TUI-8.4:** `modal_enabled` (bool, default: false) em settings.json
- **RULE-TUI-8.8:** Compatibilidade restaura COMPLETAMENTE o comportamento original

## Funcionalidades

### Comportamento

- Default: `modal_enabled: false` (modo de compatibilidade ativo)
- Quando `false`: sistema carrega `menus.py` original com handlers hierárquicos
- Quando `true`: sistema carrega `ModalEngine` com interface modal
- Alternância entre modos requer restart (ou `:set modal_enabled=true` com reload)

### Verificação de Completude

Para garantir que nada se perdeu:

| Funcionalidade | Modal | Hierárquico |
|---------------|-------|-------------|
| Listar clientes | `:e clientes` | Menu > Clientes > Listar |
| Busca global | `/termo` | Menu > Opção 4 |
| Cadastrar cliente | `:e clientes/new` | Menu > Clientes > Novo |
| Gerar documento | `v j :g` | Menu > Documentos > Gerar |
| Consultar RAG | Submenu | Configurações > RAG |
| Financeiro | `:vsplit financeiro/fulano` | Menu > Financeiro > Cliente |
| Todas as ferramentas MCP | `:e tools/nome` | Menu > ... |
| Sair | `:q!` ou `q` | `q` |

## Critérios de Aceite

- [ ] `modal_enabled: false` carrega TUI hierárquica exatamente como antes
- [ ] `modal_enabled: true` carrega ModalEngine
- [ ] Alternância requer restart (com aviso ao usuário)
- [ ] Nenhuma funcionalidade perdida em modo compatibilidade
- [ ] Testes: `test_compatibility_mode_fallback`, `test_compatibility_completeness`, `test_compatibility_toggle_requires_restart`
- [ ] Zero regressão na suite existente

## Dependências

- STORY-054 (ModalEngine — para testar alternância)

## Estimativa

1h
