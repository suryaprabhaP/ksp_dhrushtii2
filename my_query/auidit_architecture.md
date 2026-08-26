[Certain] **This is the version I would lock into the system architecture.** The earlier version was a conventional audit system; this one is designed specifically for an **AI-powered police investigation platform**, where we need to reconstruct the entire causal chain from officer action → agent → data → evidence → output → human action.

# Audit Architecture — Final Version

## 1. Core objective

The audit system must answer five questions for **every important investigation action**:

> **Who** did it?
> **What** did they ask/do?
> **What did the AI/system access?**
> **What evidence influenced the result?**
> **What happened afterward?**

The audit system should therefore be **independent of the LLM's own explanation**.

---

# 2. High-level architecture

```text
                         POLICE OFFICER
                              │
                              ▼
                     ┌──────────────────┐
                     │   Analyst UI     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ API Gateway/WAF  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Authentication   │
                     │ + Authorization  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Agent System     │
                     │                  │
                     │ Single LLM       │
                     │ Memory Manager   │
                     │ Tool Orchestrator│
                     └────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
      Memory               Tool Calls          Analysis
          │                   │                   │
          ▼                   ▼                   ▼
     Redis/PG          PostgreSQL/Neo4j      Python/ML
                              │
                              ▼
                       Evidence Layer
                              │
                              ▼
                       Verification
                              │
                              ▼
                        Final Output
                              │
                              ▼
                       HUMAN ACTION


══════════════════════════════════════════════════════════════
                    AUDIT PLANE
══════════════════════════════════════════════════════════════

Every important event
        │
        ▼
┌─────────────────────┐
│   Audit Event       │
│                     │
│ request_id          │
│ agent_run_id        │
│ tool_call_id        │
│ actor               │
│ action              │
│ resource            │
│ authorization       │
│ evidence            │
│ result              │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Event Stream │
    └──────┬───────┘
           │
     ┌─────┼──────────────┐
     ▼     ▼              ▼
 Audit DB  Immutable     Security
           Archive       Analytics
     │        │              │
     │        │              ▼
     │        │           Alerts
     │        │
     └────────┴──────────────┐
                             ▼
                       AUDIT DASHBOARD
```

The important concept is that **Audit is a separate plane from the application/data plane**.

---

# 3. The causal audit chain

This is the heart of the architecture.

Suppose the officer asks:

> "Find cases similar to Case 4821."

The system doesn't create one log entry.

It creates a **causally connected chain**.

```text
USER ACTION
    │
    ▼
REQUEST
    │
    ▼
AGENT RUN
    │
    ├──────────────┐
    ▼              ▼
MEMORY ACCESS    AUTHORIZATION
    │
    ▼
TOOL CALL
    │
    ▼
DATABASE QUERY
    │
    ▼
RETRIEVED RECORDS
    │
    ▼
EVIDENCE SET
    │
    ▼
ANALYSIS
    │
    ▼
VERIFICATION
    │
    ▼
FINAL OUTPUT
    │
    ▼
HUMAN ACTION
```

Every node gets an identifier.

```text
request_id
     │
     └── agent_run_id
             │
             ├── memory_operation_id
             ├── authorization_id
             ├── tool_call_id
             ├── database_query_id
             ├── evidence_id
             ├── verification_id
             └── response_id
```

Now you can reconstruct the entire investigation step.

---

# 4. Audit event schema

Every event should follow a common structure.

```text
AuditEvent

event_id
timestamp

actor
actor_role

request_id
session_id
agent_run_id

event_type
action
status

resource_type
resource_id

case_id
investigation_id

authorization_policy
authorization_decision

tool_name
tool_call_id

query_id
query_hash

source_record_ids
evidence_ids

data_classification

model_id
model_version

result_reference

previous_event_hash
event_hash
```

Notice something important:

**We store references to sensitive data, not unnecessary copies of the sensitive data itself.**

That reduces audit-system exposure.

---

# 5. Don't store chain-of-thought

This is a deliberate design decision.

We don't need:

```text
LLM internal reasoning:
...
...
...
```

Instead we audit the observable execution:

```text
User Request
      ↓
Agent Run
      ↓
Intent / Plan
      ↓
Tools Selected
      ↓
Tools Executed
      ↓
Data Accessed
      ↓
Evidence Retrieved
      ↓
Validation
      ↓
Final Output
```

This is enough to establish accountability and reproducibility without trying to preserve hidden reasoning.

---

# 6. Evidence lineage

This is where your system becomes significantly stronger than a normal AI chatbot.

Suppose the AI says:

> "Case 4177 has a high similarity to Case 4821."

The audit system should be able to trace:

