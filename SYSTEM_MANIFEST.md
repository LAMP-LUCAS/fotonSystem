# FOTON SYSTEM - MANUAL DO AGENTE (LLM)

Este documento descreve como Agentes de IA (LLMs) devem interagir com o Foton System para gerar documentos de arquitetura com precisão.

## 1. Princípios Básicos

O sistema opera com base em **Centros de Verdade** (Arquivos Markdown) e **Templates** (Office).
O Agente **NÃO** deve manipular DOCX/PPTX diretamente. O Agente deve manipular os DADOS (`.md`).

### Fluxo de Trabalho Ideal

1.  **Ler Contexto:** Identifique o cliente e o serviço lendo `INFO-CLIENTE.md` e `INFO-SERVICO.md`.
2.  **Calcular:** Realize estimativas financeiras (CUB) se necessário.
3.  **Criar Dados:** Gere um arquivo Markdown de dados único para a tarefa (ex: `02-001_PROPOSTA.md`).
4.  **Executar:** Chame o `DocumentService` via script Python simples.

---

## 2. Formatação de Dados (IMPORTANTE)

O sistema possui um **Middleware de Formatação Automática**.
O Agente deve fornecer **NÚMEROS PUROS** ou **DATA ISO** sempre que possível. O sistema formata para o padrão brasileiro (R$ X.XXX,XX) automaticamente.

### Regras de Tipagem

*   **Dinheiro:** Se a chave contiver `valor`, `custo`, `total`, `preco`, `cub`, `exec` -> O sistema adiciona `R$` e formata.
    *   *Input:* `@valorProposta: 5000.50`
    *   *Output no Doc:* `R$ 5.000,50`
*   **Áreas:** Se a chave contiver `area`, `aceqv` -> O sistema formata com pontos e vírgulas.
    *   *Input:* `@areaTotal: 1234.5`
    *   *Output no Doc:* `1.234,50`
*   **Texto:** Texto é mantido como está.

---

## 3. Variáveis de Sistema (Automáticas)

Não é necessário preencher estas variáveis manualmente. O sistema injeta automaticamente:

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `@DataAtual` | Data de hoje por extenso | `29 de Janeiro de 2026` |
| `@LinkCUB` | Link direto para o PDF do CUB do mês anterior | `.../cub-dezembro-2025.pdf` |
| `@ReferenciaCUB` | Rótulo do CUB utilizado | `Dezembro/2025` |

---

## 4. Estrutura de Templates (KIT DOC)

Os templates estão em `.../ADM/KIT DOC`. Use as chaves abaixo para preenchê-los.

### Proposta Anteprojeto (`...ANTEPROJETO.pptx`)

Esta é a proposta mais completa. Requer:

*   **Cliente:** `@nomeCliente`, `@empregoCliente`... (Vem do INFO-CLIENTE)
*   **Serviço:** `@demandaProposta`, `@detalhesProposta`, `@prazos`... (Vem do INFO-SERVICO)
*   **Financeiro (Essencial):**
    *   `@projArqEng`: Valor do Projeto Arquitetônico
    *   `@procLegais`: Valor de Aprovações
    *   `@execcub`: Custo de Obra (CUB * Área)
    *   `@execInfra`: 20% do CUB
    *   `@execPais`, `@execMob`: 5% do CUB cada
    *   `@totalGeral`: Soma de tudo
    *   `@ArqEng%`: (Proj / Total) * 100

### Dica de Engenharia de Valor

Para galpões simples:
1.  **Custo CUB:** Use ref. "Galpão Industrial (GI)" ou "Comercial Andar Livre (CAL-8)".
2.  **Honorários:** Entre 1.5% e 3.0% do Custo Total da Obra.

---

## 5. Exemplo de Script de Geração

```python
from foton_system.modules.documents.application.use_cases.document_service import DocumentService
# ... imports adapters ...

service = DocumentService(docx_adapter, pptx_adapter)
service.generate_document(
    template_path="...",
    data_path="...", 
    output_path="...", 
    doc_type="pptx" # ou "docx"
)
```
