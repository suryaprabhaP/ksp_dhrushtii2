[CERTAIN] Yes. The previous discussion can be rewritten into a **clean, evidence-controlled architectural finding and remediation section** suitable for your verification/risk document. I would remove the overclaim that “512 MB OOM is 100% proven” and preserve the distinction between proven code behavior and load-test-dependent outcomes.

## Document RAG — Memory Retention & Retrieval Architecture

### 1. Finding

**Component:** `app/engine/catalyst_document_store.py` (`CatalystCloudDocumentStore`)

**Severity:** 🔴 **CRITICAL**

**Finding:** `[CERTAIN]` The current `CatalystCloudDocumentStore` retains document chunks inside the AppSail process memory and performs retrieval by traversing that in-memory collection. Although document data is also persisted to Catalyst cloud storage, that persistence currently operates independently of the in-memory representation and does not eliminate the AppSail memory dependency.

The architectural problem is therefore **not that Catalyst cloud storage is unavailable**. The problem is that the current repository implementation does not use the cloud store as the authoritative retrieval source.

### 2. Current Data Flow

```text
Officer
   │
   ▼
AppSail
   │
   ▼
PDF Upload
   │
   ├──────────────► file_bytes
   │                     │
   │                     ▼
   │                PDF extraction
   │                     │
   │                     ▼
   │                  raw_text
   │                     │
   │                     ▼
   │                 chunk_texts
   │                     │
   │                     ▼
   │              DocumentChunk objects
   │                     │
   │                     ▼
   │            self._sessions[session_id]
   │                     │
   │                     ▼
   │               AppSail RAM
   │
   └──────────────► Catalyst cloud persistence
                         │
                         ▼
                    Backup/archive
```

### 3. Retrieval Problem

The current retrieval path is:

```text
User Query
    │
    ▼
CatalystCloudDocumentStore
    │
    ▼
self._sessions[session_id]["chunks"]
    │
    ▼
Iterate through chunks in Python
    │
    ▼
String/token matching
    │
    ▼
Relevant chunks
```

Therefore, the query does **not** retrieve directly from the persistent Catalyst repository.

The critical architectural issue is:

> **Persistent cloud storage exists, but the active RAG retrieval path remains memory-resident.**

---

# 4. Why This Creates an OOM Risk

### `[CERTAIN]`

The following behaviors create the risk:

1. PDF bytes are loaded into application memory during ingestion.
2. Extracted document text is materialized in memory.
3. Chunk objects are materialized in memory.
4. Chunks are retained inside the session's in-memory collection.
5. Retrieval traverses that collection rather than querying the persistent repository.
6. Therefore, accumulated document volume can increase the AppSail process's memory footprint.

### `[NOT YET PROVEN]`

The exact statement:

> `50 officers × 5 MB PDFs → 512 MB → OOM`

requires empirical load testing.

File size does not equal Python heap consumption. PDF parsing, Unicode strings, object overhead, duplication, concurrency, and allocator behavior can significantly change actual memory usage.

Therefore the correct risk statement is:

> **The implementation creates an unbounded memory-growth path that can lead to AppSail OOM under sufficiently high document volume and/or concurrency. The exact failure threshold must be established through load testing.**

---

# 5. Architectural Objective

The solution is **not to introduce another document architecture**.

The existing abstraction is correct:

```text
DocumentAgent
      │
      ▼
IDocumentRepository
      │
      ▼
CatalystCloudDocumentStore
```

`DocumentAgent` already depends on `IDocumentRepository`, allowing the storage implementation to change without redesigning the agent layer.

Therefore:

> **Modify the existing `CatalystCloudDocumentStore`; do not redesign `DocumentAgent`.**

---

# 6. Target Architecture

```text
                         POLICE OFFICER
                               │
                               ▼
                         AppSail API
                               │
                    ┌──────────┴──────────┐
                    │                     │
                  Upload                 Query
                    │                     │
                    ▼                     ▼
             Document Validation    Retrieval Request
                    │                     │
                    ▼                     ▼
             Temporary Processing   Catalyst Repository
                    │                     │
                    ▼                     ▼
                 Chunking          Bounded Retrieval
                    │                     │
                    ▼                     ▼
            Catalyst Persistent     Top-N Relevant
                Storage                Chunks
                    │                     │
                    └──────────┬──────────┘
                               ▼
                         RAG Context
                               │
                               ▼
                            LLM/Zia
                               │
                               ▼
                         Analyst Response
```

The key architectural transition is:

```text
BEFORE
Catalyst = backup
AppSail RAM = active document database

AFTER
Catalyst = authoritative document repository
AppSail RAM = temporary processing + bounded retrieval results
```

---

# 7. Storage Responsibility

The responsibilities should be separated:

| Layer                           | Responsibility                                       |
| ------------------------------- | ---------------------------------------------------- |
| **AppSail**                     | API, validation, orchestration, temporary processing |
| **Catalyst persistent storage** | Authoritative document/chunk persistence             |
| **Data Store / NoSQL**          | Document metadata and persisted retrieval records    |
| **Cache**                       | Optional short-lived acceleration                    |
| **RAG layer**                   | Retrieve only relevant chunks                        |
| **LLM/Zia**                     | Reason over retrieved context                        |

