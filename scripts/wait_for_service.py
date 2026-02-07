#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

ports = [8080, 6031]
max_wait = 90
start = time.time()

print("等待服务启动...")

while time.time() - start < max_wait:
    for port in ports:
        try:
            resp = requests.get(f"http://localhost:{port}/actuator/health", timeout=2)
            if resp.status_code == 200:
                elapsed = int(time.time() - start)
                print(f"\n✅ 服务已在端口 {port} 启动 (耗时 {elapsed}秒)")
                sys.exit(0)
        except:
            pass
    
    print(".", end="", flush=True)
    time.sleep(3)

print(f"\n❌ 服务启动超时 ({max_wait}秒)")
sys.exit(1)
