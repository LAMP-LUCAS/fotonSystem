# Conceitos e Diretrizes Arquiteturais - FOTON System

Este documento descreve a arquitetura, conceitos e padrões adotados no desenvolvimento do projeto [**FOTON System**](../README.md). Ele serve como guia para desenvolvedores de todos os níveis (Junior a Senior) entenderem a estrutura e a lógica por trás do código.

## 1. Visão Geral da Arquitetura

O sistema utiliza uma **Arquitetura Híbrida de Monólito Modular com Hexagonal (Ports and Adapters)**.

### O que isso significa?

* **Monólito Modular:** O código roda como uma única aplicação (um único processo Python), mas é organizado internamente em "módulos" independentes (ex: `clients`, `documents`). Isso facilita a organização e evita o "código espaguete", permitindo que no futuro, se necessário, um módulo seja extraído para um microsserviço.
* **Arquitetura Hexagonal (Ports and Adapters):** Dentro de cada módulo, separamos a lógica de negócio (o que o sistema *faz*) da infraestrutura (como o sistema *fala* com o mundo externo - banco de dados, arquivos, APIs).

### Benefícios

* **Testabilidade:** Podemos testar a lógica de negócio sem precisar de arquivos reais ou banco de dados.
* **Manutenibilidade:** Mudar de Excel para SQL, por exemplo, afeta apenas uma pequena parte do código (o Adaptador), sem quebrar as regras de negócio.
* **Organização:** Cada coisa tem seu lugar certo.

---

## 2. Estrutura de Diretórios

A estrutura do projeto reflete diretamente esses conceitos:

```
foton_system/
├── modules/                 # Onde vivem os módulos de negócio
│   ├── clients/             # Módulo de Gestão de Clientes
│   │   ├── application/     # Camada de Aplicação (Casos de Uso)
│   │   │   ├── ports/       # Interfaces (Contratos)
│   │   │   └── use_cases/   # Lógica de Negócio (Orquestração)
│   │   ├── infrastructure/  # Camada de Infraestrutura (Implementação Real)
│   │   │   └── repositories/# Acesso a Dados (ex: Excel)
│   │   └── domain/          # Entidades e Regras de Domínio Puras
│   │
│   ├── documents/           # Módulo de Gestão de Documentos
│   │   ├── application/
│   │   └── infrastructure/
│   │
│   └── shared/              # Código compartilhado entre módulos
│       └── infrastructure/  # Configurações, Logger, Utils
│
├── interfaces/              # Pontos de Entrada do Sistema
│   └── cli/                 # Interface de Linha de Comando (Menus)
│
├── scripts/                 # Scripts utilitários (ex: análise, correções)
└── assets/                  # Arquivos estáticos (ícones, imagens)
```

---

## 3. Conceitos Detalhados

### 3.1. Módulos (`modules/`)

Cada pasta dentro de `modules` deve ser tratada como um "mini-projeto". Um módulo não deve acessar diretamente o banco de dados de outro módulo, nem importar classes de infraestrutura de outro módulo. A comunicação ideal é via **Interfaces (Portas)** ou Serviços de Aplicação.

### 3.2. Camada de Aplicação (`application/`)

Aqui residem os **Casos de Uso** (`use_cases`). Eles representam as ações que o usuário pode realizar no sistema.

* **Exemplo:** `ClientService` (em `clients/application/use_cases`).
* **Responsabilidade:** Orquestrar o fluxo. "Receba dados, valide, chame o repositório para salvar, envie notificação".
* **Regra de Ouro:** Casos de uso **NÃO** sabem *como* os dados são salvos. Eles apenas chamam uma interface (`Port`).

### 3.3. Portas (`ports/`)

São **Interfaces** (classes abstratas em Python herdando de `ABC`). Elas definem um "contrato".

* **Exemplo:** `ClientRepositoryPort`. Define que *deve* existir um método `save_clients(df)`, mas não diz *como* salvar.
* **Por que usar?** Para que o Caso de Uso não dependa do Excel. Ele depende apenas da promessa de que alguém vai salvar os dados.

### 3.4. Infraestrutura (`infrastructure/`)

Aqui está o código "sujo", que lida com o mundo real.

* **Adaptadores:** Implementam as Portas.
  * **Exemplo:** `ExcelClientRepository` implementa `ClientRepositoryPort`. Ele sabe abrir o arquivo Excel, ler o pandas DataFrame e salvar.
* **Configuração:** Onde lemos variáveis de ambiente, caminhos de arquivos, etc.

### 3.5. Injeção de Dependência (DI)

É a técnica usada para conectar tudo. Em vez de o `ClientService` criar um `new ExcelClientRepository()` dentro dele (o que criaria um acoplamento forte), ele recebe o repositório como parâmetro no seu construtor (`__init__`).

**Onde isso acontece?**
No ponto de entrada da aplicação (`interfaces/cli/menus.py`).

```python
# Exemplo de "Wiring" (Conexão)
repo = ExcelClientRepository()          # Cria a peça de infraestrutura
service = ClientService(repo)           # Entrega a peça para o caso de uso
```

---

## 4. Diretrizes de Desenvolvimento

### Introdução

1. **Onde criar uma nova funcionalidade?** Identifique o módulo (ex: Clientes). Crie um método no `Service` (Caso de Uso). Se precisar salvar dados, adicione o método na Interface (`Port`) e implemente no Repositório (`Infrastructure`).
2. **Não coloque lógica no Menu:** O arquivo `menus.py` deve apenas coletar input do usuário e chamar o `Service`.
3. **Use o Logger:** Nunca use `print()` para erros ou logs do sistema. Use `logger.info()` ou `logger.error()`.

### Regras de Arquitetura

1. **Respeite as Fronteiras:** Não importe `infrastructure` dentro de `domain` ou `application`.
2. **Mantenha o Domínio Puro:** Entidades de domínio não devem ter dependências externas.
3. **Refatoração:** Se um módulo crescer demais, considere quebrá-lo em sub-módulos ou novos módulos.

---

## 5. Fluxo de Execução (Exemplo: Criar Cliente)

1. **Usuário** seleciona "Criar Cliente" no Menu (`interfaces/cli`).
2. **Menu** coleta os dados (input).
3. **Menu** chama `client_service.create_client(dados)`.
4. **ClientService** aplica regras de negócio (ex: gera código automático).
5. **ClientService** chama `self.repository.save_clients()`.
6. **ExcelClientRepository** (implementação injetada) abre o Excel e salva a linha.

---

## 6. Deploy e Distribuição

O sistema é distribuído via executável compilado (PyInstaller) ou código fonte conforme detalhado em [`docs/deployment_guide.md`](deployment_guide.md) .

* **Branch de Deploy:** Contém a versão estável pronta para produção.
* **Atualização:** O sistema pode ser atualizado baixando a nova versão da branch de deploy.

---

**Dúvidas?** Consulte o Tech Lead ou revise a documentação oficial do Python e Clean Architecture.

---

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
