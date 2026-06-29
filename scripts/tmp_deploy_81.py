"""
修正版：部署到 81 服务器
- JAR 上传到 start.sh 指定的路径 /data/pinguan-backend-0.0.1-SNAPSHOT.jar
- 从 app.log 或环境变量获取生产 DB 连接串，补 group_type DDL
- 杀旧进程 -> 替换 JAR -> start.sh 启动 -> 验证
"""
import paramiko
import sys
import time
import re

HOST = "81.71.44.180"
PORT = 22
USER = "root"
PASS = "Yiguo9527_"

LOCAL_JAR   = r"target\pinguan-backend-0.0.1-SNAPSHOT.jar"
REMOTE_JAR  = "/data/pinguan-backend-0.0.1-SNAPSHOT.jar"
START_SH    = "/data/pinguan/start.sh"
LOG_FILE    = "/data/logs/app.log"
PID_FILE    = "/data/pinguan/run.pid"

DDL_SQL = (
    "ALTER TABLE final_ranking_snapshots "
    "ADD COLUMN IF NOT EXISTS group_type VARCHAR(32) NULL "
    "COMMENT 'BASIC/COMPREHENSIVE/ADVANCED';"
)

def ssh_run(client, cmd, timeout=60):
    print(f"  $ {cmd[:120]}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if out: print(f"    {out[:300]}")
    if err and "warning" not in err.lower(): print(f"    [ERR] {err[:200]}")
    return out, err

def get_db_info(client):
    """从 start.sh 或 app.log 找到 DB 连接信息"""
    # 读 start.sh 中的 PINGUAN_DS1_URL 或 spring.datasource
    out, _ = ssh_run(client, "cat /data/pinguan/start.sh; cat /data/pinguan/application-prod.yml 2>/dev/null")
    # 尝试从 app.log 提取 jdbc URL
    out2, _ = ssh_run(client,
        "grep -o 'jdbc:mysql://[^?]*' /data/logs/app.log 2>/dev/null | tail -1")
    if not out2:
        out2, _ = ssh_run(client,
            "grep -o 'jdbc:mysql://[^?]*' /data/pinguan/app.log 2>/dev/null | tail -1")
    # 解析 host:port/db
    m = re.search(r'jdbc:mysql://([^:/]+):(\d+)/(\w+)', out2 or "")
    if m:
        return m.group(1), int(m.group(2)), m.group(3)
    return None, None, None

def run_ddl_remote(client, db_host, db_port, db_name):
    """通过 mysql 客户端连接远程 DB 执行 DDL"""
    cmd = (
        f"mysql -h {db_host} -P {db_port} -u root -pYiguo9527_ {db_name} "
        f"-e \"{DDL_SQL}\" 2>&1 | grep -v -i warning"
    )
    ssh_run(client, cmd, timeout=30)

def main():
    print("=" * 60)
    print(f"  Deploy to {HOST} (paramiko)")
    print("=" * 60)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("\n[1/6] 连接服务器...")
        client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
        print("  连接成功")

        print("\n[2/6] 上传 JAR...")
        sftp = client.open_sftp()
        sftp.put(LOCAL_JAR, REMOTE_JAR + ".new")
        sftp.close()
        print(f"  上传完成 -> {REMOTE_JAR}.new")

        print("\n[3/6] 获取生产 DB 连接信息并补 DDL...")
        db_host, db_port, db_name = get_db_info(client)
        if db_host:
            print(f"  DB: {db_host}:{db_port}/{db_name}")
            run_ddl_remote(client, db_host, db_port, db_name)
        else:
            print("  [WARN] 未能解析 DB 连接信息，DDL 需手动执行：")
            print(f"    {DDL_SQL}")

        print("\n[4/6] 杀旧进程...")
        out, _ = ssh_run(client, f"cat {PID_FILE} 2>/dev/null")
        if out.strip().isdigit():
            ssh_run(client, f"kill -15 {out.strip()} 2>/dev/null; sleep 2")
        ssh_run(client, "pkill -f 'pinguan-backend' 2>/dev/null; sleep 2")
        ssh_run(client, "pgrep -f 'pinguan-backend' | wc -l")

        print("\n[5/6] 替换 JAR & 启动服务...")
        ssh_run(client, f"mv {REMOTE_JAR}.new {REMOTE_JAR}")
        ssh_run(client, f"bash {START_SH}")

        print("\n[6/6] 等待 20s 验证启动...")
        time.sleep(20)
        out, _ = ssh_run(client, f"tail -8 {LOG_FILE}")
        if "Started" in out or "Tomcat started" in out:
            print("\n  [OK] 服务启动成功！")
        else:
            print("\n  [WARN] 未检测到启动成功日志，继续等待 15s...")
            time.sleep(15)
            out, _ = ssh_run(client, f"tail -5 {LOG_FILE}")
            if "Started" in out or "Tomcat started" in out:
                print("  [OK] 服务启动成功！")
            else:
                print("  [WARN] 请手动确认:")
                ssh_run(client, f"pgrep -fa pinguan-backend | head -3")

        print("\n  部署完成！")

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
