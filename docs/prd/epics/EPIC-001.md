# EPIC-001: Usabilidade da Interface TUI e Navegação

**Data:** 2026-06-24 (criado) / 2026-07-06 (reaberto — Fase 0: correção de regressões)
**Stakeholders:** Equipe do escritório (usuários da TUI), Time Core (manutenção)
**Métrica de Sucesso:** Redução de 30% no tempo médio de navegação para ações comuns

## Dor Atual

A interface TUI do Foton System foi construída sem um padrão unificado de navegação. Usuários encontram dificuldades no uso diário:

- Dificuldade em saber onde estão na hierarquia de menus (ausência de breadcrumbs)
- Termos em inglês ("Soft Delete") que confundem usuários leigos
- Impossibilidade de agir sobre resultados de busca — listas textuais sem navegação direta ao resultado
- Padrões de confirmação inconsistentes entre telas
- Ausência de atalhos de navegação (ex: voltar com uma tecla)
- Listas longas sem paginação, forçando leitura excessiva
- Prompt ambíguo em formulários que conflita comandos com valores literais
- Menus longos sem orientação hierárquica — o usuário se perde na navegação
- Operações demoradas executam sem indicador de progresso, fazendo o usuário achar que o sistema travou

## Critérios de Sucesso do Negócio

- [x] Todo submenu exibe breadcrumb com caminho hierárquico (ex: "Clientes > Serviços")
- [x] Opção "Listar Todos os Clientes" disponível com paginação de 10 itens
- [x] Busca por clientes permite navegar diretamente ao resultado selecionado
- [x] Terminologia 100% em português brasileiro na interface
- [x] Atalho `b` para voltar ao menu anterior em todos os submenus
- [x] Paginação em todas as listas com mais de 10 itens
- [x] Prompt de formulário sem ambiguidade entre comandos e valores
- [x] Padrão único de confirmação em toda a interface (S/N)
- [x] Toda tela exibe breadcrumbs (caminho de navegação hierárquico)
- [x] Busca global disponível para localizar qualquer cliente por nome, código ou documento
- [x] Operações demoradas (sincronização, exportação) exibem indicador de progresso
- [x] Ações destrutivas exigem confirmação explícita em padrão único

### Fase 0 — Correção de Regressões

- [ ] Conflito de atalho `g` resolvido (global_search vs rag_query)
- [ ] UI de indexação e consulta unificada em `menus_rag.py` (removida de `menus_config.py`)
- [ ] `_query_knowledge_ui` movido para `MenuRagHandler`
- [ ] `menus_rag.py` compliant com RULE-UX-8.3 (error suggestions) e RULE-UX-4.1 (PT-BR)
- [ ] `menus_rag.py` convertido para f-strings (consistência com demais menus)
- [ ] `show_diagnostics` com breadcrumb
- [ ] Emojis substituídos por alternativas ASCII-safe em `menus_config.py` e `menus_docs.py`
- [ ] `__getattr__` frágil em `MenuSystem` removido/substituído

### Fases 1-3 — Interface Modal Vim+tmux (EPIC-013)

Migração completa para interface modal conforme especificado em EPIC-013.

## Métricas

- NPS de usabilidade interna ≥ 7 (pesquisa pós-implementação)
- Zero termos em inglês em labels de operação
- 100% dos diálogos de confirmação seguindo o mesmo padrão
- Tempo médio para localizar cliente na lista reduzido em 30%
- Tempo médio para navegar entre telas reduzido em 30%

## Regressões Conhecidas (Identificadas em 2026-07-06)

As seguintes regressões foram identificadas durante auditoria de completude do EPIC-004 (RAG). Demonstram que a manutenção evolutiva do RAG introduziu desvios no padrão UX estabelecido por este épico:

| # | Regressão | Severidade | Arquivo(s) | RULE violada |
|---|-----------|------------|-----------|--------------|
| R1 | Atalho `g` conflitante: SPEC-UX mapeia como `global_search`, SPEC-RAG mapeia como `rag_query` | Alta | `menus.py` | RULE-UX-1.3, RULE-RAG-8.4 |
| R2 | UI de indexação e consulta duplicada entre `menus_config.py` e `menus_rag.py` | Média | `menus_config.py`, `menus_rag.py` | RULE-UX-8.1 |
| R3 | `_query_knowledge_ui` registrado em `MenuConfigHandler` em vez de `MenuRagHandler` | Média | `menus_config.py` | RULE-UX-8.1 |
| R4 | `menus_rag.py` usa `except:` genérico sem `format_error_with_suggestion` (3 ocorrências) | Alta | `menus_rag.py` | RULE-UX-8.3 |
| R5 | `menus_rag.py` exibe "Opcao invalida." (sem acento circunflexo) | Baixa | `menus_rag.py` | RULE-UX-4.1 |
| R6 | `menus_rag.py` usa `.format()` enquanto demais menus usam f-strings | Baixa | `menus_rag.py` | RULE-UX-8.1 (consistência) |
| R7 | `show_diagnostics` em `menus_rag.py` sem breadcrumb | Média | `menus_rag.py` | RULE-UX-1.1 |
| R8 | `\N` (emoji) em strings de `menus_config.py` e `menus_docs.py` causam `UnicodeEncodeError` em terminais cp1252 | Média | `menus_config.py`, `menus_docs.py` | RULE-UX-8.1 (resiliência) |
| R9 | `__getattr__` em `MenuSystem` delega dinamicamente handlers — frágil, sem type hints, difícil de debugar | Média | `menus.py` | Boa prática |

### Plano de Correção

As regressões R1-R9 serão corrigidas na **Fase 0** (6 stories, ~6h), antes de qualquer evolução modal.
O plano detalhado está em STORY-042 a STORY-047.

## Histórico

| Data | Evento |
|---|---|
| 2026-06-24 | EPIC-001 criado com escopo original (TUI audit) |
| 2026-06-25 | EPIC-001 fundido com itens de UX do EPIC-002 (breadcrumbs, progresso, busca global, confirmações) |
| 2026-06-25 | EPIC-001 movido para `completed` — todos os critérios implementados via Sprint 4 + ajustes |
| 2026-07-06 | EPIC-001 reaberto como `active` — identificadas 9 regressões durante auditoria do EPIC-004 |
| 2026-07-06 | Fase 0 definida: 6 stories de correção (STORY-042 a 047) |
| 2026-07-06 | Fases 1-3 (interface modal) movidas para novo EPIC-013 |

## Especificações Técnicas

- SPEC-UX-v1.0 (22 RULE-IDs) — Cobertura total dos critérios de navegação e usabilidade
- SPEC-UX-v1.1 (planejado) — Adiciona RULE-UX-8.9 a 8.12 para correção de regressões
- **EPIC-013** — Interface Modal Vim+tmux (evolução pós-Fase 0)
- **SPEC-TUI-MODAL-v1.0** — Spec da interface modal (8 áreas, ~40 RULE-IDs)