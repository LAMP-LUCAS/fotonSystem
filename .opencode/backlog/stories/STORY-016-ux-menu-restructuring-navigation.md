---
status: "ready"
sprint: "2026-SPRINT-5"
---

# STORY-016: UX — Reestruturação de Menu + Navegação

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Descrição

Reestruturar o menu de clientes com subgrupos visuais. Implementar busca global com atalho `g`, `parse_command()` para atalhos de teclado, paginação em MCP tools e confirmação padronizada para ações destrutivas.

## Regras Implementadas

- **RULE-DOMAIN-4.4:** Menu reestruturado em subgrupos (Cadastro, Manutenção, Serviços, Perigo)
- **RULE-DOMAIN-4.5:** Atalho `g` para busca global com drill-down
- **RULE-DOMAIN-4.6:** `parse_command()` para `h`, `00`, `q`, texto livre
- **RULE-DOMAIN-4.7:** `listar_clientes` MCP com parâmetros opcionais `pagina`/`itens_por_pagina`
- **RULE-DOMAIN-4.8:** `confirm_action()` padronizada com `dangerous=True`

## Critérios de Aceite

- [ ] Menu clientes exibe subgrupos: "--- Cadastro ---", "--- Manutenção ---", "--- Serviços ---", "--- Perigo ---"
- [ ] Ações destrutivas agrupadas sob "--- Perigo ---"
- [ ] Atalho `g` dispara `global_search()` por alias, nome, código, NIF
- [ ] Resultados da busca global numerados com drill-down para ficha do cliente
- [ ] `parse_command()`: `h` → ajuda, `00` → início, `q` → sair, texto → busca
- [ ] `listar_clientes(pagina=1, itens_por_pagina=20)` disponível no MCP
- [ ] Parâmetros opcionais não quebram chamadas sem eles (backward compat)
- [ ] `confirm_action("mensagem", dangerous=True)` com destaque visual
- [ ] `confirm_action("mensagem", dangerous=False)` padrão S/N
- [ ] Testes: parse_command, global_search, paginação, drill-down, confirm_action
- [ ] Zero regressão

## Estimativa

8h
