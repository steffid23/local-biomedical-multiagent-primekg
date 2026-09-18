# How to Use the Local Biomedical Multi-Agent System

Welcome to your **Local Biomedical AI Agent System**! This guide explains how to run the project, ask questions, and interpret the biological data returned by the system in simple terms.

---

##  1. How to Launch the Interactive Chat

### Option A: If using WSL / Linux Bash Terminal (e.g. `root@Steffi`)
Run these 2 commands in your terminal:
```bash
cd "/mnt/c/Users/Steffi Dominic/.gemini/antigravity/scratch/local_biomedical_multiagent"
python3 chat.py
```

### Option B: If using Windows PowerShell
Run these 2 commands in PowerShell:
```powershell
cd "C:\Users\Steffi Dominic\.gemini\antigravity\scratch\local_biomedical_multiagent"
py -3 chat.py
```

---

##  2. How to Ask Questions

Once `chat.py` starts, you will see a prompt like this:
```text
Biomedical Agent > 
```

You can type any natural-language question about **genes, diseases, drugs, side effects, pathways, or clinical symptoms**.

### Example Questions to Copy & Paste:

1. **Disease & Gene Questions** (CTD Data):
   - `What genes are associated with Alzheimer disease?`
   - `What genes are associated with Diabetes?`

2. **Drug Side-Effect Questions** (SIDER Data):
   - `What side effects are associated with pharmaceutical drugs?`

3. **Clinical Phenotype Questions** (HPO Data):
   - `Show clinical phenotypes for diseases in the Human Phenotype Ontology.`

4. **Database Structure Inspection**:
   - Type `schema` to see table column names.

5. **To Exit**:
   - Type `exit` or `quit`.

---

##  3. Simple Guide to Interpreting the Agent's Output

When you ask a question, the AI Agent will respond with a structured summary table like this:

| Source Entity | Relation | Target Entity | Data Provenance | Evidence / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `APP` | `associated_with_disease` | `MESH:D000544` | **CTD** | Alzheimer Disease |
| `CID100000085` | `causes_side_effect` | `PT` | **SIDER** | Abdominal pain |

### What Each Column Means:

- **Source Entity**: The starting biological item (e.g., Gene Symbol `APP` or Drug Identifier `CID100000085`).
- **Relation**: How the two entities are biologically connected:
  - `associated_with_disease`: Gene is linked to a disease.
  - `causes_side_effect`: Drug causes a side effect.
  - `has_phenotype`: Disease exhibits a clinical symptom.
- **Target Entity**: The ending biological item or medical code (e.g., `MESH:D000544` for Alzheimer's or MedDRA ID for a symptom).
- **Data Provenance**: Which official scientific dataset provided this fact:
  - **CTD**: Comparative Toxicogenomics Database (Curated gene-disease data).
  - **SIDER**: Side Effect Resource (Drug adverse effects).
  - **HPO**: Human Phenotype Ontology (Clinical symptoms).
  - **Reactome**: Biological pathways.
  - **GO**: Gene Ontology (Gene molecular functions).
- **Evidence / Notes**: Human-readable name of the disease, side effect, or symptom.

---

##  4. Quick Architecture Reference

- **100% Local & Offline**: All data is stored locally on your hard drive (`data/processed/biomedical.db`).
- **Low Disk Footprint**: Optimized to use **under 3.6 GB total storage**.
- **No Cloud Fees / No AWS Needed**: Runs completely on local Python and local database tools with zero external API calls.
