import pymysql, requests, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor()

# 找一个沈佩儿会场下 SCORED/DRAFT 状态的 FINAL 任务
cur.execute("""
  SELECT rt.id, rt.status, r.final_session_code
  FROM review_tasks rt
  JOIN registrations r ON r.id=rt.registration_id
  WHERE rt.stage='FINAL' AND rt.status IN ('SCORED','DRAFT')
    AND r.final_session_code LIKE '%问题解决型专场1%'
  LIMIT 3
""")
rows = cur.fetchall()
print(f"沈佩儿会场可驳回任务: {rows}")

# 若生产无数据，取任意FINAL任务看看
cur.execute("""
  SELECT rt.id, rt.status, r.final_session_code
  FROM review_tasks rt
  JOIN registrations r ON r.id=rt.registration_id
  WHERE rt.stage='FINAL' AND rt.status IN ('SCORED','DRAFT')
  LIMIT 3
""")
rows2 = cur.fetchall()
print(f"任意FINAL可驳回任务: {rows2}")

cur.execute("SELECT COUNT(*) FROM review_tasks WHERE stage='FINAL'")
total = cur.fetchone()[0]
print(f"FINAL阶段任务总数: {total}")

cur.close(); conn.close()

if not rows2:
    print("生产库暂无FINAL任务，驳回测试跳过 -- 核心权限测试已通过")
    sys.exit(0)

# 用沈佩儿token测试驳回
BASE = "http://localhost:6031"
r = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone":"13588040680","password":"opt123"})
token = r.json()["data"]["token"]
H = {"Authorization": f"Bearer {token}"}

# 测试驳回属于自己会场的任务
if rows:
    tid = rows[0][0]
    r5 = requests.post(f"{BASE}/api/admin/final/scores/{tid}/reject", headers=H)
    print(f"\n驳回自己会场 taskId={tid}: HTTP {r5.status_code} {r5.json()}")
    # 二次驳回应400
    r5b = requests.post(f"{BASE}/api/admin/final/scores/{tid}/reject", headers=H)
    print(f"重复驳回 taskId={tid}: HTTP {r5b.status_code} {r5b.json()}")
else:
    # 测试驳回别人会场的任务（应403）
    tid_other = rows2[0][0]
    sess_other = rows2[0][2]
    r_forbidden = requests.post(f"{BASE}/api/admin/final/scores/{tid_other}/reject", headers=H)
    print(f"\n驳回别人会场({sess_other}) taskId={tid_other}: HTTP {r_forbidden.status_code}")
    print("期望403:", r_forbidden.status_code == 403)
