#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重启云服务器上的服务
"""

import paramiko
import time

SERVER_HOST = "81.71.44.180"
SERVER_USER = "root"
SERVER_PASSWORD = "Yiguo9527_"
REMOTE_DIR = "/data"
JAR_NAME = "pinguan-backend-0.0.1-SNAPSHOT.jar"
SERVICE_PORT = 6031

def execute_command(ssh, command):
    """执行命令并返回输出"""
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')

print("="*80)
print("重启云服务器服务")
print("="*80)

# 连接服务器
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_HOST, 22, SERVER_USER, SERVER_PASSWORD)
print(f"✅ 已连接到 {SERVER_HOST}")

# 1. 查找占用端口的进程
print(f"\n[1] 查找占用端口{SERVICE_PORT}的进程...")
output, error = execute_command(ssh, f"lsof -i:{SERVICE_PORT} -t || fuser {SERVICE_PORT}/tcp 2>/dev/null || netstat -tlnp | grep {SERVICE_PORT} | awk '{{print $7}}' | cut -d'/' -f1")
pids = [pid.strip() for pid in output.strip().split('\n') if pid.strip() and pid.strip().isdigit()]

if pids:
    print(f"找到进程: {', '.join(pids)}")
    for pid in pids:
        print(f"  杀掉进程 {pid}...")
        execute_command(ssh, f"kill -9 {pid}")
    print("✅ 已杀掉旧进程")
    time.sleep(2)
else:
    print("没有找到占用端口的进程")

# 2. 再次确认没有java进程
print("\n[2] 确认没有相关java进程...")
output, error = execute_command(ssh, f"ps aux | grep '{JAR_NAME}' | grep -v grep")
if output.strip():
    print("仍有进程在运行，强制杀掉:")
    print(output)
    execute_command(ssh, f"pkill -9 -f '{JAR_NAME}'")
    time.sleep(2)
    print("✅ 已强制杀掉")
else:
    print("✅ 没有相关进程")

# 3. 确认端口已释放
print(f"\n[3] 确认端口{SERVICE_PORT}已释放...")
output, error = execute_command(ssh, f"netstat -tlnp | grep {SERVICE_PORT} || ss -tlnp | grep {SERVICE_PORT}")
if output.strip():
    print(f"⚠️  端口{SERVICE_PORT}仍被占用:")
    print(output)
else:
    print(f"✅ 端口{SERVICE_PORT}已释放")

# 4. 启动新服务
print("\n[4] 启动新服务...")
start_cmd = f"cd {REMOTE_DIR} && nohup java -jar {JAR_NAME} --server.port={SERVICE_PORT} > app.log 2>&1 &"
print(f"命令: {start_cmd}")
execute_command(ssh, start_cmd)
print("✅ 启动命令已执行")

# 5. 等待启动
print("\n[5] 等待服务启动（15秒）...")
for i in range(15, 0, -1):
    print(f"  {i}秒...", end='\r')
    time.sleep(1)
print("\n")

# 6. 检查进程
print("[6] 检查进程状态...")
output, error = execute_command(ssh, f"ps aux | grep '{JAR_NAME}' | grep -v grep")
if output.strip():
    print("✅ 服务进程已启动:")
    print(output)
    lines = output.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) > 1:
            print(f"\n进程ID: {parts[1]}")
else:
    print("❌ 服务进程未找到")

# 7. 检查端口
print(f"\n[7] 检查端口{SERVICE_PORT}...")
output, error = execute_command(ssh, f"netstat -tlnp | grep {SERVICE_PORT} || ss -tlnp | grep {SERVICE_PORT}")
if output.strip():
    print(f"✅ 端口{SERVICE_PORT}已监听:")
    print(output)
else:
    print(f"⚠️  端口{SERVICE_PORT}尚未监听，可能还在启动中")

# 8. 查看日志
print("\n[8] 查看启动日志（最后30行）...")
print("-"*80)
output, error = execute_command(ssh, f"tail -30 {REMOTE_DIR}/app.log")
print(output)
print("-"*80)

ssh.close()

print("\n" + "="*80)
print("重启完成")
print("="*80)
print(f"""
访问地址:
  API: http://{SERVER_HOST}:{SERVICE_PORT}
  Swagger: http://{SERVER_HOST}:{SERVICE_PORT}/swagger-ui/index.html
  
查看日志:
  ssh {SERVER_USER}@{SERVER_HOST} "tail -f {REMOTE_DIR}/app.log"
""")