```text
CLAIM
"Case 4177 is highly similar"

       │
       ▼

ANALYSIS RUN
Similarity Analysis #A781

       │
       ├── Location similarity
       ├── Time similarity
       ├── Modus-operandi similarity
       └── Vehicle similarity

       │
       ▼

EVIDENCE

Record #10291
Record #10322
Record #10398

       │
       ▼

SOURCE

Case 4177
Original database record
```

Therefore:

**AI claim → analysis → evidence → source**

is always traceable.

---

# 7. Fact vs inference vs hypothesis

This is essential for a police system.

The audit system should distinguish:

```text
FACT
↓
Directly supported by source record

OBSERVATION
↓
System detected something in the data

INFERENCE
↓
Analytical conclusion derived from evidence

HYPOTHESIS
↓
Possible explanation requiring investigation

HUMAN DECISION
↓
Officer/supervisor action
```

Example:

```text
FACT:
Vehicle V883 appears in Case 4821.

        ↓

OBSERVATION:
Vehicle V883 also appears in Case 4177.

        ↓

INFERENCE:
The two cases may share a vehicle connection.

        ↓

HYPOTHESIS:
The cases may be related.

        ↓

HUMAN:
Investigator chooses to examine Case 4177.
```

The audit trail must preserve these distinctions.

**The AI must never silently upgrade a hypothesis into a fact.**

---

# 8. Tamper-resistant audit trail

The audit database itself must be protected.

Each event can be chained:

```text
Event 1
   │
   ▼
Hash 1

Event 2 + Hash 1
   │
   ▼
Hash 2

Event 3 + Hash 2
   │
   ▼
Hash 3
```

Conceptually:

```text
H1 = SHA256(Event1)

H2 = SHA256(Event2 + H1)

H3 = SHA256(Event3 + H2)
```

If someone modifies Event 2:

```text
H2 changes
   ↓
H3 becomes invalid
   ↓
Integrity failure detected
```

For production, I'd combine this with **append-only/immutable storage**.

---

# 9. Separate audit storage

Don't do this:

```text
Police Database
├── Cases
├── Persons
├── Vehicles
└── Audit Logs
```

Instead:

```text
                    APPLICATION
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       OPERATIONAL DATA        AUDIT PLANE
              │                     │
              ▼                     ▼
        PostgreSQL              Audit Store
        Neo4j                   Immutable Archive
        Documents               Security Analytics
```

This gives you a security boundary.

If the operational system is compromised, the attacker shouldn't automatically be able to rewrite the audit history.

---

# 10. Audit event pipeline

For the prototype:

```text
Application
     │
     ▼
Audit Service
     │
     ▼
PostgreSQL Audit DB
```

For production:

```text
Application
     │
     ▼
Audit Event
     │
     ▼
Message Queue
     │
     ▼
Audit Processor
     │
     ├──────────────┐
     ▼              ▼
Audit DB       Immutable Archive
     │
     ▼
Security Analytics
     │
     ▼
SIEM / Alerts
```

### Prototype

Use:

```text
FastAPI
+
Redis
+
PostgreSQL
```

### Production

Potentially:

```text
Kafka / Redpanda
+
PostgreSQL
+
WORM/Object Storage
+
SIEM
```

Don't introduce Kafka merely to make the prototype look enterprise-grade.

---

# 11. Audit vs logging vs monitoring

Keep these separate.

```text
┌─────────────────────────────────────────┐
│ AUDIT                                   │
│                                         │
│ Who accessed Case 4821?                 │
│ What did they do?                       │
│ What evidence was used?                 │
│ What authorization allowed it?          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ SECURITY MONITORING                     │
│                                         │
│ Is someone behaving suspiciously?       │
│ Are there repeated denied accesses?     │
│ Is bulk extraction happening?           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ OBSERVABILITY                           │
│                                         │
│ Is PostgreSQL healthy?                  │
│ Is the API slow?                        │
│ Is the agent service failing?           │
└─────────────────────────────────────────┘
```

They interact, but they have different purposes.

---

# 12. Security analytics on top of audit

Now your audit data becomes useful operationally.

Example:

```text
Officer normally:
25 searches/day

Today:
3,500 searches
      │
      ▼
Audit analytics
      │
      ▼
ANOMALY
      │
      ▼
Security Alert
```

Another example:

```text
Repeated denied access
        +
Restricted-case attempts
        +
Bulk export attempt
        ↓
HIGH-RISK ACTIVITY
```

So:

> **Audit tells you what happened. Security analytics tells you whether it looks suspicious.**

---

# 13. Investigation replay

This is one of the strongest features I'd expose to supervisors.

Select:

