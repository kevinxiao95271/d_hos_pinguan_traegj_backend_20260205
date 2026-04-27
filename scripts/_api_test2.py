import sys, io, json, requests, bcrypt, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = 'http://localhost:6031'
DB = dict(host='gz-cdb-bq7gk3k5.sql.tencentcdb.com', port=63606,
          user='root', password='Yiguo9527_', database='d_hos_pinguan_traegj_20260205', charset='utf8mb4')

# 生成 jbcrypt 兼容的 $2a$ hash
def bcrypt_2a(password):
    h = bcrypt.hashpw(password.encode(), bcrypt.gensalt(8))
    return h.decode().replace('$2b$', '$2a$')

new_pwd = 'Test1234'
hashed = bcrypt_2a(new_pwd)
print(f'生成 jbcrypt 兼容 hash: {hashed[:20]}...')

conn = pymysql.connect(**DB)
with conn.cursor() as cur:
    # 找面谈评委
    cur.execute("""SELECT id, phone, name, interview_group_code 
                   FROM user_accounts 
                   WHERE role='REVIEWER' AND enabled=1 
                     AND interview_group_code IS NOT NULL AND interview_group_code != ''
                   LIMIT 1""")
    reviewer = cur.fetchone()
    rid, phone, name, ig = reviewer
    print(f'测试评委: {name}（id={rid}, phone={phone}, interview_group={ig}）')

    cur.execute("UPDATE user_accounts SET password=%s WHERE id=%s", (hashed, rid))
    conn.commit()
    print(f'密码已重置为: {new_pwd}')

    # 顺便看其 notice 状态
    cur.execute("SELECT notice_key FROM reviewer_integrity_notices WHERE user_id=%s", (rid,))
    confirmed = [r[0] for r in cur.fetchall()]
    pending = [k for k in ['BOOK', 'INTERVIEW'] if k not in confirmed]
    print(f'已确认须知: {confirmed}')
    print(f'待确认须知: {pending}')
conn.close()

# 登录测试
print(f'\n=== API 登录测试 ===')
r = requests.post(f'{API}/api/auth/login-with-password',
    json={'phone': phone, 'password': new_pwd}, timeout=20)
body = r.json()
data = body.get('data') or {}
print(f'success: {body.get("success")}  message: {body.get("message", "")}')
print(f'name    : {data.get("name")}')
print(f'role    : {data.get("role")}')
print(f'noticeConfirmed           : {data.get("noticeConfirmed")}')
print(f'pendingIntegrityNoticeKeys: {data.get("pendingIntegrityNoticeKeys")}')

expected = pending
actual = data.get('pendingIntegrityNoticeKeys')
print(f'\n=== 验证 ===')
print(f'数据库待确认: {expected}')
print(f'API返回字段 : {actual}')
if actual == expected:
    print('✅ 一致，逻辑正确！')
else:
    print('❌ 不一致，需排查！')
