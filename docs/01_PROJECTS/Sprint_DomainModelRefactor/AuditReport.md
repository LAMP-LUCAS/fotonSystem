---
type: audit
domain: clients
status: active
tags: [architecture, domain-model, crud, ui-ux]
---

# Relatório de Avaliação — FotonSystem v1.4.0

**Data:** 2026-06-23
**Escopo:** Semântica de domínio, pipelines, UI/UX da TUI, drill-down, controle, navegação, carga cognitiva, ferramentas MCP, CRUD de informações

---

## Scorecard Geral

| Dimensão | Nota | Estado |
|---|---|---|
| **Semântica de domínio** | 8/10 | DDD bem aplicado; gaps em entidades ausentes |
| **Pipelines** | 7/10 | 2 pipelines seguros; faltam pipelines para sync e financeiro |
| **UI/UX da TUI** | 6/10 | Funcional; problemas de densidade, feedback e erro |
| **Drill-down** | 5/10 | Limitado a 3 níveis; sem breadcrumbs, sem retorno contextual |
| **Controle** | 7/10 | Boa validação; falta delete, undo, confirmação em ações destrutivas |
| **Navegação** | 5/10 | Hierárquica rígida; sem atalhos, sem busca, sem histórico |
| **Carga cognitiva** | 6/10 | Menus com até 9 opções; textos longos; falta agrupamento visual |
| **Ferramentas MCP** | 8/10 | 38 tools completas; boa cobertura; gaps em documentação |
| **CRUD** | 7/10 | Create/Read/Update robustos; DELETE ausente; Update limitado |

---

## 🔴 Críticos

### 1. DELETE ausente — não é possível remover clientes, serviços ou entradas financeiras
- **Impacto:** O usuário não pode corrigir erros de cadastro sem editar Excel manualmente
- **Solução:** Implementar soft delete com coluna `Status` na planilha

### 2. Update limitado — INFO files só permitem append, nunca substituição ou remoção de seções
- **Impacto:** `atualizar_ficha_cliente` acumula conteúdo sem opção de limpar
- **Solução:** Adicionar operações de substituição e remoção de seções

### 3. Sem pipeline para sync — operação de alto risco sem validação intermediária
- **Impacto:** `sincronizar_clientes` pode falhar parcialmente sem relatório
- **Solução:** Criar pipeline com snapshot, diff, validação, apply, report

### 4. Financeiro sem validação — `registrar_financeiro` aceita tipos inválidos e não verifica existência do cliente
- **Impacto:** Dados corrompidos sem alerta
- **Solução:** Validar tipo contra `["ENTRADA", "SAIDA"]` e verificar cliente existe

---

## 🟠 Alta Prioridade

### 5. Menu Clientes com 9 opções — sobrecarga cognitiva acima do limite de Miller (7±2)
- **Solução:** Dividir em subgrupos: "Cadastro", "Manutenção", "Serviços", "Perigo"

### 6. Sem breadcrumbs — usuário perde contexto na navegação hierárquica
- **Solução:** Mostrar caminho em todos os submenus: `Clientes > Serviços > JOSE`

### 7. Sem feedback de progresso — operações longas bloqueiam sem indicador
- **Solução:** Adicionar contador de progresso com itens processados

### 8. 6 operações de sync confusas — diferença entre "Pastas→DB" e "DB→Arquivo" é sutil
- **Solução:** Unificar em pipeline com relatório consolidado

### 9. `listar_clientes` sem paginação — resposta gigante para escritórios com 200+ clientes
- **Solução:** Adicionar paginação com `limite` e `offset`

---

## 🟡 Média Prioridade

### 10. Sem atalhos de teclado — todas as ações requerem navegação numérica
- **Solução:** Adicionar `h` (histórico), `00` (menu principal), `q` (sair)

### 11. "Pressione Enter" repetitivo — 7+ interações para leituras simples
- **Solução:** Auto-dismiss com timeout de 3 segundos

### 12. Forms sem validação em tempo real — campos só validados no final
- **Solução:** Validação incremental com sugestões de correção

### 13. Sem undo — ações destrutivas são irreversíveis
- **Solução:** Mecanismo de undo para últimas 5 operações

### 14. Entidades sem domain model — Client e Service são DataFrames, não objetos
- **Solução:** Criar classes `Client` e `Service` como domain entities

---

## 🔵 Vapor / Dead Code

| Artefato | Problema |
|---|---|
| `client_crud.py` | Funções procedurais em vez de métodos de entidade |
| `client_service.py` | Facade com 108 linhas — deveria delegar para use cases |
| `ExcelClientRepository` | Colunas DataFrame não mapeadas para domain entities |

---

## ✅ O Que Funciona Muito Bem

| Componente | Destaque |
|---|---|
| **Circuit Breaker** | 3 estados, configurável, graceful degradation |
| **TUI Layout** | Adaptação dinâmica, emoji-aware, box-drawing limpo |
| **Environment Porter** | Detecção cross-platform impecável |
| **Ports/Adapters** | Contratos limpos no `ClientRepositoryPort` |
| **Suite de Testes** | 410 testes, zero regressão |
| **Path Traversal Security** | `Path(name).name` em todas as ferramentas |

---

## Recomendações em Ordem de Impacto

| # | Ação | Esforço | Impacto |
|---|---|---|---|
| 1 | Adicionar `delete_client()` e `delete_service()` com confirmação | Médio | Alto |
| 2 | Criar classes `Client` e `Service` como domain entities | Alto | Alto |
| 3 | Criar pipeline de sync com relatário consolidado | Médio | Médio |
| 4 | Validar `tipo` em `registrar_financeiro` | Baixo | Médio |
| 5 | Separar menu Clientes em subgrupos | Baixo | Alto |
| 6 | Adicionar breadcrumbs em submenus | Baixo | Médio |
| 7 | Adicionar confirmação em ações destrutivas | Baixo | Médio |
| 8 | Reduzir "Pressione Enter" — usar auto-dismiss | Baixo | Médio |
| 9 | Adicionar paginação em `listar_clientes` | Baixo | Médio |
| 10 | Adicionar atalhos de teclado (`h`, `00`, `q`) | Baixo | Médio |

---

## Links

- Plano de sprint: [[SprintPlan]]
- Documentação MCP: [[DocsMcp]]
- Dicionário de domínio: [[Dictionary]]