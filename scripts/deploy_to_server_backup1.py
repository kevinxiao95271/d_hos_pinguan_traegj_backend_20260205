# -*- coding: utf-8 -*-
"""
自动部署脚本
"""
import paramiko
import os
import time
import sys

# 服务器配置
SERVER_HOST = "81.71.44.180"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASSWORD = "Yiguo9527_"
REMOTE_DIR = "/data"
JAR_NAME = "pinguan-backend-0.0.1-SNAPSHOT.jar"
LOCAL_JAR_PATH = r"d:\AiCode\cursor\d_hos_pinguan_traegj_backend_20260205\target\pinguan-backend-0.0.1-SNAPSHOT.jar"

def execute_command(ssh, command, description=""):
    """执行SSH命令"""
    if description:
        print(f"\n[{description}]")
    print(f"执行: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    exit_code = stdout.channel.recv_exit_status()
    
    if output:
        print(output)
    if error:
        print(f"错误: {error}")
    
    return exit_code, output, error

def main():
    print("=" * 100)
    print("开始部署到服务器 81.71.44.180")
    print("=" * 100)
    
    # 检查本地jar包
    if not os.path.exists(LOCAL_JAR_PATH):
        print(f"错误: 本地jar包不存在: {LOCAL_JAR_PATH}")
        return False
    
    jar_size = os.path.getsize(LOCAL_JAR_PATH) / (1024 * 1024)
    print(f"\n本地jar包: {LOCAL_JAR_PATH}")
    print(f"文件大小: {jar_size:.2f} MB")
    
    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 连接服务器
        print(f"\n连接服务器 {SERVER_HOST}...")
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD, timeout=30)
        print("连接成功！")
        
        # 1. 探测/data目录
        print("\n" + "=" * 100)
        print("步骤1: 探测服务器/data目录")
        print("=" * 100)
        
        execute_command(ssh, f"ls -lh {REMOTE_DIR}", "查看/data目录")
        execute_command(ssh, f"df -h {REMOTE_DIR}", "查看磁盘空间")
        execute_command(ssh, f"pwd", "当前目录")
        
        # 2. 检查是否有运行中的服务
        print("\n" + "=" * 100)
        print("步骤2: 检查运行中的Java服务")
        print("=" * 100)
        
        exit_code, output, _ = execute_command(ssh, "ps -ef | grep pinguan-backend | grep -v grep", "查找运行中的服务")
        
        if output.strip():
            print("发现运行中的服务，准备停止...")
            execute_command(ssh, "ps -ef | grep pinguan-backend | grep -v grep | awk '{print $2}' | xargs kill -9", "停止旧服务")
            time.sleep(2)
            execute_command(ssh, "ps -ef | grep pinguan-backend | grep -v grep", "确认服务已停止")
        else:
            print("没有运行中的服务")
        
        # 3. 备份旧的jar包
        print("\n" + "=" * 100)
        print("步骤3: 备份旧jar包")
        print("=" * 100)
        
        exit_code, output, _ = execute_command(ssh, f"ls {REMOTE_DIR}/{JAR_NAME}", "检查旧jar包")
        if exit_code == 0:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"{JAR_NAME}.backup_{timestamp}"
            execute_command(ssh, f"mv {REMOTE_DIR}/{JAR_NAME} {REMOTE_DIR}/{backup_name}", "备份旧jar包")
        else:
            print("没有找到旧jar包，无需备份")
        
        # 4. 上传新jar包
        print("\n" + "=" * 100)
        print("步骤4: 上传新jar包")
        print("=" * 100)
        
        sftp = ssh.open_sftp()
        remote_path = f"{REMOTE_DIR}/{JAR_NAME}"
        
        print(f"上传 {LOCAL_JAR_PATH}")
        print(f"到 {remote_path}")
        print("上传中，请稍候...")
        
        start_time = time.time()
        sftp.put(LOCAL_JAR_PATH, remote_path)
        upload_time = time.time() - start_time
        
        print(f"上传完成！耗时: {upload_time:.2f}秒")
        sftp.close()
        
        # 验证上传
        execute_command(ssh, f"ls -lh {REMOTE_DIR}/{JAR_NAME}", "验证上传的jar包")
        
        # 5. 检查或创建启动脚本
        print("\n" + "=" * 100)
        print("步骤5: 准备启动脚本")
        print("=" * 100)
        
        start_script = f"""#!/bin/bash
cd {REMOTE_DIR}
nohup java -jar -Xms512m -Xmx1024m {JAR_NAME} > app.log 2>&1 &
echo "服务已启动，PID: $!"
"""
        
        # 创建启动脚本
        execute_command(ssh, f"cat > {REMOTE_DIR}/start.sh << 'EOF'\n{start_script}\nEOF", "创建启动脚本")
        execute_command(ssh, f"chmod +x {REMOTE_DIR}/start.sh", "设置执行权限")
        
        # 6. 启动服务
        print("\n" + "=" * 100)
        print("步骤6: 启动服务")
        print("=" * 100)
        
        execute_command(ssh, f"cd {REMOTE_DIR} && ./start.sh", "启动服务")
        
        # 等待服务启动
        print("\n等待服务启动...")
        time.sleep(5)
        
        # 7. 检查服务状态
        print("\n" + "=" * 100)
        print("步骤7: 检查服务状态")
        print("=" * 100)
        
        execute_command(ssh, "ps -ef | grep pinguan-backend | grep -v grep", "查看Java进程")
        
        # 查看最近的日志
        print("\n查看启动日志（最后50行）:")
        execute_command(ssh, f"tail -n 50 {REMOTE_DIR}/app.log", "查看应用日志")
        
        # 8. 测试服务端口
        print("\n" + "=" * 100)
        print("步骤8: 测试服务端口")
        print("=" * 100)
        
        time.sleep(10)  # 再等待10秒让服务完全启动
        
        execute_command(ssh, "netstat -tlnp | grep 6031", "检查6031端口")
        
        # 9. 健康检查
        print("\n" + "=" * 100)
        print("步骤9: 健康检查")
        print("=" * 100)
        
        exit_code, output, _ = execute_command(ssh, "curl -s http://localhost:6031/actuator/health || echo 'Health check endpoint not available'", "健康检查")
        
        print("\n" + "=" * 100)
        print("部署完成！")
        print("=" * 100)
        print(f"\n服务地址: http://{SERVER_HOST}:6031")
        print(f"查看日志: ssh root@{SERVER_HOST} 'tail -f {REMOTE_DIR}/app.log'")
        
        return True
        
    except Exception as e:
        print(f"\n部署失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        ssh.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
