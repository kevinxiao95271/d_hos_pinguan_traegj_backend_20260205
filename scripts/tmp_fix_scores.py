import pymysql, requests, random, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:6031"
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

conn = pymysql.connect(**DB)
cur = conn.cursor()

def r(lo, hi, seed_extra=0):
    v = lo + (hi - lo) * random.random()
    # 取0.5的倍数
    return round(v * 2) / 2

# 取所有 FINAL 评分记录
cur.execute("""
    SELECT rs.id, rs.score_form
    FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id = rt.id
    WHERE rt.stage = 'FINAL'
""")
rows = cur.fetchall()
print(f"共 {len(rows)} 条评分记录需更新")

updated = 0
for score_id, sf in rows:
    random.seed(score_id * 17 + 9999)

    if sf == 'QCC':
        # 计划10 项目结构15 对策行动15 成果表现20 查验5 整体运作15 现场表现20 = 100
        plan         = r(7.5, 10)
        problem      = r(11.5, 15)
        action       = r(11.5, 15)
        success      = r(15.5, 20)
        review_      = r(3.5, 5)
        operation    = r(11.5, 15)
        presentation = r(15.5, 20)
        item8        = None
        total = plan + problem + action + success + review_ + operation + presentation

        cur.execute("""UPDATE review_scores SET plan=%s, problem=%s, action=%s, success=%s,
                        review=%s, operation=%s, presentation=%s, item8=NULL, total=%s WHERE id=%s""",
                    (plan, problem, action, success, review_, operation, presentation, round(total, 1), score_id))

    elif sf == 'QFD':
        # 圈活动特征15 课题明确化25 方策拟定25 执行力成果25 现场发表10 = 100
        plan         = r(11.5, 15)    # 圈活动特征
        problem      = r(19.5, 25)    # 课题明确化
        action       = r(19.5, 25)    # 方策拟定
        success      = r(19.5, 25)    # 执行力成果
        review_      = r(7.5, 10)     # 现场发表
        operation    = None
        presentation = None
        item8        = None
        total = plan + problem + action + success + review_

        cur.execute("""UPDATE review_scores SET plan=%s, problem=%s, action=%s, success=%s,
                        review=%s, operation=NULL, presentation=NULL, item8=NULL, total=%s WHERE id=%s""",
                    (plan, problem, action, success, review_, round(total, 1), score_id))

    else:  # NON_QCC
        # 选题15 原因分析10 计划10 实施20 成果表现10 检讨10 整体运作15 现场表现10 = 100
        plan         = r(11.5, 15)    # 选题
        problem      = r(7.5, 10)     # 原因分析
        action       = r(7.5, 10)     # 计划
        success      = r(15.5, 20)    # 实施
        review_      = r(7.5, 10)     # 成果表现
        operation    = r(7.5, 10)     # 检讨
        presentation = r(11.5, 15)    # 整体运作
        item8        = r(7.5, 10)     # 现场表现
        total = plan + problem + action + success + review_ + operation + presentation + item8

        cur.execute("""UPDATE review_scores SET plan=%s, problem=%s, action=%s, success=%s,
                        review=%s, operation=%s, presentation=%s, item8=%s, total=%s WHERE id=%s""",
                    (plan, problem, action, success, review_, operation, presentation, item8, round(total, 1), score_id))

    updated += 1

conn.commit()
print(f"更新完成: {updated} 条")

# 验证一下 total 范围
cur.execute("""
    SELECT MIN(rs.total), MAX(rs.total), AVG(rs.total)
    FROM review_scores rs
    JOIN review_tasks rt ON rs.review_task_id = rt.id
    WHERE rt.stage = 'FINAL' AND rs.total IS NOT NULL
""")
row = cur.fetchone()
print(f"total 范围: min={row[0]:.1f} max={row[1]:.1f} avg={row[2]:.1f}")

conn.close()

# 重新计算排名
admin_token = requests.post(f"{BASE}/api/auth/login-with-password",
    json={"phone": "13800000005", "password": "ops2026"}).json()["data"]["token"]
headers = {"Authorization": f"Bearer {admin_token}"}
cr = requests.post(f"{BASE}/api/admin/final/compute-ranking?competitionId=1", headers=headers)
print(f"\n排名计算: {cr.json().get('data','')}")

rr = requests.get(f"{BASE}/api/admin/final/ranking?competitionId=1", headers=headers)
items = rr.json().get("data", [])
avgs = [i.get("trimmedAvg", 0) for i in items if i.get("trimmedAvg", 0) > 0]
if avgs:
    print(f"排名分值范围: min={min(avgs):.1f} max={max(avgs):.1f} avg={sum(avgs)/len(avgs):.1f}")
print("\n前10条排名:")
for item in items[:10]:
    print(f"  {item.get('sessionDate')} | {item.get('sessionCode')[:12]} | rank={item.get('rank')} | avg={item.get('trimmedAvg'):.1f} | {(item.get('projectName') or '')[:16]}")
