# System Pipelines

This document visualizes the core workflows and data pipelines of the FOTON System using flowcharts.

## 1. Client & Service Synchronization

This pipeline ensures consistency between the Central Database (`baseDados.xlsx`) and the File System (Folders).

```mermaid
flowchart TD
    subgraph DB_Central [Central Database]
        XLSX[baseDados.xlsx]
    end

    subgraph FS [File System]
        CF[Client Folders]
        SF[Service Folders]
    end

    %% Sync Base [Folders -> DB]
    subgraph Sync_Base [Sync Base Folders -> DB]
        direction TB
        SB_Start(Start) --> SB_ReadFS[Read Folder Structure]
        SB_ReadFS --> SB_UpdateDB[Update Excel Rows]
        SB_UpdateDB --> SB_End(End)
    end

    %% Sync Folders [DB -> Folders]
    subgraph Sync_Folders [Sync Folders DB -> Folders]
        direction TB
        SF_Start(Start) --> SF_ReadDB[Read Excel Data]
        SF_ReadDB --> SF_Check[Check if Folder Exists]
        SF_Check -- No --> SF_Create[Create Folder]
        SF_Check -- Yes --> SF_Skip[Skip]
        SF_Create --> SF_End(End)
        SF_Skip --> SF_End
    end

    FS --> SB_ReadFS
    SB_UpdateDB --> XLSX
    XLSX --> SF_ReadDB
    SF_Create --> FS
```

## 2. Distributed Database (Centers of Truth)

This pipeline manages the bi-directional synchronization between the Central Database and the Distributed "Truth Files" (`INFO-*.md`) located in client/service folders.

```mermaid
flowchart TD
    subgraph DB [Central Database]
        DB_Rows[Client/Service Rows]
    end

    subgraph Files [Distributed Files]
        InfoClient[INFO-CLIENTE.md]
        InfoService[INFO-SERVICO.md]
    end

    %% Export [DB -> Files]
    subgraph Export [Export DB -> Files]
        direction TB
        Exp_Start(Start) --> Exp_ReadDB[Read DB Row]
        Exp_ReadDB --> Exp_CheckFile[Check Existing INFO File]
        Exp_CheckFile -- Found --> Exp_Merge[Merge DB Data + Existing Extras]
        Exp_CheckFile -- Not Found --> Exp_New[Create New Data]
        Exp_Merge --> Exp_Diff{Has Changes?}
        Exp_Diff -- Yes --> Exp_IncRev[Increment Revision Rxx]
        Exp_Diff -- No --> Exp_Skip[Skip Write]
        Exp_New --> Exp_Write[Write .md File]
        Exp_IncRev --> Exp_Write
    end

    %% Import [Files -> DB]
    subgraph Import [Import Files -> DB]
        direction TB
        Imp_Start(Start) --> Imp_ReadFiles[Read INFO-*.md Files]
        Imp_ReadFiles --> Imp_Compare[Compare with DB]
        Imp_Compare --> Imp_Diff{Different?}
        Imp_Diff -- Yes --> Imp_Append[Append New Row to DB]
        Imp_Diff -- No --> Imp_Skip2[Skip]
        Imp_Append --> Imp_End(End)
    end

    DB_Rows --> Exp_ReadDB
    Exp_Write --> Files
    Files --> Imp_ReadFiles
    Imp_Append --> DB_Rows
```

## 3. Document Generation (Context-Aware)

This pipeline generates documents (Proposals, Contracts) by aggregating data from multiple levels of the hierarchy ("Centers of Truth").

```mermaid
flowchart TD
    subgraph Inputs [Data Sources]
        L1[INFO-CLIENTE.md]
        L2[INFO-SERVICO.md]
        L3[Document Data .md]
        TPL[Template .docx/.pptx]
    end

    subgraph Engine [Context-Aware Engine]
        Load[Load & Parse Files]
        
        subgraph Merging [Context Merging Strategy]
            direction TB
            P1[Base: Client Data]
            P2[Override: Service Data]
            P3[Override: Document Data]
            P1 --> P2 --> P3
        end
        
        Math[Math Resolver]
        Val[Validate vs Template]
        Render[Render Document]
    end

    subgraph Outputs
        File[Final Document]
        Log[Audit Log]
    end

    L1 --> Load
    L2 --> Load
    L3 --> Load
    TPL --> Val
    TPL --> Render

    Load --> P1
    P3 --> Math
    Math --> |Resolved Context| Val
    Val --> |Validated Context| Render
    
    Render --> File
    Render --> Log

    style Merging fill:#155,stroke:#333,stroke-width:2px
    style Math fill:#002,stroke:#333,stroke-width:2px
```

## 4. Administrative Tools Pipelines

These pipelines support system maintenance, data integrity, and schema evolution.

### 4.1. Schema Management (Variable Evolution)

This pipeline handles the discovery, definition, and synchronization of system variables.

```mermaid
flowchart TD
    subgraph Discovery
        Excel[Excel Columns]
        Info[Info File Keys]
        Schema[schema.json]
    end

    subgraph Manager [Schema Manager]
        Analyze[Analyze Variables]
        Report[Generate Report]
        Edit[Edit/Rename/Merge]
        Sync[Sync System]
    end

    subgraph Storage
        DB[baseDados.xlsx]
        Files[INFO-*.md]
    end

    Excel --> Analyze
    Info --> Analyze
    Schema <--> Analyze
    
    Analyze --> Report
    Analyze --> Edit
    Edit --> Schema
    
    Sync --> |Create Columns| DB
    Sync --> |Append Keys| Files
```

### 4.2. System Diagnosis (Health Check)

This pipeline performs a deep scan of the system to identify inconsistencies.

```mermaid
flowchart TD
    Start(Start Debug) --> CheckFiles[Check Critical Files]
    CheckFiles --> LoadDB[Load Excel Data]
    LoadDB --> ScanFS[Scan Folders]
    
    ScanFS --> CheckRel{Check Relations}
    CheckRel -- Orphan Service --> LogError[Log Error]
    CheckRel -- Missing Folder --> LogError
    
    ScanFS --> CheckInfo[Check INFO Files]
    CheckInfo -- Missing Keys --> LogWarn[Log Warning]
    CheckInfo -- Data Mismatch --> LogWarn
    
    LogError --> Report[Generate Report]
    LogWarn --> Report
    Report --> Save[Save to reports/]
```

### 4.3. Batch Correction (Fixer)

This pipeline automates the repair of distributed data files based on the defined schema.

```mermaid
flowchart 
    Input[Schema / Template] --> Fixer[Batch Fixer]
    Fixer --> Scan[Scan Client Folders]
    Scan --> Read[Read INFO File]
    Read --> Check{Missing Keys?}
    Check -- Yes --> Append[Append Keys]
    Check -- No --> Skip[Skip]
    Append --> Save[Save File]
```

---

**Desenvolvido para Arquitetos que querem projetar, não gerenciar arquivos.** Veja mais em [Mundo AEC](https://www.mundoaec.com)
