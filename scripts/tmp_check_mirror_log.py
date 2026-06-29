import paramiko, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', port=22, username='root', password='Yiguo9527_', timeout=15)

def run(cmd, timeout=20):
    _, out, _ = ssh.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace')

# 先看格式
print('-- mirror_access.log 最新5行 --')
print(run('tail -5 /var/log/nginx/mirror_access.log'))

print('\n-- 文件列表 --')
print(run('ls -lh /var/log/nginx/mirror_access.log*'))

# 今早 draft/submit 相关
for hour in ['08', '09', '10']:
    result = run(f'grep "final/scores" /var/log/nginx/mirror_access.log | grep " {hour}:" | head -5')
    if result.strip():
        print(f'\n-- {hour}点 final/scores 请求 --')
        print(result)

# 今早的 mirror_access.log-20260603
for hour in ['08', '09', '10']:
    result = run(f'grep "final/scores" /var/log/nginx/mirror_access.log-20260603 | grep " {hour}:" | head -5')
    if result.strip():
        print(f'\n-- mirror_access.log-20260603 {hour}点 --')
        print(result)

# app.log 中是否有 request body 记录
print('\n-- app.log 今早打分请求 --')
print(run('grep -i "draft\\|submit\\|scoreForm\\|total" /opt/pinguan/app.log | grep "2026-06-03 0[89]" | head -20'))
print(run('grep -i "draft\\|submit\\|scoreForm\\|total" /opt/pinguan/app.log | grep "2026-06-03 10" | head -20'))

ssh.close()
