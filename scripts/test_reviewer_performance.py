#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试评委列表接口性能"""

import sys, io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import time

BASE = "http://localhost:6031"

# 登录
r = requests.post(f"{BASE}/api/auth/login", json={
    "phone":"13800000009","name":"C","title":"C","role":"COMMITTEE"
})
token = r.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

print("="*60)
print("评委列表接口性能测试")
print("="*60)

# 测试多次获取评委列表
times = []
for i in range(5):
    start = time.time()
    response = requests.get(f"{BASE}/api/admin/reviewers", headers=headers)
    end = time.time()
    elapsed = (end - start) * 1000  # 转换为毫秒
    times.append(elapsed)
    
    if i == 0:
        data = response.json()
        count = len(data.get('data', []))
        print(f"\n返回数据量: {count} 个评委")
    
    print(f"第{i+1}次请求耗时: {elapsed:.0f}ms")

print(f"\n平均耗时: {sum(times)/len(times):.0f}ms")
print(f"最快: {min(times):.0f}ms")
print(f"最慢: {max(times):.0f}ms")

if sum(times)/len(times) > 1000:
    print("\n[警告] 平均耗时超过1秒，存在性能问题！")
elif sum(times)/len(times) > 500:
    print("\n[警告] 平均耗时超过500ms，建议优化")
else:
    print("\n[正常] 性能良好")

print("\n分析可能的性能瓶颈:")
print("1. N+1查询问题（每个评委单独查询机构）")
print("2. 懒加载触发多次数据库访问")
print("3. 没有使用JOIN FETCH预加载关联数据")
print("4. 缺少数据库索引")
print("="*60)
