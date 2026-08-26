[Certain] **This is the layer I would design next: the Data Access / Tool Gateway.** It is the security-and-control boundary between your single LLM and every external data source. If we get this wrong, the rest of the architecture becomes fragile.

# 1. What the Tool Gateway actually does

The LLM should **never** directly access:

* PostgreSQL
* MySQL
* MongoDB
* Neo4j
* pgvector
* uploaded files
* APIs

Instead:

```text
                    SINGLE LLM
                        │
                        │ "I need this information"
                        ▼
              ┌─────────────────────┐
              │ AGENT ORCHESTRATOR  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   TOOL GATEWAY      │
              │                     │
              │ Auth                │
              │ Policy              │
              │ Validation          │
              │ Rate limits         │
              │ Scope               │
              │ Logging             │
              └──────────┬──────────┘
                         │
          ┌──────────────┼────────────────┐
          ▼              ▼                ▼
       SQL Tool       Graph Tool       RAG Tool
          │              │                │
          ▼              ▼                ▼
      PostgreSQL       Neo4j          pgvector
```

The LLM **requests an operation**.

The gateway decides whether that operation is allowed.

---

# 2. Don't give the LLM arbitrary tools

This is a common architectural mistake.

Bad:

```text
LLM
 ↓
execute_sql("whatever")
```

Better:

```text
LLM
 ↓
query_cases(
    crime_type="robbery",
    year=2025,
    district="..."
)
```

Even better for complex systems:

```text
LLM
 ↓
Tool Request
 ↓
Policy Engine
 ↓
Tool Executor
```

The LLM asks for **capabilities**, not unrestricted system access.

---

# 3. Tool categories

I'd divide your tools into six groups.

```text
TOOLS
│
├── Structured Data
│   ├── SQL Query
│   ├── Aggregation
│   └── Statistics
│
├── Graph
│   ├── Relationship Search
│   ├── Path Search
│   └── Network Analysis
│
├── Document
│   ├── Semantic Search
│   ├── Document Retrieval
│   └── Source Inspection
│
├── Analytical
│   ├── Geospatial
│   ├── Time-series
│   ├── Similarity
│   └── Anomaly Detection
│
├── Investigation
│   ├── Case Search
│   ├── Person Search
│   └── Evidence Search
│
└── System
    ├── Memory
    ├── Data Source Discovery
    └── Investigation Context
```

---

# 4. Tool registry

Don't hard-code everything into the LLM prompt.

Create a **Tool Registry**.

```text
Tool Registry

tool_id
tool_name
description
input_schema
output_schema
required_permission
data_sources
risk_level
enabled
version
```

Example:

```text
tool_id:
TOOL-CASE-SEARCH

name:
search_cases

input:
{
    crime_type,
    date_from,
    date_to,
    location
}

permission:
CASE_READ

risk:
LOW
```

The LLM sees the tool's schema.

It does **not** see database credentials or internal implementation.

---

# 5. Tool invocation lifecycle

This is the flow I'd implement:

```text
Officer
   │
   ▼
Question
   │
   ▼
Single LLM
   │
   ▼
Tool Selection
   │
   ▼
Tool Request
   │
   ▼
Schema Validator
   │
   ▼
Authorization Engine
   │
   ▼
Investigation Scope Check
   │
   ▼
Policy Engine
   │
   ▼
Tool Executor
   │
   ▼
Data Source
   │
   ▼
Result Sanitization
   │
   ▼
Evidence Wrapper
   │
   ▼
LLM
```

That **result sanitization → evidence wrapper** step is important for hallucination control.

---

# 6. Example: SQL

Officer asks:

> "How many robbery cases occurred in Chennai during 2025?"

The LLM might produce:

```text
Tool:
search_cases

Parameters:
crime_type = robbery
location = Chennai
date_from = 2025-01-01
date_to = 2025-12-31
```

Gateway checks:

```text
✓ Officer authenticated
✓ Officer has CASE_READ
✓ Investigation allows case data
✓ Chennai within jurisdiction
✓ Parameters valid
✓ Query allowed
```

Then:

```text
SQL Tool
   ↓
PostgreSQL
   ↓
247 records
```

The gateway returns:

