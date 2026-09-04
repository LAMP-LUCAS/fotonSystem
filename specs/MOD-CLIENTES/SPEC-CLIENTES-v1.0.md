# Spec: Módulo de Clientes

**Data:** 2026-06-24
**Versão:** 1.0
**Responsável:** Time Core

## 1. Problema
O escritório de arquitetura precisa gerenciar clientes, seus serviços (sub-projetos) e a documentação associada de forma centralizada, com rastreabilidade e segurança.

## 2. Solução Proposta
Módulo clientes em Hexagonal Architecture (Ports & Adapters) com:
- Repositório Excel para persistência
- Domain entities e value objects
- Soft delete (reversível)
- INFO-*.md como Centro de Verdade (configurável via `settings.json`)
- Conformance checker para validar estrutura de pastas

## 3. Regras de Negócio

### 3.1 Entidades e Value Objects
- **RULE-CLIENTES-1.1:** `ClientCode` deve ter exatamente 5 caracteres: 3 letras (maiúsculas) + 2 dígitos. Ex: `JOS01`.
- **RULE-CLIENTES-1.2:** `ServiceCode` segue o mesmo formato `AAA00`.
- **RULE-CLIENTES-1.3:** `TaxId` aceita CPF (11 dígitos) ou CNPJ (14 dígitos), apenas números.
- **RULE-CLIENTES-1.4:** Nome de cliente não pode ser vazio (validação na criação via TUI).

### 3.2 CRUD
- **RULE-CLIENTES-2.1:** Criar cliente: verificar duplicidade por nome e NIF antes de persistir. Criar pasta + INFO file + registro no DB.
- **RULE-CLIENTES-2.2:** Ler cliente: exibir conteúdo do INFO-*.md (Centro de Verdade).
- **RULE-CLIENTES-2.3:** Atualizar cliente: alterar seção específica do INFO-*.md, criar `.bak` antes de modificar.
- **RULE-CLIENTES-2.4:** Remover cliente (soft delete): marcar como `DELETADO` na coluna Status do Excel. Pastas e arquivos NÃO são removidos.
- **RULE-CLIENTES-2.5:** Restaurar cliente: reverter Status para `ATIVO` no Excel, listar clientes deletados antes da restauração.
- **RULE-CLIENTES-2.6:** Preencher códigos faltantes (`fill_missing_codes`): gerar `CodCliente`/`CodServico` para registros com `NaN`, persistindo no Excel (com confirmação do usuário).

### 3.3 Serviços
- **RULE-CLIENTES-3.1:** Serviço é um sub-projeto vinculado a um cliente. Nome em PascalCase.
- **RULE-CLIENTES-3.2:** `create_service_entry`: ao criar estrutura de serviço, persistir `CodServico` automaticamente no DB (elimina sync manual).
- **RULE-CLIENTES-3.3:** `validar_codigos_servicos`: detectar códigos ausentes, placeholders (`000`), formato inválido e duplicatas.
- **RULE-CLIENTES-3.4:** `corrigir_codigos_servicos`: gerar novos códigos únicos via `generate_service_code()` para serviços inválidos.

### 3.4 Info Files (Centro de Verdade)
- **RULE-CLIENTES-4.1:** INFO-*.md é o Centro de Verdade. Sempre ler antes de agir sobre um cliente.
- **RULE-CLIENTES-4.2:** Nome do INFO file segue pattern configurável em `settings.json` → `info_file_patterns`.
- **RULE-CLIENTES-4.3:** Pastas ocultas (nome iniciado por `.`) são ignoradas em varreduras.
- **RULE-CLIENTES-4.4:** Conformance Checker: auditar se todos os clientes/serviços seguem o pattern configurado. Pode criar INFO files faltantes via auto-fix.

### 3.5 Segurança
- **RULE-CLIENTES-5.1:** Path traversal sanitizado com `Path(nome).name` em todas as operações de arquivo.
- **RULE-CLIENTES-5.2:** Nomes de cliente/serviço são sanitizados antes de usar como nomes de pasta.

## 4. Relações
- ADRs relacionados: `ADR002_PascalCaseNaming` (PascalCase em nomes)
- Port: `client_repository_port.py` (interface abstrata)
- Adapter: `excel_client_repository.py` (implementação Excel)
- MCP tools: `listar_clientes`, `cadastrar_cliente`, `ler_ficha_cliente`, `atualizar_ficha_cliente`, `listar_servicos_cliente`, `criar_estrutura_servico`, `verificar_conformidade_clientes`, `corrigir_conformidade`, `preencher_codigos_faltantes`, `validar_codigos_servicos`, `corrigir_codigos_servicos`
