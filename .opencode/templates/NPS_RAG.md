# NPS — Módulo RAG (Consulta Inteligente)

## Pergunta

> Em uma escala de 0 a 10, o quanto o módulo de **Consulta Inteligente (RAG)** te ajuda a encontrar informações de projetos passados?

## Instruções de Coleta

- **Periodicidade:** Semestral
- **Público:** Todos os usuários do escritório que utilizam a ferramenta `consultar_conhecimento`
- **Forma:** Questionário inline via TUI (Opção de Menu) ou formulário Google Forms
- **Registro:** Resultados salvos em `.opencode/metrics/nps_rag.jsonl`

## Cálculo

| Faixa | Classificação |
|-------|---------------|
| 0-6 | Detratores |
| 7-8 | Neutros |
| 9-10 | Promotores |

```
NPS = (% Promotores - % Detratores) × 100
```

## Meta

- **Target:** NPS ≥ 8 (ou ≥ 70 após conversão para escala -100 a +100)
- **Primeira coleta:** Pendente (STORY-041)
