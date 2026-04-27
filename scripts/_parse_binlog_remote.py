"""
在生产服务器上执行 mysqlbinlog，找李雅岑(reviewer_id=703)相关被删除的 review_scores
"""
import paramiko, sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"
DB   = "d_hos_pinguan_traegj_20260205"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=60):
    _, out, err = ssh.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o, e

# 1. 找 mysqlbinlog 路径
print("=== 查找 mysqlbinlog ===")
o, _ = run("find /usr /usr/bin /usr/local /opt -name 'mysqlbinlog' 2>/dev/null | head -5")
print(o or "未找到")

# 2. 从数据库查李雅岑的 task_id
print("\n=== 李雅岑(703) 书审任务 ===")
sql = """
SELECT rt.id, rt.status, rt.updated_at, LEFT(reg.project_name,30)
FROM review_tasks rt
JOIN registrations reg ON reg.id = rt.registration_id
WHERE rt.reviewer_id = 703 AND rt.stage = 'BOOK'
ORDER BY rt.id;
"""
o, e = run(f"mysql -u root -pYiguo9527_ {DB} -e \"{sql}\" 2>/dev/null")
print(o)

# 3. 找 binlog 文件位置
print("\n=== binlog 文件 ===")
o, _ = run("mysql -u root -pYiguo9527_ -e 'SHOW BINARY LOGS;' 2>/dev/null")
print(o)
o2, _ = run("mysql -u root -pYiguo9527_ -e 'SHOW VARIABLES LIKE \"log_bin_basename\";' 2>/dev/null")
print(o2)

# 4. 找 mysqlbinlog 并解析
print("\n=== 解析 binlog 查 review_scores DELETE ===")
o_path, _ = run("find / -name 'mysqlbinlog' 2>/dev/null | grep -v proc | head -3")
mysqlbinlog = o_path.split('\n')[0].strip() if o_path else ""

if not mysqlbinlog:
    # 尝试 docker
    o_dock, _ = run("docker ps --format '{{.Names}}' 2>/dev/null | head -5")
    print(f"Docker 容器: {o_dock}")
    # 尝试从 mysql 同目录找
    o_mysql, _ = run("which mysql 2>/dev/null")
    mysql_dir = '/'.join(o_mysql.strip().split('/')[:-1]) if o_mysql else '/usr/bin'
    mysqlbinlog = f"{mysql_dir}/mysqlbinlog"
    print(f"尝试路径: {mysqlbinlog}")

# 获取 binlog 实际路径
o_base, _ = run("mysql -u root -pYiguo9527_ -e 'SHOW VARIABLES LIKE \"datadir\";' 2>/dev/null")
datadir = '/var/lib/mysql'
for line in o_base.split('\n'):
    if 'datadir' in line:
        parts = line.split()
        if len(parts) >= 2:
            datadir = parts[-1].rstrip('/')

print(f"\nbinlog datadir: {datadir}")

# 执行 mysqlbinlog
cmd = (
    f"{mysqlbinlog} --base64-output=DECODE-ROWS -v "
    f"{datadir}/binlog.000003 {datadir}/binlog.000004 2>/dev/null "
    f"| grep -B2 -A25 'DELETE FROM.*review_scores'"
)
print(f"\n执行: {cmd[:100]}...")
o, e = run(cmd, timeout=120)
if o:
    print(o)
else:
    print(f"无输出. stderr: {e[:200]}")

ssh.close()
print("\n完成")
