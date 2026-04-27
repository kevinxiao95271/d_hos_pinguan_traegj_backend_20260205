import requests
import time
import sys
import pymysql
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:6031"

# 登录 OPS
r = requests.post(f"{BASE}/api/auth/login-with-password",
                  json={"phone": "13800000005", "password": "ops2026"})
token = r.json()["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# 先查一下当前数据规模
conn = pymysql.connect(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4', connect_timeout=10
)
cur = conn.cursor()

cur.execute("SELECT status, COUNT(*) FROM registrations WHERE competition_id=1 GROUP BY status")
print("=== 当前数据规模 ===")
total = 0
for s, c in cur.fetchall():
    print(f"  {s}: {c}")
    total += c
print(f"  合计: {total}")

cur.execute("""
    SELECT COUNT(DISTINCT institution_id), MAX(cnt) FROM (
        SELECT institution_id, COUNT(*) as cnt
        FROM registrations WHERE competition_id=1 AND status='SUBMITTED'
        GROUP BY institution_id
    ) t
""")
row = cur.fetchone()
print(f"  SUBMITTED 机构数: {row[0]}, 单机构最多项目数: {row[1]}")

cur.execute("""
    SELECT COUNT(*) FROM registrations
    WHERE competition_id=1 AND status='SUBMITTED'
""")
submitted = cur.fetchone()[0]
print(f"  SUBMITTED 总数(autoGroup处理量): {submitted}")

cur.close(); conn.close()

# 实测 autoGroup 接口
print("\n=== autoGroup 性能测试（BASIC 组，每组10条）===")
payload = {
    "competitionId": 1,
    "groupType": "BASIC",
    "groupPrefix": "A",
    "groupSize": 10,
    "status": "SUBMITTED"
}

times = []
for i in range(5):
    t0 = time.perf_counter()
    resp = requests.post(f"{BASE}/api/admin/registrations/auto-group",
                         headers=headers, json=payload)
    t1 = time.perf_counter()
    ms = (t1 - t0) * 1000
    times.append(ms)
    cnt = len(resp.json().get("data", []) or [])
    print(f"  第{i+1}次: {ms:.0f}ms  处理记录数={cnt}")

print(f"\n  平均: {sum(times)/len(times):.0f}ms")
print(f"  最小: {min(times):.0f}ms  最大: {max(times):.0f}ms")

# 测所有组别（最大负荷）
print("\n=== autoGroup 全量测试（不指定groupType）===")
payload_all = {
    "competitionId": 1,
    "groupPrefix": "X",
    "groupSize": 10,
    "status": "SUBMITTED"
}
times2 = []
for i in range(3):
    t0 = time.perf_counter()
    resp = requests.post(f"{BASE}/api/admin/registrations/auto-group",
                         headers=headers, json=payload_all)
    t1 = time.perf_counter()
    ms = (t1 - t0) * 1000
    times2.append(ms)
    cnt = len(resp.json().get("data", []) or [])
    print(f"  第{i+1}次: {ms:.0f}ms  处理记录数={cnt}")

print(f"\n  平均: {sum(times2)/len(times2):.0f}ms")
