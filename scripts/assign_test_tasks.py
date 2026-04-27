"""
测试环境数据准备：
1. 重置 OPS 管理员密码
2. 查有材料的报名项目（取前12条）
3. 查可用的 REVIEWER
4. 分配书审任务（4个项目，3位评委，部分重叠）
5. 分配面谈任务（3个项目，3位评委，与书审有重叠）
6. 重置书审/面谈各一名评委密码并输出
"""
import pymysql, bcrypt, json, random, string

DB = dict(
    host='gz-cdb-bq7gk3k5.sql.tencentcdb.com',
    port=63606,
    user='root',
    password='Yiguo9527_',
    database='d_hos_pinguan_traegj_20260205',
    charset='utf8mb4',
)

def make_hash(pwd: str) -> str:
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt(8)).decode().replace('$2b$', '$2a$')

def rand_pwd(n=8):
    chars = string.ascii_letters + string.digits
    while True:
        p = ''.join(random.choices(chars, k=n))
        if any(c.isdigit() for c in p) and any(c.isalpha() for c in p):
            return p

conn = pymysql.connect(**DB)
cur = conn.cursor(pymysql.cursors.DictCursor)

# ── 1. 重置管理员密码 ─────────────────────────────────────────────────────────
ops_pwd = 'ops2026'
ops_hash = make_hash(ops_pwd)
cur.execute("UPDATE user_accounts SET password=%s WHERE phone='13800010001'", (ops_hash,))
conn.commit()
print(f'[OK] 管理员 13800010001 密码已重置为: {ops_pwd}')

# ── 2. 查竞赛 ─────────────────────────────────────────────────────────────────
cur.execute("SELECT id, name, stage FROM competitions ORDER BY id DESC LIMIT 1")
comp = cur.fetchone()
comp_id = comp['id']
print(f'\n竞赛: id={comp_id} name={comp["name"]} stage={comp["stage"]}')

# ── 3. 查有材料且 SUBMITTED/APPROVED 的报名项目 ──────────────────────────────
cur.execute("""
    SELECT r.id, r.project_name, r.group_type, r.group_code,
           i.name AS inst_name, r.status
    FROM registrations r
    LEFT JOIN institutions i ON r.institution_id = i.id
    WHERE r.competition_id = %s
      AND r.status IN ('SUBMITTED','APPROVED')
    ORDER BY r.id
    LIMIT 12
""", (comp_id,))
regs = cur.fetchall()
print(f'\n有效报名项目（前{len(regs)}条）:')
for r in regs:
    print(f"  id={r['id']} groupType={r['group_type']} groupCode={r['group_code']} "
          f"project={r['project_name'][:18]} inst={r['inst_name']}")

if len(regs) < 5:
    print('报名项目不足5条，无法分配测试任务')
    cur.close(); conn.close()
    exit(1)

# ── 4. 查 REVIEWER（取前10条有 reviewerGroupCode 或直接取前10） ─────────────
cur.execute("""
    SELECT id, name, phone, reviewer_group_code, interview_group_code,
           expert_background, institution_id
    FROM user_accounts
    WHERE role = 'REVIEWER' AND enabled = 1
    ORDER BY id
    LIMIT 10
""")
reviewers = cur.fetchall()
print(f'\n可用评委（前{len(reviewers)}条）:')
for rv in reviewers:
    print(f"  id={rv['id']} name={rv['name']} phone={rv['phone']} "
          f"bookGrp={rv['reviewer_group_code']} interviewGrp={rv['interview_group_code']}")

if len(reviewers) < 4:
    print('评委不足4人，无法分配')
    cur.close(); conn.close()
    exit(1)

# ── 5. 清理已有测试任务（可重复跑）────────────────────────────────────────────
reg_ids_all = [r['id'] for r in regs]
rv_ids_all  = [rv['id'] for rv in reviewers]
fmt = ','.join(['%s'] * len(reg_ids_all))
cur.execute(f"DELETE FROM review_tasks WHERE registration_id IN ({fmt}) AND stage IN ('BOOK','INTERVIEW')",
            reg_ids_all)
