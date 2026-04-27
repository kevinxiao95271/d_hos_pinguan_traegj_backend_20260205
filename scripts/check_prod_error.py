import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("81.71.44.180", username="root", password="Yiguo9527_", timeout=15)

def run(cmd, timeout=30):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out)
    if err: print(f"[ERR] {err}")
    return out

# 强杀所有 java 进程
run("kill -9 $(lsof -ti:6031) 2>/dev/null || true")
time.sleep(2)
run("ss -tlnp | grep 6031 || echo 'port 6031 free'")

# 重启
run("nohup java -jar /data/pinguan-backend-0.0.1-SNAPSHOT.jar > /data/logs/app.log 2>&1 &")
print("等待启动20s...")
time.sleep(20)

run("tail -3 /data/logs/app.log")
run("ss -tlnp | grep 6031")
client.close()
