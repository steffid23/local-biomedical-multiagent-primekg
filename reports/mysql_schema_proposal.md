# MySQL Database Schema Proposal for PrimeKG Biomedical Multi-Agent System

> **Document Purpose**: Design a normalized, efficient, space-optimized MySQL relational schema for storing and querying integrated PrimeKG biomedical entity and relationship datasets.  
> **Target Database Engine**: Local MySQL 8.0+ / MariaDB 10.5+ (InnoDB Engine, UTF8MB4 charset).

---

## Data Source Schema Analysis

Based on the downloaded biomedical datasets, the table below summarizes the source data structures, key identifiers, entity types, and approximate row counts.

| Data Source | Primary Entities | Key Identifiers | Schema / Key Columns | Approx. Rows | Integration Target Table |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **CTD** | Gene, Disease | Entrez Gene ID, MESH/OMIM ID | `GeneSymbol`, `GeneID`, `DiseaseName`, `DiseaseID`, `DirectEvidence`, `InferenceScore` | ~6,000,000 | `genes`, `diseases`, `gene_disease_relationships` |
| **Reactome** | Pathway, Species | Reactome ID (R-HSA-...) | `PathwayID`, `PathwayName`, `Species` | ~2,500 | `pathways` |
| **HPO** | Phenotype, Disease | HPO ID (HP:000...), OMIM ID | `database_id`, `disease_name`, `hpo_id`, `evidence` | ~250,000 | `phenotypes`, `diseases`, `disease_phenotype_relationships` |
| **SIDER** | Drug, Side Effect | STITCH ID (CID...), MedDRA ID | `stitch_compound_id`, `meddra_concept_type`, `meddra_concept_id`, `side_effect_name` | ~300,000 | `drugs`, `phenotypes`, `drug_side_effects` |
| **SIDER Names**| Drug | STITCH CID | `stitch_compound_id`, `drug_name` | ~14,000 | `drugs` |
| **GO** | Gene, Function | UniProtKB ID, GO ID (GO:000...) | `DB_Object_ID`, `DB_Object_Symbol`, `GO_ID`, `Aspect`, `Evidence` | ~600,000 | `genes`, `gene_ontology_annotations` |
| **PrimeKG Core**| Multi-entity | MeSH, NCBIGene, MONDO, DrugBank | `x_type`, `x_id`, `x_name`, `relation`, `y_type`, `y_id`, `y_name` | Integrated Graph | `biomedical_relationships` |

---

## Relational MySQL Database Architecture

```text
+----------------------+         +----------------------------------+         +----------------------+
|        GENES         |         |     BIOMEDICAL_RELATIONSHIPS     |         |       DISEASES       |
+----------------------+         +----------------------------------+         +----------------------+
| gene_id (PK)         |<------->| relationship_id (PK)             |<------->| disease_id (PK)      |
| entrez_gene_id       |         | source_entity_type               |         | mondo_id             |
| symbol               |         | source_id                        |         | omim_id              |
| name                 |         | relationship_type                |         | mesh_id              |
| species              |         | target_entity_type               |         | name                 |
+----------------------+         | target_id                        |         | category             |
                                 | data_source                      |         +----------------------+
+----------------------+         | confidence_score                 |
|        DRUGS         |         +----------------------------------+         +----------------------+
+----------------------+                          ^                           |       PATHWAYS       |
| drug_id (PK)         |<-------------------------+-------------------------->+----------------------+
| stitch_id            |                          |                           | pathway_id (PK)      |
| drugbank_id          |                          v                           | reactome_id          |
| name                 |         +----------------------------------+         | name                 |
| pubchem_cid          |         |            PHENOTYPES            |         | species              |
+----------------------+         +----------------------------------+         +----------------------+
                                 | phenotype_id (PK)                |
                                 | hpo_id                           |
                                 | meddra_id                        |
                                 | name                             |
                                 +----------------------------------+
```

---

## Proposed MySQL Table Definitions (DDL)

