# -*- coding: utf-8 -*-
"""
等待应用启动完成
"""
import requests
import time

BASE_URL = "http://localhost:6031"

print("=" * 80)
print("等待应用启动...")
print("=" * 80)

max_attempts = 30  # 最多等待30次，每次2秒，共60秒
attempt = 0

while attempt < max_attempts:
    attempt += 1
    try:
        print(f"\n[尝试 {attempt}/{max_attempts}] 检查应用是否启动...")
        response = requests.get(f"{BASE_URL}/actuator/health", timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'UP':
                print(f"\n[OK] 应用启动成功！")
                print(f"  健康状态: {data.get('status')}")
                print(f"  耗时: {attempt * 2} 秒")
                exit(0)
            else:
                print(f"  健康状态: {data.get('status')} (还未完全启动)")
        else:
            print(f"  状态码: {response.status_code} (还未就绪)")
    except requests.exceptions.RequestException as e:
        print(f"  连接失败: {type(e).__name__} (应用还在启动中...)")
    
    if attempt < max_attempts:
        time.sleep(2)

print(f"\n[ERROR] 应用启动超时（{max_attempts * 2}秒）")
exit(1)
