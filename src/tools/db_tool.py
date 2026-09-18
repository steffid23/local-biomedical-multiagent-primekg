# -*- coding: utf-8 -*-
"""
src/tools/db_tool.py
Phase 10: Safe Python Database Tools for Local LLM Agents.
Enforces read-only query execution, schema introspection, and entity lookup.
Supports real database record counts and connection verification for UI dashboard.
"""

import os
import sqlite3
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "data", "processed", "biomedical.db")

class BiomedicalDBTool:
    """Safe, read-only database query tool for local biomedical agents."""

    def __init__(self, db_path=SQLITE_DB_PATH):
        self.db_path = db_path

    def _get_connection(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file not found at {self.db_path}. Please run scripts/parse_and_prepare_data.py first.")
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def verify_connection(self) -> bool:
        """Verify that the local database file exists and is accessible."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    def get_database_stats(self) -> dict:
        """Calculate and return real record counts from local database tables."""
        if not self.verify_connection():
            return {
                "genes": 0,
                "diseases": 0,
                "drugs": 0,
                "pathways": 0,
                "phenotypes": 0,
                "relationships": 0,
                "total_entities": 0
            }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            genes = cursor.execute("SELECT COUNT(*) FROM genes").fetchone()[0]
            diseases = cursor.execute("SELECT COUNT(*) FROM diseases").fetchone()[0]
            drugs = cursor.execute("SELECT COUNT(*) FROM drugs").fetchone()[0]
            pathways = cursor.execute("SELECT COUNT(*) FROM pathways").fetchone()[0]
            phenotypes = cursor.execute("SELECT COUNT(*) FROM phenotypes").fetchone()[0]
            relationships = cursor.execute("SELECT COUNT(*) FROM biomedical_relationships").fetchone()[0]
            conn.close()

            total_entities = genes + diseases + drugs + pathways + phenotypes

            return {
                "genes": genes,
                "diseases": diseases,
                "drugs": drugs,
                "pathways": pathways,
                "phenotypes": phenotypes,
                "relationships": relationships,
                "total_entities": total_entities
            }
        except Exception as e:
            print(f"[WARN] Error fetching database stats: {e}")
            return {
                "genes": 0, "diseases": 0, "drugs": 0, "pathways": 0,
                "phenotypes": 0, "relationships": 0, "total_entities": 0
            }

    def get_database_schema(self) -> str:
        """Return human-readable database schema description for agent context."""
        schema_info = """
### LOCAL BIOMEDICAL DATABASE SCHEMA

1. **genes** (gene_id, entrez_id, symbol, name, uniprot_id)
   - Master entity table for human genes.
   - Example: symbol = 'APP', entrez_id = '351'

2. **diseases** (disease_id, disease_code, name, category)
   - Master entity table for human diseases.
   - Example: disease_code = 'MESH:D000544', name = 'Alzheimer Disease'

3. **drugs** (drug_id, stitch_id, name)
   - Master entity table for pharmaceutical drugs.
   - Example: stitch_id = 'CID100000085', name = 'Donepezil'

4. **pathways** (pathway_id, reactome_id, name, species)
   - Biological pathways mapped to Reactome IDs.
   - Example: reactome_id = 'R-HSA-164368'

5. **phenotypes** (phenotype_id, code, name)
   - Clinical phenotypes and side effect medical terms.
   - Example: code = 'HP:0002354', name = 'Memory impairment'

6. **biomedical_relationships** (relationship_id, source_entity, source_id, relationship_type, target_entity, target_id, data_source, evidence)
   - Unified graph table connecting entities.
   - Core relationship_type values:
     * 'associated_with_disease' (gene -> disease)
     * 'causes_side_effect' (drug -> phenotype)
     * 'has_phenotype' (disease -> phenotype)
"""
        return schema_info.strip()

    def execute_query(self, sql_query: str, max_rows: int = 50) -> str:
        """Execute a read-only SQL query safely and return results as JSON string."""
        sql_clean = sql_query.strip()

        # Enforce read-only execution safety
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE", "REPLACE"]
        first_word = sql_clean.split()[0].upper() if sql_clean else ""
        if first_word not in ["SELECT", "WITH", "EXPLAIN", "PRAGMA"]:
            return json.dumps({
                "status": "ERROR",
                "error": f"Security violation: Only SELECT queries are permitted. Forbidden command: '{first_word}'"
            })

        for keyword in forbidden:
            if re.search(r'\b' + keyword + r'\b', sql_clean, re.IGNORECASE):
                return json.dumps({
                    "status": "ERROR",
                    "error": f"Security violation: SQL query contains forbidden mutation keyword '{keyword}'."
                })

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if "LIMIT" not in sql_clean.upper():
                sql_clean += f" LIMIT {max_rows}"

            cursor.execute(sql_clean)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description] if cursor.description else []

            results = [dict(zip(columns, row)) for row in rows]
            conn.close()

            return json.dumps({
                "status": "SUCCESS",
                "row_count": len(results),
                "columns": columns,
                "data": results
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "error": str(e)
            })

    def search_entity(self, entity_name: str, query_term: str) -> str:
        """Convenience search helper for finding genes, diseases, drugs, or pathways by keyword."""
        table_map = {
            "gene": ("genes", "symbol"),
            "disease": ("diseases", "name"),
            "drug": ("drugs", "name"),
            "pathway": ("pathways", "name"),
            "phenotype": ("phenotypes", "name")
        }

        entity_clean = entity_name.lower().strip()
        if entity_clean not in table_map:
            return json.dumps({"status": "ERROR", "error": f"Unknown entity name '{entity_name}'. Choose from {list(table_map.keys())}."})

        table, col = table_map[entity_clean]
        sql = f"SELECT * FROM {table} WHERE {col} LIKE ? LIMIT 10"
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(sql, (f"%{query_term}%",))
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()

            return json.dumps({"status": "SUCCESS", "entity": entity_clean, "query": query_term, "data": results}, indent=2)
        except Exception as e:
            return json.dumps({"status": "ERROR", "error": str(e)})


if __name__ == "__main__":
    db = BiomedicalDBTool()
    print("Database Stats:")
    print(db.get_database_stats())
    print("Database Schema:")
    print(db.get_database_schema())
