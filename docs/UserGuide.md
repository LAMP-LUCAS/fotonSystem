# Guia do Usuário - FOTON System

Bem-vindo ao manual completo do [**FOTON System**](../README.md). Este guia vai te ensinar a dominar todas as ferramentas do sistema, desde a gestão básica de clientes até as funcionalidades avançadas de administração.

---

## Índice

1. [Introdução e Acesso](#1-introdução-e-acesso)
2. [Gestão de Clientes e Serviços](#2-gestão-de-clientes-e-serviços)
3. [Geração de Documentos (Propostas e Contratos)](#3-geração-de-documentos)
4. [Produtividade (Pomodoro)](#4-produtividade)
5. [Ferramentas Administrativas (Modo Deus)](#5-ferramentas-administrativas)
6. [Dicas e Truques](#6-dicas-e-truques)

---

## 1. Introdução e Acesso

O FOTON System é acessado via terminal. Para iniciar, execute o script principal:

```powershell
python foton_system/interfaces/cli/main.py
```

Você verá o **Menu Principal**:

1. **Gerenciar Clientes**: Cadastro e organização.
2. **Gerenciar Serviços**: Projetos e obras vinculados a clientes.
3. **Documentos**: Geração automática de propostas e contratos.
4. **Produtividade**: Timer Pomodoro.
5. **Configurações**: Ajustes do sistema e Ferramentas Admin.

---

## 2. Gestão de Clientes e Serviços

O coração do sistema é a sincronização entre suas **Pastas** (Windows) e o **Banco de Dados** (Excel).

### Sincronização

* **Pastas -> DB**: O sistema lê suas pastas e atualiza o Excel. Use isso quando criar uma pasta manualmente.
* **DB -> Pastas**: O sistema cria pastas para clientes cadastrados no Excel. Use isso após cadastrar em massa no Excel.

### Centros de Verdade (INFO Files)

Cada pasta de cliente e serviço deve ter um arquivo "Mestre" com os dados.

* **Exportar (DB -> Arquivo)**: Cria/Atualiza o arquivo `INFO-CLIENTE.md` na pasta com os dados do Excel.
* **Importar (Arquivo -> DB)**: Lê o arquivo `INFO` e atualiza o Excel. Ideal se você prefere editar dados no Bloco de Notas/VS Code.

---

## 3. Geração de Documentos

Esqueça o "Salvar Como" e o "Localizar e Substituir".

### Passo a Passo

1. Vá em **Documentos** > **Gerar Proposta** (PPTX) ou **Contrato** (DOCX).
2. Selecione a pasta do Cliente.
3. O sistema listará os arquivos de dados (`.md`) disponíveis.
    * *Dica: Se não houver nenhum, crie um "Novo Arquivo".*
4. **Preencha apenas o necessário**: No arquivo `.md` do documento, coloque apenas os dados daquela proposta (ex: `@valorProposta`).
    * *Mágica:* O sistema puxa Nome, Endereço, CPF, etc., automaticamente dos arquivos `INFO-CLIENTE` e `INFO-SERVICO`.
5. Selecione o Template e pronto! O arquivo é gerado na pasta.

---

## 4. Produtividade

Mantenha o foco com o Pomodoro integrado.

1. Vá em **Produtividade** > **Iniciar Pomodoro**.
2. (Opcional) Vincule a um Cliente/Serviço para gerar logs de horas (`timesheet`).
3. Configure o tempo (padrão 25min) e trabalhe.

---

## 5. Ferramentas Administrativas

Acesse via **Configurações** > **Ferramentas Administrativas**.

### 1. Correção em Lote (Info Files)

Adicionou um campo novo no Template? Use essa ferramenta para varrer **todas** as pastas e adicionar esse campo nos arquivos `INFO` existentes.

### 2. Diagnóstico do Sistema (Debug DB)

O sistema está estranho? Rode o diagnóstico. Ele verifica:

* Integridade do Excel.
* Pastas órfãs (sem dono).
* Arquivos `INFO` faltando chaves.
* Gera um relatório detalhado em `reports/`.

### 3. Gestão de Variáveis (Schema Manager)

O "Painel de Controle" dos seus dados.

* **Adicionar**: Cadastre novas variáveis no sistema.
* **Renomear**: Mudou de ideia? Renomeie `@obs` para `@observacoes` e o sistema atualiza o Schema, o Excel e **todos** os arquivos Markdown automaticamente.
* **Mesclar**: Junte duas variáveis em uma sem perder dados.
* **Sincronizar Sistema**: Garante que o Excel tenha todas as colunas do Schema.

---

## 6. Dicas e Truques

* **Edição Rápida**: Você pode editar os arquivos `INFO-*.md` diretamente pelo Windows Explorer. O sistema respeita suas mudanças.
* **Backup**: O sistema faz backup automático do Excel antes de operações críticas.
* **Navegação**: Use a opção "Voltar" para navegar entre menus sem fechar o programa.

---

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
