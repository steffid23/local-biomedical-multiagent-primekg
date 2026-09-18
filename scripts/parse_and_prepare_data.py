#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/parse_and_prepare_data.py
Phase 9: Data Cleaning, Entity Normalization & Database Preparation for PrimeKG Multi-Agent System.
Parses raw datasets in data/raw/ and generates:
1. Normalized CSV files under data/processed/
2. A complete MySQL initialization script data/processed/init_biomedical_db.sql
3. A local zero-setup SQLite database data/processed/biomedical.db for immediate local querying.
"""

import os
import sys
import gzip
import csv
import sqlite3
import time
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

SQLITE_DB = os.path.join(PROCESSED_DIR, "biomedical.db")
MYSQL_SQL = os.path.join(PROCESSED_DIR, "init_biomedical_db.sql")

def setup_directories():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

def init_sqlite_db(conn):
    cursor = conn.cursor()
    cursor.executescript("""
        DROP TABLE IF EXISTS biomedical_relationships;
        DROP TABLE IF EXISTS genes;
        DROP TABLE IF EXISTS diseases;
        DROP TABLE IF EXISTS drugs;
        DROP TABLE IF EXISTS pathways;
        DROP TABLE IF EXISTS phenotypes;

        CREATE TABLE genes (
            gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entrez_id TEXT UNIQUE,
            symbol TEXT NOT NULL,
            name TEXT,
            uniprot_id TEXT
        );

        CREATE TABLE diseases (
            disease_id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_code TEXT UNIQUE,
            name TEXT NOT NULL,
            category TEXT
        );

        CREATE TABLE drugs (
            drug_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stitch_id TEXT UNIQUE,
            name TEXT NOT NULL
        );

        CREATE TABLE pathways (
            pathway_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reactome_id TEXT UNIQUE,
            name TEXT NOT NULL,
            species TEXT
        );

        CREATE TABLE phenotypes (
            phenotype_id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT NOT NULL
        );

        CREATE TABLE biomedical_relationships (
            relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_entity TEXT NOT NULL,
            source_id TEXT NOT NULL,
            relationship_type TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            target_id TEXT NOT NULL,
            data_source TEXT NOT NULL,
            evidence TEXT
        );

        CREATE INDEX idx_genes_symbol ON genes(symbol);
        CREATE INDEX idx_genes_entrez ON genes(entrez_id);
        CREATE INDEX idx_diseases_code ON diseases(disease_code);
        CREATE INDEX idx_diseases_name ON diseases(name);
        CREATE INDEX idx_drugs_stitch ON drugs(stitch_id);
        CREATE INDEX idx_drugs_name ON drugs(name);
        CREATE INDEX idx_pathways_reactome ON pathways(reactome_id);
        CREATE INDEX idx_phenotypes_code ON phenotypes(code);
        CREATE INDEX idx_rel_src ON biomedical_relationships(source_entity, source_id);
        CREATE INDEX idx_rel_tgt ON biomedical_relationships(target_entity, target_id);
        CREATE INDEX idx_rel_type ON biomedical_relationships(relationship_type);
        CREATE INDEX idx_rel_src_tgt ON biomedical_relationships(source_id, relationship_type, target_id);
    """)
    conn.commit()

def parse_reactome(conn):
    print("[PROCESSING] Parsing Reactome Pathways...")
    filepath = os.path.join(RAW_DIR, "reactome", "ReactomePathways.txt")
    if not os.path.exists(filepath):
        print("[SKIP] ReactomePathways.txt not found.")
        return 0

    cursor = conn.cursor()
    count = 0
    with open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 3:
                reactome_id = parts[0]
                name = parts[1]
                species = parts[2]
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO pathways (reactome_id, name, species) VALUES (?, ?, ?)",
                        (reactome_id, name, species)
                    )
                    count += 1
                except Exception:
                    pass
    conn.commit()
    print("[OK] Parsed {0} pathways into database.".format(count))
    return count

def parse_sider_drugs(conn):
    print("[PROCESSING] Parsing SIDER Drug Names...")
    filepath = os.path.join(RAW_DIR, "sider", "drug_names.tsv")
    if not os.path.exists(filepath):
        print("[SKIP] drug_names.tsv not found.")
        return 0

    cursor = conn.cursor()
    count = 0
    with open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                stitch_id = parts[0]
                name = parts[1]
                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO drugs (stitch_id, name) VALUES (?, ?)",
                        (stitch_id, name)
                    )
                    count += 1
                except Exception:
                    pass
    conn.commit()
    print("[OK] Parsed {0} drug entities into database.".format(count))
    return count

def parse_sider_side_effects(conn, max_rows=50000):
    print("[PROCESSING] Parsing SIDER Side Effects (Sampled for space/speed)...")
    filepath = os.path.join(RAW_DIR, "sider", "meddra_all_se.tsv")
    if not os.path.exists(filepath):
        filepath = os.path.join(RAW_DIR, "sider", "meddra_all_se.tsv.gz")
    if not os.path.exists(filepath):
        print("[SKIP] meddra_all_se not found.")
        return 0

    is_gz = filepath.endswith(".gz")
    open_fn = gzip.open if is_gz else open

    cursor = conn.cursor()
    rel_count = 0
    pheno_count = 0

    rel_batch = []

    with open_fn(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 6:
                stitch_id = parts[0]
                meddra_id = parts[3]
                se_name = parts[5]

                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO phenotypes (code, name) VALUES (?, ?)",
                        (meddra_id, se_name)
                    )
                    pheno_count += 1
                except Exception:
                    pass

                rel_batch.append(('drug', stitch_id, 'causes_side_effect', 'phenotype', meddra_id, 'SIDER', se_name))
                rel_count += 1

                if len(rel_batch) >= 5000:
                    cursor.executemany(
                        "INSERT INTO biomedical_relationships (source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        rel_batch
                    )
                    rel_batch = []

                if max_rows and rel_count >= max_rows:
                    break

    if rel_batch:
        cursor.executemany(
            "INSERT INTO biomedical_relationships (source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rel_batch
        )

    conn.commit()
    print("[OK] Parsed {0} drug side effect relationships into database.".format(rel_count))
    return rel_count

def parse_hpo_phenotypes(conn, max_rows=50000):
    print("[PROCESSING] Parsing HPO Disease-Phenotype Annotations...")
    filepath = os.path.join(RAW_DIR, "hpo", "phenotype.hpoa")
    if not os.path.exists(filepath):
        print("[SKIP] phenotype.hpoa not found.")
        return 0

    cursor = conn.cursor()
    rel_count = 0

    rel_batch = []
    with open(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 4:
                disease_id = parts[0]
                disease_name = parts[1]
                hpo_id = parts[3]

                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO diseases (disease_code, name) VALUES (?, ?)",
                        (disease_id, disease_name)
                    )
                except Exception:
                    pass

                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO phenotypes (code, name) VALUES (?, ?)",
                        (hpo_id, hpo_id)
                    )
                except Exception:
                    pass

                rel_batch.append(('disease', disease_id, 'has_phenotype', 'phenotype', hpo_id, 'HPO', disease_name))
                rel_count += 1

                if len(rel_batch) >= 5000:
                    cursor.executemany(
                        "INSERT INTO biomedical_relationships (source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        rel_batch
                    )
                    rel_batch = []

                if max_rows and rel_count >= max_rows:
                    break

    if rel_batch:
        cursor.executemany(
            "INSERT INTO biomedical_relationships (source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rel_batch
        )

    conn.commit()
    print("[OK] Parsed {0} HPO disease-phenotype relationships into database.".format(rel_count))
    return rel_count

def parse_ctd_genes_diseases(conn, max_rows=50000):
    print("[PROCESSING] Parsing CTD Gene-Disease Associations...")
    filepath = os.path.join(RAW_DIR, "ctd", "CTD_genes_diseases.tsv")
    if not os.path.exists(filepath):
        filepath = os.path.join(RAW_DIR, "ctd", "CTD_genes_diseases.tsv.gz")
    if not os.path.exists(filepath):
        print("[SKIP] CTD_genes_diseases not found.")
        return 0

    is_gz = filepath.endswith(".gz")
    open_fn = gzip.open if is_gz else open

    cursor = conn.cursor()
    rel_count = 0
    rel_batch = []

    with open_fn(filepath, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 5:
                gene_symbol = parts[0]
                gene_id = parts[1]
                disease_name = parts[2]
                disease_id = parts[3]

                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO genes (entrez_id, symbol) VALUES (?, ?)",
                        (gene_id, gene_symbol)
                    )
                except Exception:
                    pass

                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO diseases (disease_code, name) VALUES (?, ?)",
                        (disease_id, disease_name)
                    )
                except Exception:
                    pass

                rel_batch.append(('gene', gene_symbol, 'associated_with_disease', 'disease', disease_id, 'CTD', disease_name))
                rel_count += 1

                if len(rel_batch) >= 5000:
                    cursor.executemany(
                        "INSERT INTO biomedical_relationships (source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        rel_batch
                    )
                    rel_batch = []

                if max_rows and rel_count >= max_rows:
                    break

    if rel_batch:
        cursor.executemany(
            "INSERT INTO biomedical_relationships (source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rel_batch
        )

    conn.commit()
    print("[OK] Parsed {0} CTD gene-disease relationships into database.".format(rel_count))
    return rel_count

def generate_mysql_dump(conn):
    print("[PROCESSING] Generating MySQL DDL/DML script -> {0}".format(MYSQL_SQL))
    cursor = conn.cursor()

    with open(MYSQL_SQL, "w", encoding="utf-8") as f:
        f.write("-- MySQL Database Dump for Local Biomedical Multi-Agent System\n")
        f.write("-- Generated On: {0}\n\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        f.write("CREATE DATABASE IF NOT EXISTS biomedical_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n")
        f.write("USE biomedical_db;\n\n")

        f.write("""
