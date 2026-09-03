import os
import sys
from dotenv import load_dotenv

load_dotenv("d:/latest_datathon/rohith_project/.env.standalone")
sys.path.insert(0, "d:/latest_datathon/rohith_project/backend")

from app.services.catalyst_service import catalyst_datastore_service

print("[*] Testing ZCQL Queries against Catalyst Datastore...")

# Test 1: Query CRMSuspects
print("\n--- Test 1: SELECT * FROM CRMSuspects ---")
res_suspects = catalyst_datastore_service.execute_zcql("SELECT * FROM CRMSuspects LIMIT 10")
print(f"CRMSuspects result count: {len(res_suspects) if res_suspects else 0}")
if res_suspects:
    print("Sample record:", res_suspects[0])

# Test 2: Query PoliceFIRs
print("\n--- Test 2: SELECT * FROM 54626000000109574 (PoliceFIRs) or PoliceFIRs ---")
res_firs = catalyst_datastore_service.execute_zcql("SELECT * FROM PoliceFIRs LIMIT 10")
if not res_firs:
    res_firs = catalyst_datastore_service.execute_zcql("SELECT * FROM 54626000000109574 LIMIT 10")
print(f"PoliceFIRs result count: {len(res_firs) if res_firs else 0}")
if res_firs:
    print("Sample record:", res_firs[0])

# Test 3: Query DeskTickets
print("\n--- Test 3: SELECT * FROM DeskTickets ---")
res_tickets = catalyst_datastore_service.execute_zcql("SELECT * FROM DeskTickets LIMIT 10")
print(f"DeskTickets result count: {len(res_tickets) if res_tickets else 0}")
if res_tickets:
    print("Sample record:", res_tickets[0])

# Test 4: Query SessionMemory
print("\n--- Test 4: SELECT * FROM SessionMemory ---")
res_mem = catalyst_datastore_service.execute_zcql("SELECT * FROM SessionMemory LIMIT 10")
print(f"SessionMemory result count: {len(res_mem) if res_mem else 0}")
if res_mem:
    print("Sample record:", res_mem[0])
