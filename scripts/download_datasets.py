#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/download_datasets.py
Task 1: Space-Optimized Biomedical Data Downloader & Inventory Generator for PrimeKG Multi-Agent Project.
"""

import os
import sys
import gzip
import shutil
import time
import datetime
import csv
import urllib.request
import urllib.error
import ssl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

LOG_FILE = os.path.join(LOGS_DIR, "download.log")
CSV_INVENTORY = os.path.join(REPORTS_DIR, "data_inventory.csv")
MD_INVENTORY = os.path.join(REPORTS_DIR, "data_inventory.md")

DATASETS = [
    {
        "source_name": "CTD (Comparative Toxicogenomics Database)",
        "sub_dir": "ctd",
        "file_name": "CTD_genes_diseases.tsv.gz",
        "download_url": "https://ctdbase.org/reports/CTD_genes_diseases.tsv.gz",
        "official_url": "https://ctdbase.org/",
        "format": "tsv.gz",
        "extract": True,
        "biological_info": "Curated gene-disease associations and toxicogenomics metadata",
        "notes": "Public domain / open access database for toxicogenomic relationships."
    },
    {
        "source_name": "Reactome Pathway Database",
        "sub_dir": "reactome",
        "file_name": "ReactomePathways.txt",
        "download_url": "https://reactome.org/download/current/ReactomePathways.txt",
        "official_url": "https://reactome.org/",
        "format": "tsv/txt",
        "extract": False,
        "biological_info": "Biological pathway definitions, identifiers, and species mappings",
        "notes": "Open access Creative Commons CC0 pathway knowledgebase."
    },
    {
        "source_name": "Human Phenotype Ontology (HPO)",
        "sub_dir": "hpo",
        "file_name": "phenotype.hpoa",
        "download_url": "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa",
        "official_url": "https://hpo.jax.org/",
        "format": "hpoa/tsv",
        "extract": False,
        "biological_info": "Standardized disease-to-phenotypic-feature clinical annotations",
        "notes": "CC BY 4.0 ontology annotations for clinical phenotypes."
    },
    {
        "source_name": "SIDER (Side Effect Resource)",
        "sub_dir": "sider",
        "file_name": "meddra_all_se.tsv.gz",
        "download_url": "http://sideeffects.embl.de/media/download/meddra_all_se.tsv.gz",
        "official_url": "http://sideeffects.embl.de/",
        "format": "tsv.gz",
        "extract": True,
        "biological_info": "Drug-side effect associations mapped to MedDRA phenotypic concepts",
        "notes": "CC BY-NC 4.0 resource for drug adverse effects."
    },
    {
        "source_name": "SIDER Drug Names",
        "sub_dir": "sider",
        "file_name": "drug_names.tsv",
        "download_url": "http://sideeffects.embl.de/media/download/drug_names.tsv",
        "official_url": "http://sideeffects.embl.de/",
        "format": "tsv",
        "extract": False,
        "biological_info": "Drug concept identifiers (STITCH/PubChem) mapped to drug names",
        "notes": "Drug entity lookup table for SIDER side effects."
    },
    {
        "source_name": "Gene Ontology (GO)",
        "sub_dir": "go",
        "file_name": "goa_human.gaf.gz",
        "download_url": "http://current.geneontology.org/annotations/goa_human.gaf.gz",
        "official_url": "http://geneontology.org/",
        "format": "gaf.gz",
        "extract": True,
        "biological_info": "Human gene functional annotations (molecular function, cellular component, biological process)",
        "notes": "CC BY 4.0 ontology for gene functional roles."
    },
    {
        "source_name": "PrimeKG Processing Logic",
        "sub_dir": "primekg",
        "file_name": "omim_tools.py",
        "download_url": "https://raw.githubusercontent.com/mims-harvard/PrimeKG/main/datasets/processing_scripts/omim_tools.py",
        "official_url": "https://github.com/mims-harvard/PrimeKG",
        "format": "py",
        "extract": False,
        "biological_info": "PrimeKG entity construction and OMIM disease integration logic",
        "notes": "Official processing scripts from Harvard MIMS PrimeKG repository."
    }
]


def setup_directories():
    dirs = [DATA_DIR, RAW_DIR, PROCESSED_DIR, REPORTS_DIR, LOGS_DIR]
    for ds in DATASETS:
        dirs.append(os.path.join(RAW_DIR, ds["sub_dir"]))
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def log_event(source, url, dest, success, bytes_cnt, error=""):
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    status_str = "SUCCESS" if success else "FAILED"
    dest_str = str(dest).replace("\\", "/")
    log_entry = "[{0}] | Source: {1} | URL: {2} | File: {3} | Status: {4} | Bytes: {5} | Error: {6}\n".format(
        timestamp, source, url, dest_str, status_str, bytes_cnt, error
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


def is_valid_file(target_path):
    """Check if file exists, has size > 0, and if .gz, verifies gzip integrity."""
    if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
        return False
    if target_path.endswith(".gz"):
        try:
            with gzip.open(target_path, "rb") as f:
                f.seek(-1, os.SEEK_END)
            return True
        except Exception:
            print("[WARN] Corrupted or incomplete .gz detected, removing: {0}".format(target_path))
            try:
                os.remove(target_path)
            except Exception:
                pass
            return False
    return True


def download_file(url, target_path, source_name):
    if is_valid_file(target_path):
        file_size = os.path.getsize(target_path)
        mb_val = file_size / (1024.0 * 1024.0)
        print("[SKIP] Valid existing file found for '{0}': {1} ({2:.2f} MB)".format(source_name, target_path, mb_val))
        log_event(source_name, url, target_path, True, file_size, "File already exists locally (skipped download)")
        return True, file_size, None

    print("[DOWNLOADING] {0} from {1}...".format(source_name, url))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BiomedicalAgent/1.0"}
    )

    try:
        start_time = time.time()
        with urllib.request.urlopen(req, context=ctx, timeout=120) as response, open(target_path, "wb") as out_file:
            shutil.copyfileobj(response, out_file)
        elapsed = time.time() - start_time
        file_size = os.path.getsize(target_path)
        mb_val = file_size / (1024.0 * 1024.0)
        print("[OK] Downloaded {0:.2f} MB in {1:.1f}s -> {2}".format(mb_val, elapsed, target_path))
        log_event(source_name, url, target_path, True, file_size, "")
        return True, file_size, None
    except Exception as e:
        error_msg = str(e)
        print("[ERROR] Failed to download {0}: {1}".format(source_name, error_msg))
        log_event(source_name, url, target_path, False, 0, error_msg)
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except Exception:
                pass
        return False, 0, error_msg


def extract_gzip(gz_path):
    if not gz_path.endswith(".gz"):
        return None, 0
    extracted_path = gz_path[:-3]
    if os.path.exists(extracted_path) and os.path.getsize(extracted_path) > 0:
        return extracted_path, os.path.getsize(extracted_path)
    
    try:
        base_name = os.path.basename(gz_path)
        print("[EXTRACTING] Decompressing {0}...".format(base_name))
        with gzip.open(gz_path, "rb") as f_in, open(extracted_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        ext_size = os.path.getsize(extracted_path)
        mb_val = ext_size / (1024.0 * 1024.0)
        print("[OK] Extracted -> {0} ({1:.2f} MB)".format(extracted_path, mb_val))
        return extracted_path, ext_size
    except Exception as e:
        print("[WARNING] Gzip extraction error for {0}: {1}".format(gz_path, e))
        return None, 0


def inspect_tabular_file(file_path):
    if not os.path.exists(file_path):
        return None, None

    is_gz = file_path.endswith(".gz")
    rows = 0
    cols = 0

    try:
        open_fn = gzip.open if is_gz else open
        with open_fn(file_path, "rt", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#") or line.startswith("!") or not line.strip():
                    continue
                rows += 1
                if cols == 0:
                    if "\t" in line:
                        cols = len(line.split("\t"))
                    elif "," in line:
                        cols = len(line.split(","))
                    else:
                        cols = 1
        return rows, cols
    except Exception as e:
        print("[WARNING] Streaming inspection failed for {0}: {1}".format(file_path, e))
        return None, None


def get_dir_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total


def main():
    print("=" * 70)
    print("  PrimeKG Local Multi-Agent Project - Task 1 Data Acquisition")
    print("=" * 70)
    
    setup_directories()
    inventory_rows = []
    
    total_downloaded_bytes = 0
    total_extracted_bytes = 0
    successful_sources = 0
    total_files_cnt = 0

    for ds in DATASETS:
        target_dir = os.path.join(RAW_DIR, ds["sub_dir"])
        target_path = os.path.join(target_dir, ds["file_name"])

        success, comp_size, err = download_file(ds["download_url"], target_path, ds["source_name"])
        
        extracted_path = None
        ext_size = 0
        
        if success:
            successful_sources += 1
            total_files_cnt += 1
            total_downloaded_bytes += comp_size

            if ds["extract"] and target_path.endswith(".gz"):
                extracted_path, ext_size = extract_gzip(target_path)
                if ext_size > 0:
                    total_files_cnt += 1
                    total_extracted_bytes += ext_size
                else:
                    ext_size = comp_size
            else:
                ext_size = comp_size

            inspect_target = extracted_path if extracted_path else target_path
            rows, cols = inspect_tabular_file(inspect_target)
        else:
            rows, cols = None, None

        comp_mb = comp_size / (1024.0 * 1024.0) if success else 0.0
        comp_gb = comp_size / (1024.0 * 1024.0 * 1024.0) if success else 0.0
        ext_mb = ext_size / (1024.0 * 1024.0) if success else 0.0

        rel_path = os.path.relpath(target_path, BASE_DIR).replace("\\", "/")

        inventory_rows.append({
            "source_name": ds["source_name"],
            "dataset_file": ds["file_name"],
            "file_path": rel_path,
            "file_format": ds["format"],
            "compressed": "Yes" if ds["file_name"].endswith(".gz") else "No",
            "size_bytes": comp_size,
            "size_mb": round(comp_mb, 2),
            "size_gb": round(comp_gb, 4),
            "extracted_size_mb": round(ext_mb, 2),
            "download_url": ds["download_url"],
            "official_source_url": ds["official_url"],
            "download_date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
            "download_status": "SUCCESS" if success else "FAILED: {0}".format(err),
            "biological_info": ds["biological_info"],
            "rows": rows if rows is not None else "N/A",
            "columns": cols if cols is not None else "N/A",
            "notes": ds["notes"]
        })

    total_data_dir_usage = get_dir_size(DATA_DIR)

    fieldnames = [
        "source_name", "dataset_file", "file_path", "file_format", "compressed",
        "size_bytes", "size_mb", "size_gb", "extracted_size_mb", "download_url",
        "official_source_url", "download_date", "download_status",
        "biological_info", "rows", "columns", "notes"
    ]
    with open(CSV_INVENTORY, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory_rows)
    print("\n[OK] CSV inventory saved to: {0}".format(CSV_INVENTORY))

    tot_dl_mb = total_downloaded_bytes / (1024.0 * 1024.0)
    tot_dl_gb = total_downloaded_bytes / (1024.0 * 1024.0 * 1024.0)
    tot_ext_mb = total_extracted_bytes / (1024.0 * 1024.0)
    tot_ext_gb = total_extracted_bytes / (1024.0 * 1024.0 * 1024.0)
    tot_disk_mb = total_data_dir_usage / (1024.0 * 1024.0)
    tot_disk_gb = total_data_dir_usage / (1024.0 * 1024.0 * 1024.0)

    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    md_content = "# Biomedical Data Inventory (PrimeKG Local Multi-Agent Project)\n\n"
    md_content += "> **Generated On**: {0}  \n".format(now_str)
    md_content += "> **Storage Optimization Strategy**: Space-efficient selection of key PrimeKG constituent biomedical datasets.\n\n"
    md_content += "---\n\n"
    md_content += "## Data Download Summary\n\n"
    md_content += "- **Total Sources Processed**: {0}\n".format(len(DATASETS))
    md_content += "- **Sources Successfully Downloaded**: {0}\n".format(successful_sources)
    md_content += "- **Total Files Stored**: {0}\n".format(total_files_cnt)
    md_content += "- **Total Downloaded (Compressed) Size**: `{0:.2f} MB` (`{1:.4f} GB`)\n".format(tot_dl_mb, tot_dl_gb)
    md_content += "- **Total Extracted (Uncompressed) Size**: `{0:.2f} MB` (`{1:.4f} GB`)\n".format(tot_ext_mb, tot_ext_gb)
    md_content += "- **Total Data Directory Disk Usage**: `{0:.2f} MB` (`{1:.4f} GB`)\n\n".format(tot_disk_mb, tot_disk_gb)
    md_content += "---\n\n"
    md_content += "## Downloaded Biomedical Datasets\n\n"
    md_content += "| Source | Dataset / File | Biological Information | Size (MB) | Size (GB) | Format | Status | Rows | Cols |\n"
    md_content += "| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n"

    for r in inventory_rows:
        md_content += "| **{0}** | `{1}` | {2} | {3} MB | {4} GB | {5} | {6} | {7} | {8} |\n".format(
            r['source_name'], r['dataset_file'], r['biological_info'], r['size_mb'], r['size_gb'],
            r['file_format'], r['download_status'], r['rows'], r['columns']
        )

    md_content += "\n---\n\n"
    md_content += "## File Storage & Path Directory\n\n"
    md_content += "```text\n"
    md_content += "data/\n"
    md_content += "└── raw/\n"
    md_content += "    ├── ctd/\n"
    md_content += "    │   ├── CTD_genes_diseases.tsv.gz\n"
    md_content += "    │   └── CTD_genes_diseases.tsv\n"
    md_content += "    ├── reactome/\n"
    md_content += "    │   └── ReactomePathways.txt\n"
    md_content += "    ├── hpo/\n"
    md_content += "    │   └── phenotype.hpoa\n"
    md_content += "    ├── sider/\n"
    md_content += "    │   ├── meddra_all_se.tsv.gz\n"
    md_content += "    │   ├── meddra_all_se.tsv\n"
    md_content += "    │   └── drug_names.tsv\n"
    md_content += "    ├── go/\n"
    md_content += "    │   ├── goa_human.gaf.gz\n"
    md_content += "    │   └── goa_human.gaf\n"
    md_content += "    └── primekg/\n"
    md_content += "        └── omim_tools.py\n"
    md_content += "```\n\n"
    md_content += "---\n\n"
    md_content += "## Detailed Resource Provenance & Notes\n\n"

    for r in inventory_rows:
        md_content += "### {0}\n".format(r['source_name'])
        md_content += "- **Official URL**: [{0}]({0})\n".format(r['official_source_url'])
        md_content += "- **Download Link**: [{0}]({0})\n".format(r['download_url'])
        md_content += "- **Local Path**: `{0}`\n".format(r['file_path'])
        md_content += "- **Notes**: {0}\n\n".format(r['notes'])

    with open(MD_INVENTORY, "w", encoding="utf-8") as f:
        f.write(md_content)
    print("[OK] Markdown inventory saved to: {0}".format(MD_INVENTORY))

    print("\n" + "=" * 70)
    print("                    DATA DOWNLOAD SUMMARY")
    print("=" * 70)
    print("Sources successfully downloaded: {0} / {1}".format(successful_sources, len(DATASETS)))
    print("Files stored on disk:            {0}".format(total_files_cnt))
    print("Total downloaded size:          {0:.2f} MB  ({1:.4f} GB)".format(tot_dl_mb, tot_dl_gb))
    print("Total extracted size:           {0:.2f} MB  ({1:.4f} GB)".format(tot_ext_mb, tot_ext_gb))
    print("Total disk usage (data/ dir):    {0:.2f} MB  ({1:.4f} GB)".format(tot_disk_mb, tot_disk_gb))
    print("=" * 70)

if __name__ == "__main__":
    main()
