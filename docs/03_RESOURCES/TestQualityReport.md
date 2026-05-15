---
type: report
domain: dev
status: active
tags: [test, quality, coverage, e2e, io]
---
# 📊 Relatório de Qualidade de Testes (TestQualityReport)

Este documento detalha o estado da cobertura de testes, as metodologias aplicadas e os protocolos de resiliência do **FOTON System**.

## 🏗️ Arquitetura de Validação

Seguimos a **ADR 003**, que exige isolamento total via **Modo Sandbox** para todos os testes. Isso garante a soberania dos dados reais do usuário.

### Níveis de Teste

1.  **Unitários:** Validam lógicas isoladas (ex: `FotonFormatter`, `FormSession`).
2.  **Integração:** Validam a comunicação entre módulos e o sistema de arquivos (ex: `test_io_resilience`).
3.  **E2E (End-to-End):** Simulam fluxos completos de trabalho do arquiteto (ex: `test_architect_pipeline`).
4.  **UI/Interface:** Simulam interações de usuário na TUI (ex: `test_form_session`).

---

## 🛡️ Robustez e Resiliência de I/O

O sistema é testado contra cenários de erro comuns em escritórios de arquitetura:

-   **Retry on Lock:** Validado em `tests/unit/test_io_resilience.py`. O sistema utiliza um algoritmo de **Exponential Backoff** para tentar salvar arquivos Excel que possam estar bloqueados pelo OneDrive ou abertos no Excel.
-   **SSOT Lifecycle:** Validado em `tests/e2e/test_architect_pipeline.py`. Garante que as mudanças manuais em arquivos Markdown sejam sincronizadas com o banco de dados sem perda de informação.

---

## 🧪 Métricas Atuais

| Categoria | Cobertura | Status | Observações |
| :--- | :--- | :--- | :--- |
| Core Lógica | > 90% | ✅ Estável | Cobertura total de cálculos e formatação. |
| Repositórios | > 85% | ✅ Estável | Testado contra locks e permissões. |
| Pipelines E2E | 100% | ✅ Estável | Fluxo completo (Cliente -> INFO -> Documento). |
| Interface TUI | > 70% | 📈 Em Expansão | Loop de navegação e edição validado com Mocks. |

---

## 🚀 Como Executar os Testes

Para rodar a suíte completa com isolamento automático:

```powershell
$env:PYTHONPATH="."
python tests/run_tests.py
```

> [!DIDACTIC:META] Segurança de Teste: Nunca execute testes fora do ambiente de desenvolvimento. O modo Sandbox é ativado automaticamente, mas a flag `--sandbox` no CLI é o seu melhor amigo para demonstrações seguras.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- ADR Sandbox: [[ADR003_SandboxTestIsolation]]
- Guia de Desenvolvimento: [[Contributing]]
