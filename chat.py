#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chat.py
Interactive Command Line Interface for Local Biomedical Multi-Agent System.
Clean CLI without emojis.
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.agents.orchestrator import LocalBiomedicalOrchestrator

def main():
    print("=" * 70)
    print("      LOCAL BIOMEDICAL MULTI-AGENT AI SYSTEM (PRIMEKG DATA)")
    print("=" * 70)
    print("100% Offline | Local MySQL & SQLite Warehouse | Multi-Agent Architecture")
    print("Data Sources: CTD | Reactome | HPO | SIDER | Gene Ontology")
    print("-" * 70)
    print("Type your biomedical question below, or type 'exit' / 'quit' to stop.")
    print("Type 'schema' to view the database structure.")
    print("=" * 70 + "\n")

    orchestrator = LocalBiomedicalOrchestrator()

    while True:
        try:
            user_input = input("\nBiomedical Agent > ").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nExiting Biomedical AI Agent. Goodbye!")
                break

            if user_input.lower() in ["schema", "tables", "help"]:
                print("\n" + orchestrator.db_tool.get_database_schema())
                continue

            answer = orchestrator.handle_user_question(user_input)
            print("\n" + answer)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting Biomedical AI Agent. Goodbye!")
            break

if __name__ == "__main__":
    main()