```sql
-- Create Database
CREATE DATABASE IF NOT EXISTS biomedical_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biomedical_db;

-- 1. Data Provenance Sources Table
CREATE TABLE IF NOT EXISTS data_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL UNIQUE,
    official_url VARCHAR(255),
    license VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Master Genes Table
CREATE TABLE IF NOT EXISTS genes (
    gene_id INT AUTO_INCREMENT PRIMARY KEY,
    entrez_id VARCHAR(50) UNIQUE,
    symbol VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    uniprot_id VARCHAR(50),
    species VARCHAR(50) DEFAULT 'Homo sapiens',
    INDEX idx_gene_symbol (symbol),
    INDEX idx_entrez_id (entrez_id),
    INDEX idx_uniprot_id (uniprot_id)
) ENGINE=InnoDB;

-- 3. Master Diseases Table
CREATE TABLE IF NOT EXISTS diseases (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    mondo_id VARCHAR(50),
    omim_id VARCHAR(50),
    mesh_id VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    INDEX idx_disease_name (name),
    INDEX idx_mondo_id (mondo_id),
    INDEX idx_omim_id (omim_id)
) ENGINE=InnoDB;

-- 4. Master Drugs Table
CREATE TABLE IF NOT EXISTS drugs (
    drug_id INT AUTO_INCREMENT PRIMARY KEY,
    stitch_id VARCHAR(50) UNIQUE,
    drugbank_id VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    pubchem_cid VARCHAR(50),
    INDEX idx_drug_name (name),
    INDEX idx_stitch_id (stitch_id),
    INDEX idx_drugbank_id (drugbank_id)
) ENGINE=InnoDB;

-- 5. Master Pathways Table
CREATE TABLE IF NOT EXISTS pathways (
    pathway_id INT AUTO_INCREMENT PRIMARY KEY,
    reactome_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    species VARCHAR(100) DEFAULT 'Homo sapiens',
    INDEX idx_reactome_id (reactome_id),
    INDEX idx_pathway_name (name)
) ENGINE=InnoDB;

-- 6. Master Phenotypes & Side Effects Table
CREATE TABLE IF NOT EXISTS phenotypes (
    phenotype_id INT AUTO_INCREMENT PRIMARY KEY,
    hpo_id VARCHAR(50),
    meddra_id VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    INDEX idx_hpo_id (hpo_id),
    INDEX idx_meddra_id (meddra_id),
    INDEX idx_phenotype_name (name)
) ENGINE=InnoDB;

-- 7. Integrated Biomedical Relationships Table (Core PrimeKG Graph Structure)
CREATE TABLE IF NOT EXISTS biomedical_relationships (
    relationship_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_entity VARCHAR(50) NOT NULL,      -- e.g., 'gene', 'disease', 'drug'
    source_id VARCHAR(100) NOT NULL,        -- Original identifier (Entrez, MONDO, STITCH)
    relationship_type VARCHAR(100) NOT NULL,  -- e.g., 'associated_with', 'causes_side_effect', 'participates_in'
    target_entity VARCHAR(50) NOT NULL,      -- e.g., 'disease', 'phenotype', 'pathway'
    target_id VARCHAR(100) NOT NULL,        -- Original identifier
    data_source VARCHAR(100) NOT NULL,       -- e.g., 'CTD', 'SIDER', 'Reactome', 'HPO', 'GO'
    confidence_score FLOAT DEFAULT NULL,
    evidence_text TEXT DEFAULT NULL,
    INDEX idx_source (source_entity, source_id),
    INDEX idx_target (target_entity, target_id),
    INDEX idx_rel_type (relationship_type),
    INDEX idx_data_src (data_source),
    INDEX idx_composite_rel (source_id, relationship_type, target_id)
) ENGINE=InnoDB;
```

---

## Space-Efficiency & Query Performance Optimization

1. **Space Minimization**:
   - Use `VARCHAR` length limits appropriate to standard biomedical identifiers.
   - Use `BIGINT` for relationship IDs while keeping entity tables indexed with standard `INT`.
2. **Indexing Strategy**:
   - Composite indexes on `(source_id, relationship_type, target_id)` enable sub-millisecond graph traversal queries by LLM agents.
3. **Provenance Preservation**:
   - Every relationship retains `source_entity`, `source_id`, `relationship_type`, `target_entity`, `target_id`, and `data_source` so provenance is 100% traceable to original datasets.
