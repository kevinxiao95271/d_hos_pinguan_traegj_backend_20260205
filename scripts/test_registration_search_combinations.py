# -*- coding: utf-8 -*-
"""
注册环节 - 机构搜索组合测试
测试路径：选城市 -> 选等级 -> 输入关键词的各种组合
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

# 测试结果记录
test_results = []
issues_found = []

def test_api(name, method, url, **kwargs):
    """统一的API测试方法"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=30, **kwargs)
        elif method == "POST":
            response = requests.post(url, timeout=30, **kwargs)
        else:
            return None, f"不支持的方法: {method}"
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('data'), None
            else:
                return None, data.get('message', '未知错误')
        else:
            return None, f"HTTP {response.status_code}"
    except Exception as e:
        return None, str(e)

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)

def print_test(test_name, result, message=""):
    """打印测试结果"""
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} {test_name}")
    if message:
        print(f"      {message}")
    test_results.append({
        "test": test_name,
        "pass": result,
        "message": message
    })
    if not result:
        issues_found.append(f"{test_name}: {message}")

def print_data_sample(data, label, max_items=5):
    """打印数据样本"""
    if isinstance(data, list):
        print(f"  {label}: {len(data)} 项")
        for i, item in enumerate(data[:max_items]):
            if isinstance(item, dict):
                print(f"    [{i+1}] {item}")
            else:
                print(f"    [{i+1}] {item}")
        if len(data) > max_items:
            print(f"    ... 还有 {len(data) - max_items} 项")
    else:
        print(f"  {label}: {data}")

print_section("注册环节 - 机构搜索组合测试")
print("测试目标: 验证 选城市 -> 选等级 -> 输入关键词 的各种组合")
print("测试原则: 只测试，不修改，发现问题记录下来")

# ========================================
# 第一部分：基础数据接口测试
# ========================================
print_section("第一部分：基础数据接口测试（下拉框数据源）")

# 1.1 测试城市列表
print("\n[测试 1.1] 获取城市列表")
cities, error = test_api("获取城市列表", "GET", f"{BASE_URL}/institutions/cities")
if cities:
    print_test("获取城市列表", True, f"返回 {len(cities)} 个城市")
    print_data_sample(cities, "城市列表", 11)
else:
    print_test("获取城市列表", False, error)

# 1.2 测试等级列表
print("\n[测试 1.2] 获取医院等级列表")
levels, error = test_api("获取等级列表", "GET", f"{BASE_URL}/institutions/levels")
if levels:
    print_test("获取等级列表", True, f"返回 {len(levels)} 个等级")
    print_data_sample(levels, "等级列表")
else:
    print_test("获取等级列表", False, error)

# 1.3 测试字典等级列表（对比用）
print("\n[测试 1.3] 获取字典中的等级列表（对比）")
dict_levels, error = test_api("获取字典等级", "GET", f"{BASE_URL}/dictionaries/institution_level")
if dict_levels:
    dict_codes = [item.get('code') for item in dict_levels]
    print_test("获取字典等级", True, f"返回 {len(dict_levels)} 个等级")
    print_data_sample(dict_codes, "字典等级代码")
    
    # 对比两个接口的等级数据
    if levels and dict_codes:
        print("\n  [对比分析] 两个接口的等级数据:")
        levels_set = set(levels)
        dict_set = set(dict_codes)
        
        missing_in_dict = levels_set - dict_set
        if missing_in_dict:
            print(f"    [问题] 机构表有但字典表没有的等级: {missing_in_dict}")
            issues_found.append(f"等级数据不一致: 机构表有 {missing_in_dict}，但字典表没有")
        
        extra_in_dict = dict_set - levels_set
        if extra_in_dict:
            print(f"    [提示] 字典表有但机构表未使用的等级: {extra_in_dict}")
        
        if not missing_in_dict:
            print(f"    [OK] 所有实际使用的等级都在字典表中")
else:
    print_test("获取字典等级", False, error)

