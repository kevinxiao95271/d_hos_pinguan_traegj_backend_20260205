# API使用指南 - 前端必读

**版本:** v1.2 最终版  
**日期:** 2026-02-06  
**服务地址:** http://localhost:6031

---

## 🚨 重要修复说明

### 修复1: 评委端路径错误

❌ **错误:** `GET /api/reviews/tasks`  
✅ **正确:** `GET /api/reviews/my-tasks`

### 修复2: 报名创建参数简化

❌ **之前需要5个参数:**
```json
{
  "competitionId": 21,
  "institutionId": 1,
  "applicantId": 150,      // ❌ 前端不知道
  "projectName": "xxx",
  "groupType": "BASIC"
}
```

✅ **现在只需4个参数:**
```json
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "xxx",
  "groupType": "BASIC"     // applicantId自动获取
}
```

---

## 📋 评委端API（4个）

### 1. 我的任务列表

```javascript
GET /api/reviews/my-tasks

// 请求
fetch('/api/reviews/my-tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 返回
{
  "success": true,
  "data": [
    {
      "id": 101,
      "registrationId": 5,
      "projectName": "优化门诊预约流程",
      "institutionName": "浙江大学医学院附属第一医院",
      "stage": "BOOK_REVIEW",
      "status": "PENDING"
    }
  ]
}
```

### 2. 查看项目详情

```javascript
GET /api/registrations/{id}

// 请求
fetch(`/api/registrations/${registrationId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 返回完整的报名信息
{
  "success": true,
  "data": {
    "id": 5,
    "projectName": "...",
    "members": [...],
    "activity": {...},
    "summary": {...}
  }
}
```

### 3. 提交评分

```javascript
POST /api/reviews/scores

// 请求
fetch('/api/reviews/scores', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    reviewTaskId: 101,
    scores: {
      theme: 90,
      process: 85,
      method: 88,
      result: 92,
      innovation: 87
    },
    comments: "项目主题明确...",
    suggestions: "建议..."
  })
})

// 返回
{
  "success": true,
  "data": {
    "id": 201,
    "totalScore": 88.4
  }
}
```

### 4. 查看已提交评分

```javascript
GET /api/reviews/scores/{reviewTaskId}

// 返回已提交的评分详情
```

---

## 📝 参赛者端API（9个）

### 1. 我的报名列表

```javascript
GET /api/registrations/my

// 请求
fetch('/api/registrations/my', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// 返回
{
  "success": true,
  "data": [
    {
      "id": 100,
      "projectName": "优化门诊预约流程",
      "status": "DRAFT",
      "createdAt": "2026-02-06T10:00:00"
    }
  ]
}
```

### 2. 创建报名

```javascript
POST /api/registrations

// 必填参数（4个）
{
  "competitionId": 21,        // 赛事ID
  "institutionId": 1,         // 机构ID
  "projectName": "xxx",       // 项目名称（最多100字）
  "groupType": "BASIC"        // 组别："BASIC"或"ADVANCED"
}

// 请求示例
fetch('/api/registrations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    competitionId: 21,
    institutionId: 1,
    projectName: '优化门诊预约流程品管圈',
    groupType: 'BASIC'
  })
})

// 返回
{
  "success": true,
  "data": {
    "id": 100,
    "status": "DRAFT",
    "createdAt": "2026-02-06T10:00:00"
  }
}
```

### 3. 提交成员信息

```javascript
PUT /api/registrations/{id}/members

// 请求
fetch(`/api/registrations/${id}/members`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    members: [
      {
        name: "张医生",
        title: "主治医师",
        role: "LEADER",
        phone: "13900000001"
      },
      {
        name: "李护士",
        title: "护师",
        role: "MEMBER",
        phone: "13900000002"
      }
    ]
  })
})
```

### 4. 提交活动说明

```javascript
PUT /api/registrations/{id}/activity

// 必填字段
{
  "theme": "提高门诊预约效率",
  "keywords": "门诊,预约,效率",
  "subjectTypeCode": "subject_type_1",
  "methodCode": "PDCA",
  "experienceImproveCode": "experience_1",
  "qualityTopicCode": "quality_topic_1",
  "avgWorkYears": 6,
  "avgAge": 32,
  "crossDepartment": false
}
```

### 5. 提交项目总结

```javascript
PUT /api/registrations/{id}/summary

// 必填字段
{
  "background": "门诊预约效率低下...",
  "objective": "缩短预约等待时间...",
  "process": "1.现状调查 2.原因分析...",
  "result": "效率提升67%...",
  "conclusion": "项目取得显著成效..."
}
```

### 6. 上传材料

```javascript
POST /api/registrations/{id}/materials

// FormData格式
const formData = new FormData();
formData.append('type', 'PROJECT_PLAN');
formData.append('file', fileObject);

