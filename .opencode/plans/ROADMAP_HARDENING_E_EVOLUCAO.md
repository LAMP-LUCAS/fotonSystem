# Roadmap Tático: Hardening e Evolução Arquitetural

**Documento Diretivo:** `docs/01_PROJECTS/AuditoriaSet2026_PlanoHardening.md`  
**Data:** 2026-09-04  
**Status:** ATIVO

---

## 1. Visão Geral

Este documento define a sequência tática de execução das melhorias de engenharia e novas funcionalidades do Foton System, estruturadas em 3 momentos:

1. **Momento 1: Higiene Imediata** (Tático / Curto) — Limpeza de settings, saneamento de documentação e remoção de arquivos de debug.
2. **Momento 2: Sprint de Hardening e Desacoplamento** (Estrutural) — Quebra dos 5 ciclos de dependência, desacoplamento de camadas, fatiamento de `foton_mcp.py` e eliminação de código morto.
3. **Momento 3: Execução dos Marcos Estratégicos** (Negócio) — Fechamento da Sprint 9 (RAG v2), EPIC-006 (Financeiro v2), EPIC-013 (TUI Modal) e Migração para SQLite.

---

## 2. Checklist Operacional

### Momento 1: Higiene Imediata
- [x] Limpeza do arquivo `settings.json` (apontar para pastas reais de produção)
- [x] Atualização do `AGENTS.md` (47 tools catalogadas, 1.061 testes)
- [x] Remoção de resíduos de debug da raiz (`_debug_bisect.py`, `check_paths.py`, etc.)
- [x] Remoção de `foton_system/__init__-lampbook.py` e restauração de `foton_system/__init__.py`
- [x] Execução da suite de testes para validação de zero regressão (com isolamento de basetemp e mock_config)

### Momento 2: Sprint de Hardening (Técnica)
- [ ] Story HARD-01: Desacoplar `tui_form_filler_use_case` via `FormInterfacePort` (eliminar dependência da TUI)
- [ ] Story HARD-02: Eliminar `modules/sync/sync_service.py` e consolidar em `pipeline_sync.py`
- [ ] Story HARD-03: Quebrar ciclo `core.memory ↔ core.rag`
- [ ] Story HARD-04: Quebrar ciclo `core.ops ↔ modules.documents`
- [ ] Story HARD-05: Fatiar `foton_mcp.py` em sub-roteadores (`routers/`)
- [ ] Story HARD-06: Modularizar `client_crud.py` (extrair geradores e templates)

### Momento 3: Marcos Estratégicos
- [ ] Fechar Sprint 9: RAG Pipeline v2 (STORY-036 a 041)
- [ ] Planejar e fatiar o EPIC-006: Módulo Financeiro v2 (`SPEC-FINANCEIRO-v2.0.md`)
- [ ] Planejar e fatiar o EPIC-013: Interface Modal Vim+tmux
- [ ] Planejar a migração relacional para SQLite