```text
{
    "status": "success",
    "record_count": 247,
    "source": "case_database",
    "source_ids": [...]
}
```

The LLM can say:

> "247 robbery cases were found..."

because the number came from the tool.

---

# 7. SQL firewall

For arbitrary SQL connections, add another boundary.

```text
                 LLM
                  │
                  ▼
             SQL Request
                  │
                  ▼
          ┌───────────────┐
          │ SQL Firewall  │
          └───────┬───────┘
                  │
       ┌──────────┼───────────┐
       ▼          ▼           ▼
    Syntax     Permission   Scope
     Check       Check       Check
       │          │           │
       └──────────┼───────────┘
                  ▼
             Query Limits
                  │
                  ▼
          Read-only Executor
                  │
                  ▼
              Database
```

For the MVP, I would make all connected databases **read-only**.

No:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
```

---

# 8. Graph tool

For Neo4j, don't let the model generate arbitrary Cypher either.

Provide controlled operations.

Example:

```text
find_connected_people
find_shared_vehicles
find_case_relationships
find_shortest_relationship_path
find_common_locations
```

Officer asks:

> "Find people connected to Case 4821 through a vehicle."

LLM:

```text
find_shared_vehicles(
    case_id="4821"
)
```

Tool:

```text
Case 4821
   ↓
Vehicle V883
   ↓
Person P1024
Person P1198
```

The response contains evidence IDs.

---

# 9. RAG tool

RAG needs the same discipline.

Instead of:

```text
vector_search(query)
```

use:

```text
search_documents(
    query,
    investigation_id,
    case_id,
    document_type,
    date_range
)
```

The gateway automatically adds:

```text
authorization filters
classification filters
investigation filters
```

The LLM cannot override them.

---

# 10. Tool result contract

Every tool should return a common format.

```text
ToolResult

├── status
├── tool_id
├── request_id
├── data
├── source_records
├── evidence_ids
├── limitations
├── confidence
├── retrieved_at
└── execution_metadata
```

Example:

```text
{
  "status": "success",

  "data": {
    "count": 247
  },

  "source_records": [
    "CASE-1821",
    "CASE-1822"
  ],

  "evidence_ids": [
    "E-8812",
    "E-8813"
  ],

  "limitations": []
}
```

Now your hallucination layer has something concrete to validate.

---

# 11. Tool risk levels

Not every tool has the same risk.

I'd classify:

```text
LOW
│
├── case count
├── simple search
└── aggregation

MEDIUM
│
├── graph traversal
├── cross-case correlation
└── semantic analysis

HIGH
│
├── predictive analysis
├── identity matching
├── network inference
└── sensitive evidence retrieval

CRITICAL
│
└── any action affecting external systems
```

For your first version:

> **Make every tool read-only.**

That dramatically reduces your attack surface.

---

# 12. Tool permissions

Permissions should be capability-based.

Example:

```text
Officer Role
│
├── CASE_READ
├── PERSON_READ
├── VEHICLE_READ
├── DOCUMENT_READ
├── GRAPH_ANALYSIS
└── ANALYTICS_RUN
```

Another officer might have:

```text
Investigator
│
├── CASE_READ
├── PERSON_READ
├── DOCUMENT_READ
├── GRAPH_ANALYSIS
└── EVIDENCE_READ
```

The LLM doesn't determine permissions.

The **authorization service** does.

---

# 13. Investigation scope

This is particularly important because officers can upload their own data.

Suppose:

```text
Investigation A
├── Case A
├── data_A.xlsx
└── reports_A.pdf

Investigation B
├── Case B
├── data_B.csv
└── reports_B.pdf
```

Officer asks:

> "Find related cases."

The gateway should know whether cross-investigation access is permitted.

```text
Question
   ↓
Investigation Context
   ↓
Allowed Sources
   ↓
Tool Query
```

Not:

```text
Question
   ↓
Search entire database
```

---

# 14. Tool gateway + memory

Memory also goes through the gateway.

The LLM should not freely write arbitrary memory.

Instead:

```text
LLM
 ↓
Memory Tool
 ↓
Memory Policy
 ↓
Allowed memory type?
 ↓
