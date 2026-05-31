import paramiko, os, sys, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"
LOCAL_JAR = r"d:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\target\pinguan-backend-0.0.1-SNAPSHOT.jar"
REMOTE_DIR = "/data/pinguan"
REMOTE_JAR = f"{REMOTE_DIR}/pinguan-backend.jar"
BACKUP_JAR = f"{REMOTE_DIR}/pinguan-backend.bak.jar"
START_SCRIPT = f"{REMOTE_DIR}/_start_pinguan.sh"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=22, username=USER, password=PASS, timeout=30)

def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out: print(f"  > {out}")
    if err and 'warning' not in err.lower(): print(f"  ERR: {err}")
    return out

print("1. 备份旧 JAR")
run(f"[ -f {REMOTE_JAR} ] && cp {REMOTE_JAR} {BACKUP_JAR} && echo 'backup ok' || echo 'no old jar'")

print("2. 上传新 JAR (~84MB 需要一点时间...)")
sftp = ssh.open_sftp()
run(f"mkdir -p {REMOTE_DIR}")
size = os.path.getsize(LOCAL_JAR)
uploaded = [0]
def progress(sent, total):
    pct = int(sent * 100 / total)
    if pct % 20 == 0 and pct != progress.last:
        print(f"  上传进度: {pct}% ({sent//1024//1024}MB/{total//1024//1024}MB)")
        progress.last = pct
progress.last = -1
sftp.put(LOCAL_JAR, REMOTE_JAR, callback=progress)
sftp.close()
print("  上传完成")

print("3. 停止旧进程")
run("pkill -f 'pinguan-backend' || true")
run("fuser -k 6031/tcp 2>/dev/null || true")
time.sleep(3)
run("ss -tlnp | grep 6031 && echo 'port still in use' || echo 'port free'")

print("4. 检查启动脚本")
out = run(f"cat {START_SCRIPT} 2>/dev/null || echo 'NOT_FOUND'")
if "NOT_FOUND" in out:
    print("  启动脚本不存在，创建...")
    script = f"""#!/bin/bash
cd {REMOTE_DIR}
nohup java -jar -Dspring.profiles.active=prod -Xms256m -Xmx512m {REMOTE_JAR} > {REMOTE_DIR}/app.log 2>&1 &
echo $! > {REMOTE_DIR}/app.pid
echo "Started PID $!"
"""
    sftp2 = ssh.open_sftp()
    with sftp2.open(START_SCRIPT, 'w') as f:
        f.write(script)
    sftp2.close()
    run(f"chmod +x {START_SCRIPT}")

print("5. 启动新版本")
run(f"bash {START_SCRIPT}")
time.sleep(5)

print("6. 验证进程")
out = run("ps aux | grep pinguan-backend | grep -v grep")
if "pinguan" in out:
    print("  进程正常运行")
else:
    print("  警告: 进程未找到，查看日志...")
    run(f"tail -30 {REMOTE_DIR}/app.log")

print("7. 等待启动 (15s)...")
time.sleep(15)
health = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:6031/api/auth/login-with-password -X POST -H 'Content-Type: application/json' -d '{\"phone\":\"13800000005\",\"password\":\"ops2026\"}' 2>/dev/null || echo 'curl failed'")
if "200" in health or "400" in health:
    print(f"  服务健康检查通过 (HTTP {health})")
else:
    print(f"  服务响应: {health}")
    run(f"tail -20 {REMOTE_DIR}/app.log")

ssh.close()
print("\n部署完成！")
