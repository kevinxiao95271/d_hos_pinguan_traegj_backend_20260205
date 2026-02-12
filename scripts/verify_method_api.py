#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证品管工具API是否还有重复
"""

import sys
import io
import requests

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def verify_api():
    """验证API"""
    
    print("=" * 80)
    print("验证品管工具API")
    print("=" * 80)
    
    url = f"{BASE_URL}/api/dictionaries/method"
    
    print(f"\n[1] 调用API: GET {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"    状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"    ✗ 请求失败")
            return
        
        result = response.json()
        
        if not result.get('success'):
            print(f"    ✗ 接口返回失败")
            return
        
        methods = result.get('data', [])
        print(f"    ✓ 成功获取 {len(methods)} 个品管工具")
        
        # 检查重复
        print(f"\n[2] 检查label重复")
        labels = [m.get('label') for m in methods]
        unique_labels = set(labels)
        
        if len(labels) == len(unique_labels):
            print(f"    ✓ 没有重复的label")
        else:
            print(f"    ✗ 有重复的label")
            from collections import Counter
            counter = Counter(labels)
            for label, count in counter.most_common():
                if count > 1:
                    print(f"      '{label}' 出现 {count} 次")
        
        # 显示所有品管工具
        print(f"\n[3] 品管工具列表:")
        for m in methods:
            print(f"      {m.get('code'):20s} | {m.get('label')}")
        
        print("\n" + "=" * 80)
        print("验证完成!")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print(f"    ✗ 连接失败 (应用可能未启动)")
    except Exception as e:
        print(f"    ✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_api()
