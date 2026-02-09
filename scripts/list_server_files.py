#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看服务器文件"""

import paramiko

SERVER = "81.71.44.180"
USER = "root"
PASSWORD = "Yiguo9527_"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
    
    print("=" * 80)
    print("服务器文件列表: /data/pinguan")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command("ls -lh /data/pinguan/")
    print(stdout.read().decode('utf-8'))
    
    print("\n" + "=" * 80)
    print("磁盘使用情况")
    print("=" * 80)
    stdin, stdout, stderr = ssh.exec_command("du -sh /data/pinguan/*")
    print(stdout.read().decode('utf-8'))
    
    ssh.close()
except Exception as e:
    print(f"错误: {e}")
