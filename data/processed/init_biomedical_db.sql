-- MySQL Database Dump for Local Biomedical Multi-Agent System
-- Generated On: 2026-09-17 21:50:36

CREATE DATABASE IF NOT EXISTS biomedical_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biomedical_db;


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
