#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看服务器日志"""

import paramiko
from db_config import SERVER_CONFIG["host"]_CONFIG

# SERVER_CONFIG["host"]_CONFIG imported from db_config.py

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(SERVER_CONFIG["host"], username=SERVER_CONFIG["user"], password=SERVER_CONFIG["password"], timeout=10)
    
    print("=" * 80)
    print("服务器日志（最后50行）")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command("tail -50 /data/pinguan/app.log")
    print(stdout.read().decode('utf-8', errors='ignore'))
    
    ssh.close()
except Exception as e:
    print(f"错误: {e}")
