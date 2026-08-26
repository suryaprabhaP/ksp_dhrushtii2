[Certain] **Hallucination control should be its own architecture layer, not just a prompt saying “don't hallucinate.”** For a police analyst agent, that's nowhere near enough because a plausible but unsupported statement can contaminate an investigation.

I would design it as a **controlled evidence pipeline**:

# Hallucination-Control Architecture

```text id="0g4t7j"
                    OFFICER QUESTION
                          │
                          ▼
                 ┌──────────────────┐
                 │  INPUT ANALYSIS   │
                 │ Intent + Entities │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ CLAIM PLANNER     │
                 │ What must be      │
                 │ established?      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ RETRIEVAL / TOOLS │
                 └────────┬─────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
           SQL/DB       Graph        RAG
              │           │           │
              └───────────┼───────────┘
                          ▼
                 ┌──────────────────┐
                 │ EVIDENCE FUSION  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ CLAIM VALIDATOR  │
                 │                  │
                 │ Supported?       │
                 │ Contradicted?    │
                 │ Missing evidence?│
                 └────────┬─────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 PASS         FAIL
                    │           │
                    ▼           ▼
               LLM ANSWER    REFUSE /
                    │        CLARIFY /
                    │        QUALIFY
                    ▼
             ┌───────────────┐
             │ OUTPUT GUARD  │
             │ Evidence refs │
             │ Confidence    │
             │ Classification│
             └───────┬───────┘
                     ▼
                  OFFICER
```

---

# 1. The fundamental rule

The agent should operate under:

> **No evidence → no factual claim.**

Not:

> "The LLM is highly confident."

Those are completely different things.

For example:

### Bad

> "The suspect was present at the scene."

No evidence attached.

### Good

> "The available records indicate that Person P1024 was recorded at the location at 21:14. This does not establish that the person participated in the crime."

That distinction is exactly what you want.

---

# 2. Separate facts from inference

Every generated statement should internally belong to a category:

```text id="4h90k7"
FACT
│
├── Directly supported by source
│
INFERENCE
│
├── Derived from multiple facts
│
HYPOTHESIS
│
├── Possible explanation
│
UNKNOWN
│
└── Insufficient evidence
```

The model should never silently transform:

```text
FACT
   ↓
INFERENCE
   ↓
HYPOTHESIS
```

into:

```text
FACT
```

---

# 3. Claim-level verification

This is the part I'd consider **non-negotiable**.

Don't validate only the entire answer.

Break it into claims.

Example answer:

> "Case 4821 and Case 4177 occurred within 3 km of each other, involved the same vehicle, and have similar modus operandi."

Break it into:

```text id="rl2av4"
Claim C1
Distance < 3 km

Claim C2
Same vehicle appears in both cases

Claim C3
Similar modus operandi
```

Then independently validate:

```text id="e3a8mb"
C1 → GIS/PostgreSQL → PASS

C2 → Neo4j → PASS

C3 → semantic similarity + analyst rules → PASS
```

Only then can the answer be generated as a factual statement.

---

# 4. Evidence must be attached to claims

Think:

```text id="v9o1uo"
CLAIM
  │
  ├── Evidence ID
  ├── Source record
  ├── Retrieval timestamp
  ├── Evidence type
  └── Verification status
```

Example:

```text id="2vcm9b"
Claim:
"Vehicle V883 appears in both cases."

Evidence:
E1821
E1933

Source:
Case 4821
Case 4177

Verification:
PASS
```

The UI can expose:

> **Evidence: 2 sources**

and allow the officer to inspect them.

---

# 5. Retrieval must be authorization-aware

This is subtle but extremely important.

Don't do:

```text id="9v7p5d"
Question
 ↓
Vector Search
 ↓
Top 10 documents
```

because the vector database might retrieve documents the officer isn't authorized to see.

Instead:

```text id="u3q8bz"
Officer identity
       ↓
Authorization policy
       ↓
Allowed datasets
       ↓
Retrieval filters
       ↓
Semantic search
```

So the actual retrieval becomes:

