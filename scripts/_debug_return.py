import sys, io, json, requests, bcrypt, pymysql
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API = 'http://localhost:6031'
OPS_PHONE = '13800000005'
OPS_PWD   = 'OpsTest123'

# 登录
r = requests.post(f'{API}/api/auth/login-with-password',
    json={'phone': OPS_PHONE, 'password': OPS_PWD}, timeout=15)
body = r.json()
token = body['data']['token']
role = body['data']['role']
print(f'登录成功 role={role}')

# 测试驳回第一个 task
headers = {'Authorization': f'Bearer {token}'}
r2 = requests.post(f'{API}/api/admin/interview-scores/return',
    params={'reviewTaskId': 5}, headers=headers, timeout=15)
print(f'HTTP {r2.status_code}')
print(f'响应: {r2.text[:500]}')
