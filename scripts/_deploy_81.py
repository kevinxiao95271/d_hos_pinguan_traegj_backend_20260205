import paramiko, time, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"
LOCAL_JAR = "target/pinguan-backend-0.0.1-SNAPSHOT.jar"
REMOTE_JAR = "/data/pinguan-backend-0.0.1-SNAPSHOT.jar"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=15):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    o = out.read().decode().strip()
    e = err.read().decode().strip()
    return o, e

# 1. 上传 JAR
jar_size = os.path.getsize(LOCAL_JAR)
print(f"上传 JAR ({jar_size//1024//1024} MB) -> {REMOTE_JAR}.new ...")
sftp = ssh.open_sftp()
sftp.put(LOCAL_JAR, REMOTE_JAR + ".new")
sftp.close()
print("上传完成")

# 2. 备份旧 JAR
ts = time.strftime("%Y%m%d_%H%M%S")
backup = f"{REMOTE_JAR}.backup_{ts}"
run(f"cp {REMOTE_JAR} {backup}")
print(f"已备份 -> {backup}")

# 3. 替换
run(f"mv {REMOTE_JAR}.new {REMOTE_JAR}")
print("JAR 已替换")

# 4. 杀旧进程
pids_out, _ = run("ps aux | grep '[p]inguan-backend' | awk '{print $2}'")
if pids_out:
    for pid in pids_out.split():
        run(f"kill {pid}")
    print(f"旧进程已终止: {pids_out}")
    time.sleep(3)
else:
    print("无旧进程在运行")

# 5. 写启动脚本
JVM_OPTS = (
    "-Xms512m -Xmx1024m "
    "-Dfile.encoding=UTF-8 "
    "-Duser.timezone=GMT+08 "
    "-Dlogging.level.root=INFO "
    "-Dlogging.level.org.hibernate=WARN "
    "-Dlogging.level.org.hibernate.SQL=WARN "
    "-Dlogging.level.org.hibernate.type=WARN "
    "-Dlogging.level.com.zaxxer.hikari=WARN "
    "-Dlogging.level.org.springframework.web=WARN "
    "-Dlogging.level.org.apache.catalina=WARN "
    "-Dlogging.level.org.apache.coyote=WARN "
    "-Dserver.tomcat.threads.max=500 "
    "-Dspring.datasource.hikari.maximum-pool-size=30 "
    "-Dspring.datasource.hikari.minimum-idle=10 "
    "-Dspring.datasource.hikari.connection-timeout=5000 "
    "-Dspring.datasource.hikari.idle-timeout=300000 "
    "-Dspring.datasource.hikari.max-lifetime=600000"
)
script = f"""#!/bin/bash
cd /data
nohup java -jar {JVM_OPTS} pinguan-backend-0.0.1-SNAPSHOT.jar > /data/app.log 2>&1 &
echo $! > /data/pinguan.pid
echo "started pid: $!"
"""
sftp2 = ssh.open_sftp()
with sftp2.file("/data/_start_pinguan.sh", "w") as f:
    f.write(script)
sftp2.close()
run("chmod +x /data/_start_pinguan.sh")

# 6. 启动
out, err = run("setsid /data/_start_pinguan.sh > /dev/null 2>&1 & sleep 2 && cat /data/pinguan.pid")
print(f"新进程 PID: {out}")
if err:
    print(f"[err] {err}")

# 7. 等待启动，检查端口
print("等待服务启动...")
time.sleep(8)
port_out, _ = run("ss -tlnp | grep 6031")
if port_out:
    print(f"✅ 服务已启动，端口 6031 监听中")
    print(f"   {port_out}")
else:
    print("⏳ 端口未就绪，继续等待...")
    time.sleep(8)
    port_out2, _ = run("ss -tlnp | grep 6031")
    if port_out2:
        print(f"✅ 服务已启动: {port_out2}")
    else:
        log_tail, _ = run("tail -20 /data/app.log")
        print(f"❌ 端口仍未就绪，日志末尾:\n{log_tail}")

ssh.close()
print("部署完成")
