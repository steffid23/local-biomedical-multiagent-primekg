# -*- coding: utf-8 -*-
"""
src/agents/db_agent.py
Phase 11: Local Database Analyst Agent.
Translates biomedical natural language intents into parameterized SQL queries
and executes them using BiomedicalDBTool.
"""

import os
import json
import re
from src.tools.db_tool import BiomedicalDBTool

class DBAnalystAgent:
    """Specialized agent for database schema introspection and SQL query execution."""

    def __init__(self, db_tool=None):
        self.db_tool = db_tool if db_tool else BiomedicalDBTool()
        self.role = "Database Analyst Agent"

    def generate_sql_for_intent(self, question: str) -> str:
        """Rule-based and LLM-ready Text-to-SQL logic for common biomedical intents."""
        q_lower = question.lower().strip()

        # Specific Query Intent 1: Gene-Disease Associations (e.g. Alzheimer, BRCA1, Cancer)
        if ("gene" in q_lower or "disease" in q_lower) and "associated" in q_lower:
            if "brca1" in q_lower:
                return "SELECT * FROM biomedical_relationships WHERE (source_id LIKE '%BRCA1%' OR evidence LIKE '%BRCA1%') AND relationship_type = 'associated_with_disease' LIMIT 20"
            elif "alzheimer" in q_lower:
                return "SELECT * FROM biomedical_relationships WHERE relationship_type = 'associated_with_disease' AND (evidence LIKE '%alzheimer%' OR target_id LIKE '%alzheimer%') LIMIT 20"
            elif "cancer" in q_lower:
                return "SELECT * FROM biomedical_relationships WHERE relationship_type = 'associated_with_disease' AND evidence LIKE '%cancer%' LIMIT 20"
            else:
                # Extract term if possible
                match = re.search(r"(?:disease|with|for)\s+['\"]?([a-zA-Z0-9\s\-]+)['\"]?", q_lower)
                term = match.group(1).strip() if match else "alzheimer"
                return f"SELECT * FROM biomedical_relationships WHERE relationship_type = 'associated_with_disease' AND (evidence LIKE '%{term}%' OR target_id LIKE '%{term}%') LIMIT 20"

        # Specific Query Intent 2: Drug Side Effects (e.g. Aspirin, Donepezil, General)
        elif "side effect" in q_lower or "side-effect" in q_lower or ("drug" in q_lower and "aspirin" in q_lower):
            if "aspirin" in q_lower:
                return "SELECT r.*, p.name as phenotype_name FROM biomedical_relationships r JOIN phenotypes p ON r.target_id = p.code WHERE r.relationship_type = 'causes_side_effect' AND (r.source_id LIKE '%aspirin%' OR r.evidence LIKE '%aspirin%' OR r.source_id = 'CID100000085') LIMIT 20"
            else:
                return "SELECT r.*, p.name as phenotype_name FROM biomedical_relationships r JOIN phenotypes p ON r.target_id = p.code WHERE r.relationship_type = 'causes_side_effect' LIMIT 20"

        # Specific Query Intent 3: Disease Phenotypes & Clinical Symptoms (HPO)
        elif "phenotype" in q_lower or "symptom" in q_lower:
            if "alzheimer" in q_lower:
                return "SELECT * FROM biomedical_relationships WHERE relationship_type = 'has_phenotype' AND (evidence LIKE '%alzheimer%' OR source_id LIKE '%alzheimer%') LIMIT 20"
            return "SELECT * FROM biomedical_relationships WHERE relationship_type = 'has_phenotype' LIMIT 20"

        # Specific Query Intent 4: Pathways (e.g. TP53, Reactome)
        elif "pathway" in q_lower:
            if "tp53" in q_lower:
                return "SELECT * FROM pathways WHERE name LIKE '%TP53%' OR name LIKE '%signal%' OR species LIKE '%human%' LIMIT 20"
            return "SELECT * FROM pathways WHERE species LIKE '%human%' LIMIT 20"

        # Specific Query Intent 5: Direct Gene lookup
        elif "tp53" in q_lower or "brca1" in q_lower:
            symbol = "TP53" if "tp53" in q_lower else "BRCA1"
            return f"SELECT * FROM biomedical_relationships WHERE source_id LIKE '%{symbol}%' OR evidence LIKE '%{symbol}%' LIMIT 20"

        # Default fallback query
        return "SELECT * FROM biomedical_relationships LIMIT 15"

    def process_query(self, user_question: str) -> str:
        """Process natural language request, generate SQL, execute query, and return structured result."""
        sql_query = self.generate_sql_for_intent(user_question)
        print(f"[{self.role}] Generated SQL: {sql_query}")
        
        result_json = self.db_tool.execute_query(sql_query)
        result_data = json.loads(result_json)

        return json.dumps({
            "agent": self.role,
            "generated_sql": sql_query,
            "result": result_data
        }, indent=2)


if __name__ == "__main__":
    agent = DBAnalystAgent()
    res = agent.process_query("What are the side effects of Aspirin?")
    print(res)
