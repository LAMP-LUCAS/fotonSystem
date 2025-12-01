# Plano de Masterização do Framework LAMP

Este documento detalha o plano de refinamento e evolução dos módulos existentes do sistema, visando robustez, segurança e melhor experiência do usuário antes da expansão para novos módulos.

## 1. Módulo de Clientes (`clients`) - "A Verdade Única"

O objetivo é tornar a gestão de clientes mais segura e ágil.

### 1.1. Validação Robusta
*   **Problema:** Nomes de clientes com caracteres inválidos podem quebrar a criação de pastas ou scripts.
*   **Solução:** Implementar validação rigorosa na entrada de dados (input).
*   **Ação:**
    *   Bloquear caracteres proibidos pelo Windows: `/ \ : * ? " < > |`.
    *   Sanitizar inputs automaticamente (ex: remover espaços extras).

### 1.2. Busca Rápida
*   **Problema:** Encontrar um cliente em uma lista grande é lento.
*   **Solução:** Adicionar funcionalidade de busca no menu CLI.
*   **Ação:**
    *   Criar opção "Buscar Cliente" no menu.
    *   Permitir filtro por trecho do Nome ou Alias.

## 2. Módulo de Documentos (`documents`) - "Zero Erros"

O objetivo é garantir que nenhum documento seja gerado com erros ou variáveis faltando.

### 2.1. Validador de Templates (Pré-voo)
*   **Problema:** O usuário gera um documento e só descobre depois que faltou uma variável (ex: `{{CPF}}`).
*   **Solução:** Analisar o template antes de gerar.
*   **Ação:**
    *   Criar função que escaneia o arquivo `.docx` ou `.pptx` em busca de padrões `{{...}}`.
    *   Comparar com as chaves disponíveis no arquivo de dados selecionado.
    *   Exibir alerta se houver discrepância: *"O template pede X, mas o arquivo de dados não tem."*

### 2.2. Limpeza de Variáveis
*   **Problema:** Variáveis não preenchidas ficam expostas no documento final (ex: `{{TELEFONE}}`).
*   **Solução:** Tratar variáveis não encontradas.
*   **Ação:**
    *   Adicionar configuração: "Limpar variáveis não encontradas?" (Sim/Não).
    *   Se Sim, substituir por vazio ou texto padrão (ex: "---").

### 2.3. Log de Geração
*   **Problema:** Falta de rastreabilidade sobre quais documentos foram gerados e quando.
*   **Solução:** Registrar histórico.
*   **Ação:**
    *   Criar/Atualizar arquivo `history.log` na raiz da pasta do cliente.
    *   Formato: `[DATA_HORA] Documento 'X' gerado usando Template 'Y' (Versão Dados: Z)`.

## 3. Módulo de Produtividade (`productivity`) - "Rastreabilidade"

Transformar o timer simples em uma ferramenta de gestão de tempo e custos.

### 3.1. Vínculo com um Serviço de um Cliente (Time Tracking)
*   **Problema:** O Pomodoro roda solto, sem saber para quem o trabalho está sendo feito.
*   **Solução:** Associar sessão a um serviço de um cliente.
*   **Ação:**
    *   Ao iniciar Pomodoro, perguntar (opcionalmente): "Selecionar Serviço?".
    *   Usar o menu de seleção de serviços existentes e uma opção de filtragem por clientes.

### 3.2. Relatório de Horas (Timesheet)
*   **Problema:** Não saber quanto tempo foi gasto em cada projeto.
*   **Solução:** Persistir os dados das sessões.
*   **Ação:**
    *   Salvar registros em um arquivo central `timesheet.csv` ou individual por cliente.
    *   Dados: `Data, Cliente, Duração (min), Tipo (Foco/Pausa)`.

### 3.3. Configuração Persistente
*   **Problema:** Ter que digitar 25/5/15 toda vez.
*   **Solução:** Salvar preferências.
*   **Ação:**
    *   Adicionar campos no `settings.json` para tempos padrão de Pomodoro.
    *   Ler esses padrões ao iniciar o timer.

## 4. Interface (`CLI`) - "Experiência Premium"

Melhorar a usabilidade e o visual do terminal.

### 4.1. Feedback Visual (Cores)
*   **Problema:** Texto monocromático dificulta distinção entre erro, sucesso e instrução.
*   **Solução:** Implementar código de cores.
*   **Ação:**
    *   Usar `colorama` ou códigos ANSI.
    *   Verde: Sucesso ("Arquivo salvo!").
    *   Amarelo: Aviso ("Variável não encontrada").
    *   Vermelho: Erro ("Arquivo não existe").
    *   Azul/Ciano: Menus e Perguntas.

### 4.2. Graceful Shutdown
*   **Problema:** `Ctrl+C` encerra o programa abruptamente, podendo corromper dados.
*   **Solução:** Capturar sinal de interrupção.
*   **Ação:**
    *   Envolver o loop principal em `try/except KeyboardInterrupt`.
    *   Salvar estados pendentes e exibir mensagem de saída amigável.
