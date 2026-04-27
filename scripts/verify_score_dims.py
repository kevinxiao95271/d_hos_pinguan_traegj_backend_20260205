import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM review_scores WHERE ABS(plan+problem+action+success+review+operation+presentation-total)>0.05')
bad = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM review_scores WHERE plan=0 AND problem=0 AND action=0')
zero = cur.fetchone()[0]
print(f'合计不匹配: {bad} 条（应为 0）')
print(f'plan~action 全为 0: {zero} 条（应为 0）')

print()
print('随机抽 6 条验证：')
cur.execute('''SELECT id,plan,problem,action,success,review,operation,presentation,total
    FROM review_scores ORDER BY RAND() LIMIT 6''')
print(f'{"id":>4}  {"plan":>5} {"prob":>5} {"act":>5} {"succ":>5} {"rev":>5} {"op":>5} {"pres":>5}  {"total":>6}  ok?')
for r in cur.fetchall():
    s = round(sum(r[1:8]), 1)
    flag = 'OK' if abs(s - r[8]) < 0.05 else 'ERR'
    vals = '  '.join(f'{v:5.1f}' for v in r[1:8])
    print(f'{r[0]:>4}  {vals}  {r[8]:>6.1f}  {flag}')

conn.close()
