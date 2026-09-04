# Log — Sprint Sistema de Nomenclatura Configurável de Arquivos INFO

## Estrutura

Cada fase é registrada com data, arquivos alterados, e resultado dos testes.

```
[YYYY-MM-DD] Fase X.Y — Descrição
  Δ arquivos: [lista]
  ✅ Testes: X/X passed
```

---

## Pendentes

| Fase | Status | Início |
|------|--------|--------|
| 0 — Config + PatternResolver + PathManager | ✅ | 2026-06-22 |
| 1 — Criação de INFO files | ✅ | 2026-06-22 |
| 2 — Leitura e sincronização | ✅ | 2026-06-22 |
| 3 — Exportação versionada unificada | ✅ | 2026-06-22 |
| 4 — Migração retroativa | ✅ | 2026-06-22 |
| 5 — Conformance checker | ✅ | 2026-06-22 |
| 6 — Limpeza e documentação | ✅ | 2026-06-22 |

---

## Registro

```
[2026-06-22] Fase 0 — Config + PatternResolver + PathManager
  Δ arquivos: +info_pattern_resolver.py (novo), ~path_manager.py, ~config.py,
               ~settings.json, +test_info_pattern_resolver.py,
               +test_path_manager_info_pattern.py
  ✅ Testes: 341/341 passed (39 novos + 302 existentes)
  🔧 Placeholders: {codCliente}, {nomeCliente}, {aliasCliente},
                    {codServico}, {aliasServico}, {versao}, {revisao},
                    {data}, {dataISO}, {ano}, {mes}, {timestamp}, {extensao}
  📐 Default pattern: INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md

[2026-06-22] Fase 1 — Criação de INFO files (get_template_sections + MCP tools)
  Δ arquivos: ~client_crud.py, ~assets/info-Template.md, ~foton_mcp.py,
               +test_client_crud_info_pattern.py
  ✅ Testes: 348/348 passed (7 novos + 341 existentes, zero regressão)
  🔧 Mudanças:
    • get_template_sections(): usa headers do pattern configurável
    • info-Template.md: headers renomeados para ## INFO-CLIENTE / ## INFO-SERVICO
    • criar_estrutura_servico: copia template com nome do pattern (ex: INFO-SERVICO-{cod}_{versao}_R{revisao}.md)
    • pipeline_novo_cliente: busca INFO-CLIENTE via glob pattern em vez de nome fixo

[2026-06-22] Fase 2 — Leitura e sincronização (sync_service + document_service)
  Δ arquivos: ~sync_service.py, ~document_service.py
  ✅ Testes: 348/348 passed (zero regressão)
  🔧 Mudanças:
    • sync_service._collect_client_data: usa glob pattern + fallback INFO-CLIENTE.md
    • document_service._load_context_data: fnmatch com pattern + fallback legacy
    • Fallback mantido para compatibilidade com clientes existentes (INFO-CLIENTE.md)

[2026-06-22] Fase 3 — Exportação versionada unificada
  Δ arquivos: ~client_crud.py, ~test_client_service.py
  ✅ Testes: 348/348 passed (zero regressão)
  🔧 Mudanças:
    • _generate_filename → _resolve_info_filename (via InfoPatternResolver)
    • _parse_filename → _parse_revision_from_filename (via extract())
    • _get_latest_file usa to_glob() do pattern em vez de alias fixo
    • export_client_data / export_service_data refatorados

[2026-06-22] Fase 4 — Migração retroativa
  Δ arquivos: +scripts/migrate_info_to_pattern.py, ~migrate_client_structure.py
  ✅ Testes: 348/348 passed (zero regressão)
  🔧 Mudanças:
    • Novo script migrate_info_to_pattern.py (dry-run / --apply / --rollback)
    • normalize_info_files usa patterns do resolver (fnmatch + resolve)
    • Backup .bak antes de renomear; rollback via JSON mapping

[2026-06-22] Fase 5 — Conformance checker (MCP + CLI)
  Δ arquivos: +client_conformance.py, ~foton_mcp.py, +test_client_conformance.py
  ✅ Testes: 353/348 passed (5 novos, zero regressão)
  🔧 Mudanças:
    • ClientConformanceChecker: check() / auto_fix() / accept_state()
    • MCP tools: verificar_conformidade_clientes / corrigir_conformidade
    • Detecta: pastas com espaço, INFO ausente, pattern mismatch, duplicatas
    • accept_state persiste em .conformance_accepted.json

[2026-06-22] Fase 6 — Limpeza de dead code
  Δ arquivos: ~fix_info_files.py
  ✅ Testes: 353/353 passed (zero regressão)
  🔧 Mudanças:
    • fix_info_files.get_latest_info_file() atualizado para usar pattern glob
    • DeprecationWarning adicionado ao módulo
```
