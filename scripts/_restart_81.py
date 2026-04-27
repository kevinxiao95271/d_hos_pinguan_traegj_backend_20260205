import paramiko, time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=20):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    o = out.read().decode("utf-8", errors="replace").strip()
    e = err.read().decode("utf-8", errors="replace").strip()
    return o, e

# 1. 杀旧进程
pids_out, _ = run("ps aux | grep '[p]inguan-backend' | awk '{print $2}'")
if pids_out:
    for pid in pids_out.split():
        run(f"kill -9 {pid}")
    print(f"旧进程已终止: {pids_out}")
    time.sleep(3)
else:
    print("无旧进程在运行")

# 2. 启动
out, err = run("setsid /data/_start_pinguan.sh > /dev/null 2>&1 & sleep 2 && cat /data/pinguan.pid")
print(f"新进程 PID: {out}")
if err:
    print(f"[err] {err}")

# 3. 等待端口就绪
print("等待服务启动...")
time.sleep(10)
port_out, _ = run("ss -tlnp | grep 6031")
if port_out:
    print(f"服务已启动，端口 6031 监听中")
    print(f"  {port_out}")
else:
    print("端口未就绪，继续等待...")
    time.sleep(10)
    port_out2, _ = run("ss -tlnp | grep 6031")
    if port_out2:
        print(f"服务已启动: {port_out2}")
    else:
        log_tail, _ = run("tail -30 /data/app.log")
        print(f"端口仍未就绪，日志末尾:\n{log_tail}")

ssh.close()
print("重启完成")
