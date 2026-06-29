import paramiko, time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', port=22, username='root', password='Yiguo9527_', timeout=30)

def run(cmd, timeout=15):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()

def run_bg(cmd):
    ssh.exec_command(cmd)  # 不等返回，后台执行

# 强杀旧进程
print('=== 强杀旧进程 ===')
run('kill -9 $(pgrep -f pinguan-backend-0.0.1) 2>/dev/null; echo done')
time.sleep(2)
print('进程:', run('pgrep -fl pinguan-backend || echo 已停止'))

# 启动（不等待输出）
print('\n=== 启动新进程 ===')
run_bg('cd /opt/pinguan && nohup java -jar -Dspring.profiles.active=prod -Xms256m -Xmx512m pinguan-backend-0.0.1-SNAPSHOT.jar >> app.log 2>&1 &')
print('等待启动...')
time.sleep(12)

print('进程:', run('pgrep -fl pinguan-backend'))
print('端口:', run('ss -tlnp | grep 6031 || echo 未监听'))
print('\n=== 最新日志 ===')
print(run('tail -8 /opt/pinguan/app.log'))

ssh.close()
