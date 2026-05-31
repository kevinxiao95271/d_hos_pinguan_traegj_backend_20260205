import pymysql, bcrypt, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', db='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
conn = pymysql.connect(**DB)
cur = conn.cursor()

# 统计现有评委
cur.execute("SELECT COUNT(*) FROM user_accounts WHERE role='REVIEWER' AND enabled=1")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(DISTINCT reviewer_id) FROM review_tasks WHERE stage='FINAL'")
used = cur.fetchone()[0]
print(f"库中评委总数: {total}，已参与FINAL: {used}，未参与: {total-used}")

# 取所有未参与 FINAL 的评委
cur.execute("""
    SELECT id, name, phone FROM user_accounts
    WHERE role='REVIEWER' AND enabled=1
    AND id NOT IN (SELECT DISTINCT reviewer_id FROM review_tasks WHERE stage='FINAL')
    ORDER BY id
""")
unused = cur.fetchall()
print(f"可用未参与评委: {len(unused)} 人")

# 取已参与的评委
cur.execute("""
    SELECT DISTINCT ua.id, ua.name, ua.phone
    FROM user_accounts ua
    JOIN review_tasks rt ON rt.reviewer_id = ua.id
    WHERE rt.stage='FINAL'
    ORDER BY ua.phone
""")
used_revs = cur.fetchall()
print(f"已参与评委: {len(used_revs)} 人")

all_revs = list(used_revs) + list(unused)
target = 30
need_more = max(0, target - len(all_revs))
print(f"\n当前共 {len(all_revs)} 人，目标30人，{'需要新增 ' + str(need_more) + ' 人' if need_more > 0 else '已足够'}")

# 若不够30人则补充（库里找不够就提示）
if len(all_revs) < target:
    print(f"库中评委不足30人（共{len(all_revs)}），全部给出")
    final_list = all_revs
else:
    final_list = all_revs[:target]

# 批量重置密码为 user123
pwd_hash = bcrypt.hashpw(b'user123', bcrypt.gensalt(rounds=10)).decode('utf-8').replace('$2b$', '$2a$')
ids = [r[0] for r in final_list]
cur.execute(f"UPDATE user_accounts SET password=%s WHERE id IN ({','.join(['%s']*len(ids))})",
            [pwd_hash] + ids)
conn.commit()
print(f"\n已重置 {len(final_list)} 个评委密码为 user123\n")

print("全部评委手机号（密码 user123）：")
for rid, name, phone in final_list:
    cur.execute("SELECT COUNT(*) FROM review_tasks WHERE stage='FINAL' AND reviewer_id=%s", (rid,))
    task_cnt = cur.fetchone()[0]
    flag = f"[有{task_cnt}个FINAL任务]" if task_cnt > 0 else "[无任务]"
    print(f"{phone}  {name}  {flag}")

conn.close()
