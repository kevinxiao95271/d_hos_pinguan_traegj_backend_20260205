import paramiko, time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = '81.71.44.180'
PORT = 22
USER = 'root'
PWD  = 'Yiguo9527_'

JAR_LOCAL  = r'd:\iCode\cursor\d_hos_pinguan_traegj_backend_20260205\target\pinguan-backend-0.0.1-SNAPSHOT.jar'
JAR_REMOTE = '/opt/pinguan/pinguan-backend-0.0.1-SNAPSHOT.jar'
APP_PORT   = 6031

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PWD, timeout=10)
print("SSH 连接成功")

def run(cmd):
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out: print(f"  OUT: {out}")
    if err: print(f"  ERR: {err}")
    return out

# 停止旧进程
print("\n[1] 停止旧进程...")
run(f"pid=$(lsof -ti:{APP_PORT}) && [ -n \"$pid\" ] && kill -9 $pid && echo 'killed '$pid || echo 'no process'")
time.sleep(2)

# 上传 JAR
print("\n[2] 上传 JAR...")
sftp = ssh.open_sftp()
sftp.put(JAR_LOCAL, JAR_REMOTE)
sftp.close()
print("  上传完成")

# 启动
print("\n[3] 启动服务...")
start_cmd = (
    f"nohup java -jar {JAR_REMOTE} "
    f"--server.port={APP_PORT} "
    f"--spring.profiles.active=prod "
    f"> /opt/pinguan/app.log 2>&1 &"
)
run(start_cmd)
time.sleep(8)

# 检查
print("\n[4] 检查进程...")
out = run(f"lsof -ti:{APP_PORT}")
if out:
    print(f"  服务已启动 PID={out}")
else:
    print("  未检测到进程，查看日志：")
    run("tail -20 /opt/pinguan/app.log")

ssh.close()
print("\n完成")
