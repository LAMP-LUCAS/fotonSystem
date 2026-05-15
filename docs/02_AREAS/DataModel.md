---
type: concept
domain: core
status: active
tags: [datamodel, schema, database]
---
# Modelo de Dados & Centros de Verdade (DataModel)

Este documento define o modelo de dados para o [**FOTON System**](../../README.md), mapeando a Base de Dados Central (`baseDados.xlsx`) para os Centros de Verdade Distribuídos (arquivos `INFO-*.md`) e as variáveis de geração de documentos.

## Visão Geral

O sistema utiliza uma **Arquitetura de Dados Híbrida**:

1.  **Base de Dados Central (`baseDados.xlsx`):** O sistema de registro para dados estruturados, usado para listagem, filtragem e relatórios.
2.  **Centros de Verdade (`INFO-*.md`):** Arquivos mestres distribuídos localizados nas pastas de Clientes e Serviços. Estes são a **fonte primária** para a geração de documentos.

## 1. Clientes (`baseClientes` <-> `INFO-CLIENTE.md`)

> [!DIDACTIC:DADOS] Cadastro Flexível: Campos como `@cidadeProposta` não existem no Excel por padrão, mas você pode adicioná-los livremente ao `INFO-CLIENTE.md`. O Foton os encontrará e usará nos seus templates!

| Variável / Coluna | Descrição | Fonte |
| :--- | :--- | :--- |
| `@nomeCliente` | Nome completo do cliente | DB & Arquivo |
| `@cpfCnpjCliente` | CPF ou CNPJ | DB & Arquivo |
| `@enderecoCliente` | Endereço completo | DB & Arquivo |
| `@telefoneCliente` | Número de telefone | DB & Arquivo |
| `@emailCliente` | Endereço de e-mail | DB & Arquivo |
| `@estadoCivilCliente` | Estado civil | DB & Arquivo |
| `@empregoCliente` | Profissão | DB & Arquivo |
| `@cidadeProposta` | Cidade/Região para a proposta | Arquivo (Extra) |
| `@localProposta` | Endereço específico do local | Arquivo (Extra) |
| `@geolocalizacaoProposta` | Coordenadas Lat/Long | Arquivo (Extra) |

### Especificidades de Contrato

> [!DIDACTIC:DADOS] Sobrescrita de Segurança: Use `@nomeClienteContrato` se precisar que o contrato saia no nome de um representante legal, mantendo o cadastro principal no nome do cliente real.

Estas variáveis permitem sobrescrever os dados do cliente especificamente para contratos (ex: se o assinante for diferente).

* `@nomeClienteContrato`
* `@cpfCnpjClienteContrato`
* `@enderecoClienteContrato`
* `@telefoneClienteContrato`
* `@emailClienteContrato`

## 2. Serviços (`baseServicos` <-> `INFO-SERVICO.md`)

> [!DIDACTIC:PRODUTIVIDADE] Nomes de Pastas: O `@Alias` é o nome da pasta do serviço. Mantenha nomes curtos e sem espaços (ex: `Reforma_Apto_502`) para facilitar a navegação no terminal.

| Variável / Coluna | Descrição | Fonte |
| :--- | :--- | :--- |
| `@CodServico` | Código Único do Serviço | DB (Chave) |
| `@Alias` | Alias do Serviço (Nome da Pasta) | DB (Chave) |
| `@modalidadeServico` | Tipo (Projeto, Consultoria, etc.) | DB & Arquivo |
| `@anoProjeto` | Ano de Execução | DB & Arquivo |
| `@demandaProposta` | Descrição específica da demanda | DB & Arquivo |
| `@areaTotal` | Área total do terreno (m²) | DB & Arquivo |
| `@areaCoberta` | Área coberta (m²) | DB & Arquivo |
| `@areaDescoberta` | Área descoberta (m²) | DB & Arquivo |
| `@detalhesProposta` | Descrição detalhada do objetivo | DB & Arquivo |
| `@estiloProjeto` | Estilo arquitetônico | Arquivo (Extra) |
| `@ambientesProjeto` | Lista de ambientes planejados | Arquivo (Extra) |
| `@valorProposta` | Valor inicial da proposta | DB & Arquivo |
| `@valorContrato` | Valor final do contrato | DB & Arquivo |

### Datas (Marcos)

> [!DIDACTIC:DADOS] Formatação de Datas: Datas preenchidas como `2026-05-12` serão convertidas para o formato brasileiro `12/05/2026` nos documentos.

* `@inProposta`: Início da Proposta
* `@lvProposta`: Levantamento de Viabilidade
* `@anProposta`: Análise da Proposta
* `@baProposta`: Conclusão da Viabilidade
* `@prProposta`: Aprovação Preliminar
* `@inSolucao`: Início da Solução

### Estimativas de Custo (Calculadas/Manuais)

> [!DIDACTIC:FINANCEIRO] Cálculos Automáticos: Você pode usar fórmulas como `[calculo: @areaTotal * @execcub]` diretamente nos arquivos INFO. O Foton resolverá a conta para você no momento da geração!

Estas são tipicamente definidas no arquivo `INFO-SERVICO.md` ou calculadas durante a geração.

* `@projArqEng`: Custo de Arquitetura/Engenharia
* `@procLegais`: Custo de Processos Legais
* `@ACEqv`: Área de Construção Equivalente
* `@execcub`: Custo de Execução CUB
* `@execInfra`, `@execPais`, `@execMob`: Custos de Infraestrutura, Paisagismo, Mobiliário
* `@totalGeral`: Total Geral

## 3. Fluxo de Geração de Documentos

Ao gerar um documento (ex: Proposta), o sistema:

1.  **Localiza o Contexto:** Encontra as pastas pai de Cliente e Serviço.
2.  **Carrega a Verdade do Cliente:** Lê `INFO-CLIENTE.md`.
3.  **Carrega a Verdade do Serviço:** Lê `INFO-SERVICO.md` (sobrescreve dados do Cliente se houver colisões).
4.  **Carrega Dados do Documento:** Lê o arquivo `.md` específico do documento (sobrescreve todos).
5.  **Gera:** Substitui as variáveis no template `.docx` ou `.pptx`.

---
## 🔗 Links Relacionados
- Índice: [[Index]]
- Pipelines: [[Pipelines]]
- Guia do Usuário: [[UserGuide]]

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
