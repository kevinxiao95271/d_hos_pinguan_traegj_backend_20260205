#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查云服务器服务状态
"""

import paramiko

SERVER_HOST = "81.71.44.180"
SERVER_USER = "root"
SERVER_PASSWORD = "Yiguo9527_"
SERVICE_PORT = 6031

print("="*80)
print("检查云服务器服务状态")
print("="*80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_HOST, 22, SERVER_USER, SERVER_PASSWORD)
print(f"✅ 已连接到 {SERVER_HOST}\n")

# 1. 检查进程
print("[1] 检查Java进程:")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'pinguan-backend' | grep -v grep")
output = stdout.read().decode('utf-8')
if output.strip():
    print("✅ 服务进程运行中:")
    for line in output.strip().split('\n'):
        parts = line.split()
        if len(parts) > 1:
            print(f"  PID: {parts[1]}")
            print(f"  启动时间: {parts[8]}")
            print(f"  命令: {' '.join(parts[10:])}")
else:
    print("❌ 没有找到服务进程")

# 2. 检查端口
print(f"\n[2] 检查端口{SERVICE_PORT}:")
stdin, stdout, stderr = ssh.exec_command(f"netstat -tlnp | grep {SERVICE_PORT} || ss -tlnp | grep {SERVICE_PORT}")
output = stdout.read().decode('utf-8')
if output.strip():
    print(f"✅ 端口{SERVICE_PORT}已监听:")
    print(f"  {output.strip()}")
else:
    print(f"❌ 端口{SERVICE_PORT}未监听")

# 3. 查看最新日志
print("\n[3] 最新日志（最后20行）:")
print("-"*80)
stdin, stdout, stderr = ssh.exec_command("tail -20 /data/app.log")
print(stdout.read().decode('utf-8'))
print("-"*80)

ssh.close()

print("\n" + "="*80)
print(f"访问地址: http://{SERVER_HOST}:{SERVICE_PORT}")
print(f"Swagger: http://{SERVER_HOST}:{SERVICE_PORT}/swagger-ui/index.html")
print("="*80)