# 1.4 测试区县列表（选中城市后）
if cities and len(cities) > 0:
    test_city = cities[0]  # 测试第一个城市
    print(f"\n[测试 1.4] 获取 '{test_city}' 的区县列表")
    districts, error = test_api(
        f"获取{test_city}区县",
        "GET",
        f"{BASE_URL}/institutions/districts",
        params={"city": test_city}
    )
    if districts:
        print_test(f"获取{test_city}区县", True, f"返回 {len(districts)} 个区县")
        print_data_sample(districts, f"{test_city}的区县")
    else:
        print_test(f"获取{test_city}区县", False, error)

# ========================================
# 第二部分：机构搜索组合测试
# ========================================
print_section("第二部分：机构搜索组合测试（核心功能）")

# 测试用的城市和等级
test_cities = cities[:3] if cities and len(cities) >= 3 else cities
test_levels = levels[:3] if levels and len(levels) >= 3 else levels

# 2.1 无条件搜索（默认分页）
print("\n[测试 2.1] 无条件搜索（默认第一页）")
data, error = test_api(
    "无条件搜索",
    "POST",
    f"{BASE_URL}/institutions/search",
    json={
        "keyword": "",
        "region": "",
        "level": "",
        "page": 0,
        "size": 10
    }
)
if data:
    total = data.get('totalElements', 0)
    content = data.get('content', [])
    print_test("无条件搜索", True, f"总共 {total} 个机构，当前页 {len(content)} 条")
    if len(content) > 0:
        print(f"  样本数据:")
        sample = content[0]
        print(f"    name: {sample.get('name')}")
        print(f"    region: {sample.get('region')}")
        print(f"    level: {sample.get('level')}")
    
    if total == 0:
        issues_found.append("无条件搜索返回0条结果，数据库可能为空")
else:
    print_test("无条件搜索", False, error)

# 2.2 只选城市
if test_cities:
    for city in test_cities:
        print(f"\n[测试 2.2.{test_cities.index(city)+1}] 只选城市: {city}")
        
        # 方式1: 使用城市名作为region
        data, error = test_api(
            f"城市搜索-{city}",
            "POST",
            f"{BASE_URL}/institutions/search",
            json={
                "keyword": "",
                "region": city,
                "level": "",
                "page": 0,
                "size": 10
            }
        )
        if data:
            total = data.get('totalElements', 0)
            content = data.get('content', [])
            print_test(f"城市搜索-{city}", total > 0, f"找到 {total} 个机构")
            
            if total == 0:
                issues_found.append(f"城市'{city}'搜索返回0条结果，可能需要使用区县级地区")
            
            # 检查返回结果的region字段
            if len(content) > 0:
                regions_in_result = set([item.get('region') for item in content if item.get('region')])
                print(f"  返回结果中的地区: {regions_in_result}")
                
                # 检查是否包含该城市的区县
                if city not in str(regions_in_result):
                    print(f"  [警告] 搜索'{city}'但结果中的region字段不包含'{city}'")
        else:
            print_test(f"城市搜索-{city}", False, error)

# 2.3 只选等级
if test_levels:
    for level in test_levels:
        print(f"\n[测试 2.3.{test_levels.index(level)+1}] 只选等级: {level}")
        data, error = test_api(
            f"等级搜索-{level}",
            "POST",
            f"{BASE_URL}/institutions/search",
            json={
                "keyword": "",
                "region": "",
                "level": level,
                "page": 0,
                "size": 10
            }
        )
        if data:
            total = data.get('totalElements', 0)
            content = data.get('content', [])
            print_test(f"等级搜索-{level}", total > 0, f"找到 {total} 个机构")
            
            if total == 0:
                issues_found.append(f"等级'{level}'搜索返回0条结果")
            
            # 检查返回结果的level字段
            if len(content) > 0:
                sample_level = content[0].get('level')
                print(f"  返回结果样本的等级: {sample_level}")
                if sample_level != level:
                    print(f"  [警告] 搜索'{level}'但返回的level是'{sample_level}'")
        else:
            print_test(f"等级搜索-{level}", False, error)

