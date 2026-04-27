import paramiko, time

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=10):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    try:
        o = out.read().decode().strip()
    except Exception:
        o = ""
    try:
        e = err.read().decode().strip()
    except Exception:
        e = ""
    return o, e

# 1. 备份
ts = time.strftime("%Y%m%d_%H%M%S")
backup = f"/data/pinguan-backend-0.0.1-SNAPSHOT.jar.backup_{ts}"
run(f"cp /data/pinguan-backend-0.0.1-SNAPSHOT.jar {backup}")
print(f"已备份 -> {backup}")

# 2. 替换
run("mv /data/pinguan-backend-0.0.1-SNAPSHOT.jar.new /data/pinguan-backend-0.0.1-SNAPSHOT.jar")
print("JAR 已替换")

# 3. 杀旧进程
pids_out, _ = run("ps aux | grep '[p]inguan-backend' | awk '{print $2}'")
if pids_out:
    for pid in pids_out.split():
        run(f"kill {pid} || true")
    print(f"旧进程已终止: {pids_out}")
else:
    print("无旧进程在运行")

time.sleep(2)

# 4. 写启动脚本到服务器，然后 nohup 执行（避免 paramiko channel 阻塞）
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
nohup java -jar {JVM_OPTS} pinguan-backend-0.0.1-SNAPSHOT.jar > app.log 2>&1 &
echo $! > /data/pinguan.pid
echo "started pid: $!"
"""
sftp = ssh.open_sftp()
with sftp.file("/data/_start_pinguan.sh", "w") as f:
    f.write(script)
sftp.close()

run("chmod +x /data/_start_pinguan.sh")

# 使用 at 或 setsid 让进程独立于 SSH session
out, err = run("setsid /data/_start_pinguan.sh > /dev/null 2>&1 & sleep 1 && cat /data/pinguan.pid")
print(f"新进程 PID: {out}")
if err:
    print(f"[err] {err}")

ssh.close()
print("部署完成")
