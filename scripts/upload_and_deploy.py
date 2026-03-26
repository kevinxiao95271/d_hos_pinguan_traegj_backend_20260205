import paramiko, time, sys, os
sys.stdout.reconfigure(encoding='utf-8')

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"
LOCAL_JAR = os.path.join(os.path.dirname(__file__), '..', 'target', 'pinguan-backend-0.0.1-SNAPSHOT.jar')
REMOTE_JAR = "/data/pinguan-backend-0.0.1-SNAPSHOT.jar"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"连接 {HOST} ...")
client.connect(HOST, username=USER, password=PASS, timeout=20)
print("SSH 连接成功")

def run(cmd, timeout=30):
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors='replace').strip()
    err = stderr.read().decode(errors='replace').strip()
    if out: print(out)
    if err and 'warning' not in err.lower(): print(f"[ERR] {err}")
    return out

print("\n=== 1. 上传 JAR ===")
local_size = os.path.getsize(LOCAL_JAR)
print(f"本地 JAR: {LOCAL_JAR}  ({local_size/1024/1024:.1f} MB)")
sftp = client.open_sftp()
run("mkdir -p /data")

class Progress:
    def __init__(self, total):
        self.total = total
        self.last = 0
    def __call__(self, sent, total):
        pct = int(sent / total * 100)
        if pct - self.last >= 10:
            print(f"  上传进度: {pct}%  ({sent/1024/1024:.1f}/{total/1024/1024:.1f} MB)")
            self.last = pct

sftp.put(LOCAL_JAR, REMOTE_JAR, callback=Progress(local_size))
sftp.close()
print("上传完成 ✓")

print("\n=== 2. 停旧进程 ===")
run("kill -9 $(lsof -ti:6031) 2>/dev/null || true")
time.sleep(2)
run("ss -tlnp | grep 6031 || echo 'port 6031 free'")

print("\n=== 3. 验证 JAR ===")
run(f"ls -lh {REMOTE_JAR}")

print("\n=== 4. 启动服务 ===")
run("mkdir -p /data/logs")
run(f"nohup java -jar {REMOTE_JAR} > /data/logs/app.log 2>&1 &")
print("等待启动 25s ...")
time.sleep(25)

print("\n=== 5. 启动日志 ===")
run("tail -8 /data/logs/app.log")

print("\n=== 6. 端口确认 ===")
result = run("ss -tlnp | grep 6031 || echo 'NOT LISTENING'")
if '6031' in result and 'NOT' not in result:
    print("\n✓ 服务正常运行，端口 6031 已监听")
else:
    print("\n✗ 端口未监听，查看完整日志:")
    run("tail -30 /data/logs/app.log")

client.close()
print("\n=== 部署完成 ===")
