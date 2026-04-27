import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606, user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

uscc = '123302274196119278'
cur.execute('SELECT id, code, name, region, city, level, uscc FROM const_init_institutions WHERE uscc=%s OR name LIKE %s', (uscc, '%鄞州区第三%'))
print('=== const_init_institutions ===')
for r in cur.fetchall(): print(r)

cur.execute('SELECT id, code, name, region, city, level, uscc FROM institutions WHERE uscc=%s OR name LIKE %s', (uscc, '%鄞州区第三%'))
print('=== institutions ===')
for r in cur.fetchall(): print(r)

# 生成不重复的 code
import uuid, hashlib
raw = hashlib.md5(uscc.encode()).hexdigest()[:8].upper()
code_candidate = f'INST_{raw}'
cur.execute('SELECT COUNT(*) FROM const_init_institutions WHERE code=%s', (code_candidate,))
print(f'\n候选 code: {code_candidate}, const_init冲突: {cur.fetchone()[0]}')
cur.execute('SELECT COUNT(*) FROM institutions WHERE code=%s', (code_candidate,))
print(f'候选 code: {code_candidate}, institutions冲突: {cur.fetchone()[0]}')

conn.close()
