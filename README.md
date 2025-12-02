# FOTON System 💡

> **Transforme o Caos de Arquivos em uma Máquina de Gestão.**
> Pare de perder tempo procurando onde salvou aquele contrato ou qual é a versão final da proposta. O FOTON System organiza, sincroniza e automatiza seu escritório de arquitetura.

---

## 🦸 Como o FOTON salva o seu dia

### O Caos

Você é um arquiteto talentoso. Seus projetos são incríveis, mas seu "backoffice" é uma bagunça. Você tem uma planilha Excel para controlar clientes, mas ela nunca bate com as pastas do computador. Você gera contratos copiando e colando do Word, e vira e mexe esquece de mudar o CPF do cliente anterior.

### O Problema

Um dia, você precisa gerar 5 propostas urgentes. Você abre a pasta do cliente "João", mas não acha os dados dele. Abre o Excel, e lá diz que o cliente é "João Silva", mas a pasta está como "J. Silva". Você corrige na mão. Ao gerar o contrato, você percebe que o valor estava errado porque copiou de um modelo antigo. **Frustração total.**

### A Solução

Você instala o FOTON.

1. **Sincronização Mágica**: Com um clique, o FOTON lê suas pastas e arruma seu Excel. "J. Silva" e "João Silva" viram a mesma pessoa.
2. **Centros de Verdade**: O FOTON cria um arquivo `INFO-CLIENTE.md` dentro da pasta do João. Agora, os dados moram onde o projeto mora.
3. **Automação**: Para gerar as 5 propostas, você só digita o valor. O FOTON puxa o nome, endereço e CPF do João automaticamente e gera o PDF. Sem erro de digitação. Sem "Salvar Como".

### O Retorno a Produtividade

Você gastou 10 minutos no que levaria 2 horas. Seus arquivos estão organizados, seus contratos estão seguros e você tem tempo para o que importa: **Projetar.**

---

## 🚀 O Que o FOTON Faz Por Você?

### 1. Gestão de Clientes e Serviços (O Fim do "Onde Salvei?")

* **Sincronização Bidirecional**: O que está na pasta vai para o Excel, e vice-versa.
* **Banco de Dados Distribuído**: Seus dados vivem nas pastas, em arquivos de texto simples (`INFO-*.md`). Leves, seguros e fáceis de editar.

### 2. Geração de Documentos (Adeus, Ctrl+C Ctrl+V)

* **Context-Aware**: O sistema sabe quem é o cliente pela pasta onde você está.
* **Templates Inteligentes**: Use seus modelos de Word e PowerPoint. O sistema preenche as lacunas (`@nome`, `@valor`) para você.

### 3. Modo Avançado (Ferramentas Administrativas)

* **Refatoração de Dados**: Mudou o nome de uma variável? O sistema atualiza todos os seus arquivos de uma vez.
* **Diagnóstico**: Um "Check-up" completo para garantir que nenhuma pasta está perdida ou sem dono.

---

## 📚 Documentação

* **[Guia do Usuário](docs/UserGuide.md)**: O manual completo de operação.
* **[Conceitos de Arquitetura](docs/concepts.md)**: Para os devs e curiosos (Arquitetura Hexagonal).
* **[Pipelines do Sistema](docs/Pipelines.md)**: Entenda o fluxo dos dados.

---

## 🛠️ Instalação Rápida

1. **Pré-requisitos**: Python 3.10+ instalado.
2. **Instalar Dependências**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Rodar**:

    ```bash
    python foton_system/interfaces/cli/main.py
    ```

    *Ou use o launcher unificado `FOTON.py` para ferramentas administrativas.*

---

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
