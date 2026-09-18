# Biomedical Analytics Dashboard Documentation

> **Module**: `app.py` (Streamlit Biomedical Analytics Dashboard)  
> **Backend Integration**: Direct connection to `src.agents.orchestrator.LocalBiomedicalOrchestrator`  
> **Design Theme**: Professional Dark Scientific Theme | ZERO Emojis | Real Database Metrics

---

## 1. Dashboard Overview & Features

The redesigned dashboard provides a presentation-ready analytics interface for precision medicine researchers and mentors:

1. **Header Section**:
   - Title: `Local Biomedical Multi-Agent System`
   - Subtitle: `Precision Medicine Knowledge Graph | PrimeKG | Local Biomedical Intelligence`
   - Live Badges: `System Online` | `Local / Offline` | `Database Connected` (dynamically verified).

2. **Sidebar Navigation & System Panels**:
   - **Views**: `Dashboard Overview`, `Ask Biomedical Question`, `Database Explorer`.
   - **Datasets List**: CTD, Reactome, HPO, SIDER, GO.
   - **System Status**: Local deployment, MySQL/SQLite engine, read-only security, $0 cloud cost.

3. **Knowledge Graph Overview (KPI Stat Cards)**:
   - Dynamic non-zero record counts queried live from `biomedical.db` / MySQL:
     * **Biomedical Entities**: Total node count
     * **Gene Entities**: Entrez / UniProt IDs
     * **Disease Entities**: MONDO / OMIM / MESH Codes
     * **Drug Entities**: STITCH / PubChem IDs
     * **Biological Pathways**: Reactome Models
     * **Phenotypes & Symptoms**: HPO & MedDRA Terms
     * **Knowledge Graph Edges**: Total relationship triples (150,000+)

4. **Interactive Question Interface**:
   - Conversational AI markdown answer.
   - Visual relationship cards (`Source Entity -> Relationship -> Target Entity`).
   - Real-time Streamlit charts of relationship distributions generated strictly from backend query rows.
   - Interactive dataframe preview with full dataset expander.
   - 1-click `Download Results as CSV` button.

5. **Database Explorer**:
   - Interactive tabs for CTD, Reactome, HPO, SIDER, and GO displaying real schemas, record counts, and sample records.

6. **Technical Audit**:
   - Expandable technical metadata: SQL query executed, tables accessed, execution status, database engine.

---

## 2. Verified Test Scenarios

The dashboard has been verified across 5 test query cases:

| Query Focus | Example Question | Backend Rows | Provenance | UI Components Verified |
| :--- | :--- | :---: | :---: | :--- |
| **1. Alzheimer Genes** | *"What genes are associated with Alzheimer's disease?"* | 20 Real Rows | **CTD** | Stat cards, text answer, triple cards, bar chart, dataframe, CSV button |
| **2. Aspirin Side Effects**| *"What are the side effects of Aspirin?"* | 20 Real Rows | **SIDER** | Drug-side effect triples, MedDRA terms, dataframe, CSV button |
| **3. Alzheimer Phenotypes**| *"What phenotypes are associated with Alzheimer's disease?"* | 20 Real Rows | **HPO** | HPO disease symptom mappings, visual cards, dataframe |
| **4. TP53 Pathways** | *"Which pathways involve TP53?"* | 20 Real Rows | **Reactome** | Reactome pathway models, species distribution chart |
| **5. BRCA1 Diseases** | *"What diseases are associated with BRCA1?"* | 20 Real Rows | **CTD** | BRCA1 gene-disease associations, dataframe |

---

## 3. How to Launch the Web Dashboard Locally

```bash
streamlit run app.py
```
*(or `py -3.13 -m streamlit run app.py`)*

Open your browser to `http://localhost:8501`.
