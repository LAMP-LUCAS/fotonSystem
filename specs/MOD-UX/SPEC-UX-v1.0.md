# Spec: Interface de Usuário (TUI) — Experiência e Navegação

**Data:** 2026-06-25
**Versão:** 1.1
**Responsável:** Time Core

## 1. Problema
A interface TUI do Foton System possui gaps de usabilidade identificados em auditoria: falta de navegabilidade, inconsistências de terminologia, padrões de confirmação divergentes e ausência de atalhos de navegação.

## 2. Solução Proposta
Padronizar a experiência TUI em 6 eixos:
1. **Navegabilidade** — breadcrumbs consistentes, atalho de voltar, paginação
2. **Listagem** — opção "Listar Todos" + paginação em listas longas
3. **Busca** — drill-down dos resultados para ação imediata
4. **Terminologia** — PT-BR consistente em toda a interface
5. **Confirmações** — padrão único para diálogos (S/N)
6. **Formulários** — prompt não ambíguo, comandos separados de valores

## 3. Regras de Negócio

### 3.1 Navegabilidade
- **RULE-UX-1.1:** Todo submenu deve exibir breadcrumb (`print_breadcrumb`) indicando o caminho hierárquico (ex: "Clientes > Serviços").
- **RULE-UX-1.2:** Todo submenu deve aceitar `b` ou `0` como atalho para voltar ao menu anterior. `Esc` também deve funcionar quando possível.
- **RULE-UX-1.3:** O menu principal aceita `q` (sair), `h` (ajuda) e `g` (busca global). Submenus não devem capturar `q` como saída do sistema.
- **RULE-UX-1.4:** `00` no menu principal é no-op e deve ser removido ou substituído por comando útil.

### 3.2 Listagem e Paginação
- **RULE-UX-2.1:** Deve existir uma opção "Listar Todos os Clientes" no menu de clientes, exibindo código, nome, alias e status.
- **RULE-UX-2.2:** Listas com mais de 10 itens devem ser paginadas com "Pressione Enter para continuar..." entre páginas.
- **RULE-UX-2.3:** A paginação se aplica a: listagem de clientes, clientes deletados (restore), serviços, e resumo financeiro.
- **RULE-UX-2.4:** Clientes com status `DELETADO` devem aparecer com marcador visual `[DELETADO]` nas listagens.

### 3.3 Busca com Drill-Down
- **RULE-UX-3.1:** `search_client_ui` (opção 4) deve numerar os resultados e permitir selecionar um para navegar até a ficha do cliente.
- **RULE-UX-3.2:** `global_search_ui` (atalho `g`) também deve permitir navegar para um resultado selecionado.
- **RULE-UX-3.3:** A navegação a partir da busca deve abrir `read_client_info_ui` para o cliente selecionado.
- **RULE-UX-3.4:** Termo de busca vazio em `search_client_ui` deve listar todos os clientes (atalho para listagem).

### 3.4 Terminologia (PT-BR)
- **RULE-UX-4.1:** Toda string de interface deve estar em português brasileiro. Nenhum termo em inglês para labels de menu.
- **RULE-UX-4.2:** A opção 9 do menu de clientes deve ser "Remover Cliente" (sem "(Soft Delete)").
- **RULE-UX-4.3:** O cabeçalho de `remove_client_ui` já está em PT-BR ("REMOVER CLIENTE") — consistente.

### 3.5 Padrão de Confirmação
- **RULE-UX-5.1:** Todo diálogo de confirmação deve usar `input("... (S/N): ").upper() != 'S'` para cancelar se não for 'S'.
- **RULE-UX-5.2:** Exceção: `input("... (S/N): ").upper() == 'S'` é aceitável apenas se semanticamente "prosseguir apenas se S" for o comportamento correto (ex: handle_installation).
- **RULE-UX-5.3:** `form_view.py` deve usar `.upper()` em vez de `.lower()` para consistência com o resto do sistema.
- **RULE-UX-5.4:** O prompt de confirmação no form_view deve seguir o mesmo padrão visual dos demais menus.

### 3.6 Formulário Interativo (TUIFormView)
- **RULE-UX-6.1:** O prompt principal do form_view deve ser "Comando" ou "Valor" — nunca "Ação ou Novo Valor".
- **RULE-UX-6.2:** Comandos de navegação (n, p, v, s, a, c) devem ser prefixados com `/` (ex: `/n`, `/p`, `/s`) para não conflitar com valores literais.
- **RULE-UX-6.3:** O rodapé de comandos deve listar os comandos disponíveis sempre visível.
- **RULE-UX-6.4:** Campos calculados não podem ser editados (já implementado, manter).

### 3.7 Undo/Redo
- **RULE-UX-7.1:** O sistema não possui undo/redo formal. A proteção contra perda de dados é via backup `.bak` antes de cada alteração.
- **RULE-UX-7.2:** Futuramente, operações de edição devem suportar undo (Ctrl+Z) com no mínimo 1 nível de profundidade.
- **RULE-UX-7.3:** (Reservado para implementação futura)

### 3.8 Arquitetura de Interface e Navegação Avançada (migrado do EPIC-002)

> Itens migrados do EPIC-002 (SPEC-DOMAIN-CRUD-v1.1, §3.4) para centralização neste épico.

- **RULE-UX-8.1:** `menus.py` (54KB) deve ser dividido em submódulos: `menus_clients.py`, `menus_finance.py`, `menus_docs.py`, `menus_config.py`. `menus.py` mantém apenas o dispatch principal.
- **RULE-UX-8.2:** `ProgressTracker` deve exibir feedback visual para operações batch no formato `"[3/10] Processando CLIENTE..."` com `advance(item)` e `finish()`.
- **RULE-UX-8.3:** Erros capturados na TUI devem exibir sugestões de ação contextualizadas por tipo (ex: `FileNotFoundError` → "Verifique settings.json", `PermissionError` → "Feche o Excel e tente novamente").
- **RULE-UX-8.4:** Menu de clientes deve ser reestruturado em subgrupos visuais: "--- Cadastro ---", "--- Manutenção ---", "--- Serviços ---", "--- Perigo ---". Ações destrutivas agrupadas sob "Perigo".
- **RULE-UX-8.5:** Atalho `g` no menu principal deve disparar busca global (`global_search`) por alias, nome, código ou NIF. Resultados numerados com drill-down para ficha do cliente.
- **RULE-UX-8.6:** `parse_command()` deve interpretar atalhos no input principal: `h` (ajuda), `00` (home/início), `q` (sair), texto livre (busca).
- **RULE-UX-8.7:** MCP `listar_clientes` deve aceitar parâmetros opcionais `pagina` (int, default 1) e `itens_por_pagina` (int, default 20) — backward compatibility mantida.
- **RULE-UX-8.8:** Confirmação padronizada (S/N) em todas as ações destrutivas via `confirm_action()`, com variação visual `dangerous=True` para operações irreversíveis.

### 3.9 Pesquisa de Satisfação (NPS)
- **RULE-UX-9.1:** O menu Configurações deve conter a opção "Pesquisa de Satisfação (NPS)" que coleta nota 0-10, classifica como Detrator (0-6) / Neutro (7-8) / Promotor (9-10) e persiste em `nps_responses.jsonl` no diretório de configuração do usuário. Exibe a média histórica após cada resposta.

## 4. Relações
- Código: `menus.py`, `tui_layout.py`, `form_view.py`
- Specs relacionadas: `SPEC-CLIENTES-v1.0.md` (UX de clientes)
- ADRs: `ADR001_ParaZettelkastenDoc` (estrutura de navegação)
