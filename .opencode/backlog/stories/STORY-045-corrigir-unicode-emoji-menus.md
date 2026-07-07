---
status: "pending"
sprint: "2026-SPRINT-6"
---

# STORY-045: Corrigir emojis Unicode em `menus_config.py` e `menus_docs.py`

**Épico:** EPIC-001 (Fase 0)
**Spec:** `MOD-UX/SPEC-UX-v1.0.md` (RULE-UX-8.11)
**Regressão:** R8

## Descrição

`menus_config.py` e `menus_docs.py` contêm caracteres Unicode (`\N{...}` — emojis) em strings de interface que causam `UnicodeEncodeError` em terminais configurados com codificação cp1252 (padrão no Windows brasileiro).

Exemplos encontrados:
- `menus_config.py`: `f"NPS {trend_icon}"` onde `trend_icon` pode ser 📈📉➡️ (RULE-UX-9.1)
- `menus_docs.py`: Possíveis emojis em labels de documento

## Solução

Substituir emojis por alternativas ASCII-safe conforme SPEC-UI-COMPONENTS.md §2.1:

| Emoji | Alternativa |
|-------|-------------|
| 📈 | `[+]` (ou `↑`) |
| 📉 | `[-]` (ou `↓`) |
| ➡️ | `[=]` (ou `→`) |
| 📁 | `[*]` |
| ⚠ | `[!]` |
| ✅ | `[v]` |
| ❌ | `[X]` |

> Atenção: Símbolos `↑`, `↓`, `→` também podem causar problemas em cp1252.
> Preferir `[+]`, `[-]`, `[=]` que são 100% ASCII.

## Regras Implementadas

- **RULE-UX-8.11:** Strings ASCII-safe (proibido `\N{...}`)

## Critérios de Aceite

- [ ] Zero `\N{...}` ou caracteres Unicode non-ASCII em `menus_config.py`
- [ ] Zero `\N{...}` ou caracteres Unicode non-ASCII em `menus_docs.py`
- [ ] Tendência visual NPS (RULE-UX-9.1) usa `[+]`/`[-]`/`[=]`
- [ ] Teste de encoding cp1252 passa sem erro:
  ```python
  " ".join(strings).encode("cp1252")
  ```
- [ ] Testes: `test_cp1252_compatibility_menus_config`, `test_cp1252_compatibility_menus_docs`, `test_nps_trend_ascii`
- [ ] Zero regressão na suite existente

## Arquivos Afetados

- `foton_system/interfaces/cli/menus_config.py` — substituir emojis por ASCII
- `foton_system/interfaces/cli/menus_docs.py` — substituir emojis por ASCII

## Observações

- Acentos do português (á, é, í, ó, ú, ç, ã, õ) SÃO suportados em cp1252 e DEVEM ser mantidos
- Apenas caracteres FORA do range cp1252 (0-255) devem ser substituídos
- Um teste simples: `"ç ã é ó".encode("cp1252")` funciona; `"\U0001f4c8".encode("cp1252")` quebra

## Estimativa

1h
