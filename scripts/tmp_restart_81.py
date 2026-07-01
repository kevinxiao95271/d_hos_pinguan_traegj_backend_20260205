#!/usr/bin/env python3
import io, sys, time, paramiko

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', 22, 'root', 'Yiguo9527_', timeout=15)

def run(cmd, wait=True, timeout=20):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    if not wait:
        return
    out.channel.settimeout(timeout)
    try:
        o = out.read().decode('utf-8', 'replace').strip()
    except Exception:
        o = ''
    try:
        e = err.read().decode('utf-8', 'replace').strip()
    except Exception:
        e = ''
    if o:
        print(o)
    if e and 'nohup' not in e:
        print('ERR:', e)

run('pkill -9 -f pinguan-backend 2>/dev/null; sleep 2; echo killed')
run('lsof -i :6031 2>/dev/null | head -3')

# 后台启动，不等输出
run('cd /opt/pinguan && nohup java -jar pinguan-backend-0.0.1-SNAPSHOT.jar --server.port=6031 --spring.profiles.active=prod >> app.log 2>&1 &', wait=False)
print('等待启动 28s...')
time.sleep(28)
run('pgrep -af pinguan | head -2')
run('tail -8 /opt/pinguan/app.log')

ssh.close()
