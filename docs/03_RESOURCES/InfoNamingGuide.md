# Guia de Nomenclatura de Arquivos INFO

> **Propósito:** Este documento explica como configurar e usar o sistema de
> nomenclatura personalizável dos arquivos INFO-CLIENTE e INFO-SERVICO.
>
> **Versão do sistema:** 1.4.0+

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Placeholders Disponíveis](#2-placeholders-disponíveis)
3. [Configuração](#3-configuração)
4. [Patterns Default](#4-patterns-default)
5. [Exemplos de Uso](#5-exemplos-de-uso)
6. [Glob Patterns](#6-glob-patterns)
7. [Headers em Templates](#7-headers-em-templates)
8. [Migração Retroativa](#8-migração-retroativa)
9. [Conformance Checker](#9-conformance-checker)
10. [Referência do Desenvolvedor](#10-referência-do-desenvolvedor)

---

## 1. Visão Geral

Antes da v1.4.0, os arquivos INFO tinham nomes fixos:

```
CLIENTE/
├── INFO-CLIENTE.md
└── SERVICO/
    └── INFO-SERVICO.md
```

A partir da v1.4.0, você pode configurar o padrão de nomes usando
**placeholders**. Exemplo:

```json
"info_file_patterns": {
    "cliente": "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
    "servico": "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md"
}
```

Resultado:

```
CLIENTE/
├── INFO-CLIENTE-JOS01_00_R00.md
└── SERVICO/
    └── INFO-SERVICO-JOSSRV01_01_R02.md
```

### Benefícios

- **Versionamento nativo**: cada alteração gera uma nova revisão
- **Rastreabilidade**: código do cliente/serviço embutido no nome
- **Flexibilidade**: você define o pattern ideal para seu escritório

---

## 2. Placeholders Disponíveis

| Placeholder | Origem | Exemplo | Descrição |
|---|---|---|---|
| `{codCliente}` | Banco de dados | `JOS01` | Código único do cliente |
| `{nomeCliente}` | Cadastro | `JOAO_SILVA` | Nome completo do cliente |
| `{aliasCliente}` | Nome da pasta | `JOAO_SILVA` | Nome da pasta do cliente |
| `{codServico}` | Banco de dados | `JOSRES01` | Código único do serviço |
| `{aliasServico}` | Nome da subpasta | `RESIDENCIAL` | Nome da pasta do serviço |
| `{versao}` | Exportação | `00`, `01`, `02` | Versão do documento |
| `{revisao}` | Auto-incremento | `R00`, `R01` | Revisão (prefixo `R` incluso) |
| `{data}` | Sistema | `2026-06-22` | Data ISO curta |
| `{dataISO}` | Sistema | `20260622` | Data ISO sem separadores |
| `{ano}` | Sistema | `2026` | Ano com 4 dígitos |
| `{mes}` | Sistema | `06` | Mês com 2 dígitos |
| `{timestamp}` | Sistema | `20260622_153042` | Data e hora completas |
| `{extensao}` | Configurável | `md` | Extensão do arquivo (sem ponto) |

### Regras

- Placeholders **case‑sensitive**: use exatamente como listado acima
- Placeholders **não utilizados** no pattern são ignorados
- Placeholders **obrigatórios faltantes** levantam `ValueError`
- O prefixo `R` em `{revisao}` é uma **convenção** — você pode usar `rev{revisao}` ou `{revisao}` puro

---

## 3. Configuração

### 3.1 Arquivo `settings.json`

Adicione a chave `info_file_patterns` no seu `settings.json`:

```json
{
    "caminho_pastaClientes": "C:\\Clientes",
    "caminho_templates": "C:\\KIT DOC",
    "caminho_baseDados": "C:\\baseDados.xlsx",
    "info_file_patterns": {
        "cliente": "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
        "servico": "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md"
    }
}
```

### 3.2 Onde o `settings.json` está localizado

O sistema busca nesta ordem:

1. `%LOCALAPPDATA%\FotonSystem\settings.json` — cópia local (prioridade máxima)
2. `{pasta_do_executavel}\foton_system\config\settings.json` — instalação
3. `{pasta_do_executavel}\settings.json` — raiz do projeto (desenvolvimento)

> **Importante:** Se `info_file_patterns` não for definido, o sistema usa os
> patterns default (Seção 4).

### 3.3 Schema de Validação

O sistema valida o pattern automaticamente:

- Deve conter **pelo menos um placeholder** alfanumérico
- O placeholder `{extensao}` (se usado) deve estar no final: `...{extensao}`
- Cada pattern deve ter um placeholder único que o diferencie do outro tipo
- O sistema rejeita patterns inválidos na inicialização

---

## 4. Patterns Default

Se a chave `info_file_patterns` não existir no `settings.json`, o sistema usa:

```json
"cliente": "INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md",
"servico": "INFO-SERVICO-{codServico}_{versao}_R{revisao}.md"
```

Para **compatibilidade retroativa** (comportamento exato da v1.3.x):

```json
"cliente": "INFO-CLIENTE.md",
"servico": "INFO-SERVICO.md"
```

---

## 5. Exemplos de Uso

### 5.1 Simples (sem versionamento)

```json
"cliente": "CLIENTE-{codCliente}.md",
"servico": "SERVICO-{codServico}.md"
```

### 5.2 Com data e código

```json
"cliente": "{ano}_{mes}_{codCliente}_INFO.md",
"servico": "{data}_{codServico}_INFO.md"
```

### 5.3 Versionado com timestamp

```json
"cliente": "INFO_{codCliente}_v{versao}_r{revisao}.md",
"servico": "INFO_{codServico}_v{versao}_r{revisao}.md"
```

### 5.4 Com nome do cliente

```json
"cliente": "{nomeCliente}_INFO_{versao}.md",
"servico": "{aliasServico}_INFO_{versao}.md"
```

---

## 6. Glob Patterns

O sistema converte automaticamente cada pattern em um **glob pattern**
para busca de arquivos existentes. Placeholders são substituídos por `*`:

| Pattern | Glob Resultante |
|---|---|
| `INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md` | `INFO-CLIENTE-*_*_R*.md` |
| `{codCliente}_INFO.md` | `*_INFO.md` |
| `{ano}_{mes}_{codCliente}_INFO.md` | `*_*_*_INFO.md` |

> **Nota:** Placeholders adjacentes (ex.: `{cod}{versao}`) colapsam em um
> único `*` para evitar globs inválidos.

### Uso em sincronização

O `sync_service` e o `document_service` usam o glob pattern para localizar
arquivos INFO. Se nenhum arquivo for encontrado com o glob pattern, eles
fazem **fallback** para `INFO-CLIENTE.md` / `INFO-SERVICO.md` (legado),
garantindo compatibilidade com clientes existentes.

---

## 7. Headers em Templates

O arquivo `info-Template.md` usa headers `## INFO-CLIENTE` e `## INFO-SERVICO`
como **delimitadores de seção**. Quando o sistema carrega o template, ele
substitui esses headers pelo valor de `to_header()` do pattern configurado.

Exemplo: se o pattern for `INFO-CLIENTE-{codCliente}.md`, o header no arquivo
gerado será `## INFO-CLIENTE-{codCliente}.md`.

### Como funciona

```
Template (info-Template.md):
## INFO-CLIENTE
@CodCliente; ---
@dataProposta; ---

## INFO-SERVICO
@CodServico; ---

Arquivo gerado (pattern default):
## INFO-CLIENTE-JOS01_00_R00.md
@CodCliente; JOS01
@dataProposta; 2026-06-22

## INFO-SERVICO-JOSSRV01_00_R00.md
@CodServico; JOSSRV01
```

---

## 8. Migração Retroativa

O script `scripts/migrate_info_to_pattern.py` renomeia arquivos INFO legados
(`INFO-CLIENTE.md`, `INFO-SERVICO.md`) para o novo pattern configurado.

### Uso

```bash
# Modo dry-run (apenas lista, não altera nada)
python scripts/migrate_info_to_pattern.py

# Realizar a migração (cria .bak automático)
python scripts/migrate_info_to_pattern.py --apply

# Restaurar a partir do .bak
python scripts/migrate_info_to_pattern.py --rollback
```

### Comportamento

- **dry-run** (default): exibe todos os arquivos que seriam renomeados
- **apply**: renomeia cada arquivo e salva o mapeamento em
  `.bak/migrate_info_to_pattern.bak.json`
- **rollback**: restaura todos os arquivos a partir do `.bak`
- O script lê `@CodCliente` / `@CodServico` do conteúdo do arquivo para
  preencher os placeholders
- Se o código não for encontrado, usa o nome da pasta como fallback

---

## 9. Conformance Checker

A partir da v1.4.0, duas novas ferramentas MCP auditam a conformidade dos
arquivos INFO:

### `verificar_conformidade_clientes`

Examina todas as pastas de clientes e serviços e reporta:

- **Pastas com espaços ou caracteres especiais** no nome
- **INFO files ausentes** (nenhum arquivo corresponde ao pattern)
- **Pattern mismatch** (arquivo INFO legado não corresponde ao pattern atual)
- **Duplicatas** (múltiplos arquivos correspondem ao mesmo pattern)

### `corrigir_conformidade`

Aplica a correção sugerida para um item específico:

- Pattern mismatch → renomeia o arquivo para o pattern configurado
- Pasta com caracteres inválidos → renomeia substituindo por `_`

### Estados Aceitos

Itens podem ser **aceitos** (suprimidos) via `accept_state()`, que persiste
a decisão em `.conformance_accepted.json`. Isto é útil para casos onde o
estado atual é intencional.

---

## 10. Referência do Desenvolvedor

### Arquivos Envolvidos

| Arquivo | Função |
|---|---|
| `info_pattern_resolver.py` | Value Object: `resolve()`, `to_glob()`, `to_header()`, `extract()`, `validate()` |
| `path_manager.py` | Factory methods: `get_info_pattern()`, `get_info_glob()`, `get_info_header()` |
| `config.py` | Property `info_file_patterns` + schema validation |
| `client_crud.py` | `_resolve_info_filename()`, `_parse_revision_from_filename()`, `_get_latest_file()` |
| `foton_mcp.py` | MCP tools: `verificar_conformidade_clientes`, `corrigir_conformidade` |
| `client_conformance.py` | `ClientConformanceChecker` com `check()`, `auto_fix()`, `accept_state()` |
| `scripts/migrate_info_to_pattern.py` | Script de migração retroativa |

### Testes

```bash
# Testes do sistema de nomenclatura (32 + 7 + 7 + 5 = 51)
python -m pytest tests/unit/test_info_pattern_resolver.py -v
python -m pytest tests/unit/test_path_manager_info_pattern.py -v
python -m pytest tests/unit/test_client_crud_info_pattern.py -v
python -m pytest tests/unit/test_client_conformance.py -v

# Testes gerais (353, zero regressão esperada)
python -m pytest
```

### Integração Contínua

Sempre que um novo placeholder for adicionado:

1. Adicione o placeholder em `_KNOWN_PLACEHOLDERS` no `settings.json` (se aplicável)
2. Atualize a lista de placeholders neste documento
3. Adicione testes em `test_info_pattern_resolver.py`
4. Atualize `PLACEHOLDER_DESCRIPTIONS` no `PathManager` se necessário
