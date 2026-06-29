import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('81.71.44.180', port=22, username='root', password='Yiguo9527_', timeout=10)

def run(cmd):
    _, out, err = ssh.exec_command(cmd)
    return out.read().decode('utf-8', errors='replace')

# 查最近 ERROR 日志
print("=== 最近 ERROR ===")
print(run("grep 'ERROR' /opt/pinguan/app.log | tail -20"))

print("=== ranking 相关请求 ===")
print(run("grep -i 'ranking' /opt/pinguan/app.log | tail -20"))

ssh.close()
