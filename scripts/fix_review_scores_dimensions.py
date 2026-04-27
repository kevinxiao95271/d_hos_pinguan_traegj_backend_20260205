"""
修复书审评分的细节分：将 plan~operation 全为 0 的测试数据，
按真实七维权重比例重新拆解，确保各维度之和 == total。

七维标准满分分配（共 100 分）：
  plan(计划拟定)         15
  problem(问题解析)       20
  action(对策与实施)      20
  success(成果)          20
  review(检讨与改进)      10
  operation(活动运作)     10
  presentation(报告呈现)   5
"""
import pymysql, random, sys
sys.stdout.reconfigure(encoding='utf-8')

# 七维满分权重（合计 100）
WEIGHTS = [15, 20, 20, 20, 10, 10, 5]
NAMES   = ['plan','problem','action','success','review','operation','presentation']

def split_score(total: float) -> list:
    """
    把 total 按权重拆成 7 个子分，并加入 ±1.5 分随机扰动，
    最后一维用 total - sum(前6) 保证精确匹配。
    """
    random.seed(total * 7919 % 999983)   # 对同一 total 保持确定性
    parts = []
    for i, w in enumerate(WEIGHTS[:-1]):
        base = round(total * w / 100, 1)
        # 在 ±1.5 内随机微调，但不低于 0 且不超过该维度满分
        noise = round(random.uniform(-1.5, 1.5), 1)
        v = round(max(0.0, min(w, base + noise)), 1)
        parts.append(v)
    # 最后一维 = total - 前6维之和，保证合计精确
    last = round(total - sum(parts), 1)
    last = max(0.0, last)
    parts.append(last)
    return parts

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute('SELECT id, total FROM review_scores WHERE plan=0 AND problem=0 AND action=0 AND success=0')
rows = cur.fetchall()
print(f'待修复 {len(rows)} 条')

updated = 0
errors  = 0
for rid, total in rows:
    parts = split_score(float(total))
    assert abs(sum(parts) - float(total)) < 0.05, f'id={rid} sum={sum(parts)} != total={total}'
    cur.execute('''
        UPDATE review_scores
        SET plan=%s, problem=%s, action=%s, success=%s, review=%s, operation=%s, presentation=%s
        WHERE id=%s
    ''', (*parts, rid))
    updated += 1

conn.commit()

# 验证
cur.execute('''
    SELECT id, plan, problem, action, success, review, operation, presentation, total
    FROM review_scores
    ORDER BY id LIMIT 5
''')
print('\n修复后前 5 条样本：')
print(f'{"id":>5}  {"plan":>5} {"problem":>7} {"action":>6} {"success":>7} {"review":>6} {"op":>5} {"pres":>5} {"total":>6}  {"sum(6)":>6}')
for r in cur.fetchall():
    s = sum(r[1:8])
    ok = '✓' if abs(s - r[8]) < 0.05 else '✗'
    print(f'{r[0]:>5}  {r[1]:>5} {r[2]:>7} {r[3]:>6} {r[4]:>7} {r[5]:>6} {r[6]:>5} {r[7]:>5} {r[8]:>6}  {s:>6.1f} {ok}')

conn.close()
print(f'\n[完成] 更新 {updated} 条，错误 {errors} 条')
