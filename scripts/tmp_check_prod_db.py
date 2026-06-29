import paramiko, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', port=22, username='root', password='Yiguo9527_', timeout=15)

def run(cmd):
    _, out, err = ssh.exec_command(cmd, timeout=15)
    return out.read().decode('utf-8', errors='replace').strip()

# 查进程启动参数（DB连接）
print("=== 进程参数 ===")
print(run("cat /proc/$(pgrep -f pinguan-backend)/cmdline 2>/dev/null | tr '\\0' '\\n' | grep -E 'spring|DS|db|mysql|active'"))

# 查环境变量
print("\n=== DB相关环境变量 ===")
print(run("cat /proc/$(pgrep -f pinguan-backend)/environ 2>/dev/null | tr '\\0' '\\n' | grep -iE 'pinguan|DS|mysql|spring'"))

# 查启动脚本
print("\n=== 启动脚本 ===")
print(run("cat /data/pinguan/_start_pinguan.sh"))

# 查日志里的连接URL
print("\n=== 日志中的DB连接 ===")
print(run("grep -i 'jdbc\\|datasource\\|url' /data/pinguan/app.log 2>/dev/null | head -5"))

ssh.close()
