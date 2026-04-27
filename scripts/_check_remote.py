import paramiko, urllib.request

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd):
    _, out, _ = ssh.exec_command(cmd, timeout=10)
    return out.read().decode().strip()

# 进程是否存在
ps = run("ps aux | grep '[p]inguan-backend' | awk '{print $2, $11}'")
print(f"进程: {ps if ps else '未找到'}")

# health check（从服务器本地 curl）
health = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:6031/actuator/health 2>/dev/null")
print(f"Health: {health}")

# 最近日志末尾
log = run("tail -5 /data/app.log")
print(f"日志:\n{log}")

ssh.close()
