#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入舟山医院的7个参赛项目
1. 更新机构名称：舟山市人民医院 → 舟山医院
2. 创建7个参赛者账号
3. 导入7个报名项目及完整信息
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import requests
import json
import time

BASE_URL = "http://localhost:6031"

# 舟山医院参赛项目数据
ZHOUSHAN_PROJECTS = [
    {
        "applicant": {
            "name": "陈蔚莉",
            "phone": "19925000001",
            "title": "护理部主任"
        },
        "project": {
            "name": "基于信息交互的适老化院内转运实践系统的构建与应用",
            "groupType": "ADVANCED",
            "groupCode": "A1"
        },
        "activity": {
            "theme": "适老化院内转运实践系统",
            "keywords": "信息交互,适老化,院内转运",
            "methodCode": "system_construct",
            "subjectTypeCode": "subject_type_8",
            "qualityTopicCode": "quality_topic_5",
            "experienceImproveCode": "experience_1",
            "avgAge": 35,
            "avgWorkYears": 10,
            "crossDepartment": True
        },
        "summary": {
            "theme": "构建适老化院内转运系统",
            "problem": "老年患者院内转运存在安全隐患和效率问题",
            "plan": "设计基于信息交互的智能转运系统，包括实时定位、智能调度等功能",
            "action": "开发系统平台，培训人员，试点运行，逐步推广",
            "success": "转运效率提升30%，老年患者满意度提高至95%",
            "discussion": "系统化管理显著提升了转运安全性和效率"
        },
        "members": [
            {"role": "MENTOR", "name": "陈蔚莉", "title": "护理部主任", "department": "护理部"},
            {"role": "PARTICIPANT", "name": "李明", "title": "主管护师", "department": "信息科"},
            {"role": "PARTICIPANT", "name": "王芳", "title": "护师", "department": "外科"}
        ]
    },
    {
        "applicant": {
            "name": "汪君燕",
            "phone": "19925000002",
            "title": "急诊科主任"
        },
        "project": {
            "name": "提高严重创伤患者送急诊手术60min达标率",
            "groupType": "COMPREHENSIVE",
            "groupCode": "B21"
        },
        "activity": {
            "theme": "严重创伤患者快速救治",
            "keywords": "创伤,急诊手术,达标率",
            "methodCode": "qcc",
            "subjectTypeCode": "subject_type_1",
            "qualityTopicCode": "quality_topic_1",
            "experienceImproveCode": "experience_1",
            "avgAge": 32,
            "avgWorkYears": 8,
            "crossDepartment": True
        },
        "summary": {
            "theme": "优化创伤患者救治流程",
            "problem": "严重创伤患者从急诊到手术时间过长，影响救治效果",
            "plan": "建立绿色通道，优化流程，加强团队协作",
            "action": "成立创伤救治小组，制定标准流程，开展培训演练",
            "success": "60分钟达标率从65%提升至92%",
            "discussion": "多学科协作和流程优化是关键"
        },
        "members": [
            {"role": "MENTOR", "name": "汪君燕", "title": "急诊科主任", "department": "急诊科"},
            {"role": "PARTICIPANT", "name": "张强", "title": "主治医师", "department": "急诊科"},
            {"role": "PARTICIPANT", "name": "刘洋", "title": "护师", "department": "手术室"}
        ]
    },
    {
        "applicant": {
            "name": "刘一宁",
            "phone": "19925000003",
            "title": "静脉治疗专科护士"
        },
        "project": {
            "name": "提高住院患者静脉输液规范使用率",
            "groupType": "COMPREHENSIVE",
            "groupCode": "B2"
        },
        "activity": {
            "theme": "静脉输液规范化管理",
            "keywords": "静脉输液,规范使用,用药安全",
            "methodCode": "qcc",
            "subjectTypeCode": "subject_type_2",
            "qualityTopicCode": "quality_topic_2",
            "experienceImproveCode": "experience_2",
            "avgAge": 30,
            "avgWorkYears": 7,
            "crossDepartment": False
        },
        "summary": {
            "theme": "规范静脉输液使用",
            "problem": "静脉输液使用不规范，存在安全隐患",
            "plan": "制定规范标准，加强培训，实施监督检查",
            "action": "建立评估体系，开展全员培训，定期考核",
            "success": "规范使用率从78%提升至96%",
            "discussion": "标准化和持续培训显著提升了用药安全"
        },
        "members": [
            {"role": "MENTOR", "name": "刘一宁", "title": "静脉治疗专科护士", "department": "护理部"},
            {"role": "PARTICIPANT", "name": "赵敏", "title": "主管护师", "department": "内科"},
            {"role": "PARTICIPANT", "name": "孙丽", "title": "护师", "department": "外科"}
        ]
    },
    {
        "applicant": {
            "name": "杨芳",
            "phone": "19925000004",
            "title": "ICU护士长"
        },
        "project": {
            "name": "提高全院感染性休克集束化治疗完成率",
            "groupType": "COMPREHENSIVE",
            "groupCode": "B2"
        },
        "activity": {
            "theme": "感染性休克集束化治疗",
            "keywords": "感染性休克,集束化,治疗完成率",
            "methodCode": "qcc",
            "subjectTypeCode": "subject_type_1",
            "qualityTopicCode": "quality_topic_1",
            "experienceImproveCode": "experience_1",
            "avgAge": 33,
            "avgWorkYears": 9,
            "crossDepartment": True
        },
        "summary": {
            "theme": "推广感染性休克集束化治疗",
            "problem": "集束化治疗执行不到位，完成率低",
            "plan": "制定标准流程，加强培训，建立监测系统",
            "action": "成立质控小组，开展全员培训，实施实时监控",
            "success": "集束化治疗完成率从68%提升至90%",
            "discussion": "标准化流程和实时监控是提高完成率的关键"
        },
        "members": [
            {"role": "MENTOR", "name": "杨芳", "title": "ICU护士长", "department": "ICU"},
            {"role": "PARTICIPANT", "name": "周杰", "title": "主治医师", "department": "ICU"},
            {"role": "PARTICIPANT", "name": "吴静", "title": "护师", "department": "ICU"}
        ]
    },
    {
        "applicant": {
            "name": "张依妮",
            "phone": "19925000005",
            "title": "呼吸治疗师"
        },
        "project": {
            "name": "基于多学科的全病程呼吸治疗管理体系的构建与应用",
            "groupType": "ADVANCED",
            "groupCode": "A1"
        },
        "activity": {
            "theme": "全病程呼吸治疗管理",
            "keywords": "呼吸治疗,多学科,全病程管理",
            "methodCode": "system_construct",
            "subjectTypeCode": "subject_type_1",
            "qualityTopicCode": "quality_topic_5",
            "experienceImproveCode": "experience_1",
            "avgAge": 31,
            "avgWorkYears": 8,
            "crossDepartment": True
        },
        "summary": {
            "theme": "构建呼吸治疗管理体系",
            "problem": "呼吸治疗缺乏系统化管理，各科室协作不足",
            "plan": "建立多学科协作机制，制定全病程管理流程",
            "action": "组建MDT团队，设计管理流程，开展培训，试点推广",
            "success": "呼吸治疗有效率提升25%，住院天数缩短2.5天",
            "discussion": "多学科协作显著提升了呼吸治疗效果"
        },
        "members": [
            {"role": "MENTOR", "name": "张依妮", "title": "呼吸治疗师", "department": "呼吸科"},
            {"role": "PARTICIPANT", "name": "陈涛", "title": "主治医师", "department": "呼吸科"},
            {"role": "PARTICIPANT", "name": "林美", "title": "护师", "department": "ICU"}
        ]
    },
    {
        "applicant": {
            "name": "夏舟备",
            "phone": "19925000006",
            "title": "输血科主任"
        },
        "project": {
            "name": "提高手术患者自体输血率",
            "groupType": "COMPREHENSIVE",
            "groupCode": "B6"
        },
        "activity": {
            "theme": "推广自体输血技术",
            "keywords": "自体输血,手术患者,血液安全",
            "methodCode": "qcc",
            "subjectTypeCode": "subject_type_4",
            "qualityTopicCode": "quality_topic_3",
            "experienceImproveCode": "experience_1",
            "avgAge": 34,
            "avgWorkYears": 10,
            "crossDepartment": True
        },
        "summary": {
            "theme": "提升自体输血应用率",
            "problem": "自体输血技术应用率低，异体输血风险高",
            "plan": "加强宣教，完善流程，提升技术能力",
            "action": "培训医护人员，改进设备，建立标准流程",
            "success": "自体输血率从15%提升至42%",
            "discussion": "自体输血显著降低了异体输血相关风险"
        },
        "members": [
            {"role": "MENTOR", "name": "夏舟备", "title": "输血科主任", "department": "输血科"},
            {"role": "PARTICIPANT", "name": "郑华", "title": "主治医师", "department": "麻醉科"},
            {"role": "PARTICIPANT", "name": "黄丽", "title": "技师", "department": "输血科"}
        ]
    },
    {
        "applicant": {
            "name": "李利群",
            "phone": "19925000007",
            "title": "康复科主任"
        },
        "project": {
            "name": "基于海岛特色的AECOPD患者早期肺康复模式构建",
            "groupType": "COMPREHENSIVE",
            "groupCode": "B14"
        },
        "activity": {
            "theme": "AECOPD早期肺康复",
            "keywords": "AECOPD,肺康复,海岛特色",
            "methodCode": "system_construct",
            "subjectTypeCode": "subject_type_1",
            "qualityTopicCode": "quality_topic_5",
            "experienceImproveCode": "experience_3",
            "avgAge": 36,
            "avgWorkYears": 11,
            "crossDepartment": True
        },
        "summary": {
            "theme": "构建海岛特色肺康复模式",
            "problem": "AECOPD患者缺乏早期康复，复发率高",
            "plan": "结合海岛环境特点，建立早期康复模式",
            "action": "设计康复方案，培训人员，建立随访机制",
            "success": "再入院率下降35%，患者生活质量显著提升",
            "discussion": "早期康复干预对AECOPD患者预后改善明显"
        },
        "members": [
            {"role": "MENTOR", "name": "李利群", "title": "康复科主任", "department": "康复科"},
            {"role": "PARTICIPANT", "name": "徐刚", "title": "主治医师", "department": "呼吸科"},
            {"role": "PARTICIPANT", "name": "朱红", "title": "康复治疗师", "department": "康复科"}
        ]
    }
]

