import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("81.71.44.180", username="root", password="Yiguo9527_", timeout=15)

def run(cmd, timeout=30):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print(f"[ERR] {err}")
    return out

print("=== 1. 停旧进程 ===")
run("kill -9 $(lsof -ti:6031) 2>/dev/null || true")
time.sleep(2)
run("ss -tlnp | grep 6031 || echo 'port 6031 free'")

print("\n=== 2. 验证新 JAR ===")
run("ls -lh /data/pinguan-backend-0.0.1-SNAPSHOT.jar")

print("\n=== 3. 启动新服务 ===")
run("mkdir -p /data/logs")
run("nohup java -jar /data/pinguan-backend-0.0.1-SNAPSHOT.jar > /data/logs/app.log 2>&1 &")
print("等待启动 20s...")
time.sleep(20)

print("\n=== 4. 启动日志 ===")
run("tail -5 /data/logs/app.log")

print("\n=== 5. 端口确认 ===")
result = run("ss -tlnp | grep 6031")
if '6031' in result:
    print("✓ 服务正常运行，端口 6031 已监听")
else:
    print("✗ 端口未监听，请检查日志")

client.close()
print("\n=== 部署完成 ===")
