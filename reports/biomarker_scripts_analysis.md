# AWS Cancer Biomarker Discovery Reference Script Analysis

> **Document Purpose**: Analysis of Python logic and agent architectural design from the AWS Sample [`cancer_biomarker_discovery`](https://github.com/aws-samples/amazon-bedrock-agents-healthcare-lifesciences/tree/main/multi_agent_collaboration/cancer_biomarker_discovery) repository.  
> **Key Objective**: Identify reusable biomedical AI logic and systematically replace all cloud/AWS dependencies (Amazon Bedrock, Amazon Redshift, SageMaker, Lambda, S3) with 100% local Python and local MySQL infrastructure.

---

## Executive Summary of Adaptation

| Component | AWS Reference Implementation | Local Architecture Replacement |
| :--- | :--- | :--- |
| **Database Query Engine** | Amazon Redshift Serverless | Local MySQL / MariaDB Database |
| **Text-to-SQL Execution** | AWS Lambda (`querydatabaselambda.py`) | Local Python DB Tool (`mysql_tool.py`) using `mysql-connector-python` |
| **LLM Inference & Agents** | Amazon Bedrock Agent Service & Foundation Models | Local LLM / Modular Local Model Wrapper (Ollama, vLLM, or llama.cpp) |
| **Multi-Agent Orchestration**| Bedrock Supervisor Agent (`supervisor_agent.yaml`) | Local Python Orchestration Loop (`orchestrator.py`) |
| **Cloud Storage** | AWS S3 Bucket | Local File System (`data/raw/`, `data/processed/`) |
| **Statistical & Analytics** | AWS SageMaker Containers | Local Python Data Libraries (`pandas`, `scipy`, `lifelines`) |

---

## Detailed Script & Component Analysis

### 1. Database Querying & SQL Execution Logic

#### **File**: `bedrock_agents/ActionGroups/querydatabaselambda/querydatabaselambda.py`

- **What It Does**:
  Receives natural language or structured parameter queries from the agent, executes SQL against Amazon Redshift via boto3 Redshift Data API, formats tabular query results into JSON, and returns them to the caller.
- **Important Functions / Classes**:
  - `lambda_handler(event, context)`: Entry point parsing Bedrock action group parameters.
  - `execute_redshift_query(sql_query)`: Wraps boto3 Redshift client calls `execute_statement` and `get_statement_result`.
  - `format_query_results(response)`: Converts raw database cursor outputs into structured JSON rows and columns.
- **Input**: Action group payload containing target table names, filter criteria, or generated SQL string.
- **Output**: JSON payload containing database column names, row records, total record count, and execution status.
- **AWS Dependencies**: `boto3`, `botocore`, AWS Lambda runtime, Amazon Redshift Data API (`redshift-data`).
- **Logic to Reuse Locally**:
  - Input parsing, parameter validation, sanitization of SQL queries.
  - Tabular result formatting and truncation logic to fit model context windows.
  - Read-only execution safety checks.
- **What Must Be Replaced**:
  Replace `boto3.client('redshift-data')` and `lambda_handler` with a standard Python class `LocalMySQLTool` using `mysql.connector` with local connection pooling.

---

### 2. Agent Helper & Session Utilities

#### **File**: `strands_agentcore/utils/bedrock_agent_helper.py`

- **What It Does**:
  Manages session states, constructs Bedrock agent runtime payloads, triggers agent invocations, and handles streaming/chunked responses from the Bedrock runtime.
- **Important Functions / Classes**:
  - `invoke_bedrock_agent(agent_id, session_id, prompt)`: Calls `bedrock-agent-runtime.invoke_agent`.
  - `parse_agent_response(response_stream)`: Aggregates completion chunks and extracts trace / reasoning steps.
- **Input**: User prompt string, active `session_id`, target `agent_id`.
- **Output**: Final text response string alongside structured step traces.
- **AWS Dependencies**: `boto3.client('bedrock-agent-runtime')`, AWS IAM credentials.
- **Logic to Reuse Locally**:
  - Session history maintenance and conversational context management.
  - Parsing agent step traces (separating internal agent reasoning from user-facing text).
- **What Must Be Replaced**:
  Replace Bedrock runtime invocation with a local Python `AgentSession` class that manages history buffers and invokes a local LLM API endpoint (e.g. `http://localhost:11434/v1`).

---

### 3. Supervisor & Orchestration Configuration

#### **File**: `bedrock_agents/SupervisorAgent/supervisor_agent.yaml`

- **What It Does**:
  Defines supervisor agent role, system prompt, delegation routing guidelines, and sub-agent topic boundaries (e.g., routing database questions to Database Analyst, imaging to Imaging Specialist).
- **Important Functions / Configuration**:
  - `instruction`: Core prompt defining supervisor guidelines and tool dispatching rules.
  - `sub_agents`: List of delegate agent specifications.
- **Input**: User natural language query regarding cancer biomarkers, disease genes, or clinical phenotypes.
- **Output**: Direct response or routing call to specialized sub-agents.
- **AWS Dependencies**: Amazon Bedrock Agent YAML schema format.
- **Logic to Reuse Locally**:
  - Task breakdown and prompt engineering patterns.
  - Prompt structure for agent self-reflection, planning, and tool selection.
- **What Must Be Replaced**:
  Convert YAML prompt specifications into Python prompt templates (`PROMPTS["supervisor"]`) used by our local Python orchestrator.

---

### 4. Specialized Tooling (Biomarker Analysis & Statistical Tools)

#### **File**: Action Groups / Statistical & RAG Functions (`ActionGroups/clinical_evidence_search`)

- **What It Does**:
  Queries clinical research evidence (e.g. PubMed / Knowledge Bases) and performs statistical analysis (e.g. Kaplan-Meier survival curves, differential expression).
- **Important Functions / Classes**:
  - `retrieve_evidence(query)`: RAG literature search.
  - `calculate_survival(data)`: Runs statistical survival regression.
- **Input**: Disease entity names, gene symbols, or patient cohort tables.
- **Output**: Evidence snippets, p-values, hazard ratios, and visualization plots.
- **AWS Dependencies**: Amazon Bedrock Knowledge Bases, SageMaker Processing Jobs, S3 storage.
- **Logic to Reuse Locally**:
  - Python statistical logic (`lifelines`, `scipy.stats`, `pandas`).
  - Literature/provenance lookup using local PrimeKG tabular datasets.
- **What Must Be Replaced**:
  Execute Python statistical functions directly within local Python worker threads, replacing SageMaker jobs and S3 storage with local disk storage (`data/processed/`).

---

## Local Architecture Mapping & Replacement Roadmap

```text
+-----------------------------------------------------------------------+
|                         LOCAL USER INTERFACE                          |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    LOCAL PYTHON ORCHESTRATOR                          |
|  - Manages session state and conversation history                      |
|  - Parses user intent & routes to specialized local agents            |
+-----------------------------------------------------------------------+
                  |                                     |
                  v                                     v
+------------------------------------+ +--------------------------------+
|     LOCAL BIOMEDICAL DB AGENT      | |      LOCAL BIOMARKER AGENT    |
| - Text-to-SQL logic                | | - Query PrimeKG relationships  |
| - Generates safe SQL SELECT query  | | - Analyze Gene-Disease-Drug  |
+------------------------------------+ +--------------------------------+
                  \                                     /
                   v                                   v
+-----------------------------------------------------------------------+
|                          LOCAL PYTHON TOOLS                           |
|  - mysql_tool.py (Parameterized read-only queries)                    |
|  - analytics_tool.py (Local statistical analysis)                     |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         LOCAL MYSQL DATABASE                          |
|  - Contains tables: genes, diseases, drugs, pathways, relationships  |
+-----------------------------------------------------------------------+
```

---

## Key Takeaways for Local Implementation

1. **Zero AWS Footprint**: Complete removal of AWS SDK (`boto3`), Bedrock Agent runtimes, Redshift Data API, S3, and SageMaker.
2. **Modular Tool Calling**: Local Python agents will call parameterized Python functions (`execute_sql`, `search_primekg`) rather than remote Lambda functions.
3. **Local Database Security**: Enforce strictly read-only parameterized MySQL database queries with schema introspection tools.