The important rule is:

> **Never use AppSail process memory as the authoritative document corpus.**

---

# 8. Required Changes to `CatalystCloudDocumentStore`

### Change 1 — Remove persistent chunk retention

Current:

```python
self._sessions[session_id]["chunks"].extend(new_chunks)
```

This should no longer be the authoritative storage mechanism.

The repository should persist the chunks to Catalyst and release the temporary in-process objects after ingestion.

---

### Change 2 — Cloud-backed retrieval

Current:

```text
session chunks
      ↓
Python loop
      ↓
string matching
```

Target:

```text
query
  ↓
Catalyst persistent repository
  ↓
bounded result set
  ↓
relevant chunks
```

**Important:** Do not hard-code “ZCQL” as the architectural requirement yet.

The requirement is:

> **Retrieval must be cloud-backed and bounded.**

ZCQL can then be evaluated as the appropriate Catalyst mechanism for the actual schema and query requirements.

---

### Change 3 — Preserve session isolation

Every persisted document/chunk must remain associated with its session:

```text
session_id
    │
    ├── document A
    ├── document B
    └── document C
```

A query for:

```text
session_A
```

must never retrieve:

```text
session_B
```

---

### Change 4 — Bound retrieval

The application must never perform:

```text
500 documents
      ↓
load all chunks
      ↓
RAM
      ↓
search
```

Instead:

```text
500 documents
      ↓
cloud-side filtering
      ↓
bounded result set
      ↓
AppSail
```

For example, the application may retrieve only the top `N` relevant chunks required to construct the LLM context.

The exact `N` should be determined by your existing RAG prompt/context requirements rather than arbitrarily introducing a new value.

---

# 9. Acceptance Gates

I would make these the official verification gates.

### GATE-DOC-01 — Persistent Authority

**Requirement:** Catalyst persistent storage is the authoritative document/chunk repository.

**PASS:** Restarting AppSail does not delete uploaded evidence.

---

### GATE-DOC-02 — No Corpus Retention

**Requirement:** `self._sessions` does not retain the complete document corpus.

**PASS:** Document volume can grow without creating an equivalent permanent Python-memory structure.

---

### GATE-DOC-03 — Bounded Retrieval

**Requirement:** A query retrieves only the required subset of document chunks.

**PASS:**

```text
Large corpus
    ↓
bounded retrieval
    ↓
small result set
    ↓
LLM
```

---

### GATE-DOC-04 — Session Isolation

**Requirement:** Retrieval is scoped to the requesting session.

**PASS:** Session A cannot retrieve evidence belonging to Session B.

---

### GATE-DOC-05 — Persistence Across Restart

**Requirement:** Evidence survives AppSail container restart.

**PASS:**

```text
Upload
 ↓
Catalyst
 ↓
AppSail restart
 ↓
Query
 ↓
Evidence recovered
```

---

### GATE-DOC-06 — Memory Load Test

**Requirement:** Demonstrate that memory does not grow proportionally with the entire document corpus.

Measure:

```text
RSS memory
CPU
ingestion latency
retrieval latency
error rate
container restart count
```

Run progressively larger workloads and record the actual threshold.

---

# 10. Final Risk-Matrix Entry

I recommend replacing the original row with this:

| Finding                                                                                                                                                                                                                          | Evidence                                     | Impact                                                                                                                                                      | Severity        | Remediation                                                                                                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`CatalystCloudDocumentStore` retains document chunks in AppSail process memory and performs retrieval through an in-memory Python collection. Catalyst persistence currently does not remove this runtime memory dependency.** | **[CERTAIN]** Static implementation evidence | Memory usage can grow with accumulated session documents and concurrent workloads, creating an AppSail OOM risk. Exact OOM threshold requires load testing. | 🔴 **CRITICAL** | Preserve `IDocumentRepository` and `CatalystCloudDocumentStore`, but make Catalyst persistent storage authoritative. Remove full-corpus retention from `self._sessions`, implement bounded cloud-backed retrieval, preserve session isolation, and validate memory behavior under concurrent load. |

## Principal Architect Decision

**[CERTAIN] Finding:** **VALID — CRITICAL risk.**

**[CERTAIN] Root cause:** **In-process document retention + in-memory retrieval.**

**[CERTAIN] Architectural direction:** **Move authoritative document/chunk state to Catalyst persistent storage.**

**[LIKELY] Implementation mechanism:** **Catalyst Data Store/NoSQL query-backed retrieval, subject to schema/query validation.**

**[UNPROVEN] Exact OOM threshold:** **Must be load-tested.**

**Decision:** 🟢 **APPROVE REMEDIATION DESIGN — DO NOT YET APPROVE THE IMPLEMENTATION.**

The next step should be to inspect the **actual `catalyst_document_store.py` implementation** and redesign only that component, preserving the existing `IDocumentRepository` contract. That gives you a minimal-diff, SOLID-compliant fix rather than creating a second RAG architecture.
