# -*- coding: utf-8 -*-
"""
只修复机构等级字典，不影响其他字典数据
根据数据库实际情况：只保留 一级、二级、三级
"""
import requests

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("修复机构等级字典（只修复等级，不影响其他数据）")
print("=" * 100)

# 1. 登录
print("\n[步骤1] 登录管理员账号...")
login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200 or not login_response.json().get('success'):
    print("登录失败！")
    exit(1)

token = login_response.json()['data']['token']
print("登录成功！")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 获取当前机构等级字典
print("\n[步骤2] 获取当前机构等级字典...")
print("-" * 100)

response = requests.get(f"{BASE_URL}/dictionaries/institution_level", timeout=30)

if response.status_code != 200 or not response.json().get('success'):
    print("获取字典失败！")
    exit(1)

dict_items = response.json()['data']
print(f"当前字典中有 {len(dict_items)} 个机构等级:")

for item in dict_items:
    print(f"  - {item['code']:<15} (label: {item['label']:<15}, id: {item['id']})")

# 3. 根据数据库实际情况定义要保留的等级
print("\n[步骤3] 定义修复规则...")
print("-" * 100)

# 数据库中实际有数据的等级
keep_levels = ['一级', '二级', '三级']

print(f"要保留的等级: {keep_levels}")

# 找出需要删除的等级
current_codes = [item['code'] for item in dict_items]
to_delete = [item for item in dict_items if item['code'] not in keep_levels]

print(f"\n需要删除的等级 ({len(to_delete)} 个):")
for item in to_delete:
    print(f"  - {item['code']:<15} (label: {item['label']:<15}, id: {item['id']})")

# 找出需要添加的等级（如果字典里没有但应该保留的）
to_add = [level for level in keep_levels if level not in current_codes]

if to_add:
    print(f"\n需要添加的等级 ({len(to_add)} 个):")
    for level in to_add:
        print(f"  - {level}")
else:
    print(f"\n[OK] 所有需要保留的等级都已存在")

# 4. 确认修复
print("\n[步骤4] 修复确认")
print("=" * 100)

if not to_delete and not to_add:
    print("\n[完美] 字典表已经正确，无需修复！")
    exit(0)

print(f"\n修复操作:")
if to_delete:
    print(f"  [删除] {len(to_delete)} 个多余的等级")
if to_add:
    print(f"  [添加] {len(to_add)} 个缺失的等级")

print(f"\n注意：只修复 type='institution_level' 的字典，不影响其他字典数据")

# 5. 执行删除
if to_delete:
    print(f"\n[步骤5] 删除多余的等级...")
    print("-" * 100)
    
    deleted_count = 0
    failed_count = 0
    
    for item in to_delete:
        try:
            response = requests.delete(
                f"{BASE_URL}/dictionaries/{item['id']}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  [OK] 已删除: {item['code']:<15} (id: {item['id']})")
                    deleted_count += 1
                else:
                    print(f"  [FAIL] 删除失败: {item['code']} - {data.get('message')}")
                    failed_count += 1
            else:
                print(f"  [FAIL] 删除失败: {item['code']} - HTTP {response.status_code}")
                failed_count += 1
        except Exception as e:
            print(f"  [ERROR] 删除出错: {item['code']} - {e}")
            failed_count += 1
    
    print(f"\n删除结果: 成功 {deleted_count} 个, 失败 {failed_count} 个")

# 6. 执行添加
if to_add:
    print(f"\n[步骤6] 添加缺失的等级...")
    print("-" * 100)
    
    added_count = 0
    failed_count = 0
    
    for level in to_add:
        try:
            response = requests.post(
                f"{BASE_URL}/dictionaries",
                headers=headers,
                json={
                    "type": "institution_level",
                    "code": level,
                    "label": level,
                    "status": "ACTIVE"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"  [OK] 已添加: {level}")
                    added_count += 1
                else:
                    print(f"  [FAIL] 添加失败: {level} - {data.get('message')}")
                    failed_count += 1
            else:
                print(f"  [FAIL] 添加失败: {level} - HTTP {response.status_code}")
                failed_count += 1
        except Exception as e:
            print(f"  [ERROR] 添加出错: {level} - {e}")
            failed_count += 1
    
    print(f"\n添加结果: 成功 {added_count} 个, 失败 {failed_count} 个")

# 7. 验证结果
print(f"\n[步骤7] 验证修复结果...")
print("=" * 100)

response = requests.get(f"{BASE_URL}/dictionaries/institution_level", timeout=30)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        new_dict_items = data.get('data', [])
        new_codes = [item['code'] for item in new_dict_items]
        
        print(f"\n修复后的机构等级字典 ({len(new_dict_items)} 个):")
        for item in new_dict_items:
            print(f"  - {item['code']:<15} (label: {item['label']})")
        
        # 验证是否正确
        if set(new_codes) == set(keep_levels):
            print(f"\n[成功] 字典表已修复为: {keep_levels}")
            print(f"\n[确认] 只修改了机构等级字典，其他字典数据未受影响")
        else:
            missing = set(keep_levels) - set(new_codes)
            extra = set(new_codes) - set(keep_levels)
            
            if missing:
                print(f"\n[警告] 仍缺少: {missing}")
            if extra:
                print(f"\n[警告] 仍多余: {extra}")

# 8. 验证其他字典未受影响
print(f"\n[步骤8] 验证其他字典数据...")
print("-" * 100)

other_types = ['method', 'subject_type']
for dict_type in other_types:
    try:
        response = requests.get(f"{BASE_URL}/dictionaries/{dict_type}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                count = len(data.get('data', []))
                print(f"  [OK] {dict_type} 字典: {count} 个 (未受影响)")
    except:
        pass

print("\n" + "=" * 100)
print("修复完成！")
print("=" * 100)
