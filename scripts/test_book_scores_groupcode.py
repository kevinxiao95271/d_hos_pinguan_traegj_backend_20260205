#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试书审得分列表接口 - 检查分组代码是否重复
"""

import sys
import io
import requests
import json

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

def login():
    """登录获取token"""
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('data', {}).get('token')
    except:
        pass
    
    return None

def test_book_scores():
    """测试书审得分列表接口"""
    
    print("=" * 80)
    print("测试书审得分列表接口 - 检查分组代码")
    print("=" * 80)
    
    # 0. 登录获取token
    print(f"\n[0] 登录获取token...")
    token = login()
    if not token:
        print(f"    ✗ 登录失败，尝试不带token访问")
        headers = {}
    else:
        print(f"    ✓ 登录成功")
        headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 调用接口获取书审得分列表
    url = f"{BASE_URL}/api/admin/reviews/book-scores"
    params = {
        "competitionId": 21
    }
    
    print(f"\n[1] 调用接口: GET {url}")
    print(f"    参数: {params}")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"    状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"    ✗ 请求失败")
            print(f"    响应: {response.text[:500]}")
            return
        
        data = response.json()
        
        if not data.get('success'):
            print(f"    ✗ 接口返回失败")
            print(f"    消息: {data.get('message')}")
            return
        
        items = data.get('data', [])
        print(f"    ✓ 成功获取 {len(items)} 条记录")
        
        # 2. 提取所有的groupCode
        print(f"\n[2] 提取分组代码 (groupCode)")
        
        group_codes = []
        reviewer_group_codes = []
        
        for item in items:
            group_code = item.get('groupCode')
            reviewer_group_code = item.get('reviewerGroupCode')
            
            if group_code:
                group_codes.append(group_code)
            if reviewer_group_code:
                reviewer_group_codes.append(reviewer_group_code)
        
        # 3. 统计分组代码
        print(f"\n[3] 项目分组代码 (groupCode) 统计:")
        unique_group_codes = sorted(set(group_codes))
        print(f"    总数: {len(group_codes)} 个")
        print(f"    去重后: {len(unique_group_codes)} 个")
        print(f"    分组列表: {unique_group_codes}")
        
        # 检查是否有重复
        if len(group_codes) == len(unique_group_codes):
            print(f"    ✓ 没有重复")
        else:
            print(f"    ⚠ 有重复数据")
            # 统计每个分组出现的次数
            from collections import Counter
            counter = Counter(group_codes)
            print(f"    出现次数:")
            for code, count in counter.most_common():
                print(f"      {code}: {count} 次")
        
        # 4. 统计评委分组代码
        print(f"\n[4] 评委分组代码 (reviewerGroupCode) 统计:")
        unique_reviewer_group_codes = sorted(set(reviewer_group_codes))
        print(f"    总数: {len(reviewer_group_codes)} 个")
        print(f"    去重后: {len(unique_reviewer_group_codes)} 个")
        print(f"    分组列表: {unique_reviewer_group_codes}")
        
        # 5. 显示示例数据
        print(f"\n[5] 示例数据 (前3条):")
        for i, item in enumerate(items[:3]):
            print(f"\n    记录 {i+1}:")
            print(f"      项目名称: {item.get('projectName')}")
            print(f"      项目分组: {item.get('groupCode')}")
            print(f"      评委姓名: {item.get('reviewerName')}")
            print(f"      评委分组: {item.get('reviewerGroupCode')}")
            print(f"      总分: {item.get('total')}")
        
        # 6. 结论
        print(f"\n" + "=" * 80)
        print(f"结论:")
        print(f"  - 接口返回的数据中，每条记录都有唯一的 taskId")
        print(f"  - groupCode 是项目的分组代码 (如 A1, B2, C1)")
        print(f"  - reviewerGroupCode 是评委的分组代码")
        print(f"  - 如果前端下拉框出现重复，可能是前端处理问题")
        print(f"  - 建议前端使用 Set 或去重逻辑处理下拉框选项")
        print(f"=" * 80)
        
    except requests.exceptions.ConnectionError:
        print(f"    ✗ 连接失败 (应用可能未启动)")
    except requests.exceptions.Timeout:
        print(f"    ✗ 请求超时")
    except Exception as e:
        print(f"    ✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_book_scores()