```text id="8w3n4s"
Semantic similarity
+
Case permission
+
Role permission
+
Classification
+
Jurisdiction
+
Investigation scope
```

Security and hallucination control therefore reinforce each other.

---

# 6. Don't let the LLM invent database results

This is another hard boundary.

The LLM should **never directly fabricate structured facts**.

Instead:

```text id="0ezl1y"
LLM
 │
 ├── "I need cases from 2025"
 │
 ▼
SQL Tool
 │
 ▼
Actual database result
 │
 ▼
LLM
```

For example:

```text id="v6s5lq"
LLM:
"Find all robbery cases within 5 km."

        ↓

SQL/GIS Tool

        ↓

[
Case 4812,
Case 4821,
Case 4901
]

        ↓

LLM summarizes
```

The model isn't allowed to invent `Case 4932`.

---

# 7. Tool result integrity

Every tool response should have a structured envelope:

```text id="x8p7ll"
ToolResult

tool_call_id
tool_name

status

query
parameters

records
record_count

source
retrieved_at

authorization_context

integrity_hash
```

Then the LLM receives:

```text id="a5w9yq"
RESULT:
3 records returned

SOURCE:
PostgreSQL

RECORD IDS:
4812
4821
4901
```

It cannot claim that 10 records were found.

---

# 8. Contradiction detection

Hallucination control isn't only:

> "Do I have evidence?"

It must also ask:

> **"Does the evidence disagree?"**

Example:

```text id="j1v8p0"
Source A:
Vehicle color = Black

Source B:
Vehicle color = White
```

The agent should NOT produce:

> "The vehicle was black."

Instead:

> "The records contain conflicting descriptions: one identifies the vehicle as black and another as white."

That's a much safer analytical behavior.

---

# 9. Temporal validation

Police investigations are heavily time-dependent.

The system must detect impossible or inconsistent timelines.

Example:

```text id="x1q2k8"
Arrest:
20:00

Reported sighting:
21:00
```

That doesn't automatically mean one record is wrong, but the inconsistency should be surfaced.

So add:

```text id="k9r0q4"
Timeline Validator
      │
      ├── ordering
      ├── temporal overlap
      ├── impossible timestamps
      └── conflicting events
```

---

# 10. Entity resolution uncertainty

Suppose:

```text id="j6x0v4"
Ravi Kumar
R. Kumar
Ravi K.
```

The system shouldn't automatically decide:

> "These are the same person."

Instead:

```text id="1a6w5j"
Candidate Match
       │
       ├── Name similarity
       ├── DOB
       ├── Address
       ├── Identifier
       └── Other attributes
       │
       ▼
Confidence
       │
       ├── High → potentially auto-link
       ├── Medium → review
       └── Low → keep separate
```

And the UI should distinguish:

**Verified identity** vs **possible identity match**.

---

# 11. Confidence must not be a single LLM number

Avoid:

```text
AI confidence: 94%
```

That sounds scientific but can be meaningless.

Instead use **evidence status**.

```text id="qk7f8b"
SUPPORTED
PARTIALLY_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
UNVERIFIED
```

If you need numerical confidence for specific analytical models, keep it tied to that model and methodology—not to the LLM's subjective confidence.

---

# 12. The LLM gets constrained output

I would make the LLM produce structured analytical objects internally:

```text id="t3w7nq"
{
    "claim": "...",
    "claim_type": "inference",
    "evidence_ids": ["E1821", "E1933"],
    "support_status": "supported",
    "limitations": ["..."]
}
```

Then a validator checks it.

Only after validation does the system turn it into natural language.

---

# 13. The verification loop

This is the architecture I would use:

```text id="6tx8x5"
             LLM
              │
              ▼
        Draft Analysis
              │
              ▼
        Claim Extractor
              │
              ▼
       Evidence Validator
              │
       ┌──────┴──────┐
       ▼             ▼
     VALID          INVALID
       │             │
       ▼             ▼
   Continue       Remove /
       │           Qualify /
       │           Re-retrieve
       │             │
       │             ▼
       │        Evidence Search
       │             │
       └─────────────┘
              │
              ▼
         Final Answer
```

