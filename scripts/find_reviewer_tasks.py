import pymysql
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='43.139.18.26', port=3306,
    user='pinguan', password='pinguan2026',
    database='pinguan', charset='utf8mb4'
)
cur = conn.cursor()

# 找有任务的评委账号（书审+面谈都有任务）
cur.execute("""
SELECT u.id, u.phone, u.name,
    SUM(CASE WHEN rt.stage='BOOK' THEN 1 ELSE 0 END) AS book_tasks,
    SUM(CASE WHEN rt.stage='INTERVIEW' THEN 1 ELSE 0 END) AS interview_tasks,
    SUM(CASE WHEN rt.stage='BOOK' AND rt.status='SCORED' THEN 1 ELSE 0 END) AS book_scored,
    SUM(CASE WHEN rt.stage='INTERVIEW' AND rt.status='SCORED' THEN 1 ELSE 0 END) AS interview_scored
FROM user_accounts u
JOIN review_tasks rt ON rt.reviewer_id = u.id
WHERE u.role = 'REVIEWER'
GROUP BY u.id, u.phone, u.name
HAVING book_tasks > 0 OR interview_tasks > 0
ORDER BY (book_tasks + interview_tasks) DESC
LIMIT 20
""")
rows = cur.fetchall()
print(f"{'手机号':<15} {'姓名':<10} {'书审任务':>6} {'书审已评':>6} {'面谈任务':>6} {'面谈已评':>6}  {'账号ID':>6}")
print("-" * 65)
for r in rows:
    uid, phone, name, bt, it, bs, is_ = r
    print(f"{phone:<15} {(name or ''):<10} {bt:>6} {bs:>6} {it:>6} {is_:>6}  {uid:>6}")

print()
# 找同时有书审和面谈任务的评委
print("=== 同时有书审+面谈任务的评委 ===")
cur.execute("""
SELECT u.id, u.phone, u.name,
    SUM(CASE WHEN rt.stage='BOOK' THEN 1 ELSE 0 END) AS book_tasks,
    SUM(CASE WHEN rt.stage='INTERVIEW' THEN 1 ELSE 0 END) AS interview_tasks,
    SUM(CASE WHEN rt.stage='BOOK' AND rt.status='SCORED' THEN 1 ELSE 0 END) AS book_scored,
    SUM(CASE WHEN rt.stage='INTERVIEW' AND rt.status='SCORED' THEN 1 ELSE 0 END) AS interview_scored
FROM user_accounts u
JOIN review_tasks rt ON rt.reviewer_id = u.id
WHERE u.role = 'REVIEWER'
GROUP BY u.id, u.phone, u.name
HAVING book_tasks > 0 AND interview_tasks > 0
ORDER BY (book_tasks + interview_tasks) DESC
LIMIT 10
""")
rows = cur.fetchall()
for r in rows:
    uid, phone, name, bt, it, bs, is_ = r
    print(f"  {phone}  {(name or ''):<10}  书审{bt}个(已评{bs})  面谈{it}个(已评{is_})  id={uid}")

print()
print("=== 有书审有分、面谈无分 的项目 ===")
cur.execute("""
SELECT r.id AS reg_id, r.project_name, r.group_type,
    COUNT(DISTINCT CASE WHEN rt.stage='BOOK' AND rt.status='SCORED' THEN rt.id END) AS book_scored,
    COUNT(DISTINCT CASE WHEN rt.stage='INTERVIEW' AND rt.status='SCORED' THEN rt.id END) AS interview_scored
FROM registrations r
JOIN review_tasks rt ON rt.registration_id = r.id
GROUP BY r.id, r.project_name, r.group_type
HAVING book_scored > 0 AND interview_scored = 0
LIMIT 5
""")
rows = cur.fetchall()
for r in rows:
    print(f"  reg_id={r[0]}  {r[2]}  书审已评{r[3]}  面谈已评{r[4]}  {r[1][:30]}")

print()
print("=== 无书审分、有面谈有分 的项目 ===")
cur.execute("""
SELECT r.id AS reg_id, r.project_name, r.group_type,
    COUNT(DISTINCT CASE WHEN rt.stage='BOOK' AND rt.status='SCORED' THEN rt.id END) AS book_scored,
    COUNT(DISTINCT CASE WHEN rt.stage='INTERVIEW' AND rt.status='SCORED' THEN rt.id END) AS interview_scored
FROM registrations r
JOIN review_tasks rt ON rt.registration_id = r.id
GROUP BY r.id, r.project_name, r.group_type
HAVING book_scored = 0 AND interview_scored > 0
LIMIT 5
""")
rows = cur.fetchall()
for r in rows:
    print(f"  reg_id={r[0]}  {r[2]}  书审已评{r[3]}  面谈已评{r[4]}  {r[1][:30]}")

cur.close()
conn.close()
