import paramiko, time

HOST, USER, PASS = "81.71.44.180", "root", "Yiguo9527_"
DB_HOST = "gz-cdb-bq7gk3k5.sql.tencentcdb.com"
DB_PORT = 63606
DB_USER = "root"
DB_PASS = "Yiguo9527_"
DB_NAME = "d_hos_pinguan_traegj_20260205"

def run(client, cmd, t=30):
    _, out, err = client.exec_command(cmd, timeout=t)
    o = out.read().decode("utf-8","replace").strip()
    e = err.read().decode("utf-8","replace").strip()
    print(f"$ {cmd[:120]}")
    if o: print(f"  {o[:600]}")
    if e and "warning" not in e.lower(): print(f"  ERR: {e[:200]}")
    return o

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=10)

print("=== 1. 验证 group_type 列 ===")
sql_check = (
    f"mysql -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p{DB_PASS} {DB_NAME} "
    f"-e \"SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS "
    f"WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='final_ranking_snapshots' "
    f"AND COLUMN_NAME='group_type';\" 2>&1 | grep -v -i warning"
)
out = run(client, sql_check, t=20)
if "group_type" in out:
    print("  [OK] group_type 列已存在")
else:
    print("  [WARN] group_type 列不存在，手动补 DDL...")
    ddl = (
        f"mysql -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p{DB_PASS} {DB_NAME} "
        f"-e \"ALTER TABLE final_ranking_snapshots "
        f"ADD COLUMN IF NOT EXISTS group_type VARCHAR(32) NULL "
        f"COMMENT 'BASIC/COMPREHENSIVE/ADVANCED';\" 2>&1 | grep -v -i warning"
    )
    run(client, ddl, t=20)

print("\n=== 2. 验证进程健康 ===")
run(client, "pgrep -fa pinguan-backend | head -2")
run(client, "curl -s http://localhost:6031/actuator/health 2>/dev/null")

print("\n=== 3. 查服务最新日志（后10行） ===")
run(client, "tail -10 /data/logs/app.log")

client.close()
print("\n完成")
