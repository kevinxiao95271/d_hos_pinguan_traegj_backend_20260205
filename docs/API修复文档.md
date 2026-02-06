# API修复文档

**日期:** 2026-02-06  
**修复人:** Backend Team

---

## ✅ 已修复的API

### 1. 评委端 - 我的任务列表

**之前（有问题）:**
```
GET /api/reviews/tasks?reviewerId=xxx
```
❌ 问题：需要手动传reviewerId，前端不知道当前评委的ID

**现在（已修复）:**
```
GET /api/reviews/my-tasks
```
✅ 修复：自动从JWT token中获取当前登录评委的ID

**测试示例:**
```bash
# 1. 评委登录
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000021","name":"李明华","role":"REVIEWER"}'

# 2. 获取我的任务（使用返回的token）
curl -X GET http://localhost:6031/api/reviews/my-tasks \
  -H "Authorization: Bearer <token>"
```

**返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "registrationId": 5,
      "projectName": "优化门诊预约流程",
      "institutionName": "浙江大学医学院附属第一医院",
      "stage": "BOOK_REVIEW",
      "status": "PENDING",
      "assignedAt": "2026-02-06T10:00:00"
    }
  ]
}
```

---

### 2. 参赛者端 - 我的报名列表

**之前（有问题）:**
```
GET /api/registrations/by-applicant?applicantId=xxx
```
❌ 问题：需要手动传applicantId，前端不知道当前参赛者的ID

**现在（已修复）:**
```
GET /api/registrations/my
```
✅ 修复：自动从JWT token中获取当前登录参赛者的ID

**测试示例:**
```bash
# 1. 参赛者登录
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","name":"张医生","role":"CONTESTANT"}'

# 2. 获取我的报名（使用返回的token）
curl -X GET http://localhost:6031/api/registrations/my \
  -H "Authorization: Bearer <token>"
```

**返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "competitionId": 21,
      "competitionName": "2026浙江品管大赛",
      "institutionId": 1,
      "institutionName": "浙江大学医学院附属第一医院",
      "projectName": "优化门诊预约流程品管圈",
      "projectType": "医疗类",
      "status": "DRAFT",
      "createdAt": "2026-02-06T09:00:00",
      "submittedAt": null
    }
  ]
}
```

---

## 📋 完整的报名API流程

### 步骤1: 创建报名（草稿）

```bash
POST /api/registrations
```

**请求参数:**
```json
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "优化门诊预约流程品管圈",
  "projectType": "医疗类",
  "contactName": "张医生",
  "contactPhone": "13900000001",
  "contactEmail": "zhang@hospital.com"
}
```

**返回:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "status": "DRAFT",
    "createdAt": "2026-02-06T10:00:00"
  }
}
```

### 步骤2: 提交成员信息

```bash
PUT /api/registrations/{id}/members
```

**请求参数:**
```json
{
  "members": [
    {
      "name": "张医生",
      "title": "主治医师",
      "role": "LEADER",
      "phone": "13900000001"
    },
    {
      "name": "李护士",
      "title": "护师",
      "role": "MEMBER",
      "phone": "13900000002"
    }
  ]
}
```

### 步骤3: 提交活动说明

```bash
PUT /api/registrations/{id}/activity
```

**请求参数:**
```json
{
  "background": "门诊预约效率低下，患者等待时间长...",
  "objective": "将平均预约等待时间从30分钟缩短至10分钟...",
  "process": "1.现状调查 2.原因分析 3.制定对策...",
  "result": "预约等待时间缩短67%，患者满意度提升至95%...",
  "innovation": "引入智能预约算法，实现动态调度..."
}
```

### 步骤4: 提交项目总结

```bash
PUT /api/registrations/{id}/summary
```

**请求参数:**
```json
{
  "summary": "本项目通过优化预约流程，显著提升了门诊效率...",
  "impact": "年节省患者等待时间超过10000小时...",
  "sustainability": "建立了长效机制，确保改进持续有效..."
}
```

### 步骤5: 上传材料

```bash
POST /api/registrations/{id}/materials
```

**请求参数（multipart/form-data）:**
```
type: "PROJECT_PLAN"
file: <file binary>
```

**材料类型:**
- `PROJECT_PLAN` - 项目计划书
- `DATA_ANALYSIS` - 数据分析报告
- `RESULT_PROOF` - 成果证明材料
- `OTHER` - 其他材料

### 步骤6: 提交报名

```bash
POST /api/registrations/{id}/submit
```

**返回:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "status": "PENDING_REVIEW",
    "submittedAt": "2026-02-06T11:00:00"
  }
}
```

**状态说明:**
- `DRAFT` - 草稿（可编辑）
- `PENDING_REVIEW` - 待审核（已提交，不可编辑）
- `APPROVED` - 已通过
- `REJECTED` - 已驳回（可重新编辑）

