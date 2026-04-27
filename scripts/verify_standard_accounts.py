import requests, pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'

conn = pymysql.connect(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
    user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')
cur = conn.cursor()

# 标准账号 + 已知密码
std = [
    ('OPS',             '13800010001', 'ops2026'),
    ('OPS',             '13800010002', 'ops2026'),
    ('OPS',             '13800000005', 'ops2026'),   # 开发账号
    ('COMMITTEE_ADMIN', '13800020001', 'committee2026'),
    ('COMMITTEE_ADMIN', '13800020002', 'committee2026'),
    ('COMMITTEE_ADMIN', '13800000127', 'committee2026'),
]

# 评委和参赛者——通过手机号注册，尝试 SMS 登录的临时码或默认密码
reviewer_phones = ['13800002569','13811185687','13886509429']
contestant_phones = ['13799999112','13872005640','13865347123']

print(f'{"角色":<20} {"手机号":<15} {"登录结果"}')
print('-' * 55)

for role, phone, pwd in std:
    try:
        r = requests.post(f'{BASE}/api/auth/login-with-password',
            json={'phone': phone, 'password': pwd}, timeout=5)
        d = r.json()
        ok = '✓ 登录成功' if d.get('success') else f'✗ {d.get("message","失败")}'
    except Exception as e:
        ok = f'ERR: {e}'
    # 查DB确认是否存在
    cur.execute('SELECT id, name FROM user_accounts WHERE phone=%s', (phone,))
    row = cur.fetchone()
    exists = f'(db id={row[0]} {row[1]})' if row else '(DB不存在)'
    print(f'{role:<20} {phone:<15} {ok}  {exists}')

print()
# 评委/参赛者：不清楚密码，只显示DB信息
for label, phones in [('REVIEWER', reviewer_phones), ('CONTESTANT', contestant_phones)]:
    print(f'--- {label} ---')
    for phone in phones:
        cur.execute('SELECT id, name, enabled FROM user_accounts WHERE phone=%s', (phone,))
        row = cur.fetchone()
        if row:
            print(f'  phone={phone}  id={row[0]} name={row[1]} enabled={row[2]}  (密码需重置)')

conn.close()
