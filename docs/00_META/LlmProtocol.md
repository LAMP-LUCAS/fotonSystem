---
type: guide
domain: core
status: active
tags: [meta, protocol, llm, documentation]
---
# 📜 Protocolo de Documentação Agêntica (LlmProtocol)

Este documento define as regras de engajamento para Humanos e IAs (Agentes) ao interagir com o repositório **FOTON System**. O objetivo é garantir a integridade do conhecimento, a rastreabilidade das decisões e a resiliência do ecossistema.

## 🏛️ Arquitetura PARA + Zettelkasten

A documentação é organizada em quatro esferas principais (Método PARA) e interligada por grafos (Zettelkasten).

1.  **00_META:** Regras do sistema, índices (MOCs) e glossários.
2.  **01_PROJECTS:** Esforços ativos (Sprints). Contém o "como e quando" as coisas foram feitas. **Imutável após o fechamento da Sprint.**
3.  **02_AREAS:** Conhecimento perene e regras de domínio (DDD). Contém o "o que é" o sistema hoje. **Evolutivo.**
4.  **03_RESOURCES:** Manuais, guias, templates e materiais de referência.
5.  **04_ARCHIVES:** Histórico de releases e documentos depreciados.

## 🤖 Regras para Agentes (LLMs)

### 1. RalphLoop & Spec-Driven Development
Antes de iniciar qualquer tarefa de código, a IA deve:
- Consultar a Sprint ativa em `01_PROJECTS/`.
- Validar se o `PLAN_SXX.md` possui os Specs necessários.
- Atualizar o Checklist conforme avança.
- Registrar falhas e sucessos de testes no `REPORT_SXX.md`.

### 2. Frontmatter Obrigatório
Todo arquivo `.md` na pasta `docs/` **DEVE** começar com um bloco YAML:
```yaml
---
type: concept | spec | plan | report | guide
domain: core | clients | documents | finance | infra
status: draft | active | deprecated
tags: [tag1, tag2]
---
```

### 3. Navegação por Hiperlinks
- Use `[[NomeDoArquivo]]` para links internos (padrão Obsidian/Wiki).
- No final de cada documento de Área ou Recurso, adicione uma seção `## 🔗 Links Relacionados`.

### 4. Manutenção de Baixa Entropia
- **NUNCA** refatore arquivos de Sprints passadas. Eles são o log histórico.
- Ao atualizar uma regra de negócio, altere o arquivo correspondente em `02_AREAS/`.
- Se um documento se tornar obsoleto, mova-o para `04_ARCHIVES/Deprecated/` em vez de deletar.

### 5. Padronização de Nomenclatura
- **Pastas:** `00_SNAKE_CASE` (prefixo numérico + caixa alta).
- **Arquivos de Documentação:** `PascalCase.md` (ex: `UserGuide.md`, `ClientDataModel.md`).
- **Arquivos de Código:** Seguir PEP8 (snake_case.py).
- **Documentos Gerados (Saída):** `02-COD_DOC_TIPO_VER_REV_NOME.ext`.


---
## 🔗 Links Relacionados
- Índice Principal: [[Index]]
- Contexto LLM: [[LlmContext]]
