# EPIC-001: Usabilidade da Interface TUI e Navegação

**Data:** 2026-06-24 (criado) / 2026-06-25 (fundido com itens UX do EPIC-002)
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

## Métricas

- NPS de usabilidade interna ≥ 7 (pesquisa pós-implementação)
- Zero termos em inglês em labels de operação
- 100% dos diálogos de confirmação seguindo o mesmo padrão
- Tempo médio para localizar cliente na lista reduzido em 30%
- Tempo médio para navegar entre telas reduzido em 30%

## Histórico

| Data | Evento |
|---|---|
| 2026-06-24 | EPIC-001 criado com escopo original (TUI audit) |
| 2026-06-25 | EPIC-001 fundido com itens de UX do EPIC-002 (breadcrumbs, progresso, busca global, confirmações) |
| 2026-06-25 | EPIC-001 movido para `completed` — todos os critérios implementados via Sprint 4 + ajustes |

## Especificações Técnicas

- SPEC-UX-v1.0 (22 RULE-IDs) — Cobertura total dos critérios de navegação e usabilidade