import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

# 管理员 token
admin_token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone": "13800000005", "password": "ops2026"}).json()["data"]["token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 取有 FINAL 任务的评委
cur.execute("""
    SELECT DISTINCT ua.id, ua.phone
    FROM user_accounts ua
    JOIN review_tasks rt ON rt.reviewer_id = ua.id
    WHERE rt.stage = 'FINAL'
""")
reviewers = cur.fetchall()
print(f"重新打分评委数: {len(reviewers)}")

def rand_score(lo, hi):
    """在 [lo, hi] 内随机，保留1位小数，模拟真实评委打分习惯（集中在高分段）"""
    # 80% 概率落在上75%区间
    if random.random() < 0.8:
        lo = lo + (hi - lo) * 0.6
    return round(random.uniform(lo, hi) * 2) / 2  # 取0.5的倍数，更真实

def make_payload(sf, seed):
    random.seed(seed)
    if sf == "QCC":
        # 计划10 + 项目结构15 + 对策行动15 + 成果表现20 + 查验5 + 整体运作15 + 现场表现20 = 100
        return {
            "scoreForm": "QCC",
            "plan":         rand_score(7, 10),    # 满分10
            "problem":      rand_score(11, 15),   # 满分15
            "action":       rand_score(11, 15),   # 满分15
            "success":      rand_score(15, 20),   # 满分20
            "review":       rand_score(3.5, 5),   # 满分5
            "operation":    rand_score(11, 15),   # 满分15
            "presentation": rand_score(15, 20),   # 满分20
        }
    elif sf == "QFD":
        # 圈活动特征15 + 课题明确化25 + 方策拟定25 + 执行力成果25 + 现场发表10 = 100
        return {
            "scoreForm": "QFD",
            "plan":         rand_score(11, 15),   # 满分15
            "problem":      rand_score(19, 25),   # 满分25
            "action":       rand_score(19, 25),   # 满分25
            "success":      rand_score(19, 25),   # 满分25
            "review":       rand_score(7, 10),    # 满分10
        }
    else:  # NON_QCC
        # 选题15 + 原因分析10 + 计划10 + 实施20 + 成果表现10 + 检讨10 + 整体运作15 + 现场表现10 = 100
        return {
            "scoreForm": "NON_QCC",
            "plan":         rand_score(11, 15),   # 满分15
            "problem":      rand_score(7, 10),    # 满分10
            "action":       rand_score(7, 10),    # 满分10
            "success":      rand_score(15, 20),   # 满分20
            "review":       rand_score(7, 10),    # 满分10
            "operation":    rand_score(7, 10),    # 满分10
            "presentation": rand_score(11, 15),   # 满分15
            "item8":        rand_score(7, 10),    # 满分10（现场表现）
        }

total_ok = 0
for rev_id, rev_phone in reviewers:
    lr = requests.post(f"{BASE}/api/auth/login-with-password",
                       json={"phone": rev_phone, "password": "user123"})
    data = lr.json().get("data")
    if not data:
        print(f"  {rev_phone} 登录失败")
        continue
    rev_headers = {"Authorization": f"Bearer {data['token']}"}

    tasks = requests.get(f"{BASE}/api/reviews/final/my-tasks", headers=rev_headers).json().get("data", [])
    for task in tasks:
        tid = task["taskId"]
        sf = task.get("scoreForm", "QCC")
        payload = make_payload(sf, tid * 31 + rev_id)
        sr = requests.put(f"{BASE}/api/reviews/final/scores/{tid}/submit",
                          json=payload, headers=rev_headers)
        if sr.status_code == 200:
            total_ok += 1
        else:
            print(f"  任务{tid} 失败: {sr.text[:80]}")

print(f"重新提交打分成功: {total_ok} 条")

# 重算排名
cr = requests.post(f"{BASE}/api/admin/final/compute-ranking?competitionId=1", headers=headers)
print(f"排名计算: {cr.json().get('data','')}")

# 验证分值范围
rr = requests.get(f"{BASE}/api/admin/final/ranking?competitionId=1", headers=headers)
items = rr.json().get("data", [])
avgs = [i.get("trimmedAvg", 0) for i in items if i.get("trimmedAvg", 0) > 0]
if avgs:
    print(f"\n分值范围: min={min(avgs):.1f} max={max(avgs):.1f} avg={sum(avgs)/len(avgs):.1f}")
print("\n前10名排名:")
for item in items[:10]:
    print(f"  {item.get('sessionDate')} | rank={item.get('rank')} | avg={item.get('trimmedAvg'):.1f} | {item.get('sessionCode')} | {(item.get('projectName') or '')[:18]}")

conn.close()
