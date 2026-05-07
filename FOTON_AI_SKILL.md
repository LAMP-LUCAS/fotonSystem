# Foton Architecture System: AI Operational Skill (v2.0)

This skill provides the definitive operational guidelines for an AI Agent to use the **Foton Architecture System** efficiently, safely, and with architectural stability.

## Core Philosophies

1.  **Center of Truth (Centro de Verdade):** Every client/service folder contains an `INFO-*.md` file. This is the **Single Source of Truth**. Never assume data; always read the INFO file first.
2.  **Pure Data Policy:** Data stored in INFO files and processed by the engine should be "pure" (e.g., `1500.50` instead of `R$ 1.500,50`). Formatting is handled by the Template or the UI report, not by the stored data.
3.  **Agnostic Organization:** The system is adaptive. It searches the entire folder hierarchy for context. You are free to organize folders (e.g., `03_PROJETOS`) as long as INFO files exist somewhere in the path.
4.  **Audit Integrity (POP):** All critical operations (Creation, Finance, Generation) are Audited Standard Operations. They leave logs and create backups.

---

## 🛠 Operational Workflows

### 1. New Client Onboarding
**Goal:** Create a standardized project environment without duplicates.
1.  **Search:** Always run `listar_clientes` to see if a similar name exists.
2.  **Verify:** Use `pipeline_novo_cliente`. It performs a fuzzy search and prevents duplicate folders.
3.  **Execute:** If clear, the system creates the folder structure (`01_ADM`, `02_FIN`, `03_PRJ`).

### 2. Information Management
**Goal:** Keep the "Center of Truth" updated and relevant.
1.  **Read:** Use `ler_ficha_cliente` to get the context of a project.
2.  **Update:** Use `atualizar_ficha_cliente` to append meeting notes, technical decisions, or new metadata tags.
3.  **Structure:** Prefer the semicolon separator (`@Variable; Value`) for clear AI/Human parsing.

### 3. Smart Document Generation
**Goal:** Generate 100% accurate proposals or contracts.
1.  **Template Discovery:** Run `listar_templates` to identify the correct base.
2.  **Pre-Flight:** **MANDATORY.** Run `pipeline_emitir_documento`.
    - Review the missing variables list.
    - Check for existing generated files to avoid version conflicts.
3.  **Correction:** Update the INFO file with missing data OR prepare `dados_extras`.
4.  **Emission:** Run `gerar_documento`. The system is case-insensitive, so `@CLIENTE` matches `@cliente`.

### 4. Financial Tracking
**Goal:** Maintain a real-time ledger for the firm.
1.  **Record:** Use `registrar_financeiro`. Always provide a clear description (e.g., 'Sinal Projeto X').
2.  **Audit:** Use `consultar_financeiro` for a specific client or `resumo_financeiro_geral` for firm-wide BI.
3.  **Sync:** Periodically run `sincronizar_base` to keep the master Excel file aligned with individual client ledgers.

---

## 🧠 AI Best Practices (Prompt Engineering for Foton)

-   **Context Awareness:** If the user asks about "the Henry Matisse project," first use `listar_clientes` to find the exact alias (e.g., `SIMONE_SEBASTIAO`), then `listar_servicos_cliente` to find the specific project folder.
-   **Math Precision:** When updating financial tags in INFO files, use 2 decimal places. The system will auto-calculate tags like `[calculo: @valor * 0.10]`.
-   **Graceful Degradation:** If a tool fails due to a missing folder, explain the issue to the user and suggest using `sincronizar_clientes` to refresh the database.
-   **Security:** Never reveal full system paths unless necessary. Focus on the Alias/Name of the client.

## 🚦 System Status Protocol
- Always run `ping` at the start of a deep task.
- Use `info_sistema` to verify if the paths are pointing to the correct environment (e.g., OneDrive vs local).

---
*Foton: Intelligence and adaptability for the modern architect.*
