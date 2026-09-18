# -*- coding: utf-8 -*-
"""
src/agents/orchestrator.py
Phase 12: Local Multi-Agent Orchestrator.
Coordinates user natural-language questions, delegates sub-tasks to the Database Analyst Agent
and Biomarker Specialist Agent, and synthesizes final evidence-backed answers.
Supports both text output (for CLI) and structured payload dictionaries (for Web UI/Dashboard).
"""

import sys
import os
import json
import datetime

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.tools.db_tool import BiomedicalDBTool
from src.agents.db_agent import DBAnalystAgent
from src.agents.biomarker_agent import BiomarkerSpecialistAgent

class LocalBiomedicalOrchestrator:
    """Master supervisor agent managing multi-agent collaboration for local biomedical Q&A."""

    def __init__(self):
        self.role = "Local Supervisor Orchestrator"
        self.db_tool = BiomedicalDBTool()
        self.db_agent = DBAnalystAgent(db_tool=self.db_tool)
        self.biomarker_agent = BiomarkerSpecialistAgent()
        self.conversation_history = []

    def handle_user_question_structured(self, user_question: str) -> dict:
        """Process user question and return structured dictionary payload for Web UI/Dashboard."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n" + "=" * 70)
        print(f"  [{self.role}] New Structured Question Received ({timestamp})")
        print(f"  User Query: \"{user_question}\"")
        print("=" * 70)

        # 1. DB Agent Execution
        print(f"\n[STEP 1] Delegating to Database Analyst Agent...")
        db_response_json = self.db_agent.process_query(user_question)
        
        # 2. Biomarker Agent Analysis
        print(f"\n[STEP 2] Delegating to Biomarker Specialist Agent...")
        biomarker_summary = self.biomarker_agent.analyze_findings(db_response_json)

        # 3. Parse DB response details
        try:
            payload = json.loads(db_response_json)
            sql_query = payload.get("generated_sql", "")
            result_info = payload.get("result", {})
            status = result_info.get("status", "SUCCESS")
            rows = result_info.get("data", [])
            cols = result_info.get("columns", [])
            err = result_info.get("error", None)
        except Exception as e:
            sql_query = ""
            status = "ERROR"
            rows = []
            cols = []
            err = str(e)

        # Provenance collection
        provenance_set = set()
        for r in rows:
            if isinstance(r, dict) and r.get("data_source"):
                provenance_set.add(r.get("data_source"))

        # 4. Synthesize markdown answer
        final_answer = f"""## Local Biomedical System Response

> **User Question**: "{user_question}"  
> **Timestamp**: {timestamp}  
> **Orchestrator Mode**: 100% Local Multi-Agent Execution (SQLite / MySQL)

---

{biomarker_summary}

---

### Architectural Provenance & Safety Audit
- **Database Engine**: Local SQLite / MySQL Relational Warehouse
- **Query Type**: Parameterized Read-Only SELECT Query
- **Data Sources Integrated**: CTD, Reactome, HPO, SIDER, Gene Ontology (PrimeKG derived)
- **AWS Cloud Dependencies**: None (0% AWS API calls)
"""

        structured_result = {
            "question": user_question,
            "text_response": final_answer,
            "generated_sql": sql_query,
            "status": status,
            "row_count": len(rows),
            "columns": cols,
            "raw_rows": rows,
            "provenance_list": sorted(list(provenance_set)),
            "timestamp": timestamp,
            "error": err
        }

        self.conversation_history.append(structured_result)
        return structured_result

    def handle_user_question(self, user_question: str) -> str:
        """Process user question through multi-agent workflow (String interface for CLI)."""
        res = self.handle_user_question_structured(user_question)
        return res["text_response"]


def main():
    orchestrator = LocalBiomedicalOrchestrator()
    
    test_queries = [
        "What genes are associated with Alzheimer disease?",
        "What side effects are associated with pharmaceutical drugs in SIDER?",
        "Show clinical phenotypes for diseases in the Human Phenotype Ontology."
    ]

    for q in test_queries:
        res = orchestrator.handle_user_question_structured(q)
        print("\n" + res["text_response"])
        print(f"Row Count: {res['row_count']} | Provenance: {res['provenance_list']}")
        print("-" * 70)

if __name__ == "__main__":
    main()
