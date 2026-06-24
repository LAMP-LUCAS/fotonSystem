---
type: sprint
domain: clients
status: active
tags: [domain-model, crud, ui-ux, navigation, pipeline]
---

# SPRINT: Refatoração de Domain Model e CRUD

## Objetivo

Implementar entidades de domínio para Clientes e Serviços, adicionar funcionalidade DELETE, melhorar a navegação e UI/UX da TUI, e criar pipeline unificado de sincronização.

## Decisões Técnicas

- **Delete Strategy:** Soft delete (coluna `Status` com valores `ATIVO`/`DELETADO`)
- **Migration Strategy:** Gradual — novas entidades coexistem com código existente
- **Excel Schema:** Adicionar coluna `Status` (default `"ATIVO"`)
- **Testes:** 471 esperados (410 atuais + 61 novos)

---

## Fase 1 — Domain Model Foundation

### 1.1 Criar estrutura de diretórios

```
modules/clients/domain/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── client.py
│   └── service.py
└── value_objects/
    ├── __init__.py
    ├── client_code.py
    ├── service_code.py
    └── tax_id.py
```

### 1.2 Implementar Value Objects

| Arquivo | Responsabilidade |
|---|---|
| `client_code.py` | Valida formato `^[A-Z]{3}[0-9]{2}$` (ex: `JOS01`) |
| `service_code.py` | Valida formato `^[A-Z]{6}[0-9]{2}$` (ex: `JOSRES01`) |
| `tax_id.py` | Valida 8-14 dígitos (NIF/CPF/CNPJ) |

### 1.3 Implementar Entidades

**`client.py`:**
```python
@dataclass
class Client:
    nome: str
    alias: str
    codigo: Optional[ClientCode] = None
    nif: Optional[TaxId] = None
    email: str = ""
    telefone: str = ""
    status: str = "ATIVO"
    
    def soft_delete(self): self.status = "DELETADO"
    def restore(self): self.status = "ATIVO"
    def is_active(self) -> bool: return self.status == "ATIVO"
```

**`service.py`:**
```python
@dataclass
class Service:
    client_alias: str
    alias: str
    codigo: Optional[ServiceCode] = None
    modalidade: str = ""
    ano: str = ""
    status: str = "ATIVO"
```

### 1.4 Atualizar Repository Port

Adicionar métodos:
```python
@abstractmethod
def soft_delete_client(self, alias: str): pass

@abstractmethod
def soft_delete_service(self, client_alias: str, service_alias: str): pass

@abstractmethod
def restore_client(self, alias: str): pass

@abstractmethod
def get_deleted_clients(self) -> list: pass
```

### 1.5 Atualizar ExcelClientRepository

- Adicionar coluna `Status` em `_ensure_database_exists()`
- Implementar métodos de delete/restore
- Filtrar por `Status != "DELETADO"` em reads

### 1.6 Testes da Fase 1 (~20 novos)

| Arquivo | Testes |
|---|---|
| `test_client_code_valid.py` | 6 |
| `test_service_code_valid.py` | 6 |
| `test_tax_id_valid.py` | 4 |
| `test_client_entity.py` | 5 |
| `test_service_entity.py` | 5 |

---

## Fase 2 — CRUD Completeness

### 2.1 Delete no domínio

**`client_crud.py`:**
```python
def soft_delete_client(alias: str, repository, config) -> dict:
    """Marca cliente como DELETADO. Retorna resultado."""

def restore_client(alias: str, repository, config) -> dict:
    """Restaura cliente deletado."""
```

### 2.2 Update de Serviço

**`client_crud.py`:**
```python
def update_service_info(client_alias: str, service_alias: str,
                        field: str, value: str, repository) -> dict:
    """Atualiza campo específico de um serviço."""
```

### 2.3 Validação de Financeiro

**`registrar_financeiro`:**
- Validar `tipo` contra `["ENTRADA", "SAIDA"]`
- Verificar se cliente existe
- Verificar duplicatas

### 2.4 MCP Tools

Adicionar:
- `remover_cliente(cliente)` — soft delete
- `restaurar_cliente(cliente)` — restore
- `remover_servico(cliente, servico)` — soft delete serviço
- `atualizar_servico(cliente, servico, campo, valor)` — update

### 2.5 TUI Updates

| Menu | Nova Opção |
|---|---|
| Clientes | Remover Cliente |
| Clientes | Restaurar Cliente |
| Clientes > Serviços | Remover Serviço |
| Clientes > Serviços | Atualizar Serviço |

### 2.6 Testes da Fase 2 (~15 novos)

