# Foton System 🚀

**Foton** é o sistema de gestão integrado desenvolvido para o escritório **LAMP Arquitetura**. Ele centraliza a gestão de clientes, serviços e a geração automatizada de documentos (Propostas e Contratos), garantindo padronização e eficiência.

## 📋 Funcionalidades Principais

*   **Gestão de Clientes e Serviços**: Sincronização automática entre a estrutura de pastas do Windows e a base de dados do sistema.
*   **Geração de Documentos**:
    *   **Propostas (PPTX)**: Substituição inteligente de textos em apresentações PowerPoint.
    *   **Contratos (DOCX)**: Geração de contratos robustos com validação de dados, cálculos automáticos e proteção de e-mails.
*   **Produtividade**: Timer Pomodoro integrado para gestão de tempo.

## 🛠️ Instalação

### Pré-requisitos
*   Python 3.10 ou superior instalado.
*   Acesso às pastas do OneDrive da LAMP Arquitetura.

### Passo a Passo
1.  **Clone ou Baixe** este repositório para sua máquina (ex: `C:\Users\Lucas\OneDrive\LAMP_ARQUITETURA\ADM\lamp`).
2.  Abra o terminal na pasta do projeto.
3.  Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuração

O sistema já vem pré-configurado, mas você pode ajustar os caminhos principais no arquivo:
`foton_system/config/settings.json`

```json
{
    "base_clientes": "C:/Users/Lucas/OneDrive/LAMP_ARQUITETURA/CLIENTES",
    "templates_path": "C:/Users/Lucas/OneDrive/LAMP_ARQUITETURA/ADM/KIT DOC",
    "ignored_folders": ["00-MODELOS", "99-ARQUIVO MORT"]
}
```
*Certifique-se de que os caminhos apontam corretamente para as pastas do seu OneDrive.*

## 🚀 Como Usar

### Execução Rápida
Basta dar um **duplo clique** no arquivo:
`run_lamp.bat`

### Execução via Terminal
```bash
python foton_system/main.py
```

### Guia dos Menus

#### 1. Gerenciar Clientes
*   **Sincronizar**: Lê as pastas criadas no Windows e atualiza o sistema, ou cria pastas para clientes novos cadastrados no sistema.
*   **Listar**: Mostra todos os clientes ativos.

#### 2. Gerenciar Serviços
*   Similar aos clientes, mas focado nas subpastas de projetos/obras.

#### 3. Documentos (O "Coração" do Foton)
*   **Gerar Proposta/Contrato**:
    1.  O sistema abrirá uma janela para você selecionar a **Pasta do Cliente**.
    2.  Ele buscará um arquivo de dados (ex: `02-COD...PROPOSTA.txt`). Se não existir, ele oferecerá criar um novo.
    3.  **Importante**: Preencha o arquivo `.txt` com os dados do cliente (Nome, CPF, Valores).
    4.  Escolha o **Template** (Modelo de Contrato ou Proposta).
    5.  O sistema validará os dados e gerará o arquivo final na pasta do cliente.

#### 4. Produtividade
*   Inicia um timer Pomodoro (25min foco / 5min pausa) para ajudar na concentração.

## 📝 Estrutura do Arquivo de Dados (.txt)

Para que os documentos sejam gerados corretamente, o arquivo `.txt` na pasta do cliente deve seguir este padrão:

```text
@nomeCliente;Fulano de Tal
@CpfCnpj;000.000.000-00
@arqlamp;seuemail@arqlamp.com
@valorProposta;15000,00
...
```
*   **Dica**: O sistema avisa se alguma chave obrigatória estiver faltando antes de gerar o documento.

---
**Foton System** - *Iluminando a gestão da LAMP Arquitetura.*
