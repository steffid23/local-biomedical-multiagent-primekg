# -*- coding: utf-8 -*-
"""
app.py
Streamlit Web Dashboard for Local Biomedical Multi-Agent System (PrimeKG Data).
Polished, professional, presentation-ready biomedical analytics dashboard for mentor Raj.
Enforces ZERO EMOJIS, real database stats, dark scientific styling, and non-breaking architecture.
"""

import streamlit as st
import pandas as pd
import json
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.agents.orchestrator import LocalBiomedicalOrchestrator

# Configure Page Settings with Professional Dark Theme Layout
st.set_page_config(
    page_title="Local Biomedical Multi-Agent System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL DARK THEME CSS ---
st.markdown("""
<style>
    /* Dark Theme Core Styles */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Styles */
    .header-container {
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-bottom: 2px solid #334155;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #38BDF8;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .main-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }
    .status-badge-container {
        display: flex;
        gap: 0.8rem;
        margin-top: 0.5rem;
    }
    .status-badge {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        background-color: #1E293B;
        border: 1px solid #334155;
        color: #38BDF8;
    }
    .status-badge-active {
        color: #4ADE80;
        border-color: #166534;
        background-color: #052E16;
    }

    /* Card Containers */
    .stat-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.2s;
    }
    .stat-title {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38BDF8;
        margin: 0.4rem 0;
    }
    .stat-desc {
        font-size: 0.75rem;
        color: #64748B;
    }

    /* Relationship Cards */
    .rel-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-left: 4px solid #38BDF8;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.6rem;
    }
    .rel-source {
        font-weight: 700;
        color: #F8FAFC;
    }
    .rel-type {
        font-size: 0.8rem;
        color: #38BDF8;
        background-color: #0F172A;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        border: 1px solid #334155;
    }
    .rel-target {
        font-weight: 600;
        color: #CBD5E1;
    }
    .rel-prov {
        font-size: 0.75rem;
        color: #94A3B8;
        float: right;
    }

    /* Streamlit Components Dark Theme Overrides */
    div[data-testid="stSidebar"] {
        background-color: #0B1120;
        border-right: 1px solid #1E293B;
    }
    .stButton>button {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 6px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #38BDF8;
        color: #0F172A;
        border-color: #38BDF8;
    }
    div[data-baseweb="input"] {
        background-color: #1E293B;
        border-color: #334155;
        color: #F8FAFC;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_orchestrator():
    """Instantiate and cache Local Orchestrator backend."""
    return LocalBiomedicalOrchestrator()

orchestrator = load_orchestrator()

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_response" not in st.session_state:
    st.session_state.current_response = None
if "selected_query" not in st.session_state:
    st.session_state.selected_query = ""

# Verify local database connection status
is_db_connected = orchestrator.db_tool.verify_connection()
db_stats = orchestrator.db_tool.get_database_stats()


# --- SIDEBAR COMPONENT ---
with st.sidebar:
    st.markdown("### Biomedical Analytics")
    st.caption("PrimeKG Knowledge Graph Dashboard")
    
    st.markdown("---")
    st.markdown("#### NAVIGATION")
    nav_choice = st.radio(
        "Select View:",
        ["Dashboard Overview", "Ask Biomedical Question", "Database Explorer"],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("#### INTEGRATED DATASETS")
    st.markdown("""
    - **CTD**: Gene-Disease Associations
    - **Reactome**: Biological Pathways
    - **HPO**: Clinical Phenotypes
    - **SIDER**: Drug Side Effects
    - **GO**: Human Gene Functions
    """)

    st.markdown("---")
    st.markdown("#### SYSTEM STATUS")
    st.markdown(f"""
    - **Deployment**: Local / Offline
    - **Database**: {"Connected (SQLite/MySQL)" if is_db_connected else "Disconnected"}
    - **Execution**: Read-Only Parameterized
    - **Cloud Cost**: $0 (Zero AWS)
    """)


# --- HEADER SECTION ---
st.markdown(f"""
<div class="header-container">
    <div class="main-title">Local Biomedical Multi-Agent System</div>
    <div class="main-subtitle">Precision Medicine Knowledge Graph | PrimeKG | Local Biomedical Intelligence</div>
    <div class="status-badge-container">
        <span class="status-badge status-badge-active">System Online</span>
        <span class="status-badge">Local / Offline</span>
        <span class="status-badge {"status-badge-active" if is_db_connected else ""}">
            {"Database Connected" if is_db_connected else "Database Offline"}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# VIEW 1: DASHBOARD OVERVIEW
# ==============================================================================
if nav_choice == "Dashboard Overview":
    st.markdown("### Knowledge Graph Overview")
    st.caption("Real-time database record metrics queried directly from the local relational warehouse.")

    # Stat Cards Row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Biomedical Entities</div>
            <div class="stat-number">{db_stats['total_entities']:,}</div>
            <div class="stat-desc">Total Nodes (Genes, Drugs, Diseases)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Gene Entities</div>
            <div class="stat-number">{db_stats['genes']:,}</div>
            <div class="stat-desc">Entrez / UniProt Identifiers</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Disease Entities</div>
            <div class="stat-number">{db_stats['diseases']:,}</div>
            <div class="stat-desc">MONDO / OMIM / MESH Codes</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Drug Entities</div>
            <div class="stat-number">{db_stats['drugs']:,}</div>
            <div class="stat-desc">STITCH / PubChem Identifiers</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Stat Cards Row 2
    col5, col6, col7 = st.columns(3)
    with col5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Biological Pathways</div>
            <div class="stat-number">{db_stats['pathways']:,}</div>
            <div class="stat-desc">Reactome Pathway Models</div>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Phenotypes & Symptoms</div>
            <div class="stat-number">{db_stats['phenotypes']:,}</div>
            <div class="stat-desc">HPO & MedDRA Terms</div>
        </div>
        """, unsafe_allow_html=True)
    with col7:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-title">Knowledge Graph Edges</div>
            <div class="stat-number">{db_stats['relationships']:,}</div>
            <div class="stat-desc">Integrated Triples & Associations</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Actions Section
    st.markdown("### Explore the Knowledge Graph")
    st.caption("Select an analytics view to launch an example query.")

    act_col1, act_col2, act_col3, act_col4 = st.columns(4)

    if act_col1.button("Gene-Disease Associations", use_container_width=True):
        st.session_state.selected_query = "What genes are associated with Alzheimer's disease?"
        st.rerun()

    if act_col2.button("Drug Side Effects", use_container_width=True):
        st.session_state.selected_query = "What are the side effects of Aspirin?"
        st.rerun()

    if act_col3.button("Disease Phenotypes", use_container_width=True):
        st.session_state.selected_query = "What phenotypes are associated with Alzheimer's disease?"
        st.rerun()

    if act_col4.button("Biological Pathways", use_container_width=True):
        st.session_state.selected_query = "Which pathways involve TP53?"
        st.rerun()


# ==============================================================================
# VIEW 2: ASK BIOMEDICAL QUESTION & ANALYTICS
# ==============================================================================
if nav_choice == "Ask Biomedical Question" or st.session_state.selected_query:
    st.markdown("### Ask a Biomedical Question")
    st.caption("Enter a query or select an example below. Natural language intent is translated into safe SQL SELECT queries.")

    # Example Question Chips Section
    st.markdown("**Example Questions:**")
    ex_cols = st.columns(5)
    if ex_cols[0].button("Alzheimer Genes", use_container_width=True):
        st.session_state.selected_query = "What genes are associated with Alzheimer's disease?"
    if ex_cols[1].button("Aspirin Side Effects", use_container_width=True):
        st.session_state.selected_query = "What are the side effects of Aspirin?"
    if ex_cols[2].button("Alzheimer Phenotypes", use_container_width=True):
        st.session_state.selected_query = "What phenotypes are associated with Alzheimer's disease?"
    if ex_cols[3].button("TP53 Pathways", use_container_width=True):
        st.session_state.selected_query = "Which pathways involve TP53?"
    if ex_cols[4].button("BRCA1 Diseases", use_container_width=True):
        st.session_state.selected_query = "What diseases are associated with BRCA1?"

    # Question Input Form
    with st.form(key="biomedical_query_form"):
        user_query = st.text_area(
            "Enter your question:",
            value=st.session_state.selected_query,
            placeholder="What genes are associated with Alzheimer's disease?",
            height=100
        )
        submit_btn = st.form_submit_button("Ask Agent", type="primary", use_container_width=True)

    if submit_btn and user_query.strip():
        st.session_state.selected_query = user_query.strip()
        with st.spinner("Processing query through Local Multi-Agent Pipeline (Intent -> Text-to-SQL -> Database -> Analysis)..."):
            res = orchestrator.handle_user_question_structured(user_query.strip())
            st.session_state.current_response = res
            st.session_state.chat_history.append(res)

    # RESULTS DISPLAY SECTION
    res = st.session_state.current_response
    if res:
        st.markdown("---")
        st.markdown("## Analytical Results & Evidence")

        # Error handling
        if res.get("status") == "ERROR":
            st.error(f"Backend Exception / Security Alert: {res.get('error')}")

        # Metrics Row
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Records Returned", res.get("row_count", 0))
        prov_text = ", ".join(res.get("provenance_list", [])) if res.get("provenance_list") else "N/A"
        col_m2.metric("Data Provenance", prov_text)
        col_m3.metric("Execution Status", res.get("status", "SUCCESS"))
        col_m4.metric("Database Engine", "SQLite / MySQL")

        # Human-Readable Answer
        st.markdown("### Answer")
        st.markdown(res.get("text_response", ""))

        # Knowledge Graph Relationship Representation (Visual Cards)
        raw_rows = res.get("raw_rows", [])
        if raw_rows:
            st.markdown("### Knowledge Graph Relationships")
            st.caption("Visual representation of retrieved biomedical triples.")
            
            # Show up to 5 visual relationship cards
            for r in raw_rows[:5]:
                src = r.get("source_id") or r.get("source_entity") or r.get("reactome_id") or "Entity"
                rel = r.get("relationship_type") or "pathway_entry"
                tgt = r.get("target_id") or r.get("target_entity") or r.get("species") or "Target"
                prov = r.get("data_source") or "Reactome"
                evid = r.get("evidence") or r.get("phenotype_name") or r.get("name") or ""

                st.markdown(f"""
                <div class="rel-card">
                    <span class="rel-prov">{prov}</span>
                    <span class="rel-source">{src}</span> &nbsp; 
                    <span class="rel-type">{rel}</span> &nbsp; 
                    <span class="rel-target">{tgt}</span>
                    <div style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.3rem;">Notes: {evid}</div>
                </div>
                """, unsafe_allow_html=True)

            # Data Visualization (Generated strictly from retrieved rows)
            st.markdown("### Data Visualization")
            df_rows = pd.DataFrame(raw_rows)
            
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                if "data_source" in df_rows.columns:
                    st.caption("Record Distribution by Data Source")
                    src_counts = df_rows["data_source"].value_counts()
                    st.bar_chart(src_counts)
                elif "species" in df_rows.columns:
                    st.caption("Record Distribution by Species")
                    sp_counts = df_rows["species"].value_counts()
                    st.bar_chart(sp_counts)
            
            with chart_col2:
                if "relationship_type" in df_rows.columns:
                    st.caption("Distribution by Relationship Type")
                    rel_counts = df_rows["relationship_type"].value_counts()
                    st.bar_chart(rel_counts)

            # Retrieved Data Table & Preview
            st.markdown("### Retrieved Data Records")
            st.dataframe(df_rows, use_container_width=True, height=280)

            # CSV Export Option
            csv_bytes = df_rows.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv_bytes,
                file_name=f"biomedical_results_{res.get('timestamp', '').replace(':', '-').replace(' ', '_')}.csv",
                mime="text/csv",
                type="secondary"
            )

            # Technical Details Expander
            with st.expander("Technical Details & SQL Audit"):
                st.code(res.get("generated_sql", "N/A"), language="sql")
                st.json({
                    "timestamp": res.get("timestamp"),
                    "status": res.get("status"),
                    "row_count": res.get("row_count"),
                    "database_path": orchestrator.db_tool.db_path,
                    "columns": res.get("columns")
                })
        else:
            st.warning("No matching records found in the local database for this query.")


# ==============================================================================
# VIEW 3: DATABASE EXPLORER
# ==============================================================================
if nav_choice == "Database Explorer":
    st.markdown("### Database Explorer & Metadata Inspector")
    st.caption("Inspect tables, column definitions, and real record counts across PrimeKG constituent data sources.")

    tab_ctd, tab_reactome, tab_hpo, tab_sider, tab_go = st.tabs([
        "CTD (Gene-Disease)",
        "Reactome (Pathways)",
        "HPO (Phenotypes)",
        "SIDER (Side Effects)",
        "GO (Gene Functions)"
    ])

    with tab_ctd:
        st.markdown("#### Comparative Toxicogenomics Database (CTD)")
        st.markdown("""
        - **Description**: Curated relationships linking human genes to disease traits.
        - **Primary Identifiers**: Entrez Gene ID, MONDO / OMIM / MESH Disease Codes.
        - **Target Tables**: `genes`, `diseases`, `biomedical_relationships`.
        """)
        if is_db_connected:
            ctd_df_json = orchestrator.db_tool.execute_query("SELECT * FROM biomedical_relationships WHERE data_source = 'CTD' LIMIT 5")
            ctd_data = json.loads(ctd_df_json).get("data", [])
            st.dataframe(pd.DataFrame(ctd_data), use_container_width=True)

    with tab_reactome:
        st.markdown("#### Reactome Pathway Knowledgebase")
        st.markdown("""
        - **Description**: Standardized biological pathways, reactions, and species mappings.
        - **Primary Identifiers**: Reactome ID (`R-HSA-...`).
        - **Target Table**: `pathways`.
        """)
        if is_db_connected:
            react_json = orchestrator.db_tool.execute_query("SELECT * FROM pathways LIMIT 5")
            react_data = json.loads(react_json).get("data", [])
            st.dataframe(pd.DataFrame(react_data), use_container_width=True)

    with tab_hpo:
        st.markdown("#### Human Phenotype Ontology (HPO)")
        st.markdown("""
        - **Description**: Standardized clinical disease-to-phenotypic-feature annotations.
        - **Primary Identifiers**: HPO ID (`HP:...`), OMIM ID.
        - **Target Tables**: `diseases`, `phenotypes`, `biomedical_relationships`.
        """)
        if is_db_connected:
            hpo_json = orchestrator.db_tool.execute_query("SELECT * FROM biomedical_relationships WHERE data_source = 'HPO' LIMIT 5")
            hpo_data = json.loads(hpo_json).get("data", [])
            st.dataframe(pd.DataFrame(hpo_data), use_container_width=True)

    with tab_sider:
        st.markdown("#### Side Effect Resource (SIDER)")
        st.markdown("""
        - **Description**: Drug side effect associations mapped to MedDRA phenotypic terms.
        - **Primary Identifiers**: STITCH Compound ID (`CID...`), MedDRA Term Code.
        - **Target Tables**: `drugs`, `phenotypes`, `biomedical_relationships`.
        """)
        if is_db_connected:
            sider_json = orchestrator.db_tool.execute_query("SELECT * FROM biomedical_relationships WHERE data_source = 'SIDER' LIMIT 5")
            sider_data = json.loads(sider_json).get("data", [])
            st.dataframe(pd.DataFrame(sider_data), use_container_width=True)

    with tab_go:
        st.markdown("#### Gene Ontology (GO)")
        st.markdown("""
        - **Description**: Human gene functional annotations covering molecular function, cellular component, biological process.
        - **Primary Identifiers**: UniProtKB ID, GO ID (`GO:...`).
        - **Target Tables**: `genes`, `biomedical_relationships`.
        """)
        if is_db_connected:
            st.info("GO annotations integrated into master genes and biological relationships tables.")
