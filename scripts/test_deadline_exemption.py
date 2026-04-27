import requests
import json
import sys

BASE = "http://localhost:6031"

def ok(label, r):
    data = r.json()
    status = "OK" if data.get("success") else "FAIL"
    print(f"[{status}] {label} | HTTP {r.status_code} | {json.dumps(data, ensure_ascii=False)[:200]}")
    return data

# 1. Login as OPS
r = requests.post(f"{BASE}/api/auth/login-with-password", json={"phone": "13800000005", "password": "ops2026"})
d = ok("OPS login", r)
token = d["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Get list (expect empty)
r = requests.get(f"{BASE}/api/admin/deadline-exemptions?competitionId=1", headers=headers)
ok("GET list (empty)", r)

# 3. Upsert - institution-level should be rejected (no targetType field now)
r = requests.put(f"{BASE}/api/admin/deadline-exemptions", headers=headers,
                 json={"competitionId": 1, "registrationId": 20260001, "expireAt": "2026-12-31T23:59:59", "remark": "系统故障延期"})
ok("PUT upsert reg 20260001", r)

# 4. Re-upsert same registrationId (update expireAt)
r = requests.put(f"{BASE}/api/admin/deadline-exemptions", headers=headers,
                 json={"competitionId": 1, "registrationId": 20260001, "expireAt": "2026-06-30T23:59:59", "remark": "缩短到期"})
ok("PUT upsert again (update)", r)

# 5. List should show 1 record
r = requests.get(f"{BASE}/api/admin/deadline-exemptions?competitionId=1", headers=headers)
ok("GET list (1 record)", r)

# 6. Upsert another registration
r = requests.put(f"{BASE}/api/admin/deadline-exemptions", headers=headers,
                 json={"competitionId": 1, "registrationId": 20260002, "expireAt": "2026-03-10T23:59:59", "remark": "第二条"})
ok("PUT upsert reg 20260002", r)

# 7. List should show 2 records
r = requests.get(f"{BASE}/api/admin/deadline-exemptions?competitionId=1", headers=headers)
ok("GET list (2 records)", r)

# 8. Delete first
r = requests.delete(f"{BASE}/api/admin/deadline-exemptions?competitionId=1&registrationId=20260001", headers=headers)
ok("DELETE reg 20260001", r)

# 9. List should show 1 record
r = requests.get(f"{BASE}/api/admin/deadline-exemptions?competitionId=1", headers=headers)
ok("GET list (after delete, 1 record)", r)

# 10. Delete second
r = requests.delete(f"{BASE}/api/admin/deadline-exemptions?competitionId=1&registrationId=20260002", headers=headers)
ok("DELETE reg 20260002", r)

# 11. Final list should be empty
r = requests.get(f"{BASE}/api/admin/deadline-exemptions?competitionId=1", headers=headers)
ok("GET list (final empty)", r)

# 12. Verify non-OPS role is rejected
r = requests.get(f"{BASE}/api/admin/deadline-exemptions?competitionId=1")  # no auth
ok("GET without token (expect 401/error)", r)

print("\n=== 自测完成 ===")