fetch(`/api/registrations/${id}/materials`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
})
```

### 7. 提交审核

```javascript
POST /api/registrations/{id}/submit

// 请求
fetch(`/api/registrations/${id}/submit`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// 返回
{
  "success": true,
  "data": {
    "id": 100,
    "status": "PENDING_REVIEW"
  }
}
```

### 8. 查看报名详情

```javascript
GET /api/registrations/{id}
```

### 9. 查看评审结果

```javascript
GET /api/registrations/{id}/review-results
```

---

## 🎯 GroupType 组别说明

| 值 | 中文 | 说明 |
|----|------|------|
| `BASIC` | 基础组 | 初次参赛或基础项目 |
| `ADVANCED` | 高级组 | 有经验的团队或复杂项目 |

**前端选择器:**
```vue
<el-radio-group v-model="form.groupType">
  <el-radio label="BASIC">基础组</el-radio>
  <el-radio label="ADVANCED">高级组</el-radio>
</el-radio-group>
```

---

## 📊 报名状态说明

| 状态 | 说明 | 可编辑 |
|------|------|--------|
| `DRAFT` | 草稿 | ✅ 是 |
| `PENDING_REVIEW` | 待审核 | ❌ 否 |
| `APPROVED` | 已通过 | ❌ 否 |
| `REJECTED` | 已驳回 | ✅ 是（退回草稿） |

---

## 🔍 获取基础数据

### 获取赛事列表

```javascript
GET /api/competitions

// 返回
{
  "success": true,
  "data": [
    {
      "id": 21,
      "name": "2026浙江品管大赛",
      "stage": "BOOK_REVIEW"
    }
  ]
}
```

### 获取机构列表

```javascript
GET /api/institutions

// 返回33个机构
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "浙江大学医学院附属第一医院",
      "code": "INS-0001"
    },
    // ... 共33个
  ]
}
```

---

## ⚠️ 错误处理

### 401 - 未登录

```javascript
if (response.status === 401) {
  localStorage.removeItem('token');
  router.push('/login');
}
```

### 400 - 参数错误

```javascript
// 检查必填参数
const errors = {
  competitionId: !form.competitionId ? '请选择赛事' : '',
  institutionId: !form.institutionId ? '请选择机构' : '',
  projectName: !form.projectName ? '请输入项目名称' : '',
  groupType: !form.groupType ? '请选择组别' : ''
};
```

### 500 - 服务器错误

```javascript
if (response.status === 500) {
  message.error('服务器错误，请稍后重试');
}
```

---

## 🔑 测试账号

### 评委账号（16个）

| 手机号 | 姓名 | 职称 |
|--------|------|------|
| 13800000002 | 王建国 | 主任医师 |
| 13800000021 | 李明华 | 主任医师 |
| 13800000022 | 张秀英 | 护理部主任 |

### 参赛者账号

任意11位手机号 + 任意姓名，首次登录自动创建

### 登录示例

```javascript
fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13800000021',
    name: '李明华',
    role: 'REVIEWER'  // 或 'CONTESTANT'
  })
})
```

---

## 📱 完整流程示例

### 评委端流程

```javascript
// 1. 登录
const loginResp = await login('13800000021', '李明华', 'REVIEWER');
const token = loginResp.data.token;

// 2. 获取任务
const tasksResp = await fetch('/api/reviews/my-tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const tasks = tasksResp.data;

// 3. 查看项目
const projectResp = await fetch(`/api/registrations/${tasks[0].registrationId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

// 4. 提交评分
await fetch('/api/reviews/scores', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    reviewTaskId: tasks[0].id,
    scores: { theme: 90, process: 85, method: 88, result: 92, innovation: 87 },
    comments: '...',
    suggestions: '...'
  })
});
```

### 参赛者端流程

```javascript
// 1. 登录
const loginResp = await login('13900000001', '张医生', 'CONTESTANT');
const token = loginResp.data.token;

// 2. 创建报名
const createResp = await fetch('/api/registrations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    competitionId: 21,
    institutionId: 1,
    projectName: '优化门诊预约流程',
    groupType: 'BASIC'
  })
});
const registrationId = createResp.data.id;

// 3. 提交成员
await fetch(`/api/registrations/${registrationId}/members`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    members: [...]
  })
});

// 4. 提交活动说明
await fetch(`/api/registrations/${registrationId}/activity`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({...})
});

// 5. 提交总结
await fetch(`/api/registrations/${registrationId}/summary`, {
  method: 'PUT',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({...})
});

// 6. 提交审核
await fetch(`/api/registrations/${registrationId}/submit`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 📞 技术支持

**Swagger文档:** http://localhost:6031/swagger  
**测试脚本:** `python scripts/test_registration_create.py`

---

**所有API已修复完成，请按此文档对接！** 🎉
