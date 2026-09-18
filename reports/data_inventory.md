# Biomedical Data Inventory (PrimeKG Local Multi-Agent Project)

> **Generated On**: 2026-09-17 15:45:47 UTC  
> **Storage Optimization Strategy**: Space-efficient selection of key PrimeKG constituent biomedical datasets.

---

## Data Download Summary

- **Total Sources Processed**: 7
- **Sources Successfully Downloaded**: 7
- **Total Files Stored**: 10
- **Total Downloaded (Compressed) Size**: `3118.03 MB` (`3.0450 GB`)
- **Total Extracted (Uncompressed) Size**: `551.19 MB` (`0.5383 GB`)
- **Total Data Directory Disk Usage**: `3669.22 MB` (`3.5832 GB`)

---

## Downloaded Biomedical Datasets

| Source | Dataset / File | Biological Information | Size (MB) | Size (GB) | Format | Status | Rows | Cols |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **CTD (Comparative Toxicogenomics Database)** | `CTD_genes_diseases.tsv.gz` | Curated gene-disease associations and toxicogenomics metadata | 3065.71 MB | 2.9939 GB | tsv.gz | SUCCESS | 4041411 | 9 |
| **Reactome Pathway Database** | `ReactomePathways.txt` | Biological pathway definitions, identifiers, and species mappings | 1.52 MB | 0.0015 GB | tsv/txt | SUCCESS | 23603 | 3 |
| **Human Phenotype Ontology (HPO)** | `phenotype.hpoa` | Standardized disease-to-phenotypic-feature clinical annotations | 34.16 MB | 0.0334 GB | hpoa/tsv | SUCCESS | 286652 | 12 |
| **SIDER (Side Effect Resource)** | `meddra_all_se.tsv.gz` | Drug-side effect associations mapped to MedDRA phenotypic concepts | 2.27 MB | 0.0022 GB | tsv.gz | SUCCESS | 309849 | 6 |
| **SIDER Drug Names** | `drug_names.tsv` | Drug concept identifiers (STITCH/PubChem) mapped to drug names | 0.03 MB | 0.0 GB | tsv | SUCCESS | 1430 | 2 |
| **Gene Ontology (GO)** | `goa_human.gaf.gz` | Human gene functional annotations (molecular function, cellular component, biological process) | 14.35 MB | 0.014 GB | gaf.gz | SUCCESS | 906445 | 17 |
| **PrimeKG Processing Logic** | `omim_tools.py` | PrimeKG entity construction and OMIM disease integration logic | 0.0 MB | 0.0 GB | py | SUCCESS | 42 | 1 |

---

## File Storage & Path Directory

```text
data/
└── raw/
    ├── ctd/
    │   ├── CTD_genes_diseases.tsv.gz
    │   └── CTD_genes_diseases.tsv
    ├── reactome/
    │   └── ReactomePathways.txt
    ├── hpo/
    │   └── phenotype.hpoa
    ├── sider/
    │   ├── meddra_all_se.tsv.gz
    │   ├── meddra_all_se.tsv
    │   └── drug_names.tsv
    ├── go/
    │   ├── goa_human.gaf.gz
    │   └── goa_human.gaf
    └── primekg/
        └── omim_tools.py
```

---

## Detailed Resource Provenance & Notes

### CTD (Comparative Toxicogenomics Database)
- **Official URL**: [https://ctdbase.org/](https://ctdbase.org/)
- **Download Link**: [https://ctdbase.org/reports/CTD_genes_diseases.tsv.gz](https://ctdbase.org/reports/CTD_genes_diseases.tsv.gz)
- **Local Path**: `data/raw/ctd/CTD_genes_diseases.tsv.gz`
- **Notes**: Public domain / open access database for toxicogenomic relationships.

### Reactome Pathway Database
- **Official URL**: [https://reactome.org/](https://reactome.org/)
- **Download Link**: [https://reactome.org/download/current/ReactomePathways.txt](https://reactome.org/download/current/ReactomePathways.txt)
- **Local Path**: `data/raw/reactome/ReactomePathways.txt`
- **Notes**: Open access Creative Commons CC0 pathway knowledgebase.

### Human Phenotype Ontology (HPO)
- **Official URL**: [https://hpo.jax.org/](https://hpo.jax.org/)
- **Download Link**: [https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa](https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa)
- **Local Path**: `data/raw/hpo/phenotype.hpoa`
- **Notes**: CC BY 4.0 ontology annotations for clinical phenotypes.

### SIDER (Side Effect Resource)
- **Official URL**: [http://sideeffects.embl.de/](http://sideeffects.embl.de/)
- **Download Link**: [http://sideeffects.embl.de/media/download/meddra_all_se.tsv.gz](http://sideeffects.embl.de/media/download/meddra_all_se.tsv.gz)
- **Local Path**: `data/raw/sider/meddra_all_se.tsv.gz`
- **Notes**: CC BY-NC 4.0 resource for drug adverse effects.

### SIDER Drug Names
- **Official URL**: [http://sideeffects.embl.de/](http://sideeffects.embl.de/)
- **Download Link**: [http://sideeffects.embl.de/media/download/drug_names.tsv](http://sideeffects.embl.de/media/download/drug_names.tsv)
- **Local Path**: `data/raw/sider/drug_names.tsv`
- **Notes**: Drug entity lookup table for SIDER side effects.

### Gene Ontology (GO)
- **Official URL**: [http://geneontology.org/](http://geneontology.org/)
- **Download Link**: [http://current.geneontology.org/annotations/goa_human.gaf.gz](http://current.geneontology.org/annotations/goa_human.gaf.gz)
- **Local Path**: `data/raw/go/goa_human.gaf.gz`
- **Notes**: CC BY 4.0 ontology for gene functional roles.

### PrimeKG Processing Logic
- **Official URL**: [https://github.com/mims-harvard/PrimeKG](https://github.com/mims-harvard/PrimeKG)
- **Download Link**: [https://raw.githubusercontent.com/mims-harvard/PrimeKG/main/datasets/processing_scripts/omim_tools.py](https://raw.githubusercontent.com/mims-harvard/PrimeKG/main/datasets/processing_scripts/omim_tools.py)
- **Local Path**: `data/raw/primekg/omim_tools.py`
- **Notes**: Official processing scripts from Harvard MIMS PrimeKG repository.

