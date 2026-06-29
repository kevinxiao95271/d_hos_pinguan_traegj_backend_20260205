import paramiko

HOST, USER, PASS = "81.71.44.180", "root", "Yiguo9527_"

def run(c, cmd, t=20):
    _, o, e = c.exec_command(cmd, timeout=t)
    out = o.read().decode("utf-8","replace").strip()
    err = e.read().decode("utf-8","replace").strip()
    print(f"$ {cmd[:100]}")
    if out: print(f"  {out[:800]}")
    if err and "warning" not in err.lower(): print(f"  ERR: {err[:300]}")
    return out

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

print("=== 1. 进程启动命令 ===")
pid = run(client, "pgrep -f pinguan-backend | head -1")
if pid:
    run(client, f"cat /proc/{pid}/cmdline | tr '\\0' ' '")

print("\n=== 2. 日志里实际连接的 DB URL ===")
run(client, "grep -E 'HikariPool|jdbc:|datasource' /data/logs/app.log 2>/dev/null | head -10")

print("\n=== 3. 日志里的 Hibernate DDL（新增列） ===")
run(client, "grep -i 'alter table\\|add column\\|group_type' /data/logs/app.log 2>/dev/null | head -10")

print("\n=== 4. 最近的错误日志 ===")
run(client, "grep -i 'SQLGrammarException\\|could not execute\\|ERROR' /data/logs/app.log 2>/dev/null | tail -20")

print("\n=== 5. final_ranking_snapshots 表结构（从 81 直连 DB 查） ===")
# 先找 DB 连接串
env_out = run(client, f"strings /proc/{pid}/environ 2>/dev/null | grep -i 'PINGUAN_DS\\|jdbc' | head -5") if pid else ""
# 尝试默认测试 DB
run(client, (
    "mysql -h gz-cdb-bq7gk3k5.sql.tencentcdb.com -P 63606 -u root -pYiguo9527_ "
    "d_hos_pinguan_traegj_20260205 "
    "-e \"DESC final_ranking_snapshots;\" 2>&1 | grep -v -i warning"
), t=20)

client.close()
