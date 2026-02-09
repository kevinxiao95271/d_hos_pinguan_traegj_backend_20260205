#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自动部署到服务器"""

import paramiko
import os
import time

SERVER = "81.71.44.180"
USER = "root"
PASSWORD = "Yiguo9527_"
REMOTE_DIR = "/data/pinguan"
JAR_FILE = "target/pinguan-backend-0.0.1-SNAPSHOT.jar"
APP_YML = "src/main/resources/application.yml"

def execute_command(ssh, command):
    """执行SSH命令"""
    print(f"执行: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if output:
        print(output)
    if error:
        print(f"错误: {error}")
    return output, error

def deploy():
    print("=" * 80)
    print("开始部署到服务器")
    print("=" * 80)
    
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 连接服务器
        print(f"\n[1/6] 连接服务器 {SERVER}...")
        ssh.connect(SERVER, username=USER, password=PASSWORD)
        print("✅ 连接成功")
        
        # 创建目录
        print(f"\n[2/6] 创建远程目录 {REMOTE_DIR}...")
        execute_command(ssh, f"mkdir -p {REMOTE_DIR}")
        print("✅ 目录创建成功")
        
        # 停止旧服务
        print("\n[3/6] 停止旧服务...")
        execute_command(ssh, "pkill -f pinguan-backend || true")
        time.sleep(2)
        print("✅ 旧服务已停止")
        
        # 上传jar包
        print(f"\n[4/6] 上传jar包...")
        sftp = ssh.open_sftp()
        sftp.put(JAR_FILE, f"{REMOTE_DIR}/pinguan-backend.jar")
        print(f"✅ jar包上传成功")
        
        # 上传配置文件
        print(f"\n[5/6] 上传配置文件...")
        sftp.put(APP_YML, f"{REMOTE_DIR}/application.yml")
        sftp.close()
        print("✅ 配置文件上传成功")
        
        # 启动服务
        print("\n[6/6] 启动服务...")
        execute_command(ssh, f"cd {REMOTE_DIR} && nohup java -jar pinguan-backend.jar > app.log 2>&1 &")
        time.sleep(5)
        print("✅ 服务启动命令已执行")
        
        # 检查服务状态
        print("\n检查服务状态...")
        output, _ = execute_command(ssh, "ps aux | grep pinguan-backend | grep -v grep")
        if output.strip():
            print("✅ 服务正在运行")
        else:
            print("⚠️  未检测到服务进程，请查看日志")
        
        print("\n" + "=" * 80)
        print("部署完成！")
        print("=" * 80)
        print(f"\n查看日志: ssh {USER}@{SERVER} 'tail -f {REMOTE_DIR}/app.log'")
        print(f"访问地址: http://{SERVER}:6031/swagger")
        
    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    if not os.path.exists(JAR_FILE):
        print(f"❌ jar包不存在: {JAR_FILE}")
        print("请先运行: mvn clean package -DskipTests")
    else:
        deploy()
