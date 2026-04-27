import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:6031'

# 更多候选密码
extra_pwds = ['ops2026', 'Yiguo9527_', '123456', 'admin123', 'pinguan2026',
              'test1234', 'Test1234', 'password', 'P@ssw0rd', '12345678',
              'reviewer', 'contest2026', 'Pinguan@2026']

accounts = [
    ('COMMITTEE_ADMIN', '13800000127'),
    ('COMMITTEE_ADMIN', '13900000001'),
    ('REVIEWER',        '13800002569'),
    ('REVIEWER',        '13811185687'),
    ('CONTESTANT',      '13799999112'),
    ('CONTESTANT',      '13872005640'),
    ('OPS',             '13800000001'),
    ('OPS',             '13800000027'),
]

print(f'{"角色":<20} {"手机号":<15} {"可用密码"}')
print('-' * 55)
for role, phone in accounts:
    found = None
    for pwd in extra_pwds:
        try:
            r = requests.post(f'{BASE}/api/auth/login-with-password',
                json={'phone': phone, 'password': pwd}, timeout=4)
            if r.status_code == 200 and r.json().get('success'):
                found = pwd
                break
        except:
            pass
    print(f'{role:<20} {phone:<15} {found if found else "---"}')