Store
```

For example:

```text
WORKING MEMORY
✓

INVESTIGATION CONTEXT
✓

USER PREFERENCE
maybe

NEW POLICE FACT
✗
```

A discovered police fact belongs in the authoritative data/evidence system, not blindly in agent memory.

---

# 15. Tool gateway + hallucination control

This is where the architecture becomes strong.

```text
              LLM
               │
          Tool Request
               │
               ▼
        TOOL GATEWAY
               │
       ┌───────┼────────┐
       ▼       ▼        ▼
    Auth    Policy   Validation
       │       │        │
       └───────┼────────┘
               ▼
          TOOL EXECUTOR
               │
               ▼
          DATA SOURCE
               │
               ▼
        RAW TOOL RESULT
               │
               ▼
       RESULT VALIDATOR
               │
               ▼
       EVIDENCE WRAPPER
               │
               ▼
              LLM
```

The model gets **grounded results**, not raw uncontrolled access.

---

# 16. Tool gateway + audit

Every invocation becomes an audit event:

```text
TOOL INVOCATION

request_id
officer_id
investigation_id

tool_id
tool_version

input_parameters

authorization_result

execution_time

data_source

records_returned

evidence_ids

result_hash

timestamp
```

So later:

> "Why did the agent access these 42 records?"

You can reconstruct the exact chain.

---

# 17. One thing I would NOT do

Don't create a giant:

```text
AgentTools
├── SQL
├── Neo4j
├── MongoDB
├── RAG
├── Python
├── Files
├── APIs
├── Internet
├── Shell
└── ...
```

and give everything to the LLM.

That's a security nightmare.

Instead:

```text
                  TOOL REGISTRY
                       │
                       ▼
                TOOL GATEWAY
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Allowed tools   Contextual tools  Restricted
        │              │              │
        ▼              ▼              ▼
     SQL Tool       Graph Tool      Special Tool
```

**Expose the minimum capability necessary for the current investigation.**

---

# 18. Final architecture

This is the version I'd put into your system design document:

```text
                         ┌───────────────┐
                         │    OFFICER    │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │  ANALYST UI   │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ AUTH + SESSION CONTEXT │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  AGENT ORCHESTRATOR    │
                    │                        │
                    │     SINGLE LLM         │
                    └────────────┬───────────┘
                                 │
                           Tool Request
                                 │
                                 ▼
                    ╔════════════════════════╗
                    ║     TOOL GATEWAY       ║
                    ║                        ║
                    ║ • Tool Registry        ║
                    ║ • Authentication       ║
                    ║ • Authorization        ║
                    ║ • Policy Engine        ║
                    ║ • Scope Enforcement     ║
                    ║ • Schema Validation    ║
                    ║ • Rate Limiting        ║
                    ║ • Query Firewall       ║
                    ╚═══════════╤════════════╝
                                │
             ┌──────────────────┼───────────────────┐
             ▼                  ▼                   ▼
        ┌─────────┐       ┌─────────┐         ┌─────────┐
        │ SQL     │       │ Graph   │         │ RAG     │
        │ Tool    │       │ Tool    │         │ Tool    │
        └────┬────┘       └────┬────┘         └────┬────┘
             │                 │                    │
             ▼                 ▼                    ▼
        PostgreSQL           Neo4j              pgvector
             │                 │                    │
             └─────────────────┼────────────────────┘
                               │
                               ▼
                      RESULT VALIDATOR
                               │
                               ▼
                       EVIDENCE WRAPPER
                               │
                               ▼
                             LLM
                               │
                               ▼
                    HALLUCINATION CONTROL
                               │
                               ▼
                         OUTPUT POLICY
                               │
                               ▼
                            OFFICER

══════════════════════════════════════════════════════════
                         AUDIT PLANE
══════════════════════════════════════════════════════════
Tool requests → Authorization → Queries → Results →
Evidence → Claims → Response → Officer action
```

### The architectural contract is simple:

**LLM = reasoning**

**Orchestrator = decision/control**

**Tool Gateway = enforcement**

**Tools = capabilities**

**Databases = truth**

**Evidence Validator = verification**

**Audit = accountability**

That separation is what makes your single-LLM architecture viable for a police analyst system.
