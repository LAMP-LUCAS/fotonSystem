# Revisão de Sprint — 2026-07-SPRINT-4

**Data:** 2026-06-24
**Revisor:** Agente OpenCode
**Sprint:** 2026-07-SPRINT-4 — Consolidação UX + Rastreabilidade

---

## 1. Resumo

| Item | Valor |
|------|-------|
| Stories planejadas | 9 |
| Stories concluídas (declarado) | 9 |
| Stories validadas vs Spec | 9 |
| Violações de spec | 1 (menor) |
| RULE-IDs na sprint | 14 |
| RULE-IDs implementados | 12 |
| RULE-IDs não mapeados em stories | 3 (já implementados antes) |
| RULE-IDs ausentes da spec | 0 |
| Testes totais | 490/490 |
| Débito técnico pendente | 3 itens |
| Cobertura de Critérios de Aceite | ~85% |

**Veredito:** SPRINT VÁLIDA — 9/9 stories implementadas sem regressão. 1 violação menor (STORY-002 sem teste unitário direto). 3 RULE-IDs estão implementados mas não vinculados a stories. Nenhum bloqueio.

---

## 2. Adesão às Specs — Tabela Story × RULE × Status

| Story | RULE-ID | Regra | Status | Evidência | Observação |
|-------|---------|-------|--------|-----------|------------|
| STORY-003 | RULE-UX-1.1 | Breadcrumb em todo submenu | ✅ | `menus.py:148` + 5 outros. 6 testes (`test_ui_menus.py:61-91`) | Todos os 6 submenus têm breadcrumb |
| STORY-008 | RULE-UX-1.2 | Atalho `b`/`0`/`Esc` voltar | ⚠️ | `menus.py:454` e +9 handlers. 11 testes | `b` e `0` OK. `Esc` documentado como limitação (`input()` não captura). Spec diz "quando possível" — aceitável |
| STORY-009 | RULE-UX-1.4 | Remover `00` no-op | ✅ | `00` ausente em `menus.py`. 1 teste (`test_ui_menus.py:51`) | `00` cai em "Opção inválida" |
| STORY-001 | RULE-UX-2.1 | Listar Todos os Clientes | ✅ | `menus.py:1148-1182`. Opção 11. 1 teste | Exibe código, nome, alias, status |
| STORY-005 | RULE-UX-2.2 | Paginação >10 itens | ✅ | `tui_layout.py:131-158`. 7 testes | page_size=10, "Pressione Enter..." |
| STORY-005 | RULE-UX-2.3 | Paginação: restore, services, finance | ✅ | `menus.py:558,679,977` usam `paginate_items` | 3 locais confirmados |
| STORY-001 | RULE-UX-2.4 | `[DELETADO]` marker em listagens | ⚠️ | `menus.py:1170` implementa com `Fore.RED` | **Sem teste específico** para o marcador visual |
| STORY-004 | RULE-UX-3.1 | `search_client_ui` numerar + navegar | ✅ | `menus.py:1134-1143`. 5 testes | Numeração + input → `read_client_info_ui` |
| STORY-004 | RULE-UX-3.2 | `global_search_ui` numerar + navegar | ✅ | `menus.py:617-628`. 2 testes | Apenas clientes numerados (serviços sem índice) |
| STORY-004 | RULE-UX-3.3 | Navegação abre `read_client_info_ui` | ✅ | `menus.py:1143,628` | Confirmado em ambos os searches |
| STORY-004 | RULE-UX-3.4 | Termo vazio = listar todos | ✅ | `menus.py:1119-1120`. 1 teste | `list_all_clients_ui()` chamado |
| STORY-002 | RULE-UX-4.2 | "Remover Cliente" sem "(Soft Delete)" | ✅ | `menus.py:163` — opção "9" | **Sem teste unitário** para a string do menu |
| STORY-006 | RULE-UX-5.1 | `!= 'S'` em confirmações | ✅ | `form_view.py:26,31`. 2 testes | Form view padronizado |
| STORY-006 | RULE-UX-5.2 | `== 'S'` mantido no installation | ✅ | `menus.py:398` | Mantido propositalmente |
| STORY-006 | RULE-UX-5.3 | `.upper()` em vez de `.lower()` | ✅ | `form_view.py:26,31` | Verificado |
| STORY-006 | RULE-UX-5.4 | Prompt visual consistente (S/N) | ✅ | `form_view.py:26,31` — mesmo padrão | Verificado |
| STORY-007 | RULE-UX-6.1 | Prompt "Valor" ou "Comando" | ✅ | `form_view.py:20` | Prompt auto-explicativo |
| STORY-007 | RULE-UX-6.2 | Comandos com `/` | ✅ | `form_view.py:22-32`. 8 testes | `/n`, `/p`, `/v`, `/s`, `/a`, `/c` |
| STORY-007 | RULE-UX-6.3 | Rodapé de comandos visível | ✅ | `form_view.py:74-75` | `[/N]`, `[/P]`, etc. |
| — | RULE-UX-6.4 | Campos calculados bloqueados | ✅ | `form_view.py:35` | Já implementado (pré-sprint) |
| — | RULE-UX-1.3 | `q`, `h`, `g` no menu principal | ✅ | `menus.py:288` (busca global) | Já implementado (pré-sprint) |
| — | RULE-UX-4.1 | PT-BR em toda interface | ✅ | Inspeção visual | Já implementado (pré-sprint) |
| — | RULE-UX-4.3 | Cabeçalho "REMOVER CLIENTE" | ✅ | `menus.py:531` | Já implementado (pré-sprint) |
| — | RULE-UX-7.x | Undo/Redo | ❌ | Não implementado | Reservado para futuro (especificado na spec) |

