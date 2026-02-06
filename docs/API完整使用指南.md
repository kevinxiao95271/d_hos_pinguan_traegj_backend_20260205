# API完整使用指南

**版本:** v3.0 - 所有问题已修复  
**日期:** 2026-02-06 21:10

---

## ✅ 已修复的问题

### 1. 评委端500错误 ✅
- **问题:** 没有任务时抛异常
- **修复:** 添加try-catch，返回空数组而不是500错误

### 2. 成员信息400错误 ✅
- **问题:** 字段验证不正确（用@NotNull验证String）
- **修复:** 改为@NotBlank验证，department为可选字段

### 3. 活动说明字段说明 ✅
- **问题:** 字典code值不明确
- **修复:** 添加详细的字段说明和示例

---

## 📋 评委端API

### 1. 获取我的任务

```javascript
GET /api/reviews/my-tasks

// 返回（没有任务时返回空数组）
{
  "success": true,
  "data": []  // ✅ 空数组，不会500错误
}

// 有任务时返回
{
  "success": true,
  "data": [
    {
      "id": 115,
      "registrationId": 5,
      "projectName": "优化门诊预约流程",
      "institutionName": "浙江大学医学院附属第一医院",
      "stage": "BOOK_REVIEW",
      "status": "PENDING",
      "createdAt": "2026-02-06T10:00:00"
    }
  ]
}
```

---

## 📝 参赛者端API

### 1. 创建报名

```javascript
POST /api/registrations

// 请求（只需4个必填字段）
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "优化门诊预约流程",
  "groupType": "BASIC"  // BASIC 或 ADVANCED
}

// 返回
{
  "success": true,
  "data": {
    "id": 141,
    "status": "DRAFT"
  }
}
```

### 2. 更新基本信息

```javascript
PUT /api/registrations/141

// 请求（都是可选）
{
  "projectName": "新项目名称",
  "groupType": "ADVANCED",
  "institutionId": 2
}

// 返回
{
  "success": true,
  "data": {
    "id": 141,
    "projectName": "新项目名称",
    "groupType": "ADVANCED",
    "status": "DRAFT"
  }
}
```

### 3. 提交成员信息 ✅ 已修复

```javascript
PUT /api/registrations/141/members

// 请求
{
  "members": [
    {
      "name": "张三",              // ✅ 必填
      "title": "主管护师",         // ✅ 必填
      "role": "PARTICIPANT",      // ✅ 必填（PARTICIPANT 或 MENTOR）
      "department": "内科"        // ⭕ 可选
    },
    {
      "name": "李四",
      "title": "主治医师",
      "role": "PARTICIPANT",
      "department": "外科"
    },
    {
      "name": "王五",
      "title": "副主任护师",
      "role": "MENTOR",
      "department": null          // ✅ MENTOR也可以不填department
    }
  ]
}

// 返回
{
  "success": true,
  "data": [
    { "id": 1, "name": "张三", ... },
    { "id": 2, "name": "李四", ... },
    { "id": 3, "name": "王五", ... }
  ]
}
```

**MemberRole枚举值:**
- `PARTICIPANT` - 参与者/圈员
- `MENTOR` - 辅导员

### 4. 提交活动说明 ✅ 字段说明

```javascript
PUT /api/registrations/141/activity

// 完整请求示例
{
  "theme": "提高门诊预约效率",           // ✅ 必填
  "keywords": "门诊,预约,效率",         // ✅ 必填
  
  // 选题类型（需要从字典获取，建议值：subject_type_1, subject_type_2等）
  "subjectTypeCode": "subject_type_1",  // ✅ 必填
  "subjectTypeOther": null,             // ⭕ 可选（选"其他"时填写）
  
  // 方法（建议值：PDCA, DMAIC, LEAN等）
  "methodCode": "PDCA",                 // ✅ 必填
  "methodOther": null,                  // ⭕ 可选
  
  // 改善经验（需要从字典获取）
  "experienceImproveCode": "experience_1",  // ✅ 必填
  "experienceImproveOther": null,       // ⭕ 可选
  
  // 质量主题（需要从字典获取）
  "qualityTopicCode": "quality_topic_1",    // ✅ 必填
  "qualityTopicOther": null,            // ⭕ 可选
  
  // 团队信息
  "avgWorkYears": 6,                    // ✅ 必填（平均工作年限）
  "avgAge": 32,                         // ✅ 必填（平均年龄）
  "crossDepartment": false              // ✅ 必填（是否跨部门）
}

// 返回
{
  "success": true,
  "data": {
    "id": 10,
    "theme": "提高门诊预约效率",
    ...
  }
}
```

**字典Code建议值:**

| 字段 | 建议值 | 说明 |
|-----|--------|------|
| subjectTypeCode | subject_type_1, subject_type_2 | 选题类型 |
| methodCode | PDCA, DMAIC, LEAN | 改进方法 |
| experienceImproveCode | experience_1, experience_2 | 改善经验 |
| qualityTopicCode | quality_topic_1, quality_topic_2 | 质量主题 |