# 2.4 城市 + 等级组合
print("\n[测试 2.4] 城市 + 等级 组合")
if test_cities and test_levels:
    city = test_cities[0]
    level = test_levels[0]
    print(f"  组合: 城市='{city}' + 等级='{level}'")
    
    data, error = test_api(
        f"组合搜索-{city}+{level}",
        "POST",
        f"{BASE_URL}/institutions/search",
        json={
            "keyword": "",
            "region": city,
            "level": level,
            "page": 0,
            "size": 10
        }
    )
    if data:
        total = data.get('totalElements', 0)
        content = data.get('content', [])
        print_test(f"组合搜索-{city}+{level}", True, f"找到 {total} 个机构")
        
        if total == 0:
            print(f"  [警告] 城市'{city}' + 等级'{level}' 组合搜索返回0条结果")
            issues_found.append(f"城市'{city}' + 等级'{level}' 组合返回0条结果，可能筛选条件过严")
        
        if len(content) > 0:
            sample = content[0]
            print(f"  样本: {sample.get('name')} - {sample.get('region')} - {sample.get('level')}")
    else:
        print_test(f"组合搜索-{city}+{level}", False, error)

# 2.5 关键词搜索
print("\n[测试 2.5] 关键词搜索")
test_keywords = ["医院", "人民", "中医"]
for keyword in test_keywords:
    print(f"\n  关键词: '{keyword}'")
    data, error = test_api(
        f"关键词搜索-{keyword}",
        "POST",
        f"{BASE_URL}/institutions/search",
        json={
            "keyword": keyword,
            "region": "",
            "level": "",
            "page": 0,
            "size": 10
        }
    )
    if data:
        total = data.get('totalElements', 0)
        content = data.get('content', [])
        print_test(f"关键词搜索-{keyword}", total > 0, f"找到 {total} 个机构")
        
        if total == 0:
            issues_found.append(f"关键词'{keyword}'搜索返回0条结果")
        
        if len(content) > 0:
            print(f"    样本: {content[0].get('name')}")
    else:
        print_test(f"关键词搜索-{keyword}", False, error)

# 2.6 城市 + 关键词
print("\n[测试 2.6] 城市 + 关键词 组合")
if test_cities:
    city = test_cities[0]
    keyword = "医院"
    print(f"  组合: 城市='{city}' + 关键词='{keyword}'")
    
    data, error = test_api(
        f"组合-{city}+{keyword}",
        "POST",
        f"{BASE_URL}/institutions/search",
        json={
            "keyword": keyword,
            "region": city,
            "level": "",
            "page": 0,
            "size": 10
        }
    )
    if data:
        total = data.get('totalElements', 0)
        print_test(f"组合-{city}+{keyword}", True, f"找到 {total} 个机构")
        
        if total == 0:
            issues_found.append(f"城市'{city}' + 关键词'{keyword}' 返回0条结果")
    else:
        print_test(f"组合-{city}+{keyword}", False, error)

# 2.7 等级 + 关键词
print("\n[测试 2.7] 等级 + 关键词 组合")
if test_levels:
    level = test_levels[0]
    keyword = "医院"
    print(f"  组合: 等级='{level}' + 关键词='{keyword}'")
    
    data, error = test_api(
        f"组合-{level}+{keyword}",
        "POST",
        f"{BASE_URL}/institutions/search",
        json={
            "keyword": keyword,
            "region": "",
            "level": level,
            "page": 0,
            "size": 10
        }
    )
    if data:
        total = data.get('totalElements', 0)
        print_test(f"组合-{level}+{keyword}", True, f"找到 {total} 个机构")
        
        if total == 0:
            issues_found.append(f"等级'{level}' + 关键词'{keyword}' 返回0条结果")
    else:
        print_test(f"组合-{level}+{keyword}", False, error)

