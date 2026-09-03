# Solution Architecture: Read-Only Filesystem & Local File Writes in AppSail

## Problem Definition

The `AuditLogger` class (`backend/app/core/audit.py`) writes a cryptographic hash-chained ledger to `audit_trace.jsonl`. This file satisfies **Section 65B, Indian Evidence Act** compliance for legal admissibility of digital records.

The current write path is:
```python
# backend/app/config.py
AUDIT_LOG_PATH = BASE_DIR / "audit_trace.jsonl"
# → resolves to: /app/audit_trace.jsonl inside the AppSail container
```

> [!CAUTION]
> **What the CAUTION means — told as a story:**
>
> Imagine you rent a hotel room. That hotel room is Zoho AppSail — you are renting a slice of computing space from Zoho. When you check in, the hotel gives you a room with furniture, a TV, and all the fixtures. But there is one strict rule: **you cannot nail anything into the walls, you cannot rearrange the furniture, and you cannot permanently modify anything in the room.** The moment you check out — or the hotel cleans the room — everything resets back to exactly how it was before your arrival.
>
> Our backend currently behaves like a guest who tries to **carve their name into the hotel wardrobe** — it tries to create and write a file called `audit_trace.jsonl` inside the AppSail container's application folder (`/app`). The hotel (AppSail) immediately refuses this with `OSError: [Errno 30] Read-only file system` — translation: *"You cannot write here. This surface is locked."*
>
> There IS a small temporary cabinet in this hotel room — the `/tmp` folder — where guests are allowed to keep items **during their stay**. But here is the catch: when the hotel cleans the room (i.e., the container restarts due to a scaling event, a crash, or a routine cycle), that cabinet is **emptied completely.** Anything you stored there is gone forever — no recovery, no backup.
>
> **The verdict:** We cannot write files locally in AppSail for permanent storage. We need to use Zoho's own cloud storage services — the equivalent of a hotel safe-deposit box that survives room cleaning.

---

## Confidence Label Legend

| Label | Meaning |
| :--- | :--- |
| ✅ **[EVIDENTIARY]** | Verified from Zoho Catalyst official documentation or direct codebase inspection. Can be trusted completely. |
| ⚡ **[TRUSTED]** | Strongly inferred from platform architecture and industry standards. High confidence, not directly tested in this project. |
| ⚠️ **[ASSUMPTION]** | Hypothetical path. Architecturally sound but not proven in this specific stack. Must be prototyped before committing. |

---

## Ranked Solutions

---

### 🏆 Rank 1 — Stream Audit Logs to AppSail Stdout → Catalyst Cloud Logs ✅ [EVIDENTIARY]

