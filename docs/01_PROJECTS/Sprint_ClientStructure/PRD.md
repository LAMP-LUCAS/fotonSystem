---
type: prd
domain: core
status: active
tags: [clients, structure, folder-convention, architecture]
---

# PRD: Reestruturação da Pasta de Clientes

## 1. Problema

A estrutura atual da pasta `CLIENTES/` apresenta diversos problemas que comprometem a resiliência, robustez e automação do sistema:

1. **Mistura de responsabilidades**: FINANCEIRO.csv, documentos gerados, logs e pastas de serviço convivem no mesmo nível sem separação clara.
2. **Nomenclatura inconsistente**: Clientes nomeados com espaços, acentos, hífens e underscores de forma não padronizada (`Condomínio Edifício Henry Matisse`, `ANTONIO-FERREIRA`, `ANDRE E DANIEL`, `ANA_MARIA_MAG`).
3. **Duplicatas**: Um mesmo cliente existe em múltiplas pastas (`Condomínio Edifício Henry Matisse` e `CONDOMINIO_ED_HENRY_MATISSE`).
4. **Ignored_folders case-sensitive**: `DOC` é ignorado mas `doc` não, causando vazamento na detecção de serviços.
5. **Sub-serviços aninhados verticalmente**: Pastas dentro de pastas dentro de pastas, arriscando o limite de 260 caracteres do Windows.
6. **Sem padronização de pastas funcionais**: Não há um contrato claro sobre onde cada tipo de arquivo deve residir.
7. **Documentos gerados soltos na raiz**: Misturados com dados fonte, sem separação por serviço ou tipo documental.

## 2. Objetivo

Estabelecer uma convenção de pastas para a árvore de `CLIENTES/` que seja:

- **Resiliente**: Tolerante a desvios de localização (busca regressa de contexto)
- **Robusta**: Nomes normalizados, sem duplicatas, sem caracteres especiais em caminhos
- **Coesa**: Cada pasta tem um propósito claro e não ambíguo
- **Coerente**: Mesma estrutura se repete em todos os nós (cliente, serviço, sub-serviço)
- **Segura**: Profundidade máxima de 2 níveis, proteção contra path traversal
- **Versátil**: Funciona em Windows (limite 260 chars) e mapeável para S3 tags
- **Automatizável**: O sistema sabe onde ler/escrever cada tipo de arquivo

## 3. Estrutura Alvo

```
CLIENTES/
└── CLIENTE_UPPER_SNAKE/
    ├── INFO-CLIENTE.md              ← Metadados do cliente (raiz)
    ├── _SYS/                        ← Sistema (ignorado como serviço)
    │   ├── FINANCEIRO.csv
    │   └── history.log
    │
    ├── SERVICO_A/                   ← Serviço raiz (UPPER_SNAKE_CASE, sem __)
    │   ├── INFO-SERVICO.md          ← Metadados do serviço (raiz)
    │   ├── {DOC}/                   ← Documentos (sistema + usuário)
    │   │   ├── RECEBIDOS/
    │   │   ├── CONTRATOS/
    │   │   ├── PROPOSTAS/
    │   │   └── GERADOS/             ← Sistema gera documentos aqui
    │   │       ├── PROPOSTA/
    │   │       ├── CONTRATO/
    │   │       ├── MEMORIAL/
    │   │       └── RECIBO/
    │   ├── {ADM}/                   ← Administrativo
    │   │   ├── CONTATO/
    │   │   ├── COMERCIAL/
    │   │   ├── FINANCEIRO/
    │   │   └── REUNIOES/
    │   └── {OP}/                    ← Operação (o trabalho em si)
    │       ├── EP/                  ← Estudos Preliminares
    │       ├── AP/                  ← Anteprojeto
    │       ├── EXE/                 ← Execução
    │       └── REL/                 ← Relatórios
    │
    ├── SERVICO_A__SUB/             ← Sub-serviço (horizontal, __)
    │   └── (mesma estrutura)
    │
    └── SERVICO_B/
        └── (mesma estrutura)
```

