import paramiko, re, time

HOST, USER, PASS = "81.71.44.180", "root", "Yiguo9527_"

def run(client, cmd, t=30):
    _, out, err = client.exec_command(cmd, timeout=t)
    o = out.read().decode("utf-8","replace").strip()
    e = err.read().decode("utf-8","replace").strip()
    print(f"$ {cmd[:100]}")
    if o: print(f"  {o[:500]}")
    if e and "warning" not in e.lower(): print(f"  ERR: {e[:200]}")
    return o

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

# 1. 查进程环境变量，找 DB URL
pid = run(client, "pgrep -f pinguan-backend | head -1")
if pid.isdigit():
    env_out = run(client, f"cat /proc/{pid}/environ 2>/dev/null | tr '\\0' '\\n' | grep -i 'DS1\\|datasource\\|jdbc\\|MYSQL\\|DB_' | head -20")
    # 尝试 grep 启动命令
    cmdline = run(client, f"cat /proc/{pid}/cmdline 2>/dev/null | tr '\\0' ' '")
    print(f"\ncmdline: {cmdline[:300]}")

# 2. 查 /etc/environment 或 /data/pinguan/.env
for f in ["/etc/environment", "/data/pinguan/.env", "/data/.env", "/root/.bashrc"]:
    run(client, f"grep -i 'PINGUAN_DS\\|jdbc\\|DB_' {f} 2>/dev/null | head -5")

# 3. 从 Hibernate 启动日志找 url
run(client, "grep -i 'HikariPool\\|jdbc:mysql' /data/logs/app.log 2>/dev/null | head -5")

# 4. 服务现在是否健康
run(client, "curl -s -o /dev/null -w '%{http_code}' http://localhost:6031/actuator/health 2>/dev/null || echo no_actuator")

client.close()
