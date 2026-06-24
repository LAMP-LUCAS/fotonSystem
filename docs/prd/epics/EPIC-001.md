# EPIC-001: Auditoria e Correção de Usabilidade da Interface TUI

**Data:** 2026-06-24
**Stakeholders:** Equipe do escritório (usuários da TUI), Time Core (manutenção)
**Métrica de Sucesso:** Redução de 30% no tempo médio de navegação para ações comuns

## Dor Atual

A interface TUI do Foton System foi construída sem um padrão unificado de navegação. Usuários encontram dificuldades no uso diário:

- Dificuldade em saber onde estão na hierarquia de menus (ausência de breadcrumbs)
- Termos em inglês ("Soft Delete") que confundem usuários leigos
- Impossibilidade de agir sobre resultados de busca — listas textuais sem navegação
- Padrões de confirmação inconsistentes entre telas
- Ausência de atalhos de navegação (ex: voltar com uma tecla)
- Listas longas sem paginação, forçando leitura excessiva
- Prompt ambíguo em formulários que conflita comandos com valores literais

## Critérios de Sucesso do Negócio

- [ ] Todo submenu exibe breadcrumb com caminho hierárquico (ex: "Clientes > Serviços")
- [ ] Opção "Listar Todos os Clientes" disponível com paginação de 10 itens
- [ ] Busca por clientes permite navegar diretamente ao resultado selecionado
- [ ] Terminologia 100% em português brasileiro na interface
- [ ] Atalho `b` para voltar ao menu anterior em todos os submenus
- [ ] Paginação em todas as listas com mais de 10 itens
- [ ] Prompt de formulário sem ambiguidade entre comandos e valores
- [ ] Padrão único de confirmação em toda a interface (S/N)

## Métricas

- NPS de usabilidade interna ≥ 7 (pesquisa pós-implementação)
- Zero termos em inglês em labels de operação
- 100% dos diálogos de confirmação seguindo o mesmo padrão
- Tempo médio para localizar cliente na lista reduzido em 30%
