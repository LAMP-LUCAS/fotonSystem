# Spec: Módulo de Sincronização

**Data:** 2026-06-24
**Versão:** 1.0
**Responsável:** Time Core

## 1. Problema
O Foton System mantém dados em dois locais: Excel (base de dados consolidada) e filesystem (pastas de clientes com INFO-*.md). Essas duas visões podem divergir, causando inconsistências.

## 2. Solução Proposta
Pipeline de sincronização com três direções:
- **Pastas → DB:** Descobrir pastas novas e importar para o Excel
- **DB → Pastas:** Criar pastas/arquivos para registros do Excel que não têm representação física
- **Bidirecional (DB ↔ Arquivo):** Sincronizar dados entre INFO files e Excel

SyncReport gerado ao final de cada operação documentando o que foi alterado.

## 3. Regras de Negócio

### 3.1 Direções
- **RULE-SYNC-1.1:** `sincronizar_clientes` (Pastas → DB): varre diretório de clientes, descobre pastas novas, adiciona ao Excel. Ignora pastas ocultas (iniciadas por `.`).
- **RULE-SYNC-1.2:** `sincronizar_pastas_clientes` (DB → Pastas): para cada cliente no Excel sem pasta correspondente, cria a estrutura de pastas.
- **RULE-SYNC-1.3:** `sincronizar_pastas_servicos` (DB → Pastas de serviços): cria pastas de serviço para registros no DB sem representação física.
- **RULE-SYNC-1.4:** `sincronizar_base`: atalho para Pastas → DB (atualiza Excel mestre com dados do filesystem).

### 3.2 Pipeline Unificado
- **RULE-SYNC-2.1:** `pipeline_sync`: executa sync em direção configurável (`pastas_to_db`, `db_to_pastas`, `bidir`) com barra de progresso e relatório.
- **RULE-SYNC-2.2:** SyncReport: documento gerado ao final listando clientes/serviços criados, atualizados ou ignorados.

### 3.3 Importação/Exportação
- **RULE-SYNC-3.1:** `exportar_dados_clientes`: exporta dados do Excel para arquivos .md nas pastas dos clientes.
- **RULE-SYNC-3.2:** `exportar_dados_servicos`: exporta dados de serviços do Excel para .md.
- **RULE-SYNC-3.3:** `importar_dados_servicos`: importa dados de .md de serviço de volta ao Excel.
- **RULE-SYNC-3.4:** `importar_dados_clientes`: importa dados de INFO files de volta ao Excel (paridade export/import).

### 3.4 Segurança e Integridade
- **RULE-SYNC-4.1:** Pastas ocultas (`.` prefix) são ignoradas em TODAS as operações de varredura.
- **RULE-SYNC-4.2:** Sincronização nunca remove dados — apenas adiciona ou atualiza.
- **RULE-SYNC-4.3:** Em caso de conflito (dado diferente no DB vs filesystem), o dado do filesystem (INFO-*.md) prevalece como Centro de Verdade.

## 4. Relações
- Service: `sync_service.py`
- Pipeline: `pipeline_sync.py`
- MCP tools: `info_sistema`, `sincronizar_base`, `sincronizar_clientes`, `sincronizar_pastas_clientes`, `sincronizar_pastas_servicos`, `exportar_dados_clientes`, `exportar_dados_servicos`, `importar_dados_servicos`, `importar_dados_clientes`
- ADR relacionado: `ADR001_ParaZettelkastenDoc` (estrutura de pastas)
