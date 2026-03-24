"""
把所有 PENDING / RETURNED 的 review_tasks 批量补为 SCORED 状态，
同时插入对应的得分记录（book review 7维度 / interview 4维度），
目标让 SCORED 总量达到 ~200 条。
"""
import pymysql, random, sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_',
          db='d_hos_pinguan_traegj_20260205', charset='utf8mb4',
          autocommit=False)

conn = pymysql.connect(**DB)
cur = conn.cursor()

# 书审维度权重比例（7维，比例之和 = 1，用于按比例分配总分）
BOOK_WEIGHTS = [0.15, 0.18, 0.20, 0.18, 0.12, 0.10, 0.07]
# plan, problem, action, success, review, operation, presentation

def rand_submit_at():
    base = datetime(2026, 3, 1)
    return base + timedelta(days=random.randint(0, 21),
                            hours=random.randint(8, 22),
                            minutes=random.randint(0, 59))

def gen_book_dims(total):
    """按权重分配总分到7个维度，整数，保证加和 == total"""
    raw = [w * total for w in BOOK_WEIGHTS]
    dims = [max(1, round(v)) for v in raw]
    # 调整尾差
    diff = total - sum(dims)
    dims[-1] += diff
    dims[-1] = max(1, dims[-1])
    return dims  # plan, problem, action, success, review, operation, presentation

def gen_interview_dims(total):
    """4个维度，float，保证加和 == total"""
    weights = [0.25, 0.25, 0.25, 0.25]
    dims = [round(w * total, 1) for w in weights]
    diff = round(total - sum(dims), 1)
    dims[-1] = round(dims[-1] + diff, 1)
    return dims  # topic, process, operation, result

# ── 获取 PENDING/RETURNED BOOK 任务 ──────────────────────────────────────────
cur.execute("""
    SELECT rt.id
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id = 1
      AND rt.stage = 'BOOK'
      AND rt.status IN ('PENDING', 'RETURNED')
    ORDER BY rt.id
""")
book_tasks = [r[0] for r in cur.fetchall()]
print(f'待补分 BOOK 任务: {len(book_tasks)} 条')

# ── 获取 PENDING/RETURNED INTERVIEW 任务 ────────────────────────────────────
cur.execute("""
    SELECT rt.id
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id = 1
      AND rt.stage = 'INTERVIEW'
      AND rt.status IN ('PENDING', 'RETURNED')
    ORDER BY rt.id
""")
interview_tasks = [r[0] for r in cur.fetchall()]
print(f'待补分 INTERVIEW 任务: {len(interview_tasks)} 条')

# ── 删除已有 RETURNED 任务的旧得分（避免主键冲突） ──────────────────────────
if book_tasks:
    cur.execute(f"DELETE FROM review_scores WHERE review_task_id IN ({','.join(str(x) for x in book_tasks)})")
if interview_tasks:
    cur.execute(f"DELETE FROM interview_scores WHERE review_task_id IN ({','.join(str(x) for x in interview_tasks)})")

# ── 批量插入 review_scores ───────────────────────────────────────────────────
BOOK_INSERT = """
INSERT INTO review_scores
  (review_task_id, plan, problem, action, success, review, operation, presentation, total, submitted_at, highlight, weakness)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
book_rows = []
highlights = ['选题准确，改善思路清晰', '数据收集完整，统计方法正确', '对策切实可行，效果显著', '团队协作良好，活动规范', '改善成果具有推广价值']
weaknesses = ['目标设定依据不够充分', '原因分析深度有待加强', '标准化措施需进一步落实', '数据呈现方式可以更直观', '巩固期跟进不够完整']

for tid in book_tasks:
    total = random.randint(72, 94)
    dims = gen_book_dims(total)
    sat = rand_submit_at()
    book_rows.append((
        tid,
        dims[0], dims[1], dims[2], dims[3], dims[4], dims[5], dims[6],
        total, sat,
        random.choice(highlights), random.choice(weaknesses)
    ))

cur.executemany(BOOK_INSERT, book_rows)
print(f'  -> 插入 review_scores: {len(book_rows)} 条')

# ── 批量插入 interview_scores ────────────────────────────────────────────────
INT_INSERT = """
INSERT INTO interview_scores
  (review_task_id, topic, process, operation, result, total, submitted_at, highlight, weakness)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
int_rows = []
for tid in interview_tasks:
    total = round(random.uniform(74, 95), 1)
    dims = gen_interview_dims(total)
    sat = rand_submit_at()
    int_rows.append((
        tid,
        dims[0], dims[1], dims[2], dims[3],
        total, sat,
        random.choice(highlights), random.choice(weaknesses)
    ))

cur.executemany(INT_INSERT, int_rows)
print(f'  -> 插入 interview_scores: {len(int_rows)} 条')

# ── 批量更新任务状态为 SCORED ────────────────────────────────────────────────
all_task_ids = book_tasks + interview_tasks
if all_task_ids:
    cur.execute(
        f"UPDATE review_tasks SET status='SCORED', updated_at=NOW() WHERE id IN ({','.join(str(x) for x in all_task_ids)})"
    )
print(f'  -> 更新 review_tasks 状态: {len(all_task_ids)} 条 -> SCORED')

conn.commit()
conn.close()

print('\n完成！验证当前统计:')

conn2 = pymysql.connect(**DB)
cur2 = conn2.cursor()
cur2.execute("""
    SELECT rt.stage, rt.status, COUNT(*)
    FROM review_tasks rt
    JOIN registrations r ON r.id = rt.registration_id
    WHERE r.competition_id = 1
    GROUP BY rt.stage, rt.status
    ORDER BY rt.stage, rt.status
""")
for row in cur2.fetchall():
    print(f'  {row[0]} | {row[1]}: {row[2]}')
cur2.execute("SELECT COUNT(*) FROM review_scores")
print(f'review_scores 总数: {cur2.fetchone()[0]}')
cur2.execute("SELECT COUNT(*) FROM interview_scores")
print(f'interview_scores 总数: {cur2.fetchone()[0]}')
conn2.close()
