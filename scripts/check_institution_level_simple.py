# -*- coding: utf-8 -*-
"""
检查医院等级API和字典数据
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("医院等级数据检查")
print("=" * 100)

# 1. 测试字典API - 医院等级
print("\n[API 1] GET /api/dictionaries/institution_level (字典表)")
print("-" * 100)

try:
    response = requests.get(
        f"{BASE_URL}/dictionaries/institution_level",
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            items = data.get('data', [])
            print(f"返回 {len(items)} 个医院等级选项:\n")
            
            dict_codes = []
            for item in items:
                code = item.get('code', '')
                label = item.get('label', '')
                status = item.get('status', '')
                dict_codes.append(code)
                print(f"  code: {code:<20} label: {label:<15} status: {status}")
        else:
            print(f"API返回失败: {data.get('message')}")
    else:
        print(f"API请求失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"API请求出错: {e}")

# 2. 测试机构API - 实际使用的等级
print(f"\n[API 2] GET /api/institutions/levels (机构表实际值)")
print("-" * 100)

try:
    response = requests.get(
        f"{BASE_URL}/institutions/levels",
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            levels = data.get('data', [])
            print(f"返回 {len(levels)} 个实际使用的等级:\n")
            
            for level in levels:
                print(f"  {level}")
                
            # 对比分析
            print(f"\n[对比分析]")
            print("-" * 100)
            
            if 'dict_codes' in locals():
                # 检查实际值是否在字典中
                missing = [level for level in levels if level not in dict_codes]
                if missing:
                    print(f"\n[问题] 机构表中有 {len(missing)} 个等级值不在字典表中:")
                    for level in missing:
                        print(f"  [X] {level}")
                else:
                    print(f"\n[OK] 所有机构等级值都在字典表中")
                
                # 检查字典中未使用的值
                unused = [code for code in dict_codes if code not in levels]
                if unused:
                    print(f"\n[提示] 字典表中有 {len(unused)} 个等级值未被机构使用:")
                    for code in unused:
                        print(f"  [WARN] {code}")
        else:
            print(f"API返回失败: {data.get('message')}")
    else:
        print(f"API请求失败: HTTP {response.status_code}")
        
except Exception as e:
    print(f"API请求出错: {e}")

# 3. 测试筛选功能
print(f"\n[测试] 筛选功能测试")
print("-" * 100)

print("\n登录组委会账号...")
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code == 200 and login_response.json().get('success'):
    token = login_response.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试筛选 - 使用字典code
    print(f"\n测试筛选 competitionId=1, 不带等级筛选:")
    filter_response = requests.get(
        f"{BASE_URL}/admin/registrations/filter",
        headers=headers,
        params={"competitionId": 1},
        timeout=30
    )
    
    if filter_response.status_code == 200:
        data = filter_response.json()
        if data.get('success'):
            total = len(data.get('data', []))
            print(f"  返回 {total} 条记录")
            
            # 统计各等级数量
            if total > 0:
                levels_count = {}
                for item in data['data']:
                    level = item.get('institutionLevel', '[空]')
                    levels_count[level] = levels_count.get(level, 0) + 1
                
                print(f"\n  等级分布:")
                for level, count in sorted(levels_count.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {level}: {count} 条")

print("\n" + "=" * 100)
