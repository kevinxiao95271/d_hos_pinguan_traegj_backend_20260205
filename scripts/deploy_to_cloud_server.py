#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署到云服务器
上传jar文件并重启服务
"""

import paramiko
import os
import time
from datetime import datetime

# 服务器配置
SERVER_HOST = "81.71.44.180"
SERVER_USER = "root"
SERVER_PASSWORD = "Yiguo9527_"
SERVER_PORT = 22

# 部署配置
REMOTE_DIR = "/data"
JAR_NAME = "pinguan-backend-0.0.1-SNAPSHOT.jar"
LOCAL_JAR = f"target/{JAR_NAME}"
REMOTE_JAR = f"{REMOTE_DIR}/{JAR_NAME}"
SERVICE_PORT = 6031

def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*80}")
    print(f"[{step}] {message}")
    print('='*80)

def execute_command(ssh, command, description):
    """执行SSH命令"""
    print(f"\n执行: {description}")
    print(f"命令: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_code = stdout.channel.recv_exit_status()
    
    if output:
        print(f"输出:\n{output}")
    if error:
        print(f"错误:\n{error}")
    
    return exit_code, output, error

def main():
    print_step("开始", f"部署到云服务器 {SERVER_HOST}")
    print(f"部署时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查本地jar文件
    print_step("1", "检查本地jar文件")
    if not os.path.exists(LOCAL_JAR):
        print(f"❌ 本地jar文件不存在: {LOCAL_JAR}")
        print("请先运行: mvn clean package -DskipTests")
        return
    
    jar_size = os.path.getsize(LOCAL_JAR) / (1024 * 1024)
    print(f"✅ 找到jar文件: {LOCAL_JAR}")
    print(f"   文件大小: {jar_size:.2f} MB")
    
    # 2. 连接服务器
    print_step("2", "连接到云服务器")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print(f"✅ 成功连接到 {SERVER_HOST}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    try:
        # 3. 检查远程目录
        print_step("3", "检查远程目录")
        exit_code, output, error = execute_command(
            ssh, 
            f"ls -lh {REMOTE_DIR}",
            "查看远程目录"
        )
        
        if exit_code != 0:
            print(f"❌ 远程目录不存在或无权限访问: {REMOTE_DIR}")
            return
        
        print(f"✅ 远程目录存在: {REMOTE_DIR}")
        
        # 4. 查找并停止旧进程
        print_step("4", "停止旧进程")
        exit_code, output, error = execute_command(
            ssh,
            f"ps aux | grep '{JAR_NAME}' | grep -v grep",
            "查找运行中的进程"
        )
        
        if output.strip():
            print("找到运行中的进程:")
            print(output)
            
            # 提取PID并杀掉进程
            lines = output.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    print(f"\n杀掉进程 PID: {pid}")
                    execute_command(ssh, f"kill -9 {pid}", f"杀掉进程 {pid}")
            
            # 等待进程完全停止
            print("\n等待3秒确保进程完全停止...")
            time.sleep(3)
            
            # 验证进程已停止
            exit_code, output, error = execute_command(
                ssh,
                f"ps aux | grep '{JAR_NAME}' | grep -v grep",
                "验证进程已停止"
            )
            
            if output.strip():
                print("⚠️  仍有进程在运行，尝试再次杀掉")
                execute_command(ssh, f"pkill -9 -f '{JAR_NAME}'", "强制杀掉所有相关进程")
                time.sleep(2)
            else:
                print("✅ 旧进程已停止")
        else:
            print("✅ 没有运行中的进程")
        
        # 5. 备份旧jar文件
        print_step("5", "备份旧jar文件")
        backup_name = f"{JAR_NAME}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        exit_code, output, error = execute_command(
            ssh,
            f"[ -f {REMOTE_JAR} ] && cp {REMOTE_JAR} {REMOTE_DIR}/{backup_name} || echo 'No old jar to backup'",
            "备份旧jar文件"
        )
        
        if "No old jar" in output:
            print("✅ 没有旧jar文件需要备份")
        else:
            print(f"✅ 已备份旧jar文件为: {backup_name}")
        
        # 6. 上传新jar文件
        print_step("6", "上传新jar文件")
        print(f"上传: {LOCAL_JAR} -> {REMOTE_JAR}")
        print("上传中，请稍候...")
        
        sftp = ssh.open_sftp()
        start_time = time.time()
        sftp.put(LOCAL_JAR, REMOTE_JAR)
        upload_time = time.time() - start_time
        sftp.close()
        
        print(f"✅ 上传完成，耗时: {upload_time:.2f}秒")
        
        # 验证上传
        exit_code, output, error = execute_command(
            ssh,
            f"ls -lh {REMOTE_JAR}",
            "验证上传的文件"
        )
        print(f"远程文件信息:\n{output}")
        
        # 7. 启动新服务
        print_step("7", "启动新服务")
        
        # 使用nohup在后台启动
        start_command = f"cd {REMOTE_DIR} && nohup java -jar {JAR_NAME} --server.port={SERVICE_PORT} > app.log 2>&1 &"
        
        print(f"启动命令: {start_command}")
        execute_command(ssh, start_command, "启动Spring Boot应用")
        
        print("\n等待10秒让服务启动...")
        time.sleep(10)
        
        # 8. 验证服务启动
        print_step("8", "验证服务启动")
        
        # 检查进程
        exit_code, output, error = execute_command(
            ssh,
            f"ps aux | grep '{JAR_NAME}' | grep -v grep",
            "检查进程是否运行"
        )
        
        if output.strip():
            print("✅ 服务进程已启动:")
            print(output)
            
            # 提取PID
            parts = output.strip().split()
            if len(parts) > 1:
                pid = parts[1]
                print(f"\n进程ID: {pid}")
        else:
            print("❌ 服务进程未找到")
            print("\n查看日志:")
            execute_command(ssh, f"tail -50 {REMOTE_DIR}/app.log", "查看启动日志")
            return
        
        # 检查端口
        exit_code, output, error = execute_command(
            ssh,
            f"netstat -tlnp | grep {SERVICE_PORT} || ss -tlnp | grep {SERVICE_PORT}",
            f"检查端口{SERVICE_PORT}是否监听"
        )
        
        if output.strip():
            print(f"✅ 端口{SERVICE_PORT}已监听:")
            print(output)
        else:
            print(f"⚠️  端口{SERVICE_PORT}尚未监听，可能还在启动中")
            print("请稍后手动检查")
        
        # 9. 查看启动日志
        print_step("9", "查看启动日志（最后30行）")
        execute_command(ssh, f"tail -30 {REMOTE_DIR}/app.log", "查看启动日志")
        
        # 10. 部署完成
        print_step("完成", "部署成功")
        print(f"""
部署信息:
  服务器: {SERVER_HOST}
  部署目录: {REMOTE_DIR}
  jar文件: {JAR_NAME}
  服务端口: {SERVICE_PORT}
  
访问地址:
  API: http://{SERVER_HOST}:{SERVICE_PORT}
  Swagger: http://{SERVER_HOST}:{SERVICE_PORT}/swagger-ui/index.html
  
后续操作:
  查看日志: ssh {SERVER_USER}@{SERVER_HOST} "tail -f {REMOTE_DIR}/app.log"
  停止服务: ssh {SERVER_USER}@{SERVER_HOST} "pkill -f '{JAR_NAME}'"
  重启服务: ssh {SERVER_USER}@{SERVER_HOST} "cd {REMOTE_DIR} && nohup java -jar {JAR_NAME} --server.port={SERVICE_PORT} > app.log 2>&1 &"
        """)
        
    except Exception as e:
        print(f"\n❌ 部署过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()
        print("\n已关闭SSH连接")

if __name__ == '__main__':
    main()
