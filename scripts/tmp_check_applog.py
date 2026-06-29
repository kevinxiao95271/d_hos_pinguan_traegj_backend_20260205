import paramiko, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', port=22, username='root', password='Yiguo9527_', timeout=15)

def run(cmd, timeout=20):
    _, out, _ = ssh.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace')

print('-- app.log 大小 --')
print(run('ls -lh /opt/pinguan/app.log'))

print('\n-- app.log 时间范围 --')
print(run('head -3 /opt/pinguan/app.log'))
print(run('tail -3 /opt/pinguan/app.log'))

print('\n-- 有无 final/scores 请求记录 --')
print(run('grep -c "final/scores" /opt/pinguan/app.log'))

print('\n-- 今早 draft/submit 相关日志 --')
print(run('grep -i "draft\\|submit\\|FinalService\\|scoreForm" /opt/pinguan/app.log | grep "2026-06-03 0[89]\\|2026-06-03 10:[0-4]" | head -30'))

print('\n-- 有无其他日志文件 --')
print(run('ls -lh /opt/pinguan/*.log 2>/dev/null'))
print(run('find /opt/pinguan -name "*.log*" 2>/dev/null'))

ssh.close()
