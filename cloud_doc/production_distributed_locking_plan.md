# 🔒 Production Distributed Locking Plan (Zoho Catalyst)

## Objective
Migrate from the current in-memory `threading.RLock` to a distributed mutex lock to prevent Zoho OAuth token exhaustion (`TOO_MANY_REQUESTS` / 429) across horizontally scaled application instances (e.g., AppSail pods).

## Current Architecture Bottleneck
- Currently, token refresh calls are serialized using a local thread lock (`threading.RLock()`) in `ZohoTokenManager`.
- This works perfectly for a single node. However, in a multi-pod containerized environment, each pod has its own memory space.
- If the OAuth token expires under heavy burst traffic, all pods will simultaneously detect the expiration and trigger a refresh, hitting the Zoho Accounts API concurrently and causing rate-limit failures.

## Proposed Architecture
- Use **Zoho Catalyst Cache (Redis)** as the centralized locking mechanism.
- When a token refresh is required, the pod will attempt to acquire a lock via Catalyst Cache (e.g., `SET token_refresh_lock 1 NX EX 10`).
- The pod that acquires the lock performs the HTTP token refresh.
- Other pods waiting for the lock will poll or wait until the lock is released or the token is updated in the shared cache.

## Implementation Steps
1. **Initialize Catalyst Cache:** Setup a basic Cache segment in the Zoho Catalyst console named `OAuth_Tokens`.
2. **Update Token Manager:**
   - Modify `ZohoTokenManager` to query the Catalyst Cache before initiating a token refresh.
   - Implement the `acquire_lock()` logic using Catalyst Cache `put` with TTL.
3. **Fail-Safe Mechanism:**
   - Implement a fallback where if Catalyst Cache is unavailable, the system defaults back to the internal `RLock` to guarantee token refresh on a single node without stalling the application.
4. **Deploy & Stress Test:** Validate with a distributed load testing tool across 3+ scaled containers.