Notice:

**The LLM doesn't get the final say on whether its own statement is valid.**

---

# 14. But don't create another LLM

You told me:

> **We only have one model.**

So I would **not** propose a second LLM as a hallucination checker.

Instead:

```text id="r1y2v4"
ONE LLM
   +
Deterministic Validators
   +
Database Verification
   +
Graph Verification
   +
Schema Validation
   +
Evidence Matching
   +
Rule Engine
```

This is actually better for your architecture.

Use the LLM for:

* interpretation
* planning
* synthesis
* explanation

Use deterministic systems for:

* exact numbers
* IDs
* dates
* permissions
* relationships
* existence checks
* evidence validation
* schema validation

---

# 15. Hallucination firewall

I'd put an explicit **output firewall** before the officer sees the answer.

```text id="9b0m5d"
                    LLM OUTPUT
                         │
                         ▼
              ┌────────────────────┐
              │ HALLUCINATION      │
              │ FIREWALL           │
              └─────────┬──────────┘
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Claim Check     Evidence Check    Policy Check
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                ┌───────────────┐
                │ Decision       │
                └───────┬───────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            PASS     QUALIFY     BLOCK
              │         │         │
              ▼         ▼         ▼
           Answer    "Insufficient   Refusal
                     evidence"
```

---

# 16. What happens when evidence is insufficient?

This is critical.

The agent must be comfortable saying:

> **"I cannot establish this from the available records."**

Not:

> "Based on the available evidence, it is likely..."

unless there is actually a defensible analytical basis for that inference.

There should be explicit refusal states:

```text id="8n1f8d"
NO_DATA
INSUFFICIENT_DATA
CONFLICTING_DATA
UNAUTHORIZED_DATA
UNVERIFIED_RELATIONSHIP
LOW_CONFIDENCE_MATCH
TOOL_FAILURE
```

---

# 17. Hallucination control + audit

Now connect it to the architecture we already built.

```text id="kh1tqz"
Claim
 │
 ▼
Evidence
 │
 ▼
Validator
 │
 ▼
Validation Result
 │
 ▼
Final Answer
 │
 ▼
AUDIT
```

Audit records:

```text id="d2g5la"
Claim ID
Evidence IDs
Validation rule
Validation result
Tool results
Final disposition
```

Therefore a supervisor can later ask:

> "Why did the agent say this?"

And the system can answer:

```text id="0ec0q8"
Claim C182
    ↓
Evidence E1821
Evidence E1933
    ↓
Validator V821
    ↓
SUPPORTED
    ↓
Included in response
```

---

# 18. The complete hallucination-control stack

I'd lock this into the architecture:

```text id="0x4y1a"
┌──────────────────────────────────────────────┐
│            HALLUCINATION CONTROL             │
├──────────────────────────────────────────────┤
│                                              │
│  1. Input / Intent Validation                │
│                    ↓                         │
│  2. Claim Planning                           │
│                    ↓                         │
│  3. Authorized Retrieval                     │
│                    ↓                         │
│  4. Tool-grounded Facts                      │
│                    ↓                         │
│  5. Evidence Fusion                          │
│                    ↓                         │
│  6. Claim-level Validation                   │
│                    ↓                         │
│  7. Contradiction Detection                  │
│                    ↓                         │
│  8. Temporal Validation                      │
│                    ↓                         │
│  9. Entity Resolution Checks                 │
│                    ↓                         │
│ 10. Structured Output Validation             │
│                    ↓                         │
│ 11. Output Firewall                          │
│                    ↓                         │
│ 12. Evidence-linked Response                 │
│                                              │
└──────────────────────────────────────────────┘
```

### The governing rule:

> **The LLM may propose an interpretation. It may not manufacture a fact.**

And the stronger version:

> **Every factual claim shown to an officer must either be traceable to authoritative data or explicitly labeled as an inference/hypothesis with its supporting evidence and limitations.**

That's the hallucination architecture I would put alongside your **Memory + Security + Audit + Data architectures**.
