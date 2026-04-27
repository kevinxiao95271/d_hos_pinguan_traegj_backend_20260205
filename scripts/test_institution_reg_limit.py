"""
测试：同一机构超过8个报名项目是否会被后端拦截
策略：注册一个全新账号（随机手机号），绑定到一个已有机构，然后连续报名9次
"""
import requests, json, random, string, time

BASE = "http://localhost:6031"

# ---- 1. 先用 OPS 账号取得 token，查一个已有机构id ----
ops = requests.post(f"{BASE}/api/auth/login-with-password",
                    json={"phone": "13800000005", "password": "ops2026"}, timeout=10).json()
assert ops["success"], f"OPS login failed: {ops}"
ops_token = ops["data"]["token"]
ops_headers = {"Authorization": f"Bearer {ops_token}"}

# 取第一个机构
insts = requests.post(f"{BASE}/api/institutions/search",
                      json={"keyword": "医院", "page": 0, "size": 1},
                      headers=ops_headers, timeout=10).json()
inst = insts["data"]["content"][0]
inst_id = inst["id"]
inst_name = inst["name"]
print(f"Target institution: [{inst_id}] {inst_name}")

# ---- 2. 注册一个新的参赛者账号 ----
rand_phone = "139" + "".join([str(random.randint(0, 9)) for _ in range(8)])
reg_body = {
    "phone": rand_phone,
    "password": "test1234",
    "confirmPassword": "test1234",
    "name": "压测用户",
    "role": "CONTESTANT",
    "institutionId": inst_id
}
reg_resp = requests.post(f"{BASE}/api/auth/register", json=reg_body, timeout=10).json()
print(f"\nRegister new user {rand_phone}: success={reg_resp.get('success')} msg={reg_resp.get('message')}")

if not reg_resp.get("success"):
    print("Register failed, abort")
    exit(1)

# ---- 3. 用新账号登录 ----
login = requests.post(f"{BASE}/api/auth/login-with-password",
                      json={"phone": rand_phone, "password": "test1234"}, timeout=10).json()
assert login["success"], f"Login failed: {login}"
token = login["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"Login OK, userId={login['data']['id']}")

# competition id
comp_id = ops["data"]["currentCompetitionId"] or 1
print(f"competitionId={comp_id}")

# ---- 4. 连续报名9次，观察哪次被拦 ----
print("\n-- Submitting registrations --")
results = []
for i in range(9):
    body = {
        "competitionId": comp_id,
        "projectName": f"压测项目_{i+1:02d}_{rand_phone[-4:]}",
        "groupType": "COMPREHENSIVE"
    }
    r = requests.post(f"{BASE}/api/registrations", headers=headers, json=body, timeout=10)
    try:
        resp = r.json()
    except Exception:
        resp = {"raw": r.text}
    success = resp.get("success", False)
    message = resp.get("message", "")
    reg_id = (resp.get("data") or {}).get("id")
    results.append({
        "attempt": i + 1,
        "http": r.status_code,
        "success": success,
        "message": message,
        "reg_id": reg_id
    })
    status_label = "OK  " if success else "FAIL"
    print(f"  [{status_label}] #{i+1}: HTTP {r.status_code} | reg_id={reg_id} | {message}")

print("\n=== Result Summary ===")
success_count = sum(1 for r in results if r["success"])
blocked = [r for r in results if not r["success"]]
print(f"Total attempts: 9")
print(f"Succeeded: {success_count}")
print(f"Blocked: {len(blocked)}")
if blocked:
    print(f"First block at attempt #{blocked[0]['attempt']}: {blocked[0]['message']}")
else:
    print("=> NOT BLOCKED: all 9 registrations accepted by backend")
