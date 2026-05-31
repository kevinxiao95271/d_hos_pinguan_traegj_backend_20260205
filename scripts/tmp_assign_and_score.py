import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

# ── 登录管理员 ────────────────────────────────────────────────────────────────
r = requests.post(f"{BASE}/api/auth/login-with-password",
                  json={"phone": "13800000005", "password": "ops2026"})
admin_token = r.json()["data"]["token"]
headers = {"Authorization": f"Bearer {admin_token}"}
print("管理员登录成功")

# ── 取部分评委账号（取前5个 REVIEWER） ────────────────────────────────────────
cur.execute("""
    SELECT id, phone FROM user_accounts
    WHERE role='REVIEWER' AND enabled=1
    LIMIT 5
""")
reviewers = cur.fetchall()
print(f"取到 {len(reviewers)} 名评委: {[r[1] for r in reviewers]}")

# ── 取所有专场 ────────────────────────────────────────────────────────────────
r = requests.get(f"{BASE}/api/admin/final/sessions?competitionId=1", headers=headers)
sessions = r.json()["data"]
print(f"共 {len(sessions)} 个专场")

# ── 为每个专场分配 3 名评委 ────────────────────────────────────────────────────
assigned_sessions = sessions[:7]  # 先选第一天 6.3 的7个场次
for sess in assigned_sessions:
    code = sess["sessionCode"]
    for rev_id, rev_phone in reviewers[:3]:
        resp = requests.post(
            f"{BASE}/api/admin/final/sessions/{requests.utils.quote(code, safe='')}/assign-reviewer",
            params={"competitionId": 1, "reviewerId": rev_id},
            headers=headers
        )
        if resp.status_code == 200:
            print(f"  分配 {rev_phone} → {code}: {resp.json().get('data','')}")
        else:
            print(f"  分配失败 {rev_phone} → {code}: {resp.text[:80]}")

# ── 每位评委登录并提交打分 ────────────────────────────────────────────────────
for rev_id, rev_phone in reviewers[:3]:
    # 登录
    lr = requests.post(f"{BASE}/api/auth/login-with-password",
                       json={"phone": rev_phone, "password": "user123"})
    if lr.json().get("data") is None:
        print(f"评委 {rev_phone} 登录失败: {lr.text[:100]}")
        continue
    rev_token = lr.json()["data"]["token"]
    rev_headers = {"Authorization": f"Bearer {rev_token}"}

    # 取我的任务
    tr = requests.get(f"{BASE}/api/reviews/final/my-tasks", headers=rev_headers)
    tasks = tr.json().get("data", [])
    print(f"\n评委 {rev_phone} 有 {len(tasks)} 个任务")

    for task in tasks:
        task_id = task["taskId"]
        sf = task.get("scoreForm", "QCC")

        # 根据评分表随机生成分数
        random.seed(task_id)
        if sf == "QCC":
            payload = {
                "scoreForm": "QCC",
                "item1": round(random.uniform(14, 20), 1),
                "item2": round(random.uniform(14, 20), 1),
                "item3": round(random.uniform(9, 15), 1),
                "item4": round(random.uniform(9, 15), 1),
                "item5": round(random.uniform(9, 15), 1),
                "item6": round(random.uniform(9, 15), 1),
                "item7": round(random.uniform(4, 10), 1),
            }
        elif sf == "QFD":
            payload = {
                "scoreForm": "QFD",
                "item1": round(random.uniform(14, 20), 1),
                "item2": round(random.uniform(14, 20), 1),
                "item3": round(random.uniform(9, 15), 1),
                "item4": round(random.uniform(9, 15), 1),
                "item5": round(random.uniform(9, 15), 1),
                "item6": round(random.uniform(9, 15), 1),
                "item7": round(random.uniform(4, 10), 1),
            }
        else:  # NON_QCC
            payload = {
                "scoreForm": "NON_QCC",
                "item1": round(random.uniform(14, 20), 1),
                "item2": round(random.uniform(14, 20), 1),
                "item3": round(random.uniform(9, 15), 1),
                "item4": round(random.uniform(9, 15), 1),
                "item5": round(random.uniform(9, 15), 1),
                "item6": round(random.uniform(9, 15), 1),
                "item7": round(random.uniform(4, 10), 1),
                "item8": round(random.uniform(4, 10), 1),
            }

        sr = requests.put(
            f"{BASE}/api/reviews/final/scores/{task_id}/submit",
            json=payload, headers=rev_headers
        )
        if sr.status_code == 200:
            print(f"  任务 {task_id} ({sf}) 提交成功")
        else:
            print(f"  任务 {task_id} 提交失败: {sr.text[:100]}")

# ── 触发排名计算 ──────────────────────────────────────────────────────────────
cr = requests.post(f"{BASE}/api/admin/final/compute-ranking?competitionId=1", headers=headers)
print(f"\n计算排名: {cr.json().get('data','')}")

# ── 验证结果 ──────────────────────────────────────────────────────────────────
rr = requests.get(f"{BASE}/api/admin/final/ranking?competitionId=1", headers=headers)
items = rr.json().get("data", [])
print(f"\n排名结果共 {len(items)} 条")
for item in items[:10]:
    print(f"  {item.get('sessionDate')} | {item.get('sessionCode')} | rank={item.get('rank')} | avg={item.get('trimmedAvg')} | {item.get('projectName','')[:20]}")

# ── 评分汇总 ──────────────────────────────────────────────────────────────────
sr2 = requests.get(f"{BASE}/api/admin/final/scores?competitionId=1", headers=headers)
items2 = sr2.json().get("data", [])
print(f"\n评分汇总共 {len(items2)} 条（任务数）")

conn.close()
