# 前端开发指引

## 基本信息
- 服务地址：http://localhost:6031
- 鉴权方式：Authorization: Bearer <token>
- 返回结构：{ success: boolean, data: any, message: string | null }

## 近期改动点
- 登录返回新增 expertBackground
- 登录返回新增 institutionName/institutionCode/institutionUscc
- 报名结果新增评审详情接口 /api/registrations/{id}/review-details
- 管理端新增退回评分接口 /api/admin/reviews/scores/return
- 管理端新增报名筛选接口 /api/admin/registrations/filter（支持 methodCode、subjectTypeCode 过滤）
- 评审自动分配加入专家背景约束与进阶组面谈限制
- 机构与字典管理补齐 CRUD
- 新增评委管理接口 /api/admin/reviewers

## 登录
POST /api/auth/login

请求示例
```json
{
  "phone": "13800000009",
  "name": "Committee",
  "title": "Title",
  "role": "COMMITTEE",
  "institutionId": null,
  "reviewerGroupCode": "A1",
  "interviewGroupCode": "A1",
  "expertBackground": "MEDICAL"
}
```

返回 data 字段示例
```json
{
  "id": 1,
  "phone": "13800000009",
  "name": "Committee",
  "title": "Title",
  "role": "COMMITTEE",
  "institutionId": null,
  "institutionName": null,
  "institutionCode": null,
  "institutionUscc": null,
  "expertBackground": "MEDICAL",
  "token": "jwt..."
}
```

## 机构与维护
- GET /api/institutions
- GET /api/institutions/{id}
- POST /api/institutions
- PUT /api/institutions/{id}
- DELETE /api/institutions/{id}
- POST /api/institutions/import
- POST /api/institution-updates
- POST /api/institution-updates/review
- GET /api/institution-updates/pending
机构字段新增：
- region（地区）

## 字典
用于报名活动说明的下拉配置，后台维护后可立即生效。
- GET /api/dictionaries/subject_type
- GET /api/dictionaries/method
- GET /api/dictionaries/experience_improve
- GET /api/dictionaries/quality_topic
- GET /api/dictionaries
- POST /api/dictionaries
- PUT /api/dictionaries/{id}
- DELETE /api/dictionaries/{id}

## 活动说明模板
- POST /api/activity-templates
- GET /api/activity-templates?type=quality_topic
- GET /api/activity-templates/{id}/download
- DELETE /api/activity-templates/{id}

## 赛事与资料模板
- GET /api/competitions
- POST /api/competitions
- GET /api/competitions/{id}
- PUT /api/competitions/{id}/stage
- POST /api/competitions/{id}/templates
- GET /api/competitions/{id}/templates
- GET /api/competitions/{id}/templates/{templateId}/download
- DELETE /api/competitions/{id}/templates/{templateId}

## 参赛者报名
### 创建报名
POST /api/registrations

```json
{
  "competitionId": 21,
  "institutionId": 1,
  "applicantId": 100,
  "projectName": "项目-某医院",
  "groupType": "BASIC"
}
```

### 报名表成员信息
PUT /api/registrations/{id}/members

```json
{
  "items": [
    { "role": "PARTICIPANT", "name": "成员A", "title": "护士", "department": "科室A" },
    { "role": "MENTOR", "name": "辅导员A", "title": "主任", "department": "医务处" }
  ]
}
```

### 活动说明
PUT /api/registrations/{id}/activity

```json
{
  "theme": "主题",
  "keywords": "关键词1,关键词2",
  "subjectTypeCode": "patient_care",
  "subjectTypeOther": null,
  "methodCode": "qc_problem",
  "methodOther": null,
  "experienceImproveCode": "appointment",
  "experienceImproveOther": null,
  "qualityTopicCode": "stemi",
  "qualityTopicOther": null,
  "avgWorkYears": 6,
  "avgAge": 32,
  "crossDepartment": false
}
```

### 参赛项目摘要
PUT /api/registrations/{id}/summary

```json
{
  "theme": "摘要主题",
  "plan": "计划",
  "problem": "问题结构与对策措施探讨",
  "action": "对策行动过程",
  "success": "成功表现",
  "discussion": "讨论总结"
}
```

### 提交材料
POST /api/registrations/{id}/materials?type=report
FormData: file

### 报名提交与回退
- POST /api/registrations/{id}/submit
- POST /api/registrations/{id}/return
- POST /api/registrations/{id}/approve

回退限制：报名截止后或已评分时不可回退。

## 参赛者查看
- GET /api/registrations/by-applicant?applicantId=xx
- GET /api/registrations/{id}
- GET /api/registrations/{id}/review-results
- GET /api/registrations/{id}/review-details

review-details 返回每阶段分项均分与亮点/不足集合，可用于书审/面谈/决赛结果页。

## 评审
- GET /api/reviews/tasks?reviewerId=xx
- PUT /api/reviews/tasks/status
- POST /api/reviews/scores
- GET /api/reviews/scores/{reviewTaskId}
- GET /api/reviews/summary?competitionId=xx&stage=BOOK
- GET /api/reviews/rankings?competitionId=xx&stage=BOOK

