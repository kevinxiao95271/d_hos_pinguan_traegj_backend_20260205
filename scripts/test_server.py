#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

ports = [8080, 6031]

for port in ports:
    try:
        resp = requests.get(f"http://localhost:{port}/actuator/health", timeout=2)
        print(f"✅ 端口 {port} 上有服务运行: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   服务状态: {resp.json()}")
            print(f"\n✅ 可以使用端口 {port} 进行API测试！")
            sys.exit(0)
    except Exception as e:
        print(f"❌ 端口 {port} 无服务或无法访问")

print("\n❌ 没有可用的服务")
sys.exit(1)
