import paramiko, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = '81.71.44.180'
USER = 'root'
PWD  = 'Yiguo9527_'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PWD, timeout=10)

def run(cmd):
    _, o, e = ssh.exec_command(cmd)
    out = o.read().decode('utf-8', errors='replace').strip()
    err = e.read().decode('utf-8', errors='replace').strip()
    return out or err

print('=== 进程 ===')
print(run('lsof -ti:6031'))

print('\n=== 健康检查 ===')
print(run('curl -s --max-time 5 http://localhost:6031/api/health || echo NO_HEALTH'))

print('\n=== 登录 ===')
login_resp = run(
    'curl -s --max-time 10 -X POST http://localhost:6031/api/auth/login-with-password '
    '-H "Content-Type: application/json" '
    '-d \'{"phone":"13309090909","password":"test0909"}\''
)
print(login_resp[:400])

try:
    token = json.loads(login_resp)['data']['token']
    print('\n=== GET /registrations/my ===')
    resp = run(
        f'curl -s --max-time 10 http://localhost:6031/api/registrations/my '
        f'-H "Authorization: Bearer {token}"'
    )
    print(resp[:500])

    print('\n=== GET /registrations/by-applicant ===')
    resp2 = run(
        f'curl -s --max-time 10 http://localhost:6031/api/registrations/by-applicant '
        f'-H "Authorization: Bearer {token}"'
    )
    print(resp2[:500])
except Exception as ex:
    print(f'解析 token 失败: {ex}')

ssh.close()
