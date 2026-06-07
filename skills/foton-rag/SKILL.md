---
name: foton-rag
description: Memória semântica do escritório — indexação e consulta vetorial (ChromaDB) em projetos passados
---

# Foton Skill: RAG (Memória Semântica)

Skill especializada em **busca semântica e indexação** do Foton System.
Carregue esta skill quando a tarefa envolver consultar conhecimento de projetos passados ou atualizar a base vetorial.

## Skills relacionadas

Este skill faz parte do ecossistema Foton. Consulte as demais conforme necessário:

| Skill | Quando usar |
|---|---|
| `foton-architecture` | Visão geral do sistema, primeiros passos |
| `foton-clients` | Cadastro e fichas de clientes (fonte de dados para indexação) |
| `foton-documents` | Gerar documentos (pode usar RAG para contexto) |
| `foton-finance` | Registrar entradas/saídas, consultar financeiro |

## Ferramentas

| Ferramenta | Descrição |
|---|---|
| `indexar_conhecimento` | Indexa arquivos (.md, .txt) no ChromaDB |
| `consultar_conhecimento` | Busca semântica em todos os projetos indexados |

## Workflows

### Indexação
1. `indexar_conhecimento()` — indexar todos os clientes
2. `indexar_conhecimento(pasta_alvo="caminho/especifico")` — indexar pasta específica
3. **Melhor prática**: indexar após cada alteração em INFO files

### Consulta
1. `consultar_conhecimento(pergunta="...")` — buscar conhecimento relevante
2. Resultados incluem: documento, fonte, similaridade (%)

## Comportamento do sistema

### Circuit Breaker (ChromaDB)
O acesso ao banco vetorial é protegido por circuit breaker:
- **3 falhas consecutivas** → estado OPEN por 60 segundos
- Durante OPEN: consultas retornam vazio, indexações são ignoradas
- Após 60s: 1 tentativa de sonda → se ok, volta ao normal
- **Logs**: eventos registrados em `foton_mcp.log`

### Subprocesso (modo frozen)
Quando o Foton está compilado (EXE), a consulta RAG delega para o Python do sistema via subprocesso:
- Usa `tempfile.mkdtemp()` temporário — limpo automaticamente no `finally`
- Timeout de 120 segundos

## Convenções

- **Indexar antes de consultar**: base vazia retorna "No relevant knowledge found"
- **Perguntas concisas**: máximo 5000 caracteres
- **Fontes**: resultados incluem caminho do arquivo de origem
- **Modelo**: paraphrase-multilingual-MiniLM-L12-v2 (otimizado PT-BR)