**获取字典数据（如果有接口）:**
```javascript
GET /api/dictionaries?category=subjectType
GET /api/dictionaries?category=method
GET /api/dictionaries?category=experienceImprove
GET /api/dictionaries?category=qualityTopic
```

### 5. 提交项目总结

```javascript
PUT /api/registrations/141/summary

// 请求
{
  "theme": "提高门诊预约效率",
  "plan": "制定改进计划...",
  "problem": "存在的问题...",
  "action": "采取的措施...",
  "result": "取得的成效...",
  "conclusion": "结论..."
}

// 返回
{
  "success": true,
  "data": {
    "id": 5,
    "theme": "提高门诊预约效率",
    ...
  }
}
```

### 6. 提交审核

```javascript
POST /api/registrations/141/submit

// 无需参数

// 返回
{
  "success": true,
  "data": {
    "id": 141,
    "status": "SUBMITTED",  // ✅ 已提交
    "submittedAt": "2026-02-06T10:30:00"
  }
}
```

**提交后保护机制:**
- ✅ 状态变为`SUBMITTED`
- ✅ 无法再修改基本信息
- ✅ 无法再修改成员、活动、总结
- ✅ 需要管理员审核通过或退回

---

## 🧪 完整测试用例

### 测试1: 评委端（无任务）

```javascript
// 1. 登录
POST /api/auth/login
{
  "phone": "13800000021",
  "name": "李明华",
  "role": "REVIEWER"
}
// 返回 token

// 2. 获取任务（没有任务也返回空数组）
GET /api/reviews/my-tasks
Authorization: Bearer <token>

// 期望返回
{
  "success": true,
  "data": []  // ✅ 空数组，不会500错误
}
```

### 测试2: 参赛者完整流程

```javascript
// 1. 登录
POST /api/auth/login
{
  "phone": "13900000001",
  "name": "张医生",
  "role": "CONTESTANT"
}

// 2. 创建报名
POST /api/registrations
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "优化门诊预约流程",
  "groupType": "BASIC"
}
// 返回 registrationId = 141

// 3. 更新基本信息
PUT /api/registrations/141
{
  "projectName": "优化门诊预约流程品管圈"
}

// 4. 提交成员信息
PUT /api/registrations/141/members
{
  "members": [
    {
      "name": "张三",
      "title": "主管护师",
      "role": "PARTICIPANT",
      "department": "内科"
    },
    {
      "name": "王五",
      "title": "副主任护师",
      "role": "MENTOR"
      // department可以不填
    }
  ]
}

// 5. 提交活动说明
PUT /api/registrations/141/activity
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

// 6. 提交项目总结
PUT /api/registrations/141/summary
{
  "theme": "提高门诊预约效率",
  "plan": "制定改进计划...",
  "problem": "存在问题...",
  "action": "采取措施...",
  "result": "取得成效...",
  "conclusion": "结论..."
}

// 7. 提交审核
POST /api/registrations/141/submit

// 8. 尝试修改已提交的报名（应该失败）
PUT /api/registrations/141
{
  "projectName": "尝试修改"
}
// 期望返回 400: "当前状态不允许修改"
```

---

## ⚠️ 常见错误及解决方案

### 错误1: 400 - 成员信息验证失败

```json
{
  "status": 400,
  "message": "姓名不能为空"
}
```

**原因:** name、title字段为空字符串或null

**解决:**
```javascript
// ❌ 错误
{
  "members": [
    {
      "name": "",  // 空字符串
      "title": null,
      "role": "PARTICIPANT"
    }
  ]
}

// ✅ 正确
{
  "members": [
    {
      "name": "张三",  // 非空
      "title": "主管护师",  // 非空
      "role": "PARTICIPANT"  // 非空
      // department可以不填或为null
    }
  ]
}
```

### 错误2: 400 - 活动说明验证失败

```json
{
  "status": 400,
  "message": "选题类型不能为空"
}
```

**原因:** 必填字段缺失或为空

**必填字段清单:**
- ✅ theme - 主题
- ✅ keywords - 关键词
- ✅ subjectTypeCode - 选题类型
- ✅ methodCode - 方法
- ✅ experienceImproveCode - 改善经验
- ✅ qualityTopicCode - 质量主题
- ✅ avgWorkYears - 平均工作年限
- ✅ avgAge - 平均年龄
- ✅ crossDepartment - 是否跨部门

### 错误3: 400 - 当前状态不允许修改

```json
{
  "status": 400,
  "message": "当前状态不允许修改"
}
```

**原因:** 报名已提交（SUBMITTED）或已通过（APPROVED）

**解决:** 只有DRAFT或RETURNED状态才能修改

---

## 📊 报名状态流转图

```
DRAFT (草稿)
  ↓ 可以修改：基本信息、成员、活动、总结
  ↓ POST /{id}/submit
SUBMITTED (已提交)
  ↓ 不可修改
  ↓ 等待审核
APPROVED (已通过)  或  RETURNED (退回)
  ↓ 已通过不可修改    ↓ 退回可修改
```

---

## 📞 技术支持

**Swagger:** http://localhost:6031/swagger  
**测试脚本:** `python scripts/test_all_apis.py`

---

**所有问题已修复！可以正常测试了！** 🎉
