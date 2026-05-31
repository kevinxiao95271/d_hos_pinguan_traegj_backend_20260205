import paramiko, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("81.71.44.180", port=22, username="root", password="Yiguo9527_", timeout=30)

def run(cmd, timeout=15):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace')

# 取最近500行日志，过滤 ERROR/Exception/login 相关
log = run("tail -500 /data/pinguan/app.log | grep -i 'error\\|exception\\|login\\|password\\|authenticate' | tail -60")
print(log)
ssh.close()
