---
type: guide
domain: rag
status: active
tags: [rag, user-guide, troubleshooting]
---

# Guia do Usuário — RAG Multi-Modelo

> **RAG** é como um arquivista que leu todos os seus projetos antigos e consegue responder perguntas em segundos. "Que acabamento usamos no apto 502?" — o RAG busca nos documentos, acha a resposta e mostra a fonte.

---

## 1. Acessando o RAG

Menu Principal → Opção **7 (Configurações)** → **RAG**

Você verá o menu:

```
┌── RAG — CONFIGURAÇÃO ──────────────────────────┐
│ 1. Diagnóstico do Sistema (Hardware + Coleções) │
│ 2. Modo de Embedding (MiniLM / BGE-M3 / Ambos) │
│ 3. Re-indexar Base para Modelo Ativo            │
│ 4. Status dos Modelos Instalados                │
│ 0. Voltar                                       │
└─────────────────────────────────────────────────┘
```

---

## 2. Modos de Operação

| Modo | Modelo | Velocidade | Precisão | RAM Necessária | Disco |
|------|--------|-----------|---------|---------------|-------|
| **MiniLM** 🐇 | `paraphrase-multilingual-MiniLM-L12-v2` | Rápido | Boa | ~1 GB | ~450 MB |
| **BGE-M3** 🐢 | `BAAI/bge-m3` | Moderado | Excelente | ~4.5 GB | ~2.2 GB |
| **Dual** 🔄 | Ambos (consulta em paralelo) | Moderado | Máxima (merge) | ~8 GB | ~2.7 GB |

### Como escolher?

O sistema recomenda automaticamente com base no seu hardware:

| Hardware | Recomendação |
|----------|-------------|
| **< 8 GB RAM** | MiniLM (modo seguro, evita travamentos) |
| **8–16 GB RAM** | BGE-M3 (melhor custo-benefício) |
| **> 16 GB RAM** | Dual (redundância total, sem limitações) |
| **GPU NVIDIA (CUDA)** | BGE-M3 ou Dual — aceleração por GPU disponível |

> 💡 Você pode trocar o modo a qualquer momento. A troca só afeta **novas consultas** — o histórico permanece intacto.

---

## 3. Instalando Modelos

1. Acesse Menu Principal → Opção 7 → RAG → Opção 4 (Status dos Modelos)
2. Se o modelo desejado aparecer como **"Não instalado"**, selecione-o para baixar
3. Uma **barra de progresso** mostra o andamento:

```
Baixando BAAI/bge-m3... ████████████░░░░ 65% (1.4 GB / 2.2 GB)
```

4. Após o download, o modelo fica disponível imediatamente

> ⚠️ O download do BGE-M3 (~2.2 GB) pode levar alguns minutos dependendo da sua conexão.

---

## 4. Entendendo o Diagnóstico

Na opção **1 (Diagnóstico do Sistema)**, você vê:

```
═══ HARDWARE ═══
CPU: 8 cores | RAM: 15.2 GB disponível | GPU: CUDA 12.1 (6 GB VRAM)

═══ COLECÕES ═══
▶ minilm (MiniLM)
  • Coleção: foton_minilm_384d
  • Dimensões: 384
  • Chunks indexados: 1.247
  • Circuit Breaker: FECHADO (0 falhas)
  • Última indexação: 2026-07-05 14:32

▶ bgem3 (BGE-M3)
  • Coleção: foton_bgem3_1024d
  • Dimensões: 1.024
  • Chunks indexados: 1.247
  • Circuit Breaker: FECHADO (0 falhas)
  • Última indexação: 2026-07-05 14:35
```

| Campo | Significado |
|-------|-------------|
| **Coleção** | Nome da base no ChromaDB (`foton_{modelo}_{dimensões}d`) |
| **Dimensões** | Tamanho do vetor de embedding (quanto maior, mais preciso) |
| **Chunks indexados** | Quantos fragmentos de documentos foram processados |
| **Circuit Breaker** | "FECHADO" = normal; "ABERTO" = muitas falhas, desligado temporariamente |
| **Última indexação** | Quando a base foi atualizada pela última vez |

---

## 5. Troubleshooting

### "Modelo não encontrado"

**Causa:** O modelo não está instalado no cache local.
**Solução:** Vá em Menu → RAG → Opção 4 → selecione o modelo para instalar.

### "Memória insuficiente"

**Causa:** O modelo escolhido requer mais RAM do que você tem disponível.
**Solução:** Troque para um modo mais leve (MiniLM) ou feche outros programas.

| Modelo | RAM Mínima |
|--------|-----------|
| MiniLM | 1 GB |
| BGE-M3 | 4.5 GB |
| Dual | 8 GB |

### "Download falhou"

**Causa:** Conexão com HuggingFace Hub interrompida ou espaço em disco insuficiente.
**Soluções:**
- Verifique sua conexão com a internet
- Verifique espaço em disco (MiniLM: ~450 MB, BGE-M3: ~2.2 GB)
- Tente novamente — o download retoma do ponto onde parou

### "Slow query"

**Causa:** Consulta demorando mais que o esperado.
**Soluções:**
- Troque para MiniLM (mais rápido)
- Verifique se outros programas estão usando muita CPU/RAM
- Se estiver no modo Dual, considere mudar para modo único

---

## 6. Dicas Rápidas

- ✅ **Sempre indexe** após alterar documentos do cliente para manter a base atualizada
- ✅ Use **MiniLM** no dia a dia e **BGE-M3** quando precisar de precisão máxima
- ✅ O **modo Dual** é ideal para consultas críticas onde nenhum resultado pode ser perdido
- ❌ **Não altere** o modo de embedding sem re-indexar a base
