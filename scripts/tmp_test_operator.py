import requests, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"

def p(label, r):
    try:
        body = r.json()
    except:
        body = r.text[:200]
    print(f"\n{'='*60}")
    print(f"{label}  HTTP {r.status_code}")
    print(json.dumps(body, ensure_ascii=False, indent=2)[:800])

# 1. OPERATOR 登录
r = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone":"13588040680","password":"opt123"})
p("1. OPERATOR登录（沈佩儿）", r)
body = r.json()
token = body.get("data",{}).get("token","") if r.status_code==200 else ""
role  = body.get("data",{}).get("role","")
print(f"   role={role}  token前20={token[:20]}...")

if not token:
    print("登录失败，终止")
    sys.exit(1)

H = {"Authorization": f"Bearer {token}"}

# 2. 不传sessionCode 查汇总（应自动返回3个会场）
r2 = requests.get(f"{BASE}/api/admin/final/scores", params={"competitionId":1}, headers=H)
p("2. 不传sessionCode（自动聚合）", r2)
items = r2.json().get("data",[]) if r2.status_code==200 else []
print(f"   共返回 {len(items)} 条任务")

# 3. 查自己的会场（合法）
r3 = requests.get(f"{BASE}/api/admin/final/scores",
    params={"competitionId":1,"sessionCode":"综合组-问题解决型专场1（三楼开元A厅）"}, headers=H)
p("3. 查自己会场（合法）", r3)
items3 = r3.json().get("data",[]) if r3.status_code==200 else []
print(f"   返回 {len(items3)} 条")

# 4. 查别人的会场（应403）
r4 = requests.get(f"{BASE}/api/admin/final/scores",
    params={"competitionId":1,"sessionCode":"综合组-PDCA专场1（二楼名仕厅）"}, headers=H)
p("4. 查别人会场（期望403）", r4)

# 5. 找一个SCORED任务尝试驳回
scored = [x for x in items if x.get("status")=="SCORED"]
if scored:
    tid = scored[0]["taskId"]
    r5 = requests.post(f"{BASE}/api/admin/final/scores/{tid}/reject", headers=H)
    p(f"5. 驳回taskId={tid}（期望200）", r5)
    # 再驳回同一个应该报400（已是PENDING）
    r5b = requests.post(f"{BASE}/api/admin/final/scores/{tid}/reject", headers=H)
    p(f"5b. 重复驳回taskId={tid}（期望400）", r5b)
else:
    print("\n5. 无SCORED任务可驳回（跳过）")

# 6. OPERATOR 不能访问compute-ranking（应403）
r6 = requests.post(f"{BASE}/api/admin/final/compute-ranking",
    params={"competitionId":1}, headers=H)
p("6. compute-ranking（期望403）", r6)
