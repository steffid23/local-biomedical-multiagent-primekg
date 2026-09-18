# Database Ingestion Summary (Phase 9)

> **Generated On**: 2026-09-17 21:50:36  
> **Target Databases**: Local SQLite (`data/processed/biomedical.db`) and MySQL DDL (`data/processed/init_biomedical_db.sql`).

---

## Entity and Relationship Counts

| Table Name | Record Count | Primary Identifier / Description |
| :--- | :---: | :--- |
| **genes** | `65` | Entrez ID & Gene Symbol |
| **diseases** | `4,770` | MONDO / OMIM / MESH Disease Codes & Names |
| **drugs** | `1,430` | STITCH Compound Identifiers & Names |
| **pathways** | `23,603` | Reactome Pathway Identifiers & Names |
| **phenotypes** | `6,114` | HPO & MedDRA Phenotype Codes |
| **biomedical_relationships** | `150,000` | Integrated Knowledge Graph Triples |

---

## Database Files Created

- **Local Zero-Setup SQLite Database**: `data/processed/biomedical.db` (37.96 MB)
- **MySQL DDL Script**: `data/processed/init_biomedical_db.sql`
