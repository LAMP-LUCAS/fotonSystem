# Data Model & Centers of Truth

This document defines the data model for the [**FOTON System**](../README.md), mapping the Central Database (`baseDados.xlsx`) to the Distributed Centers of Truth (`INFO-*.md` files) and the Document Generation variables.

## Overview

The system uses a **Hybrid Data Architecture**:

1. **Central Database (`baseDados.xlsx`)**: The system of record for structured data, used for listing, filtering, and reporting.
2. **Centers of Truth (`INFO-*.md`)**: Distributed master files located in Client and Service folders. These are the **primary source** for document generation.

## 1. Clients (`baseClientes` <-> `INFO-CLIENTE.md`)

| Variable / Column | Description | Source |
| :--- | :--- | :--- |
| `@nomeCliente` | Full name of the client | DB & File |
| `@cpfCnpjCliente` | CPF or CNPJ | DB & File |
| `@enderecoCliente` | Full address | DB & File |
| `@telefoneCliente` | Phone number | DB & File |
| `@emailCliente` | Email address | DB & File |
| `@estadoCivilCliente` | Marital status | DB & File |
| `@empregoCliente` | Profession | DB & File |
| `@cidadeProposta` | City/Region for the proposal | File (Extra) |
| `@localProposta` | Specific location address | File (Extra) |
| `@geolocalizacaoProposta` | Lat/Long coordinates | File (Extra) |

### Contract Specifics

These variables allow overriding client data specifically for contracts (e.g., if the signer is different).

* `@nomeClienteContrato`
* `@cpfCnpjClienteContrato`
* `@enderecoClienteContrato`
* `@telefoneClienteContrato`
* `@emailClienteContrato`

## 2. Services (`baseServicos` <-> `INFO-SERVICO.md`)

| Variable / Column | Description | Source |
| :--- | :--- | :--- |
| `@CodServico` | Unique Service Code | DB (Key) |
| `@Alias` | Service Alias (Folder Name) | DB (Key) |
| `@modalidadeServico` | Type (Project, Consulting, etc.) | DB & File |
| `@anoProjeto` | Execution Year | DB & File |
| `@demandaProposta` | Specific demand description | DB & File |
| `@areaTotal` | Total terrain area (m²) | DB & File |
| `@areaCoberta` | Covered area (m²) | DB & File |
| `@areaDescoberta` | Uncovered area (m²) | DB & File |
| `@detalhesProposta` | Detailed objective description | DB & File |
| `@estiloProjeto` | Architectural style | File (Extra) |
| `@ambientesProjeto` | List of planned environments | File (Extra) |
| `@valorProposta` | Initial proposal value | DB & File |
| `@valorContrato` | Final contract value | DB & File |

### Dates (Milestones)

* `@inProposta`: Start of Proposal
* `@lvProposta`: Viability Survey
* `@anProposta`: Proposal Analysis
* `@baProposta`: Viability Conclusion
* `@prProposta`: Preliminary Approval
* `@inSolucao`: Solution Start

### Cost Estimates (Calculated/Manual)

These are typically defined in the `INFO-SERVICO.md` file or calculated during generation.

* `@projArqEng`: Architecture/Engineering Cost
* `@procLegais`: Legal Processes Cost
* `@ACEqv`: Equivalent Construction Area
* `@execcub`: CUB Execution Cost
* `@execInfra`, `@execPais`, `@execMob`: Infrastructure, Landscaping, Furniture Costs
* `@totalGeral`: Grand Total

## 3. Document Generation Flow

When generating a document (e.g., Proposal), the system:

1. **Locates Context**: Finds the parent Client and Service folders.
2. **Loads Client Truth**: Reads `INFO-CLIENTE.md`.
3. **Loads Service Truth**: Reads `INFO-SERVICO.md` (overrides Client data if collisions exist).
4. **Loads Document Data**: Reads the specific `.md` file for the document (overrides all).
5. **Generates**: Replaces variables in the `.docx` or `.pptx` template.

---
**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
