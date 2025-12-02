# System Pipelines

This document visualizes the core workflows and data pipelines of the LAMP system using flowcharts.

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
flowchart LR
    subgraph Context [Centers of Truth]
        L1[Level 1: Client Truth]
        L2[Level 2: Service Truth]
        L3[Level 3: Document Data]
    end

    subgraph Process [Generation Process]
        Start(Start) --> LoadL1[Load INFO-CLIENTE.md]
        LoadL1 --> LoadL2[Load INFO-SERVICO.md]
        LoadL2 --> LoadL3[Load Document.md]
        LoadL3 --> Merge[Merge Data]
        Merge --> Resolve[Resolve Calculations]
        Resolve --> Validate[Validate Template Keys]
        Validate --> Generate[Generate DOCX/PPTX]
    end

    subgraph Output
        Doc[Final Document]
        Log[History Log]
    end

    L1 -- @nomeCliente... --> Merge
    L2 -- @areaTotal... --> Merge
    L3 -- @valorProposta... --> Merge
    
    note[Merge Priority: L3 > L2 > L1]
    Merge -.-> note

    Generate --> Doc
    Generate --> Log
```
