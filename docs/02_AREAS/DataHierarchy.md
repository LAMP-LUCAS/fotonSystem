# 🪜 Hierarquia de Dados e SSOT (Single Source of Truth)

O FOTON System utiliza uma arquitetura de dados em camadas, inspirada no conceito de "Herança". Isso garante que você nunca precise repetir informações e que seus dados estejam sempre sincronizados.

## 🌀 O Fluxo de Resolução
Ao gerar um documento, o sistema busca o valor de cada variável (como `@nomeCliente` ou `@areaTotal`) seguindo esta ordem de prioridade:

### 1. Camada de Individualização (Arquivo Selecionado)
*   **Local:** O arquivo `.md` específico que você abriu para preencher (ex: `02-PROPOSTA_V2.md`).
*   **Uso:** Ideal para ajustes que só valem para este documento específico.
*   **Poder:** Sobrescreve todas as outras camadas.

### 2. Camada de Projeto (Pasta do Serviço)
*   **Local:** Arquivo `INFO-SERVICO.md` dentro da pasta do projeto.
*   **Uso:** Contém o "Cérebro do Projeto" (Áreas, Prazos, Custos Estimados).
*   **Poder:** Garante que todas as propostas de um mesmo projeto usem a mesma metragem.

### 3. Camada de Cliente (Pasta Raiz do Cliente)
*   **Local:** Arquivo `INFO-CLIENTE.md` na raiz da pasta do cliente.
*   **Uso:** Contém o "DNA do Cliente" (CPF, CNPJ, Endereço, E-mail, Profissão).
*   **Poder:** Você preenche uma vez e todos os serviços deste cliente herdam esses dados.

### 4. Camada de Sistema (Variáveis Automáticas)
*   **Local:** Gerado dinamicamente pelo núcleo do Foton.
*   **Exemplos:** `@DataAtual`, `@LinkCUB`, `@ReferenciaCUB`.

---

## 💡 Vantagens Práticas

1.  **Edição Única:** O cliente mudou de endereço? Altere apenas o `INFO-CLIENTE.md` e gere os documentos novamente. Tudo estará atualizado.
2.  **Sombreamento (Shadowing):** Precisa que em um contrato específico o nome do cliente apareça diferente? Basta adicionar a variável `@nomeCliente` no arquivo daquele contrato. O sistema usará o valor local e ignorará o global apenas para aquele caso.
3.  **Segurança de Cálculos:** Áreas e valores baseados em fórmulas (como `ACEqv` ou `CustoExecucao`) geralmente residem na **Camada de Projeto**, evitando divergências entre diferentes propostas.

---

## 🧬 O Template Mestre (DNA)
O arquivo `foton_system/assets/info-Template.md` serve como o mapa mestre. Ele define a estrutura que será copiada para as pastas de novos clientes e serviços, garantindo que o seu ecossistema de dados seja padronizado e escalável.
