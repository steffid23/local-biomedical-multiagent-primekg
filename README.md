# Local Biomedical Multi-Agent System (PrimeKG Data)

[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-Streamlit-ff4b4b.svg)](https://streamlit.io/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20MySQL-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AWS Free](https://img.shields.io/badge/AWS-0%25%20Cloud%20Dependencies-red.svg)]()

> A **100% local, offline-capable biomedical multi-agent system and analytics dashboard** designed for precision medicine research. Integrates primary biomedical knowledge datasets from **PrimeKG** into a relational data warehouse and uses specialized AI agents for natural-language-to-SQL translation, evidence retrieval, and biomarker analysis.

---

## Implementation Examples & Dashboard Screenshots

The application provides a presentation-ready biomedical analytics interface displaying live database metrics, multi-agent AI answers, visual relationship triples, dynamic charts, and CSV data exports:

### 1. Dashboard Overview & Knowledge Graph Statistics
![Dashboard Overview](reports/assets/01_dashboard_overview.png)
> **Description**: The main landing page showing verified live status badges (`System Online`, `Local / Offline`, `Database Connected`) and real KPI stat cards queried live from the local relational database (**35,982 Biomedical Entities**, **65 Genes**, **4,770 Diseases**, **1,430 Drugs**, **23,603 Pathways**, **6,114 Phenotypes**, and **150,000 Knowledge Graph Edges**).

---

### 2. Analytical Results & Multi-Agent Execution Summary
![Analytical Results & Evidence](reports/assets/02_analytical_results.png)
> **Description**: Displays the analytical response view for a user query (*"What genes are associated with Alzheimer disease?"*), highlighting execution status metrics (**20 Records Returned**, **CTD Data Provenance**, **SUCCESS Status**, **SQLite / MySQL Engine**), the executed backend SQL query, and structured biomarker evidence tables.

---

### 3. Knowledge Graph Relationship Triples & Provenance Audit
![Knowledge Graph Relationships](reports/assets/03_relationship_triples.png)
> **Description**: Demonstrates multi-agent relationship extraction displaying visual triple cards (`Source Entity -> Relationship -> Target Entity`), CTD data provenance tracking, and architectural safety audit metadata.

---

### 4. Data Visualizations, Dataframe Table & CSV Export
![Data Visualization & Dataframe](reports/assets/04_visualization_dataframe.png)
> **Description**: Shows the dynamic analytics view, bar charts of record distributions by data source and relationship type generated strictly from retrieved backend rows, an interactive Streamlit dataframe table, and a 1-click **Download Results as CSV** button.

---

## Key Features

- **Professional Web Dashboard & Analytics UI (`app.py`)**: Presentation-ready dark theme interface featuring dynamic KPI stat cards, interactive query execution, visual relationship triples, analytical data charts, and 1-click CSV exports.
- **Zero Emojis**: Clean, formal scientific presentation suitable for demonstrations to research mentors and biomedical informatics teams.
- **100% Local & Offline Execution**: Zero cloud API fees, no AWS credentials required. Runs entirely on local Python and local relational databases (SQLite / MySQL).
- **Space-Optimized Storage**: Stores **over 150,000 biomedical relationships in under 3.7 GB total disk space**.
- **Multi-Agent Architecture**: Inspired by AWS's Cancer Biomarker Discovery design pattern, refactored with 0% cloud dependencies:
  - **Supervisor Orchestrator**: Intent routing and multi-turn session management.
  - **Database Analyst Agent**: Schema introspection & safe Text-to-SQL query generation.
  - **Biomarker Specialist Agent**: Provenance tracking & biological evidence synthesis.
- **Safe Read-Only Querying**: Parameterized execution that strictly prevents data mutation (`INSERT`, `UPDATE`, `DELETE`, `DROP` forbidden).

---

## System Architecture

```mermaid
sequenceDiagram
    autonumber
    actor User as Researcher / User
    participant Dashboard as Web Dashboard (app.py)
    participant Orchestrator as Local Orchestrator Agent
    participant DBAgent as Local DB Analyst Agent
    participant PyTools as Local DB Tool (db_tool.py)
    participant Warehouse as Local Database (SQLite/MySQL)

    User->>Dashboard: Ask Question (e.g. "What genes are associated with Alzheimer's disease?")
    Dashboard->>Orchestrator: handle_user_question_structured(query)
    Orchestrator->>DBAgent: Delegate SQL Query Generation
    DBAgent->>PyTools: Execute Safe Read-Only SELECT Query
    PyTools->>Warehouse: Query Index-Optimized Relational Tables
    Warehouse-->>PyTools: Return Entity Rows
    PyTools-->>DBAgent: Return Formatted JSON Results
    DBAgent-->>Orchestrator: Synthesize Findings with Data Provenance
    Orchestrator-->>Dashboard: Return Structured Payload (Text + Raw Rows)
    Dashboard-->>User: Display AI Response, Relationship Cards, Charts & CSV Export
```

---

## Integrated Data Sources

Data derived from primary constituent resources of **PrimeKG** (Precision Medicine Knowledge Graph):

| Resource | Primary Entities | Relationship Type | Size on Disk | Records | Provenance |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **CTD** | Genes, Diseases | `associated_with_disease` | 3,065.71 MB | 4,041,411 | Public Domain |
| **Reactome** | Pathways, Species | `pathway_mapping` | 1.52 MB | 23,603 | CC0 |
| **HPO** | Diseases, Phenotypes | `has_phenotype` | 34.16 MB | 286,652 | CC BY 4.0 |
| **SIDER** | Drugs, Side Effects | `causes_side_effect` | 2.27 MB | 309,849 | CC BY-NC 4.0 |
| **SIDER Names**| Drugs | `drug_name_mapping` | 0.03 MB | 1,430 | CC BY-NC 4.0 |
| **Gene Ontology**| Genes, Functions | `has_go_function` | 14.35 MB | 906,445 | CC BY 4.0 |

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Local Web Dashboard UI
Launch the interactive Streamlit web dashboard:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

### 3. Launch Interactive Command-Line Interface (CLI)
Alternatively, run the command-line chat script:
```bash
python3 chat.py
```

---

## Project Structure

```text
local-biomedical-multiagent-primekg/
├── app.py                    # Streamlit Biomedical Analytics Dashboard & UI
├── chat.py                   # Interactive user chat CLI
├── HOW_TO_USE.md             # Easy user guide & output interpretation
├── requirements.txt          # Python dependencies (including Streamlit)
├── scripts/
│   ├── download_datasets.py  # Streaming dataset downloader & inventory generator
│   └── parse_and_prepare_data.py # Data ETL & SQLite/MySQL database ingestion
├── src/
│   ├── agents/
│   │   ├── orchestrator.py   # Master supervisor orchestrator (text & structured APIs)
│   │   ├── db_agent.py       # Database Analyst agent (Text-to-SQL)
│   │   └── biomarker_agent.py# Biomarker Specialist agent
│   └── tools/
│       └── db_tool.py        # Safe read-only database query tool with stats API
├── reports/
│   ├── assets/               # Implementation UI screenshots
│   │   ├── 01_dashboard_overview.png
│   │   ├── 02_analytical_results.png
│   │   ├── 03_relationship_triples.png
│   │   └── 04_visualization_dataframe.png
│   ├── data_inventory.md     # Downloaded dataset metrics report
│   ├── biomarker_scripts_analysis.md # AWS code analysis & local mapping
│   ├── mysql_schema_proposal.md     # Relational database schema design DDL
│   └── ui_documentation.md          # Web dashboard architecture & test report
└── data/
    ├── raw/                  # Downloaded raw TSV/GZ datasets
    └── processed/            # MySQL initialization DDL (init_biomedical_db.sql)
```

---

## License & Attribution

- Built as a **Local Biomedical AI System** using constituent datasets from [PrimeKG](https://github.com/mims-harvard/PrimeKG).
- Multi-agent workflow inspired by [AWS Healthcare & Life Sciences Samples](https://github.com/aws-samples/amazon-bedrock-agents-healthcare-lifesciences).
- Released under the [MIT License](LICENSE).
