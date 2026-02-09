#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查服务器状态"""

import paramiko
import requests

SERVER = "81.71.44.180"
USER = "root"
PASSWORD = "Yiguo9527_"

def check_status():
    print("=" * 80)
    print("检查服务器状态")
    print("=" * 80)
    
    # 检查进程
    print("\n[1/3] 检查进程...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep pinguan-backend | grep -v grep")
        output = stdout.read().decode('utf-8')
        
        if output.strip():
            print("✅ 服务进程正在运行")
            print(output)
        else:
            print("❌ 未检测到服务进程")
            
            # 查看日志
            print("\n查看最后20行日志:")
            stdin, stdout, stderr = ssh.exec_command("tail -20 /data/pinguan/app.log")
            print(stdout.read().decode('utf-8'))
        
        ssh.close()
    except Exception as e:
        print(f"❌ SSH连接失败: {e}")
    
    # 检查端口
    print("\n[2/3] 检查端口6031...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
        
        stdin, stdout, stderr = ssh.exec_command("netstat -tuln | grep 6031")
        output = stdout.read().decode('utf-8')
        
        if output.strip():
            print("✅ 端口6031正在监听")
            print(output)
        else:
            print("❌ 端口6031未监听")
        
        ssh.close()
    except Exception as e:
        print(f"❌ 检查端口失败: {e}")
    
    # 检查HTTP接口
    print("\n[3/3] 检查HTTP接口...")
    try:
        response = requests.get(f"http://{SERVER}:6031/actuator/health", timeout=5)
        if response.status_code == 200:
            print("✅ HTTP接口正常")
            print(response.json())
        else:
            print(f"❌ HTTP接口异常: {response.status_code}")
    except Exception as e:
        print(f"❌ HTTP接口无法访问: {e}")
    
    print("\n" + "=" * 80)
    print(f"Swagger地址: http://{SERVER}:6031/swagger")
    print("=" * 80)

if __name__ == '__main__':
    check_status()