---

## 📊 评审打分API

### 提交评分

```bash
POST /api/reviews/scores
```

**请求参数:**
```json
{
  "reviewTaskId": 101,
  "scores": {
    "theme": 90,           // 主题选择 (0-100)
    "process": 85,         // 活动过程 (0-100)
    "method": 88,          // 改进方法 (0-100)
    "result": 92,          // 成果效果 (0-100)
    "innovation": 87       // 创新性 (0-100)
  },
  "comments": "项目主题明确，改进措施得当，成效显著。",
  "suggestions": "建议进一步量化成本效益分析。"
}
```

**返回:**
```json
{
  "success": true,
  "data": {
    "id": 201,
    "reviewTaskId": 101,
    "totalScore": 88.4,
    "submittedAt": "2026-02-06T14:00:00"
  }
}
```

### 查看评分详情

```bash
GET /api/reviews/scores/{reviewTaskId}
```

---

## 🔍 查询API

### 1. 查看报名详情

```bash
GET /api/registrations/{id}
```

**返回完整信息:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "competition": { ... },
    "institution": { ... },
    "projectName": "...",
    "members": [ ... ],
    "activity": { ... },
    "summary": { ... },
    "materials": [ ... ],
    "status": "PENDING_REVIEW"
  }
}
```

### 2. 查看报名的评审结果

```bash
GET /api/registrations/{id}/review-results
```

**返回:**
```json
{
  "success": true,
  "data": [
    {
      "stage": "BOOK_REVIEW",
      "reviewerName": "李明华",
      "totalScore": 88.4,
      "comments": "项目主题明确...",
      "submittedAt": "2026-02-06T14:00:00"
    }
  ]
}
```

### 3. 查看评审汇总（组委会）

```bash
GET /api/admin/reviews/summary?competitionId=21&stage=BOOK_REVIEW
```

### 4. 查看评审排名（组委会）

```bash
GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK_REVIEW
```

---

## 🎯 前端对接指南

### 评委端页面

**1. 任务列表页**
```javascript
// 获取我的任务
const response = await fetch('/api/reviews/my-tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: tasks } = await response.json();

// 渲染任务列表
tasks.forEach(task => {
  console.log(`${task.projectName} - ${task.status}`);
});
```

**2. 评审打分页**
```javascript
// 提交评分
const response = await fetch('/api/reviews/scores', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    reviewTaskId: taskId,
    scores: {
      theme: 90,
      process: 85,
      method: 88,
      result: 92,
      innovation: 87
    },
    comments: '...',
    suggestions: '...'
  })
});
```

### 参赛者端页面

**1. 我的报名列表**
```javascript
// 获取我的报名
const response = await fetch('/api/registrations/my', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: registrations } = await response.json();
```

**2. 创建报名**
```javascript
// 创建报名（草稿）
const response = await fetch('/api/registrations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    competitionId: 21,
    institutionId: 1,
    projectName: '...',
    projectType: '医疗类',
    contactName: '...',
    contactPhone: '...',
    contactEmail: '...'
  })
});

const { data: registration } = await response.json();
const registrationId = registration.id;

// 保存成员信息
await fetch(`/api/registrations/${registrationId}/members`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ members: [...] })
});

// 保存活动说明
await fetch(`/api/registrations/${registrationId}/activity`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ background: '...', objective: '...', ... })
});

// 提交报名
await fetch(`/api/registrations/${registrationId}/submit`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 📝 测试账号

### 评委账号（16个）

| 手机号 | 姓名 | 职称 | 专家背景 |
|--------|------|------|---------|
| 13800000002 | 王建国 | 主任医师 | 医疗 |
| 13800000021 | 李明华 | 主任医师 | 医疗 |
| 13800000022 | 张秀英 | 护理部主任 | 护理 |
| 13800002001 | 陈卫东 | 副主任医师 | 医疗 |
| ... | ... | ... | ... |

### 参赛者账号（测试用）

| 手机号 | 姓名 | 说明 |
|--------|------|------|
| 任意11位 | 任意姓名 | 登录时自动创建 |

### 组委会账号

| 手机号 | 姓名 | 角色 |
|--------|------|------|
| 13800000009 | 组委会 | COMMITTEE |

---

## ⚠️ 注意事项

1. **所有接口都需要JWT token认证**（除了登录接口）
2. **token放在Header中:** `Authorization: Bearer <token>`
3. **报名状态流转:**
   - DRAFT → PENDING_REVIEW → APPROVED/REJECTED
   - REJECTED可退回DRAFT重新编辑
4. **评分维度可配置**，示例中的5个维度仅供参考
5. **文件上传使用multipart/form-data**

---

## 🚀 快速测试

```bash
# 运行测试脚本
python scripts/test_fixed_apis.py
```

---

**文档结束**

如有疑问，请联系后端开发团队。
