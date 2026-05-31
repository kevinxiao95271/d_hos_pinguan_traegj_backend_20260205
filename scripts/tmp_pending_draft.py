import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

admin_token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone": "13800000005", "password": "ops2026"}).json()["data"]["token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 取2个还没参与过 FINAL 任务的评委
cur.execute("""
    SELECT id, phone FROM user_accounts
    WHERE role='REVIEWER' AND enabled=1
    AND id NOT IN (SELECT DISTINCT reviewer_id FROM review_tasks WHERE stage='FINAL')
    LIMIT 2
""")
new_reviewers = cur.fetchall()
print(f"新评委: {[r[1] for r in new_reviewers]}")

# 取前3个专场代码
r = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=headers)
sessions = r.json()["data"][:3]
session_codes = [s["sessionCode"] for s in sessions]
print(f"分配到场次: {session_codes}")

# 把这2个新评委分配到前3个专场 → 产生 PENDING 任务
for sess_code in session_codes:
    for rev_id, rev_phone in new_reviewers:
        resp = requests.post(
            f"{BASE}/api/admin/final/sessions/{requests.utils.quote(sess_code, safe='')}/assign-reviewer",
            params={"competitionId": 1, "reviewerId": rev_id},
            headers=headers
        )
        print(f"  分配 {rev_phone} → {sess_code[:15]}: {resp.json().get('data','err')[:30]}")

# 让第一个新评委在第1个专场的任务里保存草稿（不提交）
if new_reviewers:
    rev_id, rev_phone = new_reviewers[0]
    lr = requests.post(f"{BASE}/api/auth/login-with-password",
                       json={"phone": rev_phone, "password": "user123"})
    data = lr.json().get("data")
    if data:
        rev_headers = {"Authorization": f"Bearer {data['token']}"}
        tasks = requests.get(f"{BASE}/api/reviews/final/my-tasks", headers=rev_headers).json().get("data", [])
        # 只对前5个任务保存草稿
        draft_count = 0
        for task in tasks[:5]:
            tid = task["taskId"]
            sf = task.get("scoreForm", "QCC")
            random.seed(tid + 1234)
            def rs(lo, hi): return round((lo + (hi-lo)*random.random()) * 2) / 2
            if sf == "QCC":
                payload = {"scoreForm":"QCC","plan":rs(7.5,10),"problem":rs(11.5,15),
                           "action":rs(11.5,15),"success":rs(15.5,20),"review":rs(3.5,5),
                           "operation":rs(11.5,15),"presentation":rs(15.5,20)}
            elif sf == "QFD":
                payload = {"scoreForm":"QFD","plan":rs(11.5,15),"problem":rs(19.5,25),
                           "action":rs(19.5,25),"success":rs(19.5,25),"review":rs(7.5,10)}
            else:
                payload = {"scoreForm":"NON_QCC","plan":rs(11.5,15),"problem":rs(7.5,10),
                           "action":rs(7.5,10),"success":rs(15.5,20),"review":rs(7.5,10),
                           "operation":rs(7.5,10),"presentation":rs(11.5,15),"item8":rs(7.5,10)}
            sr = requests.put(f"{BASE}/api/reviews/final/scores/{tid}/draft",
                              json=payload, headers=rev_headers)
            if sr.status_code == 200:
                draft_count += 1
                print(f"  草稿保存 任务{tid} ({sf})")
            else:
                print(f"  草稿失败 任务{tid}: {sr.text[:60]}")
        print(f"共保存草稿: {draft_count} 条")
    else:
        print(f"评委 {rev_phone} 登录失败")

# 验证状态分布
cur.execute("""
    SELECT status, COUNT(*) FROM review_tasks WHERE stage='FINAL' GROUP BY status
""")
print("\n任务状态分布:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}条")

conn.close()