### 3.1 Aliases configuráveis

Os nomes `{DOC}`, `{ADM}`, `{OP}` são definidos em `settings.json`:

```json
{
  "folder_conventions": {
    "doc": "00_DOC",
    "adm": "01_ADM",
    "op": "02_OPERACAO",
    "op_phases": ["EP", "AP", "EXE", "REL"],
    "op_phase_labels": {
      "EP": "Estudos Preliminares",
      "AP": "Anteprojeto",
      "EXE": "Execução",
      "REL": "Relatórios"
    }
  }
}
```

## 4. Comportamento do Sistema

### 4.1 Detecção de serviços

```
TODO subdir do cliente que NÃO começa com _
E NÃO está em ignored_folders
E NÃO é {DOC|ADM|OP}
→ é um nó de serviço (raiz ou sub-serviço)
```

Hierarquia decodificada pelo separador `__`:
- `SERVICO_A` → serviço raiz
- `SERVICO_A__SUB` → sub-serviço de SERVICO_A
- `SERVICO_A__SUB__DETALHE` → sub-sub-serviço

### 4.2 Busca regressa de contexto

```python
def _load_context_data(self, data_path: Path) -> dict:
    data = {}
    base = Path(self._config.base_pasta_clientes).parent
    current = data_path.parent if data_path.is_file() else data_path
    dirs = []
    while current != base:
        dirs.append(current)
        current = current.parent
    dirs.reverse()
    for folder in dirs:
        for name in ('INFO-CLIENTE.md', 'INFO-SERVICO.md'):
            info = folder / name
            if info.exists():
                data.update(self._parse_md_data(info))
    return data
```

### 4.3 Geração de documentos

```python
output_dir = service_path / config.folder_doc / 'GERADOS' / tipo_documento
```

Tipo inferido do template:
| Template | Tipo |
|---|---|
| `PROPOSTA_*` | `PROPOSTA` |
| `CONTRATO-*` | `CONTRATO` |
| `MEMORIAL-*` | `MEMORIAL` |
| `RECIBO-*` | `RECIBO` |
| outros | `GERAL` |

### 4.4 Financeiro

```python
# Tenta {ADM}/FINANCEIRO.csv primeiro, fallback raiz
ledger = client_path / config.folder_adm / 'FINANCEIRO.csv'
if not ledger.exists():
    ledger = client_path / 'FINANCEIRO.csv'  # legacy
```

### 4.5 Normalização de nomes

```python
def normalize_client_name(name: str) -> str:
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
    name = re.sub(r'[^A-Za-z0-9]', '_', name.upper())
    name = re.sub(r'_+', '_', name).strip('_')
    name = name.replace('__', '_')  # sub-serviço não usa __ no nome raiz
    return name
```

## 5. Compatibilidade S3

| POSIX | S3 Equivalente |
|---|---|
| `CLIENTES/CLIENTE/SERVICO/` | Prefixo: `CLIENTE/SERVICO/` |
| `SERVICO__SUB` | Tag: `parent=SERVICO` |
| `{DOC}/` | Tag: `function=doc` |
| `{ADM}/` | Tag: `function=adm` |
| `{OP}/EP` | Tag: `function=op, phase=EP` |

## 6. Critérios de Sucesso

- [ ] 100% dos testes (novos + existentes) passando
- [ ] `normalize_client_name` cobre acentos, espaços, hífens, caracteres especiais
- [ ] `list_service_nodes` decodifica `__` corretamente em árvore
- [ ] Busca regressa encontra INFO-CLIENTE.md na raiz OU em subpastas
- [ ] Financeiro funciona com fallback (novo local → legado)
- [ ] Geração de documentos salva em `{DOC}/GERADOS/{tipo}/`
- [ ] Script de migração executa dry-run + real + rollback
- [ ] Nenhuma regression nos 200+ testes existentes
