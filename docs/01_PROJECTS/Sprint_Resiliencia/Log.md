# Log — Sprint Resiliência e Robustez

## Estrutura

Cada fase é registrada com data, arquivos alterados, e resultado dos testes.

```
[YYYY-MM-DD] Fase X.Y — Descrição
  Δ arquivos: [lista]
  ✅ Testes: 264/264 passed
```

---

## Pendentes

| Fase | Status | Início |
|------|--------|--------|
| 1 — `safe_eval()` + substituições | ✅ | 2026-06-08 |
| 2 — Bare excepts | ✅ | 2026-06-08 |
| 3 — Bugs e placebos | ✅ | 2026-06-08 |
| 4 — Vapor removal | ✅ | 2026-06-08 |
| 5 — Arquitetura | ✅ | 2026-06-08 |
| 6 — Robustez | ✅ | 2026-06-08 |
| 7 — Qualidade agêntica | ✅ | 2026-06-08 |
| 8 — Testes | ✅ | 2026-06-08 |

---

## Registro

```
[2026-06-08] Fase 1 — safe_eval() substitui eval() em 2 locais
  Δ arquivos: +safe_math.py (novo), +test_safe_math.py (novo), ~document_service.py, ~form_session.py
  ✅ Testes: 293/293 passed (27 novos + 266 existentes)
  🔐 eval() removido de: document_service.py:379, form_session.py:130
  📊 Baseline: 264 → 293 (+29 testes)

[2026-06-08] Fase 2 — 23 bare except: blocks eliminados
  Δ arquivos: ~environment_porter.py, ~menus.py, ~form_view.py, ~excel_client_repository.py,
               ~document_service.py, ~tui_form_filler_use_case.py, ~form_session.py,
               ~install_service.py, ~op_doc_gen.py, ~manage_schema.py, ~test_environment_porter.py
  ✅ Testes: 293/293 passed (zero regressão)
  🔧 Fix: test_environment_porter.py — monkeypatch.open salva original_open
  📊 Bare excepts: 23 → 0

[2026-06-08] Fase 3 — 4 bugs/placebos corrigidos
  Δ arquivos: ~main.py, ~interfaces/cli/main.py, ~scripts/admin_launcher.py,
               ~interfaces/cli/menus.py, ~core/memory/vector_store.py
  ✅ Testes: 293/293 passed (zero regressão)
  🔧 3.1: Version hardcoded 1.0.0 → __version__ dinâmico em main.py:95 e cli/main.py:158
  🔧 3.2: Admin launcher off-by-one corrigido (idx-1)
  🔧 3.3: Watcher "Desativar" agora chama watcher.stop() real
  🔧 3.4: Circuit breaker reseta _last_failure_time na transição HALF_OPEN→CLOSED

[2026-06-08] Fase 4 — Vapor/dead code removido (~70 linhas)
  Δ arquivos: ~client_service.py (removidos 9 methods backward-compat),
               ~bootstrap_service.py (removido enable_mcp),
               ~environment_porter.py (removido get_form_filler())
               docs/04_ARCHIVES/chat.py (movido de interfaces/cli/)
               ~test_client_service.py (3 tests atualizados p/ módulo direto)
  ✅ Testes: 293/293 passed (zero regressão)
  📊 Vapor removido: ~70 linhas (chat.py:32, backward-compat:26, enable_mcp:1, get_form_filler:12)
  📝 4.5 removido do plano — except ValueError em tools é legítimo (decorator re-lança)

[2026-06-08] Fase 5 — Arquitetura (entry points, factory, DI, domain sem infra)
  Δ arquivos: +foton_system/entry.py (novo),
               ~interfaces/cli/main.py (MCP delegado p/ safety_entry),
               ~interfaces/mcp/foton_mcp.py (2 tools sem import direto de ClientService),
               ~modules/documents/application/use_cases/document_service.py (_parse_md_data static; info_template_path param),
               ~modules/sync/sync_service.py (DocumentService._parse_md_data direto),
               ~modules/clients/application/use_cases/client_crud.py (import PathManager localizado)
  🔧 5.1: entry.py criado — `python -m foton_system.entry --mcp` funciona
  🔧 5.2: cli/main.py --mcp agora delega para safety_entry() (stdout zero antes do mcp.run())
  🔧 5.3: cadastrar_cliente e criar_estrutura_servico usam normalize_client_name direto, sem ClientService
  🔧 5.4: SyncService.sync_dashboard usa DocumentService._parse_md_data static (sem DocumentService(None,None))
  🔧 5.5: document_service.create_custom_data_file aceita info_template_path param;
           client_crud.get_template_sections importa PathManager localmente
  ✅ Testes: 293/293 passed (zero regressão)

[2026-06-08] Fase 6 — Robustez e UX (JSON Schema, sync loops, --reset-config, webview)
  Δ arquivos: ~modules/shared/infrastructure/config/config.py (_validate_settings + schema),
               ~interfaces/cli/menus.py (handle_client_sync_menu e handle_service_sync_menu com while True),
               ~interfaces/cli/main.py (--reset-config recria via BootstrapService.initialize()),
               ~interfaces/webview_bridge.py (remove fallback PathManager.get_app_dir() morto)
  🔧 6.1: _validate_settings() checa tipos de chaves críticas, substitui inválidos por default
  🔧 6.2: handle_client_sync_menu + handle_service_sync_menu agora com while True (0 + inválido tratados)
  🔧 6.3: --reset-config remove + recria settings.json imediatamente via BootstrapService.initialize()
  🔧 6.4: webview_bridge.remove fallback PathManager.get_app_dir() — nunca existiu, primeiro caminho
           `__file__.parent / "fotonInfoInterface.html"` funciona em dev e frozen
  ✅ Testes: 293/293 passed (zero regressão)

[2026-06-08] Fase 7 — Qualidade Agêntica (views __init__, paginação, idempotência)
  Δ arquivos: +interfaces/cli/views/__init__.py (vazio — pacote Python),
               ~interfaces/mcp/foton_mcp.py (listar_clientes com limite; pipeline_novo_cliente com NIF check)
  🔧 7.1: views/__init__.py criado (diretório agora é pacote Python)
  🔧 7.2: listar_clientes(limite=0) — mostra N de M quando limite > 0
  🔧 7.3: pipeline_novo_cliente verifica NIF duplicado nos INFO-CLIENTE.md existentes
  ✅ Testes: 293/293 passed (zero regressão)

[2026-06-08] Fase 8 — Cobertura de Testes (TipService + AuditLogger)
  Δ arquivos: +tests/unit/test_tip_service.py (5 testes — indexação, fallback, docs ausentes, pattern, non-md),
               +tests/unit/test_audit_logger.py (4 testes — JSONL, get_events, permissão negada, append múltiplo)
  🔧 8.1: TipService — testes para get_random_tip (com contexto, fallback, docs_dir ausente),
           _index_tips (captura [!DIDACTIC:...], ignora não-.md)
  🔧 8.2: AuditLogger — testes para log_event (escreve JSONL), get_recent_events (lista), PermissionError tratado, append
  📊 Baseline: 293 → 302 testes
  ✅ Testes: 302/302 passed (zero regressão)
```
