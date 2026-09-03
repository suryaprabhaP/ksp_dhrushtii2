# State Persistence & DB Migration: Architectural Proposal

Moving away from the local file-backed DuckDB is critical because AppSail serverless containers are ephemeral. If a container scales down or restarts, all local `.duckdb` files are permanently destroyed, leading to lost chat histories and session states.

Here are the ranked architectural solutions, tradeoffs, and potential bottlenecks.

## Rank 1: Zoho Catalyst Data Store (ZCQL) [Recommended]
**Overview:** Migrate the `MemoryAgent` and `session_store` to use Catalyst’s native relational Data Store using ZCQL (Zoho Catalyst Query Language).
- **Pros:** 
  - **Serverless Native:** Fully managed, infinitely scalable, and decoupled from the AppSail container instance.
  - **Data Residency:** Inherently honors the India DC sovereign requirements.
  - **Built-in Security:** Secured via Catalyst's internal IAM; no external database credentials to manage.
- **Cons (Tradeoffs):** 
  - **Learning Curve:** Requires rewriting our SQL abstractions to match ZCQL syntax rather than standard Postgres/DuckDB SQL.
  - **Latency:** Slightly higher read/write latency than an in-memory or local DB.
- **Bottlenecks:** Potential rate limiting on rapid consecutive writes (e.g., if we try to save every single keystroke instead of batching turn-based chat history).

## Rank 2: Zoho Catalyst Cache (Redis-backed)
**Overview:** Use Catalyst Cache for short-term conversational memory, pushing long-term analytics data to the Data Store in the background.
- **Pros:** Ultra-low latency (millisecond response). Perfect for ephemeral chatbot context windows.
- **Cons (Tradeoffs):** Data is volatile and has an expiration limit. Not suitable for long-term audit compliance or permanent FIR storage.
- **Bottlenecks:** Memory size limits depending on the Catalyst subscription tier.

## Rank 3: SQLite3 (Local Mount)
**Overview:** Switch from DuckDB to SQLite3 to fix the immediate C-compiler package build failures.
- **Pros:** Zero configuration, requires no code changes other than swapping the connection string. Guaranteed to compile in AppSail.
- **Cons (Tradeoffs):** **High Risk in Production.** Because AppSail doesn't guarantee persistent local volumes across container instances, the SQLite file will be overwritten or lost on restarts.
- **Bottlenecks:** Total data loss during high-traffic horizontal scaling (Instance A doesn't share SQLite with Instance B).

## Proposed Implementation Plan (The "What To Do Now"):
1. We implement **Rank 3 (SQLite3)** purely as a temporary mock layer for the local development environment so we don't need DuckDB.
2. We write an interface for **Rank 1 (Catalyst Data Store)** using the Catalyst Python SDK, injecting this interface when the app detects it is running in the `production` environment.
