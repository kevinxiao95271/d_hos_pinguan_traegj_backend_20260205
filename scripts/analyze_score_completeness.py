import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

for stage, score_table in [('BOOK','review_scores'), ('INTERVIEW','interview_scores')]:
    print('='*60)
    print(f'【{stage}阶段】')

    # 任务总数 & 状态分布
    cur.execute("""
        SELECT rt.status, COUNT(*) cnt
        FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE rt.stage=%s AND r.competition_id=1
        GROUP BY rt.status ORDER BY rt.status
    """, (stage,))
    rows = cur.fetchall()
    total_tasks = sum(r[1] for r in rows)
    print(f'  评审任务总数: {total_tasks}')
    for r in rows:
        pct = r[1]/total_tasks*100
        print(f'    {r[0]:10s}: {r[1]:3d} 条  ({pct:.1f}%)')

    # 涉及多少个项目（registrationId）
    cur.execute("""
        SELECT COUNT(DISTINCT rt.registration_id)
        FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE rt.stage=%s AND r.competition_id=1
    """, (stage,))
    total_regs = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT rt.registration_id)
        FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE rt.stage=%s AND r.competition_id=1 AND rt.status='SCORED'
    """, (stage,))
    scored_regs = cur.fetchone()[0]
    print(f'  涉及项目数: {total_regs}，其中有打分的: {scored_regs}，完全无打分: {total_regs-scored_regs}')

    # 项目维度：分配了任务但没有任何SCORED的
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT rt.registration_id
            FROM review_tasks rt
            JOIN registrations r ON rt.registration_id = r.id
            WHERE rt.stage=%s AND r.competition_id=1
            GROUP BY rt.registration_id
            HAVING SUM(CASE WHEN rt.status='SCORED' THEN 1 ELSE 0 END) = 0
        ) t
    """, (stage,))
    zero_scored = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT rt.registration_id
            FROM review_tasks rt
            JOIN registrations r ON rt.registration_id = r.id
            WHERE rt.stage=%s AND r.competition_id=1
            GROUP BY rt.registration_id
            HAVING SUM(CASE WHEN rt.status='SCORED' THEN 1 ELSE 0 END) >= 1
               AND SUM(CASE WHEN rt.status='SCORED' THEN 1 ELSE 0 END) <
                   COUNT(rt.id)
        ) t
    """, (stage,))
    partial_scored = cur.fetchone()[0]

    print(f'  项目打分完整度：')
    print(f'    全部未打分: {zero_scored} 个项目（评委已分配但全部 PENDING/RETURNED）')
    print(f'    部分打分:   {partial_scored} 个项目（有评委打了，有评委还没打）')
    print(f'    全部打完:   {scored_regs - partial_scored} 个项目')

    # RETURNED 的说明
    cur.execute("""
        SELECT COUNT(*) FROM review_tasks rt
        JOIN registrations r ON rt.registration_id = r.id
        WHERE rt.stage=%s AND r.competition_id=1 AND rt.status='RETURNED'
    """, (stage,))
    returned = cur.fetchone()[0]
    if returned:
        print(f'  注：RETURNED={returned} 条，表示已退回重审，评分数据已清除，重新等待打分')

    print()

# 看一下 score-list API 返回的"没有分"是哪种情况
print('='*60)
print('【score-list 里"没有总分"的项目构成】')
cur.execute("""
    SELECT rt.status, COUNT(*) cnt
    FROM review_tasks rt
    JOIN registrations r ON rt.registration_id = r.id
    WHERE rt.stage='BOOK' AND r.competition_id=1
      AND rt.registration_id NOT IN (
          SELECT DISTINCT rt2.registration_id
          FROM review_tasks rt2
          WHERE rt2.status='SCORED' AND rt2.stage='BOOK'
      )
    GROUP BY rt.status
""")
for r in cur.fetchall():
    print(f'  无打分项目的任务状态: {r[0]} = {r[1]} 条')

conn.close()
