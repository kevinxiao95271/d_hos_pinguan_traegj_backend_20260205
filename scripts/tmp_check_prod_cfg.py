import paramiko, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', port=22, username='root', password='Yiguo9527_', timeout=15)

def run(cmd):
    _, out, err = ssh.exec_command(cmd, timeout=15)
    return out.read().decode('utf-8', errors='replace').strip()

# 找prod配置文件
print("=== /data/pinguan 目录 ===")
print(run("ls -la /data/pinguan/"))

print("\n=== application-prod.yml ===")
print(run("cat /data/pinguan/application-prod.yml 2>/dev/null || echo NOT_FOUND"))

print("\n=== application.yml ===")
print(run("cat /data/pinguan/application.yml 2>/dev/null || echo NOT_FOUND"))

# jar内部config
print("\n=== jar内部application-prod ===")
print(run("unzip -p /data/pinguan/pinguan-backend.jar BOOT-INF/classes/application-prod.yml 2>/dev/null || echo NOT_FOUND"))
print(run("unzip -p /data/pinguan/pinguan-backend.jar BOOT-INF/classes/application.yml 2>/dev/null | grep -A3 'url\\|username'"))

ssh.close()
