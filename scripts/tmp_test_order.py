import requests, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = 'http://localhost:6031'

# 直接用已知可登录的评委
test_accounts = [
    ('13859958962', 'user123'),
    ('13881619681', 'user123'),
    ('13857064373', 'user123'),
]

for phone, pwd in test_accounts:
    r = requests.post(f'{BASE}/api/auth/login-with-password',
                      json={'phone': phone, 'password': pwd}, timeout=5)
    if r.status_code != 200 or not r.json().get('success'):
        continue
    token = r.json()['data']['token']
    name = r.json()['data']['name']

    r2 = requests.get(f'{BASE}/api/reviews/final/my-tasks',
                      headers={'Authorization': f'Bearer {token}'}, timeout=10)
    tasks = r2.json().get('data', [])
    if not tasks:
        continue

    print(f"\n== {name} ({phone})  共{len(tasks)}条")
    print(f"{'#':>3}  {'order':>5}  {'status':<8}  {'score':>5}  项目名称")
    for i, t in enumerate(tasks[:15]):
        print(f"{i+1:>3}  {str(t.get('sessionOrder') or ''):>5}  "
              f"{t.get('status'):<8}  {str(t.get('total') or ''):>5}  "
              f"{t.get('projectName','')[:30]}")

    # 验证 sessionCode+sessionOrder 单调递增
    ok = True
    ls, lo = None, -1
    for t in tasks:
        s = t.get('sessionCode')
        o = t.get('sessionOrder') or 0
        if s != ls:
            ls, lo = s, -1
        if o < lo:
            print(f"  !! 顺序异常 order={o} < prev={lo}")
            ok = False
        lo = o
    print(f"顺序验证: {'OK - 按sessionOrder单调递增' if ok else 'FAIL'}")
    break
