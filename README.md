# LAMP System

Sistema de automação e gestão para arquitetura, focado em organização de clientes, serviços e geração de documentos (Propostas e Contratos).

## 🏛️ Arquitetura

O projeto segue uma **Arquitetura Híbrida de Monólito Modular com Hexagonal (Ports and Adapters)**.
Para entender profundamente os conceitos, estrutura e diretrizes de desenvolvimento, leia a **[Documentação de Arquitetura](docs/concepts.md)**.

### Estrutura Resumida
*   `foton_system/modules`: Módulos de negócio (Clients, Documents, Shared).
*   `foton_system/interfaces`: Pontos de entrada (CLI).
*   `foton_system/scripts`: Scripts utilitários.

## 🚀 Como Executar

### Pré-requisitos
*   Python 3.10+
*   Dependências listadas em `requirements.txt`

### Instalação
1.  Clone o repositório.
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Execução
Para iniciar o sistema, execute o arquivo bat na raiz:
```bash
run_lamp.bat
```
Ou via terminal:
```bash
python foton_system/main.py
```

## 🛠️ Desenvolvimento

### Adicionando Novas Funcionalidades
Siga o fluxo da arquitetura:
1.  Defina a Interface (Porta) em `application/ports`.
2.  Implemente a Lógica de Negócio em `application/use_cases`.
3.  Implemente o Adaptador em `infrastructure`.
4.  Conecte tudo no `interfaces/cli/menus.py`.

## 📦 Deploy

O sistema possui uma branch dedicada `deploy` para versões estáveis.
Para gerar um executável:
```bash
pyinstaller --onefile --name foton_system foton_system/main.py
```

---
Desenvolvido por Mundoaec.com
