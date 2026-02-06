# 接口自测记录

## 环境
- 数据库：腾讯云 MySQL 8.0
- 库名：d_hos_pinguan_traegj_20260205
- 服务端口：6031

## 数据准备
执行脚本：
- scripts/seed_and_test.py
- scripts/seed_competition_23.py

结果摘要：
- institutions=33
- registrations=47
- review_tasks=109
- user_accounts=61
- dictionary_items=104
- 创建结构一致的测试库：d_hos_pinguan_traegj_20260205-2、d_hos_pinguan_traegj_20260205-3
- competitionId=23 报名数=20，分布在 BASIC/COMPREHENSIVE/ADVANCED 与 A1/A2/B1/B2

## 角色流程自测
输出文件：
- data/exports/e2e_api_output.json

关键步骤与响应示例：

### 报名创建
POST /api/registrations

```json
{ "competitionId": 21, "institutionId": 1, "applicantId": 100, "projectName": "流程项目-进阶组", "groupType": "ADVANCED" }
```

响应节选
```json
{ "success": true, "data": { "id": 50, "status": "DRAFT" } }
```

### 报名提交与退回
POST /api/registrations/50/submit  
POST /api/registrations/50/return  
POST /api/registrations/50/submit  
POST /api/registrations/50/approve

响应节选
```json
{ "success": true, "data": { "id": 50, "status": "APPROVED" } }
```

### 分组
POST /api/admin/registrations/batch-classify

```json
{ "registrationIds": [50], "groupCode": "B1" }
```

### 评审分配与评分
POST /api/admin/reviews/tasks

```json
{ "registrationId": 50, "reviewerId": 61, "stage": "BOOK" }
```

PUT /api/reviews/tasks/status
```json
{ "reviewTaskId": 112, "status": "CONFIRMED" }
```

POST /api/reviews/scores
```json
{
  "reviewTaskId": 112,
  "plan": 20,
  "problem": 20,
  "action": 20,
  "success": 15,
  "review": 10,
  "operation": 10,
  "presentation": 5,
  "highlight": "结构清晰",
  "weakness": "细节可加强"
}
```

## 补充接口说明
- 登录返回新增 institutionName/institutionCode/institutionUscc
- 机构与字典 CRUD、评委管理接口未在此文档中做逐条自测

### 参赛者查看结果
GET /api/registrations/50/review-details

响应节选
```json
{
  "success": true,
  "data": [
    {
      "stage": "BOOK",
      "taskCount": 1,
      "scoredCount": 1,
      "avgTotal": 100.0,
      "highlights": ["结构清晰"],
      "weaknesses": ["细节可加强"]
    }
  ]
}
```

### 退回评分与重评
POST /api/admin/reviews/scores/return
```json
{ "reviewTaskId": 112 }
```

POST /api/reviews/scores
```json
{
  "reviewTaskId": 112,
  "plan": 18,
  "problem": 18,
  "action": 18,
  "success": 14,
  "review": 9,
  "operation": 9,
  "presentation": 4,
  "highlight": "数据扎实",
  "weakness": "表达可提升"
}
```