# 2.8 城市 + 等级 + 关键词（全组合）
print("\n[测试 2.8] 城市 + 等级 + 关键词 （全组合）")
if test_cities and test_levels:
    city = test_cities[0]
    level = test_levels[0]
    keyword = "医院"
    print(f"  全组合: 城市='{city}' + 等级='{level}' + 关键词='{keyword}'")
    
    data, error = test_api(
        f"全组合-{city}+{level}+{keyword}",
        "POST",
        f"{BASE_URL}/institutions/search",
        json={
            "keyword": keyword,
            "region": city,
            "level": level,
            "page": 0,
            "size": 10
        }
    )
    if data:
        total = data.get('totalElements', 0)
        print_test(f"全组合", True, f"找到 {total} 个机构")
        
        if total == 0:
            print(f"  [警告] 三重组合返回0条结果，筛选条件可能过严")
            issues_found.append(f"城市+等级+关键词全组合返回0条结果")
    else:
        print_test(f"全组合", False, error)

# ========================================
# 第三部分：边界情况测试
# ========================================
print_section("第三部分：边界情况测试")

# 3.1 空字符串
print("\n[测试 3.1] 空字符串处理")
data, error = test_api(
    "空字符串",
    "POST",
    f"{BASE_URL}/institutions/search",
    json={
        "keyword": "",
        "region": "",
        "level": "",
        "page": 0,
        "size": 10
    }
)
if data:
    total = data.get('totalElements', 0)
    print_test("空字符串", True, f"正常返回 {total} 个机构")
else:
    print_test("空字符串", False, error)

# 3.2 不存在的城市
print("\n[测试 3.2] 不存在的城市")
data, error = test_api(
    "不存在的城市",
    "POST",
    f"{BASE_URL}/institutions/search",
    json={
        "keyword": "",
        "region": "不存在的城市123",
        "level": "",
        "page": 0,
        "size": 10
    }
)
if data:
    total = data.get('totalElements', 0)
    print_test("不存在的城市", True, f"返回 {total} 个机构（预期为0）")
    if total > 0:
        print(f"  [警告] 搜索不存在的城市却返回了结果")
else:
    print_test("不存在的城市", False, error)

# 3.3 不存在的等级
print("\n[测试 3.3] 不存在的等级")
data, error = test_api(
    "不存在的等级",
    "POST",
    f"{BASE_URL}/institutions/search",
    json={
        "keyword": "",
        "region": "",
        "level": "九级特等",
        "page": 0,
        "size": 10
    }
)
if data:
    total = data.get('totalElements', 0)
    print_test("不存在的等级", True, f"返回 {total} 个机构（预期为0）")
    if total > 0:
        print(f"  [警告] 搜索不存在的等级却返回了结果")
else:
    print_test("不存在的等级", False, error)

# 3.4 大页码
print("\n[测试 3.4] 大页码（第100页）")
data, error = test_api(
    "大页码",
    "POST",
    f"{BASE_URL}/institutions/search",
    json={
        "keyword": "",
        "region": "",
        "level": "",
        "page": 100,
        "size": 10
    }
)
if data:
    content = data.get('content', [])
    print_test("大页码", True, f"返回 {len(content)} 条（可能为空）")
else:
    print_test("大页码", False, error)

# ========================================
# 测试总结
# ========================================
print_section("测试总结报告")

total_tests = len(test_results)
passed_tests = sum(1 for r in test_results if r['pass'])
failed_tests = total_tests - passed_tests

print(f"\n总测试数: {total_tests}")
print(f"通过: {passed_tests}")
print(f"失败: {failed_tests}")
print(f"通过率: {passed_tests*100//total_tests}%")

if issues_found:
    print(f"\n发现的问题 ({len(issues_found)} 个):")
    for i, issue in enumerate(issues_found, 1):
        print(f"  {i}. {issue}")
else:
    print("\n[太棒了] 未发现明显问题！")

print("\n" + "=" * 100)
print("测试完成")
print("=" * 100)