conn.commit()
print(f'\n[清理] 删除旧测试任务: {cur.rowcount} 条')

# ── 6. 分配书审任务 ──────────────────────────────────────────────────────────
# 取前6条项目，3位评委
book_regs = regs[:6]
book_rvs  = reviewers[:3]

# 分配规则：每个项目分给 2 位评委（轮询），覆盖所有3位评委
from datetime import datetime
now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
book_tasks = []
for i, r in enumerate(book_regs):
    # 轮流选2位评委
    rv_a = book_rvs[i % 3]
    rv_b = book_rvs[(i + 1) % 3]
    for rv in [rv_a, rv_b]:
        book_tasks.append((r['id'], rv['id'], now_str))

cur.executemany("""
    INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
    VALUES ('BOOK', %s, %s, 'PENDING', %s)
""", book_tasks)
conn.commit()
print(f'\n[书审] 已分配 {cur.rowcount} 条任务，涉及项目 {[r["id"] for r in book_regs]}，评委 {[rv["id"] for rv in book_rvs]}')

# ── 7. 分配面谈任务 ──────────────────────────────────────────────────────────
# 取第 3-7 条项目（与书审有重叠），3位评委（与书审有重叠：共用评委[0][1]，新增评委[3]）
interview_regs = regs[2:7]  # 与书审有重叠的项目
interview_rvs  = reviewers[:2] + [reviewers[3]]  # 前两位与书审重叠，第3位新增

interview_tasks = []
for i, r in enumerate(interview_regs):
    rv_a = interview_rvs[i % 3]
    rv_b = interview_rvs[(i + 1) % 3]
    for rv in [rv_a, rv_b]:
        interview_tasks.append((r['id'], rv['id'], now_str))

cur.executemany("""
    INSERT IGNORE INTO review_tasks (stage, registration_id, reviewer_id, status, created_at)
    VALUES ('INTERVIEW', %s, %s, 'PENDING', %s)
""", interview_tasks)
conn.commit()
print(f'[面谈] 已分配 {cur.rowcount} 条任务，涉及项目 {[r["id"] for r in interview_regs]}，评委 {[rv["id"] for rv in interview_rvs]}')

# ── 8. 汇总每位评委的任务数量 ─────────────────────────────────────────────────
print('\n各评委任务汇总:')
for rv in reviewers[:4]:
    cur.execute("""
        SELECT stage, COUNT(*) cnt FROM review_tasks
        WHERE reviewer_id=%s AND stage IN ('BOOK','INTERVIEW')
        GROUP BY stage
    """, (rv['id'],))
    rows = cur.fetchall()
    summary = {row['stage']: row['cnt'] for row in rows}
    print(f"  {rv['name']}(id={rv['id']}) 书审={summary.get('BOOK',0)} 面谈={summary.get('INTERVIEW',0)}")

# ── 9. 重置书审评委[2] 和面谈专属评委[3] 密码 ─────────────────────────────────
targets = [
    {'rv': book_rvs[2],       'label': '书审专属评委（单书审任务）'},
    {'rv': interview_rvs[2],  'label': '面谈专属评委（单面谈任务）'},
    {'rv': book_rvs[0],       'label': '书审+面谈重叠评委（多任务）'},
]
result = []
print('\n密码重置结果:')
for t in targets:
    rv = t['rv']
    new_pwd = rand_pwd()
    new_hash = make_hash(new_pwd)
    cur.execute("UPDATE user_accounts SET password=%s WHERE id=%s", (new_hash, rv['id']))
    conn.commit()
    result.append({
        'label': t['label'],
        'id': rv['id'],
        'name': rv['name'],
        'phone': rv['phone'],
        'new_password': new_pwd,
    })
    print(f"  [{t['label']}]")
    print(f"    姓名: {rv['name']}  手机: {rv['phone']}  新密码: {new_pwd}")

cur.close()
conn.close()

with open('scripts/test_reviewer_accounts.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('\n已保存到 scripts/test_reviewer_accounts.json')
