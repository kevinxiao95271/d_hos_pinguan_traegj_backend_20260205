# -*- coding: utf-8 -*-
"""
测试报名统计API
"""
import requests
import json

BASE_URL = "http://localhost:6031/api"

print("=" * 100)
print("测试报名统计API")
print("=" * 100)

# 1. 登录获取token（使用组委会账号）
print("\n[步骤1] 登录组委会账号...")

login_response = requests.post(
    f"{BASE_URL}/auth/login-with-password",
    json={
        "phone": "13800000127",
        "password": "committee2026"
    },
    timeout=30
)

if login_response.status_code != 200:
    print(f"登录失败: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()

if login_data.get('success') != True:
    print(f"登录失败: {login_data.get('message')}")
    exit(1)

token = login_data['data']['token']
print(f"登录成功！")
print(f"  用户: {login_data['data']['name']}")
print(f"  角色: {login_data['data']['role']}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 调用统计接口
print("\n[步骤2] 调用统计汇总接口...")
print(f"API: GET {BASE_URL}/admin/stats/summary")

stats_response = requests.get(
    f"{BASE_URL}/admin/stats/summary",
    headers=headers,
    timeout=30
)

print(f"状态码: {stats_response.status_code}")

if stats_response.status_code != 200:
    print(f"请求失败:")
    print(stats_response.text)
    exit(1)

stats_data = stats_response.json()

print(f"\n响应数据结构:")
print(json.dumps(stats_data, ensure_ascii=False, indent=2)[:500] + "...")

# 3. 解析统计数据
print("\n" + "=" * 100)
print("统计数据详情")
print("=" * 100)

if stats_data.get('success') == True and 'data' in stats_data:
    summary = stats_data['data']
elif isinstance(stats_data, dict) and 'competitionId' in stats_data:
    summary = stats_data
else:
    print("无法解析统计数据")
    exit(1)

print(f"\n【基础信息】")
print(f"  赛事ID: {summary.get('competitionId', 'N/A')}")
print(f"  赛事名称: {summary.get('competitionName', 'N/A')}")
print(f"  报名总数: {summary.get('totalRegistrations', 0)}")
print(f"  品管工具种类数: {summary.get('totalToolTypes', 0)}")
print(f"  评审专家数: {summary.get('totalReviewers', 0)}")
print(f"  参与机构数: {summary.get('totalReviewerInstitutions', 0)}")
print(f"  书面评审任务数: {summary.get('totalBookReviewTasks', 0)}")
print(f"  未评分任务数: {summary.get('unscoredBookTasks', 0)}")

# 地区分布
region_counts = summary.get('regionCounts', {})
if region_counts:
    print(f"\n【地区分布】(Top 10)")
    sorted_regions = sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for region, count in sorted_regions:
        print(f"  {region:<30} {count:>3} 条")

# 主题类型分布
subject_type_counts = summary.get('subjectTypeCounts', {})
if subject_type_counts:
    print(f"\n【主题类型分布】(Top 10)")
    sorted_subjects = sorted(subject_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for subject, count in sorted_subjects:
        print(f"  {subject:<30} {count:>3} 条")

# 品管工具分布
method_counts = summary.get('methodCounts', {})
if method_counts:
    print(f"\n【品管工具分布】(Top 15)")
    sorted_methods = sorted(method_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    for method, count in sorted_methods:
        print(f"  {method:<30} {count:>3} 条")

# 项目负责人职称分布
leader_title_counts = summary.get('leaderTitleCounts', {})
if leader_title_counts:
    print(f"\n【项目负责人职称分布】(Top 10)")
    sorted_titles = sorted(leader_title_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for title, count in sorted_titles:
        print(f"  {title:<30} {count:>3} 条")

# 评分平均值
print(f"\n【书面评审平均分】")
print(f"  计划 (Plan): {summary.get('avgPlan', 0):.2f}")
print(f"  问题 (Problem): {summary.get('avgProblem', 0):.2f}")
print(f"  行动 (Action): {summary.get('avgAction', 0):.2f}")
print(f"  成果 (Success): {summary.get('avgSuccess', 0):.2f}")
print(f"  讨论 (Review): {summary.get('avgReview', 0):.2f}")
print(f"  操作 (Operation): {summary.get('avgOperation', 0):.2f}")
print(f"  展示 (Presentation): {summary.get('avgPresentation', 0):.2f}")

# 4. 数据覆盖率验证
print("\n" + "=" * 100)
print("数据覆盖率验证")
print("=" * 100)

print(f"\n主题类型覆盖:")
print(f"  数据库中共有: 21 种主题类型")
print(f"  实际使用了: {len(subject_type_counts)} 种")
print(f"  覆盖率: {len(subject_type_counts)/21*100:.1f}%")

print(f"\n品管工具覆盖:")
print(f"  数据库中共有: 33 种品管工具")
print(f"  实际使用了: {len(method_counts)} 种")
print(f"  覆盖率: {len(method_counts)/33*100:.1f}%")

print("\n" + "=" * 100)
print("统计API测试完成！")
print("=" * 100)