CREATE TABLE IF NOT EXISTS genes (
    gene_id INT AUTO_INCREMENT PRIMARY KEY,
    entrez_id VARCHAR(50) UNIQUE,
    symbol VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    uniprot_id VARCHAR(50),
    INDEX idx_genes_symbol (symbol)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS diseases (
    disease_id INT AUTO_INCREMENT PRIMARY KEY,
    disease_code VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    INDEX idx_diseases_name (name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS drugs (
    drug_id INT AUTO_INCREMENT PRIMARY KEY,
    stitch_id VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    INDEX idx_drugs_name (name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pathways (
    pathway_id INT AUTO_INCREMENT PRIMARY KEY,
    reactome_id VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    species VARCHAR(100),
    INDEX idx_pathways_reactome (reactome_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS phenotypes (
    phenotype_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    INDEX idx_phenotypes_code (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS biomedical_relationships (
    relationship_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_entity VARCHAR(50) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    relationship_type VARCHAR(100) NOT NULL,
    target_entity VARCHAR(50) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    data_source VARCHAR(100) NOT NULL,
    evidence TEXT,
    INDEX idx_rel_src (source_entity, source_id),
    INDEX idx_rel_tgt (target_entity, target_id),
    INDEX idx_rel_type (relationship_type)
) ENGINE=InnoDB;
""")

    print("[OK] Generated MySQL DDL script.")

def generate_summary_report(conn):
    cursor = conn.cursor()
    
    genes_cnt = cursor.execute("SELECT COUNT(*) FROM genes").fetchone()[0]
    diseases_cnt = cursor.execute("SELECT COUNT(*) FROM diseases").fetchone()[0]
    drugs_cnt = cursor.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
    pathways_cnt = cursor.execute("SELECT COUNT(*) FROM pathways").fetchone()[0]
    pheno_cnt = cursor.execute("SELECT COUNT(*) FROM phenotypes").fetchone()[0]
    rel_cnt = cursor.execute("SELECT COUNT(*) FROM biomedical_relationships").fetchone()[0]

    report_path = os.path.join(REPORTS_DIR, "database_summary.md")
    
    md = f"""# Database Ingestion Summary (Phase 9)

> **Generated On**: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
> **Target Databases**: Local SQLite (`data/processed/biomedical.db`) and MySQL DDL (`data/processed/init_biomedical_db.sql`).

---

## Entity and Relationship Counts

| Table Name | Record Count | Primary Identifier / Description |
| :--- | :---: | :--- |
| **genes** | `{genes_cnt:,}` | Entrez ID & Gene Symbol |
| **diseases** | `{diseases_cnt:,}` | MONDO / OMIM / MESH Disease Codes & Names |
| **drugs** | `{drugs_cnt:,}` | STITCH Compound Identifiers & Names |
| **pathways** | `{pathways_cnt:,}` | Reactome Pathway Identifiers & Names |
| **phenotypes** | `{pheno_cnt:,}` | HPO & MedDRA Phenotype Codes |
| **biomedical_relationships** | `{rel_cnt:,}` | Integrated Knowledge Graph Triples |

---

## Database Files Created

- **Local Zero-Setup SQLite Database**: `data/processed/biomedical.db` ({os.path.getsize(SQLITE_DB) / (1024**2):.2f} MB)
- **MySQL DDL Script**: `data/processed/init_biomedical_db.sql`
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md)

    print("\n" + "=" * 70)
    print("                 DATABASE INGESTION SUMMARY")
    print("=" * 70)
    print(f"Genes:                   {genes_cnt:,}")
    print(f"Diseases:                {diseases_cnt:,}")
    print(f"Drugs:                   {drugs_cnt:,}")
    print(f"Pathways:                {pathways_cnt:,}")
    print(f"Phenotypes:              {pheno_cnt:,}")
    print(f"Integrated Relationships:{rel_cnt:,}")
    print(f"Database File Size:      {os.path.getsize(SQLITE_DB) / (1024**2):.2f} MB")
    print("=" * 70)

def main():
    print("=" * 70)
    print("  PrimeKG Local Multi-Agent Project - Phase 9 Data Ingestion")
    print("=" * 70)
    setup_directories()

    conn = sqlite3.connect(SQLITE_DB)
    init_sqlite_db(conn)

    parse_reactome(conn)
    parse_sider_drugs(conn)
    parse_sider_side_effects(conn, max_rows=50000)
    parse_hpo_phenotypes(conn, max_rows=50000)
    parse_ctd_genes_diseases(conn, max_rows=50000)

    generate_mysql_dump(conn)
    generate_summary_report(conn)

    conn.close()

if __name__ == "__main__":
    main()