### Violações Identificadas

| Severidade | Item | Justificativa |
|------------|------|---------------|
| **Menor** | STORY-002 — sem teste unitário direto | O acceptance criteria diz "Testes de menu atualizados se necessário". O teste de roteamento existe, mas não há teste que verifique a string exata do menu. |
| **Menor** | STORY-001 — sem teste do marcador `[DELETADO]` | O acceptance criteria diz "Clientes deletados aparecem com marcador visual". Implementado no código mas sem teste. |
| **Info** | RULE-UX-1.3, 4.1, 4.3, 6.4 — sem story vinculada | Já implementados antes da sprint. A spec precisa ser atualizada ou stories criadas. |

---

## 3. Métricas do PRD (EPIC-001)

| Métrica | Meta | Status | Evidência |
|---------|------|--------|-----------|
| Redução de 30% no tempo médio de navegação | 30% | 🔴 Sem medição | Nenhum log de performance ou teste de tempo implementado |
| NPS de usabilidade interna >= 7 | >= 7 | 🔴 Sem medição | Nenhuma pesquisa implementada |
| Zero termos em inglês em labels | 100% | 🟢 OK | Verificado por inspeção de código |
| 100% diálogos de confirmação padronizados | 100% | 🟢 OK | 2 padrões válidos (`!= 'S'` e `== 'S'`) — mapeados |
| Tempo para localizar cliente reduzido 30% | 30% | 🔴 Sem medição | Nenhum benchmark ou log |

**Recomendação:** O PRD (EPIC-001) define métricas de sucesso quantitativas que **não podem ser validadas** com os artefatos atuais. Sugere-se:
1. Adicionar logs de tempo de navegação (ex: `logger.info(f"menu_navigation: client_list took {elapsed:.2f}s")`)
2. Criar testes de performance com `time.perf_counter()` para operações críticas
3. Implementar pesquisa de NPS via CLI (opção no menu de configurações)
4. Rodar `/translate EPIC-001 MOD-UX` para incorporar métricas na spec

---

## 4. Recomendações

### Prioridade Alta
1. **STORY-002: Adicionar teste unitário** — Criar teste em `test_ui_menus.py` que verifique se a opção 9 do menu de clientes contém "Remover Cliente" e não contém "Soft Delete".
2. **STORY-001: Adicionar teste para `[DELETADO]` marker** — Criar teste que verifique se clientes com status `DELETADO` exibem o marcador na listagem.

### Prioridade Média
3. **Mapear RULE-IDs órfãos** — RULE-UX-1.3, RULE-UX-4.1, RULE-UX-4.3, RULE-UX-6.4 estão implementados mas sem story vinculada. Criar stories ou atualizar a spec.
4. **Métricas de performance** — Adicionar ao backlog da Sprint 5: criar testes de tempo para operações de navegação e listagem.

### Prioridade Baixa
5. **Débito técnico** — Os 3 itens pendentes da sprint (`pyproject.toml`, CI/CD, `requirements-*.txt`) continuam abertos.
6. **RULE-UX-1.2 (Esc)** — Documentar a limitação na spec como nota técnica, já que `Esc` não é capturável via `input()` padrão do Python.

### Se o PRD mudou
- O PRD (EPIC-001) menciona métricas quantitativas que não foram traduzidas para a spec. **Sugere-se rodar `/translate EPIC-001 MOD-UX`** para criar RULE-IDs de performance antes da Sprint 5.

---

## 5. Estatísticas

| Indicador | Valor |
|-----------|-------|
| RULE-IDs na spec | 22 |
| RULE-IDs vinculados a stories | 14 |
| RULE-IDs implementados | 18 (12 via stories + 4 pré-existentes + 2 parcial) |
| RULE-IDs não implementados | 4 (RULE-UX-7.x — futuro) |
| Violações (major) | 0 |
| Violações (minor) | 2 |
| Testes criados na sprint | ~49 |
| Testes totais | 490 |
| Regressão | Zero |

**Conclusão:** Sprint válida para arquivamento. As 2 violações menores não invalidam as stories. Recomenda-se endereçar as recomendações #1 e #2 antes da Sprint 5.