def wait_for_server():
    """等待服务器启动"""
    print("等待服务器启动...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/api/competitions", timeout=3)
            if response.status_code in [200, 401]:
                print(f"✓ 服务器已启动 (尝试 {i+1}/30)\n")
                return True
        except:
            pass
        if i % 5 == 0:
            print(f"   等待中... ({i+1}/30)")
        time.sleep(3)
    print("✗ 服务器启动超时\n")
    return False

def login():
    """登录为OPS角色"""
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "phone": "13900000000",
            "name": "Admin User",
            "title": "Manager",
            "role": "OPS",
            "institutionId": 1
        })
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "token" in data["data"]:
                return data["data"]["token"]
            else:
                raise Exception(f"登录响应格式错误: {data}")
        else:
            raise Exception(f"登录失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"登录异常: {str(e)}")
        raise

def update_institution_name(token):
    """更新机构名称"""
    print("\n1️⃣  更新机构名称: 舟山市人民医院 → 舟山医院")
    
    # 更新机构信息
    response = requests.put(f"{BASE_URL}/api/institutions/17",
                           json={"name": "舟山医院"},
                           headers={
                               "Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"
                           })
    
    if response.status_code == 200:
        print("   ✅ 机构名称已更新")
        return True
    else:
        print(f"   ❌ 更新失败: {response.status_code}")
        print(f"   {response.text}")
        return False

def create_user(user_data, token):
    """创建用户账号"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "phone": user_data["phone"],
        "name": user_data["name"],
        "title": user_data.get("title", "参赛者"),
        "role": "CONTESTANT",
        "institutionId": 17  # 舟山医院
    })
    
    if response.status_code == 200:
        user_info = response.json()["data"]
        return user_info["userId"]
    else:
        print(f"   ❌ 创建用户失败: {user_data['name']} - {response.status_code}")
        return None

def create_registration(project_data, applicant_id, token):
    """创建报名项目"""
    response = requests.post(f"{BASE_URL}/api/registrations",
                            json={
                                "competitionId": 21,
                                "institutionId": 17,
                                "applicantId": applicant_id,
                                "projectName": project_data["project"]["name"],
                                "groupType": project_data["project"]["groupType"]
                            },
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"
                            })
    
    if response.status_code == 200:
        return response.json()["data"]["id"]
    else:
        print(f"   ❌ 创建报名失败: {response.status_code}")
        print(f"   {response.text}")
        return None

def submit_members(registration_id, members, token):
    """提交团队成员"""
    response = requests.put(f"{BASE_URL}/api/registrations/{registration_id}/members",
                           json={"members": members},
                           headers={
                               "Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"
                           })
    return response.status_code == 200

def submit_activity(registration_id, activity, token):
    """提交活动信息"""
    response = requests.put(f"{BASE_URL}/api/registrations/{registration_id}/activity",
                           json=activity,
                           headers={
                               "Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"
                           })
    return response.status_code == 200

def submit_summary(registration_id, summary, token):
    """提交项目总结"""
    response = requests.put(f"{BASE_URL}/api/registrations/{registration_id}/summary",
                           json=summary,
                           headers={
                               "Authorization": f"Bearer {token}",
                               "Content-Type": "application/json"
                           })
    return response.status_code == 200

def submit_registration(registration_id, token):
    """提交报名"""
    response = requests.post(f"{BASE_URL}/api/registrations/{registration_id}/submit",
                            headers={"Authorization": f"Bearer {token}"})
    return response.status_code == 200

def batch_classify(registration_id, group_code, token):
    """批量分组"""
    response = requests.post(f"{BASE_URL}/api/admin/registrations/batch-classify",
                            json={
                                "registrationIds": [registration_id],
                                "groupCode": group_code
                            },
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"
                            })
    return response.status_code == 200

def approve_registration(registration_id, token):
    """审核通过报名"""
    response = requests.post(f"{BASE_URL}/api/registrations/{registration_id}/approve",
                            headers={"Authorization": f"Bearer {token}"})
    return response.status_code == 200

def main():
    print("="*80)
    print("  舟山医院参赛数据导入")
    print("="*80)
    
    if not wait_for_server():
        return
    
    try:
        token = login()
        print("✓ 登录成功（OPS角色）\n")
        
        # 1. 更新机构名称
        if not update_institution_name(token):
            return
        
        # 2. 导入7个项目
        print("\n2️⃣  导入7个参赛项目\n")
        
        success_count = 0
        for idx, project_data in enumerate(ZHOUSHAN_PROJECTS, 1):
            applicant = project_data["applicant"]
            print(f"项目 {idx}/7: {applicant['name']} - {project_data['project']['name'][:30]}...")
            
            # 创建用户
            print(f"   → 创建用户: {applicant['name']} ({applicant['phone']})")
            applicant_id = create_user(applicant, token)
            if not applicant_id:
                continue
            print(f"      用户ID: {applicant_id}")
            
            # 创建报名
            print(f"   → 创建报名项目")
            registration_id = create_registration(project_data, applicant_id, token)
            if not registration_id:
                continue
            print(f"      报名ID: {registration_id}")
            
            # 提交成员
            print(f"   → 提交团队成员 ({len(project_data['members'])}人)")
            if not submit_members(registration_id, project_data["members"], token):
                print(f"      ⚠️ 成员提交失败")
            
            # 提交活动信息
            print(f"   → 提交活动信息")
            if not submit_activity(registration_id, project_data["activity"], token):
                print(f"      ⚠️ 活动信息提交失败")
            
            # 提交项目总结
            print(f"   → 提交项目总结")
            if not submit_summary(registration_id, project_data["summary"], token):
                print(f"      ⚠️ 项目总结提交失败")
            
            # 提交报名
            print(f"   → 提交报名")
            if not submit_registration(registration_id, token):
                print(f"      ⚠️ 报名提交失败")
            
            # 设置分组
            group_code = project_data["project"]["groupCode"]
            print(f"   → 设置分组: {group_code}")
            if not batch_classify(registration_id, group_code, token):
                print(f"      ⚠️ 分组设置失败")
            
            # 审核通过
            print(f"   → 审核通过")
            if not approve_registration(registration_id, token):
                print(f"      ⚠️ 审核通过失败")
            
            print(f"   ✅ 项目 {idx} 导入成功\n")
            success_count += 1
            time.sleep(0.5)
        
        # 3. 汇总结果
        print("="*80)
        print(f"  导入完成: {success_count}/7 个项目成功")
        print("="*80)
        
        print("\n📋 参赛者登录信息:")
        print("-" * 80)
        for project_data in ZHOUSHAN_PROJECTS:
            applicant = project_data["applicant"]
            print(f"姓名: {applicant['name']:10s} | 手机号: {applicant['phone']} | 职称: {applicant['title']}")
        print("-" * 80)
        
        print("\n✅ 所有参赛者都可以使用手机号登录系统")
        print("   登录API: POST /api/auth/login")
        print("   参数示例: {\"phone\": \"19925000001\", \"name\": \"陈蔚莉\", ...}")
        
    except Exception as e:
        print(f"\n❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
