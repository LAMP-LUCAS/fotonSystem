---
status: "done"
sprint: "2026-SPRINT-5"
---

# STORY-013: CRUD — Validação Financeiro + INFO Files

**Épico:** EPIC-002
**Spec:** `MOD-DOMAIN-CRUD/SPEC-DOMAIN-CRUD-v1.0.md`

## Descrição

Adicionar validações ao `registrar_financeiro` (tipo, cliente existente, duplicata) e melhorar `atualizar_ficha_cliente` com substituição de seção inteira, remoção de seção e atualização de campo via regex.

## Regras Implementadas

- **RULE-DOMAIN-2.5:** Validação de `registrar_financeiro` (tipo, cliente, duplicata, DataRegistro automática)
- **RULE-DOMAIN-2.6:** `atualizar_ficha_cliente` com substituição/remoção de seção e update via regex

## Critérios de Aceite

- [ ] `registrar_financeiro` valida tipo (`"ENTRADA"`/`"SAIDA"` case-insensitive)
- [ ] `registrar_financeiro` verifica existência do cliente no DB
- [ ] `registrar_financeiro` gera warning (não bloqueia) para duplicatas (descrição + valor + data)
- [ ] `DataRegistro` adicionada automaticamente nas entradas
- [ ] `atualizar_ficha_cliente` suporta substituição de seção inteira
- [ ] `atualizar_ficha_cliente` suporta remoção de seção
- [ ] `atualizar_ficha_cliente` suporta update de campo via regex `@campo: valor`
- [ ] Testes para validações de financeiro e operações de INFO file
- [ ] Zero regressão

## Estimativa

4h