## 管理端报名与分组
- POST /api/admin/registrations/batch-classify
- POST /api/admin/registrations/auto-group
- GET /api/admin/registrations/filter?competitionId=xx&groupType=BASIC&groupCode=A1&projectName=项目&institutionName=医院&methodCode=qc_problem&subjectTypeCode=patient_care
- GET /api/admin/registrations/interview-groups?competitionId=xx
- GET /api/admin/registrations/final-groups?competitionId=xx

## 管理端项目列表与操作指引
### 项目列表数据来源
推荐使用：
GET /api/admin/registrations/filter?competitionId=xx&groupType=...&groupCode=...&projectName=...&institutionName=...&methodCode=...&subjectTypeCode=...
请求头：
- Authorization: Bearer <token>

返回字段映射：
- registrationId → 项目编号
- projectName → 项目名称
- institutionName → 医疗机构名称
- groupType → 竞赛组别
- groupCode → 分组
- submittedAt → 报名时间
- applicantName → 报名人
- subjectTypeCode → 主题类型 code
- methodCode → 品管工具 code
- subjectTypeLabel → 主题类型名称
- methodLabel → 品管工具名称

### 下拉筛选（主题类型/品管工具）
1. 主题类型下拉：GET /api/dictionaries/subject_type
2. 品管工具下拉：GET /api/dictionaries/method
3. 列表筛选：GET /api/admin/registrations/filter?competitionId=xx&subjectTypeCode=xxx&methodCode=yyy
4. 展示名称：优先使用 subjectTypeLabel/methodLabel，无需二次查询

### 详情按钮
GET /api/registrations/{id}
- 返回报名表详情（成员/活动说明/摘要/材料）

详情页展示机构与报名人建议：
- 医疗机构名称：列表页已有 institutionName，可直接透传或按 institutionId 调 GET /api/institutions/{id}
- 报名人信息：列表页已有 applicantName；详情页可用 registrations/{id} 的 applicantId 再拉用户详情（如需）

详情页展示辅导员与参与人员：
- GET /api/registrations/{id} 返回 members 列表
- role=MENTOR 为辅导员，role=PARTICIPANT 为项目参与人员

详情页活动信息补充：
- activityInfo.methodLabel 为品管工具中文名称
- activityInfo.subjectTypeLabel 为主题类型中文名称

### 变更分组按钮
POST /api/admin/registrations/batch-classify
```json
{ "registrationIds": [101,102], "groupCode": "A2" }
```

### 乱码排查建议
- 统一使用 UTF-8/UTF-8MB4 显示与字体
- 列表接口优先使用 filter 接口返回的 institutionName

## 管理端评审
- POST /api/admin/reviews/tasks
- POST /api/admin/reviews/auto-assign
- GET /api/admin/reviews/summary?competitionId=xx&stage=BOOK
- GET /api/admin/reviews/rankings?competitionId=xx&stage=BOOK
- GET /api/admin/reviews/shortlist?competitionId=xx&stage=BOOK&limit=10&minAvgTotal=0
- GET /api/admin/reviews/feedback?competitionId=xx&stage=BOOK
- POST /api/admin/reviews/scores/return

## 评委管理
- GET /api/admin/reviewers?institutionId=xx&reviewerGroupCode=A1&interviewGroupCode=B1&expertBackground=MEDICAL
- GET /api/admin/reviewers/{id}
- POST /api/admin/reviewers
- PUT /api/admin/reviewers/{id}
- DELETE /api/admin/reviewers/{id}

## 机构运维（OPS）
- GET /api/admin/institutions/export
- GET /api/admin/institutions/export?unknownRegionOnly=true
- POST /api/admin/institutions/import/precheck
- POST /api/admin/institutions/import/confirm
- PUT /api/admin/institutions/{id}/region?region=杭州

## 系统管理
- GET /api/admin/datasource
- POST /api/admin/datasource/switch
- POST /api/admin/settings
- GET /api/admin/settings?key=reviewerMaxLoad
- GET /api/admin/stats/summary
- 统计新增字段：regionCounts（按地区统计报名数量）
- 统计新增字段：subjectTypeCounts（按主题类型统计报名数量）

## 赛程节点与页面映射
### 参赛者
- 报名表单：registrations + members + activity + summary + materials + submit
- 我的赛事：registrations/by-applicant + registrations/{id}
- 书审/面谈/决赛结果：registrations/{id}/review-details

### 赛事管理者
- 报名管理与分组：registrations/status + admin/registrations/batch-classify + auto-group
- 评委分配：admin/reviews/tasks 或 admin/reviews/auto-assign
- 评分汇总/排名/入围：admin/reviews/summary + rankings + shortlist
- 专家意见反馈：admin/reviews/feedback
- 面谈/决赛分组：admin/registrations/interview-groups + final-groups
