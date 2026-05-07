---
name: foton-architecture
description: Manage architecture projects, generate smart documents (DOCX/PPTX), and track financial ledgers using the Foton system. Use for client onboarding, document pre-flight validation, and semantic knowledge base queries.
---

# Foton Architecture System

This skill enables Gemini CLI to act as a specialized architectural engineering assistant, capable of managing complex project folders, generating automated documents, and maintaining financial integrity.

## Core Philosophies

1.  **Center of Truth (Centro de Verdade):** Every client/service folder contains an `INFO-*.md` file. Always read this file using `ler_ficha_cliente` before making decisions.
2.  **Pure Data Policy:** Store numeric values as raw floats (e.g., `1500.50`). The engine handles formatting for the final document.
3.  **Agnostic Organization:** The system is adaptive and searches the entire folder hierarchy for context.

## 🛠 Operational Workflows

### 1. New Client Onboarding
Always prefer the safe pipeline to avoid duplicates:
1.  Run `listar_clientes` to search for similar existing projects.
2.  Execute `pipeline_novo_cliente(nome, ...)` to create the standard folder structure.

### 2. Information Management
Keep the "Center of Truth" updated with meeting notes and technical decisions:
1.  Use `ler_ficha_cliente` to get context.
2.  Use `atualizar_ficha_cliente` to record new data.
3.  **Format:** Prefer the semicolon separator (`@Variable; Value`).

### 3. Smart Document Generation
1.  **Template Discovery:** Run `listar_templates`.
2.  **Pre-Flight:** **MANDATORY.** Run `pipeline_emitir_documento`.
3.  **Correction:** Update INFO files with missing variables.
4.  **Emission:** Run `gerar_documento`. (Note: System is case-insensitive).

### 4. Financial Tracking
1.  **Record:** Use `registrar_financeiro` (ENTRADA or SAIDA).
2.  **Audit:** Use `consultar_financeiro` or `resumo_financeiro_geral` for BI.
3.  **Sync:** Run `sincronizar_base` periodically to align Excel and folders.

## 🧠 AI Best Practices

- **Context Loading:** When asked about a specific project, first find the client alias (`listar_clientes`), then the specific service folder (`listar_servicos_cliente`).
- **Math Precision:** Use 2 decimal places in financial tags.
- **Environment:** Use `info_sistema` to verify active paths (e.g., OneDrive vs Local).

---
*Foton: Intelligence and adaptability for the modern architect.*