| Arquivo | Testes |
|---|---|
| `test_soft_delete_client.py` | 4 |
| `test_restore_client.py` | 3 |
| `test_soft_delete_service.py` | 3 |
| `test_update_service_info.py` | 3 |
| `test_financeiro_validation.py` | 2 |

---

## Fase 3 — Pipeline de Sync

### 3.1 Pipeline de Sync Unificado

```python
def pipeline_sincronizacao(direcao: str = "bidirecional") -> SyncReport:
    """
    direcao: "pastas_to_db" | "db_to_pastas" | "bidirecional"
    
    Steps:
    1. snapshot() — estado atual
    2. diff() — calcula diferenças
    3. validate() — verifica conflitos
    4. apply() — aplica mudanças
    5. report() — relatório consolidado
    """
```

### 3.2 SyncReport

```python
@dataclass
class SyncReport:
    clientes_novos: list[str]
    clientes_atualizados: list[str]
    clientes_deletados: list[str]
    servicos_novos: list[str]
    servicos_atualizados: list[str]
    conflitos: list[dict]
    erros: list[str]
    duracao_segundos: float
```

### 3.3 Testes da Fase 3 (~8 novos)

| Arquivo | Testes |
|---|---|
| `test_pipeline_sync_pastas_to_db.py` | 3 |
| `test_pipeline_sync_db_to_pastas.py` | 3 |
| `test_pipeline_sync_bidirecional.py` | 2 |

---

## Fase 4 — UI/UX

### 4.1 Restruturação do Menu Clientes

Dividir em 4 grupos:
```
--- Cadastro ---
1. Cadastrar Cliente
2. Buscar Cliente
3. Ler Ficha

--- Manutenção ---
4. Atualizar Ficha
5. Preencher Códigos
6. Sincronizar

--- Serviços ---
7. Gerenciar Serviços

--- Perigo ---
8. Remover Cliente
0. Voltar
```

### 4.2 Breadcrumbs

Adicionar função:
```python
def print_breadcrumb(path: list[str]):
    print(f"  {' > '.join(path)}")
```

### 4.3 Confirmação Padronizada

```python
def confirm_action(action: str, details: str = "") -> bool:
    print(f"\n  ⚠️  {action}")
    if details:
        print(f"  {details}")
    return input("  Confirmar? (S/N): ").upper() == 'S'
```

### 4.4 Auto-Dismiss

```python
def pause_or_auto(seconds=3):
    print(f"\n  (Enter para continuar ou aguarde {seconds}s)")
```

### 4.5 Progress Tracker

```python
class ProgressTracker:
    def __init__(self, total: int, label: str): ...
    def advance(self, item: str): ...
    def finish(self): ...
```

### 4.6 Testes da Fase 4 (~10 novos)

| Arquivo | Testes |
|---|---|
| `test_tui_breadcrumbs.py` | 2 |
| `test_tui_confirm_action.py` | 2 |
| `test_tui_progress_tracker.py` | 3 |
| `test_tui_menu_structure.py` | 3 |

---

## Fase 5 — Navegação

### 5.1 Atalhos de Teclado

| Atalho | Ação |
|---|---|
| `h` | Mostra histórico de ações |
| `00` | Volta ao menu principal |
| `q` | Sai do programa |
| Texto livre | Busca incremental |

### 5.2 Busca Global

```python
def global_search(query: str, client_service) -> list[dict]:
    """Busca por alias, nome, código, ou NIF."""
```

### 5.3 Paginação

```python
def list_clients_paginated(page: int = 1, per_page: int = 20) -> dict:
    """Retorna {items, total, page, pages}"""
```

### 5.4 Testes da Fase 5 (~8 novos)

| Arquivo | Testes |
|---|---|
| `test_global_search.py` | 3 |
| `test_pagination.py` | 3 |
| `test_parse_command.py` | 2 |

---

## Sumário de Entregas

| Fase | Novos Arquivos | Novos Testes | MCP Tools | TUI Updates |
|---|---|---|---|---|
| 1. Domain | 8 | ~20 | 0 | 0 |
| 2. CRUD | 2 | ~15 | 4 | 4 |
| 3. Pipeline | 1 | ~8 | 1 | 1 |
| 4. UI/UX | 3 | ~10 | 0 | 15+ |
| 5. Navegação | 1 | ~8 | 1 | 5 |
| **Total** | **15** | **~61** | **6** | **25+** |

**Total esperado:** 471 testes (410 + 61 novos)

---

## Ordem de Execução

```
Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5
  │         │         │         │         │
  └─ Phase 2 & 3 deps                    └─ Can parallelize
```

### Dependências
- Fase 2 depende de Fase 1 (usa domain entities)
- Fase 3 depende de Fase 2 (usa delete para relatório)
- Fase 4 e 5 são independentes de 3, mas dependem de 1-2