# -*- coding: utf-8 -*-
"""
src/agents/biomarker_agent.py
Phase 11: Local Biomarker Specialist Agent.
Analyzes query results from the Database Analyst Agent, checks biological data provenance,
and synthesizes evidence-backed biomarker insights with ZERO emojis.
"""

import json

class BiomarkerSpecialistAgent:
    """Specialized agent for biomedical relationship interpretation and biomarker evidence synthesis."""

    def __init__(self):
        self.role = "Biomarker Specialist Agent"

    def analyze_findings(self, db_agent_response_json: str) -> str:
        """Synthesize database query output into biological findings with data provenance."""
        try:
            payload = json.loads(db_agent_response_json)
            result_data = payload.get("result", {})
            rows = result_data.get("data", [])
            sql = payload.get("generated_sql", "")

            if not rows:
                return f"[{self.role}] No direct biomedical relationships found for query. Executed SQL: `{sql}`"

            summary = []
            summary.append(f"### Biomarker Analysis Summary ({len(rows)} Records Found)\n")
            summary.append(f"**Executed SQL Query**: `{sql}`\n")
            summary.append("| Source Entity | Relation | Target Entity | Data Provenance | Evidence / Notes |")
            summary.append("| :--- | :--- | :--- | :--- | :--- |")

            for r in rows[:10]:
                src = r.get("source_id") or r.get("source_entity") or r.get("reactome_id") or r.get("code") or "N/A"
                rel = r.get("relationship_type") or "pathway_entry"
                tgt = r.get("target_id") or r.get("target_entity") or r.get("species") or "N/A"
                prov = r.get("data_source") or "Reactome"
                evid = r.get("evidence") or r.get("phenotype_name") or r.get("name") or "N/A"
                summary.append(f"| `{src}` | `{rel}` | `{tgt}` | **{prov}** | {evid} |")

            return "\n".join(summary)

        except Exception as e:
            return f"[{self.role}] Error synthesizing biomarker findings: {str(e)}"


if __name__ == "__main__":
    from src.agents.db_agent import DBAnalystAgent
    db_agent = DBAnalystAgent()
    biomarker_agent = BiomarkerSpecialistAgent()
    
    db_out = db_agent.process_query("What genes are associated with Alzheimer disease?")
    print(biomarker_agent.analyze_findings(db_out))
