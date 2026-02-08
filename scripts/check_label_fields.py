#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查Label字段是否正确返回
用于前端开发人员验证API
"""

import requests
import json

BASE_URL = "http://localhost:6031"

def check_labels():
    print("=" * 80)
    print("Label字段检查工具")
    print("=" * 80)
    
    # 登录
    print("\n1. 登录...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"phone": "13900000001", "name": "李明华", "role": "REVIEWER"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return
    
    token = login_response.json()["data"]["token"]
    print("✅ 登录成功")
    
    # 获取详情
    print("\n2. 获取报名详情...")
    detail_response = requests.get(
        f"{BASE_URL}/api/registrations/119",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if detail_response.status_code != 200:
        print(f"❌ 获取详情失败: {detail_response.status_code}")
        return
    
    activity_info = detail_response.json()["data"]["activityInfo"]
    print("✅ 获取详情成功")
    
    # 检查4个Label字段
    print("\n" + "=" * 80)
    print("Label字段检查结果")
    print("=" * 80)
    
    fields = [
        {
            "name": "主题类型",
            "code_field": "subjectTypeCode",
            "label_field": "subjectTypeLabel",
            "code": activity_info.get("subjectTypeCode"),
            "label": activity_info.get("subjectTypeLabel")
        },
        {
            "name": "运用手法",
            "code_field": "methodCode",
            "label_field": "methodLabel",
            "code": activity_info.get("methodCode"),
            "label": activity_info.get("methodLabel")
        },
        {
            "name": "改善就医环境",
            "code_field": "experienceImproveCode",
            "label_field": "experienceImproveLabel",
            "code": activity_info.get("experienceImproveCode"),
            "label": activity_info.get("experienceImproveLabel")
        },
        {
            "name": "医疗质量相关主题",
            "code_field": "qualityTopicCode",
            "label_field": "qualityTopicLabel",
            "code": activity_info.get("qualityTopicCode"),
            "label": activity_info.get("qualityTopicLabel")
        }
    ]
    
    all_passed = True
    
    for field in fields:
        print(f"\n【{field['name']}】")
        print(f"  Code字段 ({field['code_field']}): {field['code']}")
        print(f"  Label字段 ({field['label_field']}): {field['label']}")
        
        if field['code'] and field['label']:
            print(f"  ✅ 正确：Code和Label都存在")
            print(f"  📝 前端应该显示: {field['label']}")
        elif field['code'] and not field['label']:
            print(f"  ❌ 错误：Code存在但Label缺失")
            print(f"  ⚠️  前端会显示: {field['code']} (这是错误的！)")
            all_passed = False
        else:
            print(f"  ⚠️  未填写")
    
    # 显示前端代码示例
    print("\n" + "=" * 80)
    print("前端代码示例")
    print("=" * 80)
    
    print("\n❌ 错误的前端代码（会显示Code）:")
    print("```vue")
    print("<div>{{ activityInfo.experienceImproveCode }}</div>")
    print("<div>{{ activityInfo.qualityTopicCode }}</div>")
    print("```")
    print("显示结果: experience_1, quality_1 ❌")
    
    print("\n✅ 正确的前端代码（会显示Label）:")
    print("```vue")
    print("<div>{{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode }}</div>")
    print("<div>{{ activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode }}</div>")
    print("```")
    print("显示结果: 门诊就诊流程更加优化, 降低住院患者围手术期死亡率 ✅")
    
    # 总结
    print("\n" + "=" * 80)
    print("检查总结")
    print("=" * 80)
    
    if all_passed:
        print("✅ 后端API正确返回了所有Label字段")
        print("✅ 前端可以直接使用Label字段")
        print("\n如果前端显示的是Code（如 experience_1），说明前端代码有问题！")
        print("请检查前端代码是否优先使用了Label字段。")
    else:
        print("❌ 部分Label字段缺失")
        print("请联系后端开发人员修复。")
    
    # 显示完整的activityInfo
    print("\n" + "=" * 80)
    print("完整的 activityInfo 数据（供前端参考）")
    print("=" * 80)
    print(json.dumps(activity_info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        check_labels()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保:")
        print("1. 应用正在运行（端口6031）")
        print("2. 网络连接正常")
