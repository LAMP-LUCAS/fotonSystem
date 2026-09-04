---
status: "completed"
sprint: "2026-SPRINT-6"
---

# STORY-047: Refatorar `__getattr__` frágil em `MenuSystem`

**Épico:** EPIC-001 (Fase 0)
**Spec:** Boa prática de engenharia (menus modulares — RULE-UX-8.1)
**Regressão:** R9

## Descrição

`menus.py` contém um `__getattr__` em `MenuSystem` que delega dinamicamente chamadas para handlers de menu.
Essa abordagem tem 3 problemas:

1. **Sem type hints:** O interpretador (e o desenvolvedor) não sabe quais métodos estão disponíveis
2. **Erros silenciosos:** Atributos com typo viram `None` ou `AttributeError` em tempo de execução
3. **Dificuldade de debug:** Stack traces apontam para `__getattr__` genérico, não para o handler real

## Solução

Substituir `__getattr__` dinâmico por um dispatch explícito com type hints:

```python
# ANTES (frágil)
class MenuSystem:
    def __getattr__(self, name):
        handler = self._get_handler(name)
        if handler:
            return handler
        raise AttributeError(...)

# DEPOIS (explícito)
class MenuSystem:
    client_handler: MenuClientHandler
    finance_handler: MenuFinanceHandler
    docs_handler: MenuDocsHandler
    config_handler: MenuConfigHandler
    rag_handler: MenuRagHandler

    def __init__(self):
        self.client_handler = MenuClientHandler()
        self.finance_handler = MenuFinanceHandler()
        self.docs_handler = MenuDocsHandler()
        self.config_handler = MenuConfigHandler()
        self.rag_handler = MenuRagHandler()
```

## Impacto

- `MenuSystem` passa a ser type-checkable (mypy compatible)
- IDE autocomplete funciona para todos os handlers
- Erros de digitação são capturados em tempo de import, não runtime
- Performance: chamadas diretas (sem overhead de `__getattr__`)

## Riscos

- Qualquer código que dependa do `__getattr__` para resolver nomes não-padrão vai quebrar
- É necessário verificar todos os callers de `MenuSystem` para garantir que os nomes estão corretos

## Critérios de Aceite

- [ ] `__getattr__` removido de `MenuSystem`
- [ ] Todos os handlers são atributos explícitos com type hints
- [ ] Todos os callers de `MenuSystem` continuam funcionando (nomes de handler não mudaram)
- [ ] IDE autocomplete funciona para `menu_system.client_handler`, etc.
- [ ] `mypy` (ou `pyright`) passa sem erros em `menus.py`
- [ ] Testes: `test_menusystem_explicit_handlers`, `test_menusystem_no_getattr`, `test_menusystem_callers`
- [ ] Zero regressão na suite existente

## Arquivos Afetados

- `foton_system/interfaces/cli/menus.py` — refatorar `MenuSystem`

## Notas de Implementação

```python
# Estrutura esperada após refatoração
class MenuSystem:
    client_handler: MenuClientHandler
    finance_handler: MenuFinanceHandler  
    docs_handler: MenuDocsHandler
    config_handler: MenuConfigHandler
    rag_handler: MenuRagHandler

    def __init__(self):
        self.client_handler = MenuClientHandler()
        self.finance_handler = MenuFinanceHandler()
        self.docs_handler = MenuDocsHandler()
        self.config_handler = MenuConfigHandler()
        self.rag_handler = MenuRagHandler()
        self.router = MenuRouter(
            client=self.client_handler,
            finance=self.finance_handler,
            docs=self.docs_handler,
            config=self.config_handler,
            rag=self.rag_handler,
        )

    # NO: __getattr__
    # YES: router.run(action, ...)
```

## Dependências

- STORY-043 (unificação RAG em `menus_rag.py`) deve estar completa para garantir que `MenuRagHandler` está correto

## Estimativa

1h