```text
INVESTIGATION #INV-4821
```

The system reconstructs:

```text
10:21
Officer started investigation

        ↓

10:22
Question submitted

        ↓

10:22
Authorization → ALLOWED

        ↓

10:22
Agent Run #AR-821

        ↓

10:23
Memory retrieved

        ↓

10:23
PostgreSQL query

        ↓

10:23
Neo4j traversal

        ↓

10:24
12 evidence records retrieved

        ↓

10:24
Similarity analysis

        ↓

10:25
Evidence verification → PASSED

        ↓

10:25
Final response generated

        ↓

10:26
Officer generated report

        ↓

10:27
Human review
```

That is **investigation replayability**.

---

# 14. Human action must also be audited

This is something I would explicitly add to the final design.

The system shouldn't stop auditing at:

```text
AI → Final Answer
```

It should continue:

```text
AI Answer
    ↓
Officer reviews
    ↓
Officer accepts/rejects/edits
    ↓
Officer takes action
```

For example:

```text
AI:
"Potential relationship identified."

Officer:
[Reviewed]

Officer decision:
"Investigate further"

Timestamp:
10:31

Officer ID:
OFF-204
```

This establishes the boundary:

**AI assisted → human decided.**

---

# 15. Privacy-conscious auditing

Audit logs themselves contain sensitive information.

Therefore don't blindly store:

```text
Full FIR
Full witness statement
Full phone number
Full address
```

inside every audit event.

Instead:

```text
resource_id
record_id
evidence_id
query_hash
classification
```

Then authorized auditors can follow the reference.

So:

> **Audit should prove access without unnecessarily duplicating the data that was accessed.**

---

# 16. Audit access control

Even the audit system needs RBAC/ABAC.

```text
CONSTABLE
   │
   └── No audit access

INVESTIGATOR
   │
   └── Limited own investigation audit

SUPERVISOR
   │
   └── Department investigation audit

AUDITOR
   │
   └── Full audit investigation

SYSTEM ADMIN
   │
   └── Infrastructure management
       BUT NOT silent audit modification
```

That last distinction is important.

**System administrator ≠ audit authority.**

---

# 17. Final technology stack

For your current system:

```text
Audit Event Generation
    FastAPI middleware
    + Agent instrumentation

Event Transport
    Redis initially
    Kafka/Redpanda production

Audit Storage
    PostgreSQL

Immutable Archive
    WORM/Object Storage

Integrity
    SHA-256 hash chaining

Tracing
    OpenTelemetry

Monitoring
    Prometheus
    Grafana

Security Analytics
    SIEM

Dashboard
    Next.js
```

---

# 18. The final audit architecture

If I had to put only **one diagram** into your system-design document, I'd use this:

```text
                         POLICE OFFICER
                              │
                              ▼
                     ┌──────────────────┐
                     │   Analyst UI     │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ API Gateway/WAF  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ AuthN + AuthZ    │
                     └────────┬─────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │    AGENT SYSTEM       │
                  │                       │
                  │ Single LLM            │
                  │ Memory                │
                  │ Tool Orchestrator     │
                  └───────────┬───────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
          Memory           Tools            Analysis
             │                │                │
             ▼                ▼                ▼
          Redis          PostgreSQL          Python
                         Neo4j               ML
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                       Evidence Layer
                              │
                              ▼
                       Verification
                              │
                              ▼
                         AI OUTPUT
                              │
                              ▼
                       HUMAN REVIEW
                              │
                              ▼
                        HUMAN ACTION


════════════════════════════════════════════════════════════════

                         AUDIT PLANE

 Every significant event
          │
          ▼
 ┌───────────────────────┐
 │     Audit Event       │
 │                       │
 │ Actor                 │
 │ Request ID            │
 │ Agent Run ID          │
 │ Tool Call ID          │
 │ Authorization         │
 │ Resources             │
 │ Evidence              │
 │ Result                │
 │ Classification        │
 │ Hash                  │
 └───────────┬───────────┘
             │
             ▼
      ┌───────────────┐
      │ Event Stream  │
      └───────┬───────┘
              │
       ┌──────┼─────────────┐
       ▼      ▼             ▼
   Audit DB  Immutable   Security
             Archive     Analytics
       │       │             │
       └───────┼─────────────┘
               ▼
        ┌──────────────┐
        │ Audit / SOC  │
        │ Dashboard    │
        └──────────────┘
```

## The non-negotiable rule

> **If we cannot reconstruct the path `Officer → Request → Agent Run → Authorization → Tool → Data → Evidence → Analysis → Output → Human Action`, then the system is not sufficiently auditable.**

That is the version I would carry forward into the **overall system architecture**.
