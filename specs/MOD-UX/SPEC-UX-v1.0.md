# Spec: Interface de Usuário (TUI) — Experiência e Navegação

**Data:** 2026-07-06
**Versão:** 1.3
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

### 3.9 Correção de Regressões (v1.3)

> Regras adicionadas em 2026-07-06 para corrigir regressões identificadas na auditoria do EPIC-004.

- **RULE-UX-8.9:** O atalho `g` no menu principal DEVE disparar exclusivamente `global_search`. Qualquer outro módulo (ex: RAG) que deseje usar `g` DEVE fazê-lo em seu próprio contexto de submenu, sem conflitar com o menu principal. A SPEC-RAG deve ser atualizada para remover o mapeamento conflitante de `g`.
- **RULE-UX-8.10:** Todo handler de menu DEVE usar `format_error_with_suggestion()` em TODOS os `except:` blocks. É proibido `except:` sem formatação de erro contextualizada. Três níveis de severidade:
  - Erros conhecidos (FileNotFoundError, PermissionError, etc.) → sugestão específica
  - Erros de negócio (ValueError, KeyError) → sugestão de configuração
  - Erros genéricos (Exception) → "Caso o erro persista, contate o suporte"
- **RULE-UX-8.11:** Toda string de interface DEVE ser ASCII-safe (proibido `\N{...}` ou caracteres Unicode que quebrem em cp1252). Acentos do português (á, é, í, ó, ú, ç, ã, õ) são permitidos e recomendados. Alternativas para ícones: `[!]` (aviso), `[X]` (erro), `[v]` (sucesso), `[>]` (progresso), `[*]` (destaque).
- **RULE-UX-8.12:** `show_diagnostics` (ou qualquer tela de diagnóstico/informação do sistema) DEVE exibir breadcrumb indicando o caminho hierárquico, em conformidade com RULE-UX-1.1.
- **RULE-UX-8.13:** Todo arquivo de menu DEVE usar exclusivamente f-strings para formatação de strings. `str.format()` é proibido em novos códigos e DEVE ser migrado onde existente.

### 3.9 Pesquisa de Satisfação (NPS)

- **RULE-UX-9.1:** O menu Configurações deve conter a opção "Pesquisa de Satisfação (NPS)" que:
  - Coleta nota 0-10 e classifica como **Detrator** (0-6) / **Neutro** (7-8) / **Promotor** (9-10)
  - Coleta comentário ou sugestão opcional (textarea multi-linha)
  - Injeta automaticamente no registro: `session_count` (total de execuções do sistema), `operation_count` (total de operações realizadas), `interface` (TUI|MCP), `session_id` (UUID da sessão atual), `timestamp` (ISO 8601)
  - Persiste em `nps_responses.jsonl` no diretório de configuração do usuário
  - Exibe após cada resposta: nota atual com classificação, média histórica geral, tendência visual (📈📉➡️ baseada nas últimas 3 respostas) e uma tabela simples das últimas 5 respostas
- **RULE-UX-9.2:** O formulário NPS deve oferecer a opção "Exportar para Email" que:
  - Gera um arquivo na área de trabalho do usuário contendo: (a) relatório da avaliação em formato Markdown legível com nota, classificação, comentário e contexto de uso, (b) evolução histórica de todas as respostas NPS, (c) dados brutos de telemetria das operações (`operation_log.jsonl`) do período
  - Exibe a instrução: "Envie o arquivo para contato@mundoaec.com"
  - NÃO realiza envio automático — o arquivo é local e o compartilhamento é responsabilidade do usuário

## 4. Relações
- Código: `menus.py`, `tui_layout.py`, `form_view.py`, `menus_config.py`
- Specs relacionadas: `SPEC-CLIENTES-v1.0.md` (UX de clientes), `SPEC-TELEMETRY-v1.0.md` (telemetria subjacente ao contexto de uso do NPS)
- ADRs: `ADR001_ParaZettelkastenDoc` (estrutura de navegação)

## 5. Histórico de Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2026-06-24 | Versão inicial (22 RULE-IDs, seções 3.1 a 3.9) |
| 1.1 | 2026-06-25 | Migração das RULE-UX-8.x do EPIC-002 (8 novas regras: menus modulares, ProgressTracker, error_suggestions, subgrupos, busca global, parse_command, paginação MCP, confirmação perigosa) |
| 1.2 | 2026-06-28 | RULE-UX-9.1 expandida: comentário, contexto automático (session/operation/interface), tendência visual. RULE-UX-9.2 adicionada: exportação para email (arquivo .zip local + instrução). Relacionamento com SPEC-TELEMETRY-v1.0 |
| 1.3 | 2026-07-06 | RULE-UX-8.9 a 8.13 adicionadas: correção de regressões (conflito atalho `g`, error_suggestions obrigatório, ASCII-safe, breadcrumb em diagnóstico, f-strings obrigatórias). Relacionamento com SPEC-UI-COMPONENTS.md |
