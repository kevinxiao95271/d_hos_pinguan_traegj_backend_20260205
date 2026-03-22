#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端全流程测试脚本
测试所有角色的完整流程，验证接口是否正常工作
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional

# 设置UTF-8输出编码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:6031"

class APITester:
    def __init__(self):
        self.tokens = {}
        self.test_data = {
            "competition_id": None,
            "registration_ids": [],
            "reviewer_ids": [],
            "review_task_ids": [],
            "institution_ids": []
        }
        self.results = []
        
    def log(self, message: str, data: Any = None):
        """记录测试结果"""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": message
        }
        if data:
            log_entry["data"] = data
        self.results.append(log_entry)
        print(f"[{log_entry['timestamp']}] {message}")
        if data:
            print(f"  Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    def call_api(self, method: str, path: str, token: Optional[str] = None, 
                 data: Any = None, params: Dict = None) -> Dict[str, Any]:
        """调用API"""
        url = f"{BASE_URL}{path}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                resp = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                resp = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                resp = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            result = {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response": resp.json() if resp.text else None
            }
            
            if not result["success"]:
                self.log(f"[FAIL] API调用失败: {method} {path}", result)
            
            return result
        except Exception as e:
            error_result = {
                "status_code": 0,
                "success": False,
                "error": str(e)
            }
            self.log(f"[ERROR] API调用异常: {method} {path}", error_result)
            return error_result
    
    # ========== 角色1: 系统运维/赛事管理员 ==========
    
    def test_admin_login(self):
        """测试管理员登录"""
        self.log("=" * 60)
        self.log("步骤1: 管理员登录")
        
        result = self.call_api("POST", "/api/auth/login", data={
            "phone": "13800000001",
            "name": "系统管理员",
            "title": "运维主管",
            "role": "OPS",
            "institutionId": None
        })
        
        if result["success"] and result["response"]["success"]:
            self.tokens["admin"] = result["response"]["data"]["token"]
            self.log("[OK] 管理员登录成功", {
                "userId": result["response"]["data"]["id"],
                "name": result["response"]["data"]["name"],
                "role": result["response"]["data"]["role"]
            })
            return True
        else:
            self.log("[FAIL] 管理员登录失败")
            return False
    
    def test_check_dictionaries(self):
        """检查字典配置"""
        self.log("=" * 60)
        self.log("步骤2: 检查字典配置")
        
        dict_types = ["subject_type", "method", "experience_improve", "quality_topic"]
        for dict_type in dict_types:
            result = self.call_api("GET", f"/api/dictionaries/{dict_type}", 
                                  token=self.tokens["admin"])
            if result["success"]:
                count = len(result["response"]["data"]) if result["response"]["data"] else 0
                self.log(f"[OK] 字典 {dict_type} 配置数量: {count}")
            else:
                self.log(f"[FAIL] 获取字典 {dict_type} 失败")
    
    def test_create_competition(self):
        """创建赛事"""
        self.log("=" * 60)
        self.log("步骤3: 创建新赛事")
        
        result = self.call_api("POST", "/api/competitions", 
                              token=self.tokens["admin"],
                              data={
                                  "name": "2026年浙江省医疗质量改进大赛",
                                  "description": "全流程端到端测试赛事"
                              })
        
        if result["success"] and result["response"]["success"]:
            self.test_data["competition_id"] = result["response"]["data"]["id"]
            self.log("[OK] 赛事创建成功", {
                "competitionId": self.test_data["competition_id"],
                "name": result["response"]["data"]["name"]
            })
            return True
        else:
            self.log("[FAIL] 赛事创建失败")
            return False
    
    def test_set_competition_stage(self, stage: str):
        """设置赛事阶段"""
        self.log(f"步骤: 设置赛事阶段为 {stage}")
        
        result = self.call_api("PUT", 
                              f"/api/competitions/{self.test_data['competition_id']}/stage",
                              token=self.tokens["admin"],
                              data={
                                  "stage": stage
                              })
        
        if result["success"]:
            self.log(f"[OK] 赛事阶段设置为 {stage}")
            return True
        else:
            self.log(f"[FAIL] 设置赛事阶段失败")
            return False
    
    # ========== 角色2: 参赛者 ==========
    
    def test_participant_login(self, phone: str, institution_id: int):
        """参赛者登录"""
        self.log(f"步骤: 参赛者登录 (机构ID: {institution_id})")
        
        result = self.call_api("POST", "/api/auth/login", data={
            "phone": phone,
            "name": f"项目负责人-{institution_id}",
            "title": "主任医师",
            "role": "PARTICIPANT",
            "institutionId": institution_id
        })
        
        if result["success"] and result["response"]["success"]:
            token_key = f"participant_{institution_id}"
            self.tokens[token_key] = result["response"]["data"]["token"]
            self.log(f"[OK] 参赛者登录成功", {
                "userId": result["response"]["data"]["id"],
                "institutionName": result["response"]["data"].get("institutionName"),
                "institutionId": institution_id
            })
            return result["response"]["data"]["id"]
        else:
            self.log("[FAIL] 参赛者登录失败")
            return None
    
    def test_create_registration(self, institution_id: int, applicant_id: int, 
                                 group_type: str, project_name: str):
        """创建报名"""
        self.log(f"步骤: 创建报名 - {project_name} ({group_type})")
        
        token_key = f"participant_{institution_id}"
        result = self.call_api("POST", "/api/registrations",
                              token=self.tokens[token_key],
                              data={
                                  "competitionId": self.test_data["competition_id"],
                                  "institutionId": institution_id,
                                  "applicantId": applicant_id,
                                  "projectName": project_name,
                                  "groupType": group_type
                              })
        
        if result["success"] and result["response"]["success"]:
            reg_id = result["response"]["data"]["id"]
            self.test_data["registration_ids"].append({
                "id": reg_id,
                "institutionId": institution_id,
                "groupType": group_type,
                "projectName": project_name
            })
            self.log(f"[OK] 报名创建成功", {"registrationId": reg_id})
            return reg_id
        else:
            self.log("[FAIL] 报名创建失败")
            return None
    
    def test_fill_registration_form(self, registration_id: int, institution_id: int):
        """填写报名表单"""
        self.log(f"步骤: 填写报名表 (报名ID: {registration_id})")
        
        token_key = f"participant_{institution_id}"
        
        # 1. 填写成员信息
        members_result = self.call_api("PUT", 
                                       f"/api/registrations/{registration_id}/members",
                                       token=self.tokens[token_key],
                                       data={
                                           "items": [
                                               {
                                                   "role": "PARTICIPANT",
                                                   "name": "张医生",
                                                   "title": "主治医师",
                                                   "department": "内科"
                                               },
                                               {
                                                   "role": "PARTICIPANT",
                                                   "name": "李护士",
                                                   "title": "护师",
                                                   "department": "内科"
                                               },
                                               {
                                                   "role": "MENTOR",
                                                   "name": "王主任",
                                                   "title": "主任医师",
                                                   "department": "医务处"
                                               }
                                           ]
                                       })
        
        if members_result["success"]:
            self.log(f"[OK] 成员信息填写成功")
        else:
            self.log(f"[FAIL] 成员信息填写失败")
            return False
        
        # 2. 填写活动说明
        activity_result = self.call_api("PUT",
                                        f"/api/registrations/{registration_id}/activity",
                                        token=self.tokens[token_key],
                                        data={
                                            "theme": "提高患者满意度",
                                            "keywords": "患者体验,流程优化",
                                            "subjectTypeCode": "patient_care",
                                            "methodCode": "qc_problem",
                                            "experienceImproveCode": "appointment",
                                            "qualityTopicCode": "stemi",
                                            "avgWorkYears": 8,
                                            "avgAge": 35,
                                            "crossDepartment": True
                                        })
        
        if activity_result["success"]:
            self.log(f"[OK] 活动说明填写成功")
        else:
            self.log(f"[FAIL] 活动说明填写失败")
            return False
        
        # 3. 填写项目摘要
        summary_result = self.call_api("PUT",
                                       f"/api/registrations/{registration_id}/summary",
                                       token=self.tokens[token_key],
                                       data={
                                           "theme": "提高患者满意度项目摘要",
                                           "plan": "通过分析患者流程，找出痛点",
                                           "problem": "等待时间长，信息不透明",
                                           "action": "优化预约流程，增加信息推送",
                                           "success": "满意度从75%提升到90%",
                                           "discussion": "流程优化效果显著，可推广"
                                       })
        
        if summary_result["success"]:
            self.log(f"[OK] 项目摘要填写成功")
        else:
            self.log(f"[FAIL] 项目摘要填写失败")
            return False
        
        return True
    
    def test_submit_registration(self, registration_id: int, institution_id: int):
        """提交报名"""
        self.log(f"步骤: 提交报名 (报名ID: {registration_id})")
        
        token_key = f"participant_{institution_id}"
        result = self.call_api("POST",
                              f"/api/registrations/{registration_id}/submit",
                              token=self.tokens[token_key])
        
        if result["success"]:
            self.log(f"[OK] 报名提交成功")
            return True
        else:
            self.log(f"[FAIL] 报名提交失败")
            return False
    
    def test_approve_registration(self, registration_id: int):
        """管理员审批报名"""
        self.log(f"步骤: 审批报名 (报名ID: {registration_id})")
        
        result = self.call_api("POST",
                              f"/api/registrations/{registration_id}/approve",
                              token=self.tokens["admin"])
        
        if result["success"]:
            self.log(f"[OK] 报名审批通过")
            return True
        else:
            self.log(f"[FAIL] 报名审批失败")
            return False
    
    # ========== 角色3: 赛事管理 - 分组 ==========
    
    def test_auto_group_registrations(self):
        """自动分组"""
        self.log("=" * 60)
        self.log("步骤: 自动分组所有报名")
        
        result = self.call_api("POST", "/api/admin/registrations/auto-group",
                              token=self.tokens["admin"],
                              data={
                                  "competitionId": self.test_data["competition_id"]
                              })
        
        if result["success"]:
            self.log(f"[OK] 自动分组成功")
            return True
        else:
            self.log(f"[FAIL] 自动分组失败")
            return False
    
    def test_batch_classify(self, registration_ids: list, group_code: str):
        """批量分类"""
        self.log(f"步骤: 批量分类到 {group_code}")
        
        result = self.call_api("POST", "/api/admin/registrations/batch-classify",
                              token=self.tokens["admin"],
                              data={
                                  "registrationIds": registration_ids,
                                  "groupCode": group_code
                              })
        
        if result["success"]:
            self.log(f"[OK] 批量分类成功")
            return True
        else:
            self.log(f"[FAIL] 批量分类失败")
            return False
    
    def test_view_registrations_by_filter(self):
        """查看报名列表"""
        self.log("=" * 60)
        self.log("步骤: 查看报名列表(筛选)")
        
        result = self.call_api("GET", "/api/admin/registrations/filter",
                              token=self.tokens["admin"],
                              params={
                                  "competitionId": self.test_data["competition_id"]
                              })
        
        if result["success"] and result["response"]["success"]:
            registrations = result["response"]["data"]
            self.log(f"[OK] 查看报名列表成功，共 {len(registrations)} 个报名")
            
            # 按组别统计
            stats = {}
            for reg in registrations:
                group = f"{reg.get('groupType', 'UNKNOWN')}-{reg.get('groupCode', 'N/A')}"
                stats[group] = stats.get(group, 0) + 1
            
            self.log("分组统计:", stats)
            return True
        else:
            self.log("[FAIL] 查看报名列表失败")
            return False
    
    # ========== 角色4: 评审专家 ==========
    
    def test_reviewer_login(self, phone: str, reviewer_group: str, expert_bg: str):
        """评审专家登录"""
        self.log(f"步骤: 评审专家登录 ({reviewer_group}, {expert_bg})")
        
        result = self.call_api("POST", "/api/auth/login", data={
            "phone": phone,
            "name": f"评审专家-{reviewer_group}",
            "title": "教授",
            "role": "REVIEWER",
            "institutionId": None,
            "reviewerGroupCode": reviewer_group,
            "interviewGroupCode": reviewer_group,
            "expertBackground": expert_bg
        })
        
        if result["success"] and result["response"]["success"]:
            reviewer_id = result["response"]["data"]["id"]
            token_key = f"reviewer_{reviewer_id}"
            self.tokens[token_key] = result["response"]["data"]["token"]
            self.test_data["reviewer_ids"].append({
                "id": reviewer_id,
                "groupCode": reviewer_group,
                "background": expert_bg
            })
            self.log(f"[OK] 评审专家登录成功", {
                "reviewerId": reviewer_id,
                "name": result["response"]["data"]["name"]
            })
            return reviewer_id
        else:
            self.log("[FAIL] 评审专家登录失败")
            return None
    
    def test_assign_review_task(self, registration_id: int, reviewer_id: int, stage: str):
        """分配评审任务"""
        self.log(f"步骤: 分配评审任务 (报名: {registration_id}, 评审: {reviewer_id}, 阶段: {stage})")
        
        result = self.call_api("POST", "/api/admin/reviews/tasks",
                              token=self.tokens["admin"],
                              data={
                                  "registrationId": registration_id,
                                  "reviewerId": reviewer_id,
                                  "stage": stage
                              })
        
        if result["success"] and result["response"]["success"]:
            task_id = result["response"]["data"]["id"]
            self.test_data["review_task_ids"].append({
                "id": task_id,
                "registrationId": registration_id,
                "reviewerId": reviewer_id,
                "stage": stage
            })
            self.log(f"[OK] 评审任务分配成功", {"taskId": task_id})
            return task_id
        else:
            self.log("[FAIL] 评审任务分配失败")
            return None
    
    def test_auto_assign_reviews(self, stage: str):
        """自动分配评审"""
        self.log(f"步骤: 自动分配评审任务 (阶段: {stage})")
        
        result = self.call_api("POST", "/api/admin/reviews/auto-assign",
                              token=self.tokens["admin"],
                              data={
                                  "competitionId": self.test_data["competition_id"],
                                  "stage": stage
                              })
        
        if result["success"]:
            self.log(f"[OK] 自动分配评审成功")
            return True
        else:
            self.log(f"[FAIL] 自动分配评审失败")
            return False
    
    def test_reviewer_view_tasks(self, reviewer_id: int):
        """评审专家查看任务"""
        self.log(f"步骤: 评审专家查看任务 (评审ID: {reviewer_id})")
        
        result = self.call_api("GET", "/api/reviews/tasks",
                              token=self.tokens[f"reviewer_{reviewer_id}"],
                              params={"reviewerId": reviewer_id})
        
        if result["success"] and result["response"]["success"]:
            tasks = result["response"]["data"]
            self.log(f"[OK] 查看任务成功，共 {len(tasks)} 个任务")
            return tasks
        else:
            self.log("[FAIL] 查看任务失败")
            return []
    
    def test_confirm_review_task(self, task_id: int, reviewer_id: int):
        """确认评审任务"""
        self.log(f"步骤: 确认评审任务 (任务ID: {task_id})")
        
        result = self.call_api("PUT", "/api/reviews/tasks/status",
                              token=self.tokens[f"reviewer_{reviewer_id}"],
                              data={
                                  "reviewTaskId": task_id,
                                  "status": "CONFIRMED"
                              })
        
        if result["success"]:
            self.log(f"[OK] 确认任务成功")
            return True
        else:
            self.log(f"[FAIL] 确认任务失败")
            return False
    
    def test_submit_review_score(self, task_id: int, reviewer_id: int):
        """提交评审评分"""
        self.log(f"步骤: 提交评审评分 (任务ID: {task_id})")
        
        result = self.call_api("POST", "/api/reviews/scores",
                              token=self.tokens[f"reviewer_{reviewer_id}"],
                              data={
                                  "reviewTaskId": task_id,
                                  "plan": 18,
                                  "problem": 17,
                                  "action": 19,
                                  "success": 16,
                                  "review": 14,
                                  "operation": 11,
                                  "presentation": 8,
                                  "highlight": "项目设计合理，数据真实可靠",
                                  "weakness": "展示方式可以更生动"
                              })
        
        if result["success"]:
            self.log(f"[OK] 提交评分成功")
            return True
        else:
            self.log(f"[FAIL] 提交评分失败")
            return False
    
    # ========== 查看结果 ==========
    
    def test_participant_view_results(self, registration_id: int, institution_id: int):
        """参赛者查看评审结果"""
        self.log(f"步骤: 参赛者查看结果 (报名ID: {registration_id})")
        
        token_key = f"participant_{institution_id}"
        result = self.call_api("GET", 
                              f"/api/registrations/{registration_id}/review-details",
                              token=self.tokens[token_key])
        
        if result["success"] and result["response"]["success"]:
            details = result["response"]["data"]
            self.log(f"[OK] 查看结果成功", details)
            return True
        else:
            self.log("[FAIL] 查看结果失败")
            return False
    
    def test_admin_view_summary(self, stage: str):
        """管理员查看评分汇总"""
        self.log(f"步骤: 查看评分汇总 (阶段: {stage})")
        
        result = self.call_api("GET", "/api/admin/reviews/summary",
                              token=self.tokens["admin"],
                              params={
                                  "competitionId": self.test_data["competition_id"],
                                  "stage": stage
                              })
        
        if result["success"] and result["response"]["success"]:
            summary = result["response"]["data"]
            self.log(f"[OK] 查看汇总成功，共 {len(summary)} 个项目")
            return True
        else:
            self.log("[FAIL] 查看汇总失败")
            return False
    
    def test_admin_view_rankings(self, stage: str):
        """管理员查看排名"""
        self.log(f"步骤: 查看排名 (阶段: {stage})")
        
        result = self.call_api("GET", "/api/admin/reviews/rankings",
                              token=self.tokens["admin"],
                              params={
                                  "competitionId": self.test_data["competition_id"],
                                  "stage": stage
                              })
        
        if result["success"] and result["response"]["success"]:
            rankings = result["response"]["data"]
            self.log(f"[OK] 查看排名成功，共 {len(rankings)} 个项目")
            if rankings:
                top3 = rankings[:3]
                self.log("前三名:", [
                    {
                        "irank": r["irank"],
                        "projectName": r["projectName"],
                        "avgTotal": r["avgTotal"]
                    } for r in top3
                ])
            return True
        else:
            self.log("[FAIL] 查看排名失败")
            return False
    
    # ========== 主流程 ==========
    
    def run_full_flow(self):
        """运行完整流程测试"""
        self.log("=" * 80)
        self.log("开始端到端全流程测试")
        self.log("=" * 80)
        
        # 1. 管理员登录
        if not self.test_admin_login():
            return False
        
        # 2. 检查字典
        self.test_check_dictionaries()
        
        # 3. 创建赛事
        if not self.test_create_competition():
            return False
        
        # 4. 设置为报名阶段
        if not self.test_set_competition_stage("REGISTER"):
            return False
        
        # 5. 创建参赛者和报名（至少6个：2个进阶组，2个综合组，2个基层组）
        self.log("=" * 60)
        self.log("步骤5: 创建参赛报名")
        
        test_registrations = [
            {"institution_id": 1, "phone": "13900000001", "group_type": "ADVANCED", "name": "进阶组项目1"},
            {"institution_id": 2, "phone": "13900000002", "group_type": "ADVANCED", "name": "进阶组项目2"},
            {"institution_id": 3, "phone": "13900000003", "group_type": "COMPREHENSIVE", "name": "综合组项目1"},
            {"institution_id": 4, "phone": "13900000004", "group_type": "COMPREHENSIVE", "name": "综合组项目2"},
            {"institution_id": 5, "phone": "13900000005", "group_type": "BASIC", "name": "基层组项目1"},
            {"institution_id": 6, "phone": "13900000006", "group_type": "BASIC", "name": "基层组项目2"},
        ]
        
        for tr in test_registrations:
            applicant_id = self.test_participant_login(tr["phone"], tr["institution_id"])
            if applicant_id:
                reg_id = self.test_create_registration(
                    tr["institution_id"], applicant_id, tr["group_type"], tr["name"]
                )
                if reg_id:
                    if self.test_fill_registration_form(reg_id, tr["institution_id"]):
                        self.test_submit_registration(reg_id, tr["institution_id"])
                        self.test_approve_registration(reg_id)
        
        if not self.test_data["registration_ids"]:
            self.log("[FAIL] 没有成功创建任何报名")
            return False
        
        # 6. 自动分组
        self.test_auto_group_registrations()
        
        # 7. 查看报名列表
        self.test_view_registrations_by_filter()
        
        # 8. 设置为书审阶段
        self.log("=" * 60)
        self.log("步骤8: 进入书审阶段")
        if not self.test_set_competition_stage("BOOK_REVIEW"):
            return False
        
        # 9. 创建评审专家
        self.log("=" * 60)
        self.log("步骤9: 创建评审专家")
        
        reviewers = [
            {"phone": "15800000001", "group": "A1", "bg": "MEDICAL"},
            {"phone": "15800000002", "group": "A2", "bg": "NURSING"},
            {"phone": "15800000003", "group": "B1", "bg": "MANAGEMENT"},
        ]
        
        for rv in reviewers:
            self.test_reviewer_login(rv["phone"], rv["group"], rv["bg"])
        
        # 10. 自动分配评审任务
        self.log("=" * 60)
        self.log("步骤10: 自动分配书审任务")
        self.test_auto_assign_reviews("BOOK")
        
        # 11. 评审专家评分
        self.log("=" * 60)
        self.log("步骤11: 评审专家评分")
        
        for reviewer in self.test_data["reviewer_ids"][:2]:  # 只测试前2个评审
            reviewer_id = reviewer["id"]
            tasks = self.test_reviewer_view_tasks(reviewer_id)
            
            for task in tasks[:2]:  # 每个评审只评前2个任务
                task_id = task["id"]
                if self.test_confirm_review_task(task_id, reviewer_id):
                    self.test_submit_review_score(task_id, reviewer_id)
        
        # 12. 查看书审结果
        self.log("=" * 60)
        self.log("步骤12: 查看书审结果")
        self.test_admin_view_summary("BOOK")
        self.test_admin_view_rankings("BOOK")
        
        # 13. 参赛者查看结果
        if self.test_data["registration_ids"]:
            first_reg = self.test_data["registration_ids"][0]
            self.test_participant_view_results(first_reg["id"], first_reg["institutionId"])
        
        # 14. 面谈阶段（仅进阶组）
        self.log("=" * 60)
        self.log("步骤14: 进入面谈阶段（仅进阶组）")
        if not self.test_set_competition_stage("INTERVIEW"):
            return False
        
        # 15. 自动分配面谈任务（仅进阶组）
        self.log("步骤15: 自动分配面谈任务")
        self.test_auto_assign_reviews("INTERVIEW")
        
        # 16. 决赛阶段
        self.log("=" * 60)
        self.log("步骤16: 进入决赛阶段")
        if not self.test_set_competition_stage("FINAL"):
            return False
        
        # 17. 自动分配决赛任务
        self.log("步骤17: 自动分配决赛任务")
        self.test_auto_assign_reviews("FINAL")
        
        # 18. 最终排名
        self.log("=" * 60)
        self.log("步骤18: 查看最终排名")
        self.test_admin_view_rankings("FINAL")
        
        self.log("=" * 80)
        self.log("[OK] 端到端全流程测试完成")
        self.log("=" * 80)
        
        return True
    
    def save_results(self):
        """保存测试结果"""
        output_file = "data/exports/e2e_full_flow_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "test_data": self.test_data,
                "results": self.results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存到: {output_file}")

if __name__ == "__main__":
    tester = APITester()
    try:
        tester.run_full_flow()
    except Exception as e:
        print(f"测试过程发生异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.save_results()