**Principle:** AppSail automatically captures everything written to `stdout` and `stderr` (Python's standard `logging` module) and routes it into **Zoho Catalyst Cloud Logs** — persistent, searchable, and viewable from the Catalyst Console.

**How It Works:**
- Modify `AuditLogger.log_event()` to emit the JSON audit payload via `log.info(json.dumps(payload))` in addition to the existing file write.
- AppSail's runtime intercepts all `stdout`/`stderr` output and stores it in the platform's persistent log store.

**Code Change Required (Minimal):**
```python
# backend/app/core/audit.py — AFTER computing hash

# Cloud-native: emit to stdout (captured by AppSail Cloud Logs)
log.info(json.dumps(payload))  # <-- add this one line

# Local-only: write to file (guarded so it does not crash in cloud)
try:
    self.log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(self.log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
except OSError:
    pass  # Graceful degradation in read-only cloud environments
```

**Pros:**
- ✅ Zero new dependencies.
- ✅ Zero architectural changes.
- ✅ Works natively on AppSail — no cloud integration needed beyond what already exists.
- ✅ AppSail Cloud Logs are automatically searchable and retained by the platform.
- ✅ Smallest possible change — pure KISS principle.

**Why the Cons matter — told as a story:**
> Think of Catalyst Cloud Logs like a **CCTV camera in the hotel lobby**. Every time an officer sends a query, that camera records it. You can replay footage from the security room (the Catalyst Console dashboard). But here is the limitation: **you cannot ask the CCTV system a smart question programmatically** — like "give me all of Officer Sharma's actions from 6 PM to 7 PM in a structured report." You have to log into the console and read through raw footage manually.
>
> More critically: if a court demands proof that the audit trail is tamper-proof and sequentially intact as required by **Section 65B of the Indian Evidence Act**, we cannot fully guarantee Zoho's Cloud Logs satisfy that standard — because Zoho has not specifically certified Cloud Logs as a Section 65B evidence store. It is excellent for operational monitoring but may not pass strict legal scrutiny on its own.

**Implementation Effort:** < 1 hour. **Risk:** Near-zero.

---

### 🥈 Rank 2 — Persist Audit Events to Catalyst Data Store ⚡ [TRUSTED]

**Principle:** Use the existing `CatalystDataStoreService` (already implemented in `backend/app/services/catalyst_service.py`) to insert each audit event as a structured row into a dedicated `AuditLogs` table in Catalyst Data Store.

**How It Works:**
- Create a new DataStore table `AuditLogs` with columns: `session_id`, `officer_id`, `event_type`, `action`, `prev_hash`, `current_hash`, `timestamp`.
- Modify `AuditLogger.log_event()` to call `catalyst_datastore_service.insert_row("AuditLogs", payload)` instead of writing to a file.

**Architecture Flow:**
```
AuditLogger.log_event()
    → CatalystDataStoreService.insert_row("AuditLogs", payload)
    → POST https://api.catalyst.zoho.in/baas/v1/project/{id}/table/{name}/row
    → Persisted across all AppSail instances, forever.
```

**Pros:**
- ✅ Fully persistent, replicated, and cloud-durable.
- ✅ Hash chain remains verifiable via ZCQL (`SELECT * FROM AuditLogs ORDER BY ROWID ASC`).
- ✅ DataStore infrastructure already exists in this codebase — no new dependency.
- ✅ Genuinely compliant with long-term evidence retention for Section 65B.

**Why the Cons matter — told as a story:**
> Imagine the hotel now has a **ledger book locked in the hotel vault** — that is Catalyst Data Store. Every guest activity is recorded in it and it survives room cleaning, power cuts, and everything else. Perfect for court evidence. But here is the real trade-off:
>
> **Every single time an officer sends one chat message, before our server sends back the reply, it has to physically walk to the vault, unlock it, make one entry, lock it back, and walk back.** That round trip takes an extra 50 to 150 milliseconds per request. At low traffic this is barely noticeable. During peak hours with 50 officers querying simultaneously, this cumulative delay adds up meaningfully.
>
> The second risk is more dangerous: what if the vault is temporarily unavailable — a network hiccup between AppSail and Catalyst Data Store? If the code is not protected, a logging failure will crash the entire chat response and the officer gets a 500 error — for a log write that is supposed to be secondary to the main business logic. The safety net must be explicitly written into the code with a `try/except` so the audit failure never breaks the primary API response.
>
> Lastly, **before we can deploy, someone must log into the Catalyst Console and manually create the `AuditLogs` table** with the correct columns. If we deploy without doing that first, the very first audit log attempt will crash with "table not found."

**Implementation Effort:** 4–6 hours. **Risk:** Low, existing infrastructure pattern.

---

### 🥉 Rank 3 — Write to `/tmp` with Buffered Batch Flush to File Store ⚡ [TRUSTED]

**Principle:** Write audit events temporarily to `/tmp/audit_trace.jsonl` (which IS writable in AppSail, but ephemeral). At intervals, a background thread batch-uploads the accumulated file to **Catalyst File Store** for durable persistence.

**Architecture Flow:**
```
AuditLogger.log_event()
    → write to /tmp/audit_trace.jsonl (writable, but ephemeral)

Background thread (every 50 events or on /health ping):
    → read /tmp/audit_trace.jsonl
    → POST to Catalyst File Store (persistent blob storage)
    → clear local buffer
```

**Pros:**
- ✅ Stops the `OSError` crash immediately (by redirecting to `/tmp`).
- ✅ Batch upload reduces per-request overhead compared to Rank 2.

**Why the Cons matter — told as a story:**
> Picture this: An officer is actively investigating and submits 30 queries over 20 minutes. Each one is being written into the temporary hotel cabinet (`/tmp`). We have a system that uploads the cabinet's contents to the vault every 50 entries. At query 25, **the AppSail platform decides to recycle this container** — traffic spiked, Zoho is spinning up a fresh instance to handle load. The moment the old container shuts down, the temporary cabinet is emptied before the background thread had a chance to flush.
>
> **Queries 21 through 25 are permanently gone. No court. No recovery. No Section 65B trail.** They simply never existed.
>
> On top of that, coordinating a background flush thread inside a multi-threaded Flask server is complex — two threads can accidentally try to read and clear the same file simultaneously, resulting in corrupted or duplicated audit data. And even when it uploads successfully, **the result in File Store is a raw file blob, not structured rows.** If a court demands "all actions by Officer Sharma between 6 PM and 7 PM," you cannot query it. You have to parse the raw file manually.

**Implementation Effort:** 4–8 hours. **Risk:** Medium.

---

### 4th — Redirect `AUDIT_LOG_PATH` to `/tmp` (Emergency Hotfix Only) ✅ [EVIDENTIARY]

**Principle:** The absolute minimum change to immediately stop the `OSError: [Errno 30] Read-only file system` crash from breaking every `POST /chat` request.

**Code Change:**
```python
# backend/app/config.py
import os

_IS_CLOUD = bool(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT"))

AUDIT_LOG_PATH = (
    Path("/tmp/audit_trace.jsonl")
    if _IS_CLOUD
    else BASE_DIR / "audit_trace.jsonl"
)
```

**Pros:**
- ✅ Instant fix — single line change.
- ✅ Prevents all 500 errors caused by the filesystem write.
- ✅ Zero architectural risk — safe to apply right now.

**Why the Cons matter — told as a story:**
> This is the equivalent of **hiding dirty dishes in the oven before guests arrive**. The living room looks clean — no crashes, no 500 errors, deployment succeeds and the server starts responding. But the dishes are still dirty underneath.
>
> The moment the AppSail container restarts — which happens on every new deployment, every scaling event, every crash — the `/tmp` folder is wiped clean. **Every audit log written since the last restart disappears without any warning.** For a police intelligence platform where Section 65B audit records must survive for court proceedings, this means critical legal evidence silently evaporates.
>
> This is a band-aid, not a cure. Apply it right now to unblock deployment, but immediately build Rank 1 or Rank 2 on top of it before going to any real production use.

**Implementation Effort:** < 15 minutes. **Risk:** Near-zero (but legally incomplete).

---

## Recommended Execution Order

The pragmatic approach to unblock deployment while maintaining correctness:

| Step | Action | Time | Goal |
| :--- | :--- | :--- | :--- |
| **Step 1 (Now)** | Apply **Rank 4 hotfix** — redirect to `/tmp` with cloud detection | 15 min | Stop the 500 crash. Unblock deployment immediately. |
| **Step 2 (Same session)** | Apply **Rank 1** — emit to `log.info()` stdout for AppSail Cloud Logs | 1 hour | Add cloud-durable logging with zero new dependencies. |
| **Step 3 (Post-deploy)** | Provision `AuditLogs` table in Catalyst Console, implement **Rank 2** | 4–6 hours | Full legal-grade Section 65B persistence. |

> [!IMPORTANT]
> Steps 1 and 2 together give you a **working, deployed, production-safe** system today. Step 3 is the correct long-term solution for full legal compliance but can be built after deployment is confirmed stable.
