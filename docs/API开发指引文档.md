# 品管圈大赛后台API开发指引文档

**版本:** 1.0  
**服务地址:** `http://localhost:6031`  
**日期:** 2026-02-06

---

## 目录

1. [认证相关](#1-认证相关)
2. [机构管理](#2-机构管理)
3. [赛事管理](#3-赛事管理)
4. [报名管理](#4-报名管理)
5. [评委管理](#5-评委管理)
6. [评审管理](#6-评审管理)
7. [统计数据](#7-统计数据)
8. [系统管理](#8-系统管理)

---

## 1. 认证相关

### 1.1 用户登录/注册

**接口:** `POST /api/auth/login`  
**权限:** 无需认证  
**说明:** 用户登录或自动注册，支持多种角色

**请求参数:**
```json
{
  "phone": "13800000009",
  "name": "张三",
  "title": "组委会主任",
  "role": "COMMITTEE"
}
```

**参数说明:**
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| phone | String | 是 | 手机号（11位） |
| name | String | 是 | 用户姓名 |
| title | String | 否 | 职称/职务 |
| role | String | 是 | 角色：COMMITTEE（组委会）、REVIEWER（评委）、CONTESTANT（参赛者）、OPS（运维）、COMMITTEE_ADMIN（组委会管理员） |

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "phone": "13800000009",
    "name": "Committee",
    "title": "组委会",
    "role": "COMMITTEE",
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwicm9sZSI6IkNPTU1JVFRFRSIsImlhdCI6MTc3MDM3MzkwNywiZXhwIjoxNzcwNDE3MTA3fQ.xxx"
  },
  "message": "登录成功"
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| success | Boolean | 请求是否成功 | 判断接口调用状态 |
| data.id | Long | 用户ID | 用于关联用户数据 |
| data.phone | String | 手机号 | 用户唯一标识 |
| data.name | String | 姓名 | 显示用户信息 |
| data.title | String | 职称 | 显示用户职务 |
| data.role | String | 角色 | 权限控制，决定可访问的功能 |
| data.token | String | JWT令牌 | **重要！后续所有接口都需要在Header中携带** |

**前端使用示例:**
```javascript
// 1. 登录
const loginResponse = await fetch('http://localhost:6031/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13800000009',
    name: '张三',
    title: '组委会主任',
    role: 'COMMITTEE'
  })
});
const loginData = await loginResponse.json();

// 2. 保存token到localStorage
localStorage.setItem('token', loginData.data.token);
localStorage.setItem('userInfo', JSON.stringify(loginData.data));

// 3. 后续请求都需要携带token
const headers = {
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
};
```

---

## 2. 机构管理

### 2.1 获取机构列表

**接口:** `GET /api/institutions`  
**权限:** 需要登录  
**说明:** 获取所有机构列表，用于报名时选择机构

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/institutions
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "330100001",
      "name": "浙江大学医学院附属第一医院",
      "address": "杭州市庆春路79号",
      "creditCode": "12330000470000123X"
    },
    {
      "id": 2,
      "code": "330100002",
      "name": "浙江大学医学院附属第二医院",
      "address": "杭州市解放路88号",
      "creditCode": "12330000470000124Y"
    }
    // ... 共33个机构
  ],
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| id | Long | 机构ID | 报名时需要传此ID |
| code | String | 机构编号 | 显示用，唯一标识 |
| name | String | 机构名称 | 显示用，选择器展示 |
| address | String | 地址 | 显示用 |
| creditCode | String | 统一社会信用代码 | 机构认证标识 |

**前端使用示例:**
```javascript
// 获取机构列表用于下拉选择
const response = await fetch('http://localhost:6031/api/institutions', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: institutions } = await response.json();

// 渲染为选择器
<Select>
  {institutions.map(inst => (
    <Option key={inst.id} value={inst.id}>
      {inst.name}
    </Option>
  ))}
</Select>
```

---

## 3. 赛事管理

### 3.1 获取赛事列表

**接口:** `GET /api/competitions`  
**权限:** 需要登录  
**说明:** 获取所有赛事，支持按状态筛选

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| stage | String | 否 | 赛事阶段：REGISTER（报名）、REVIEW（初审）、INTERVIEW（终审）、FINISHED（已结束） |

**请求示例:**
```bash
# 获取所有赛事
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/competitions

# 获取报名阶段的赛事
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/competitions?stage=REGISTER"
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "2024年浙江省医院品管圈大赛",
      "description": "提升医疗质量，推动持续改进",
      "stage": "REGISTER",
      "startDate": "2024-01-01 00:00:00",
      "endDate": "2024-12-31 23:59:59",
      "createdAt": "2024-01-01 10:00:00"
    }
  ],
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| id | Long | 赛事ID | 报名时必须指定赛事ID |
| name | String | 赛事名称 | 显示在页面标题和选择器中 |
| description | String | 赛事描述 | 显示赛事简介 |
| stage | String | 赛事阶段 | **关键字段**：控制页面功能展示<br>- REGISTER: 可报名<br>- REVIEW: 评委初审<br>- INTERVIEW: 评委终审<br>- FINISHED: 已结束 |
| startDate | String | 开始时间 | 显示赛事时间范围 |
| endDate | String | 结束时间 | 显示赛事时间范围 |

### 3.2 创建赛事（组委会专用）

**接口:** `POST /api/admin/competitions`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 创建新的赛事

**请求参数:**
```json
{
  "name": "2025年浙江省医院品管圈大赛",
  "description": "以患者为中心，持续改进医疗质量",
  "startDate": "2025-01-01 00:00:00",
  "endDate": "2025-12-31 23:59:59"
}
```

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "2025年浙江省医院品管圈大赛",
    "description": "以患者为中心，持续改进医疗质量",
    "stage": "REGISTER",
    "startDate": "2025-01-01 00:00:00",
    "endDate": "2025-12-31 23:59:59",
    "createdAt": "2026-02-06 18:35:00"
  },
  "message": null
}
```

### 3.3 更新赛事阶段（组委会专用）

**接口:** `PUT /api/admin/competitions/{id}/stage`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 推进赛事到下一阶段，这是赛事流程控制的核心接口

**请求参数:**
```json
{
  "stage": "REVIEW"
}
```

**阶段流转规则:**
```
REGISTER (报名) 
    ↓
REVIEW (初审) 
    ↓
INTERVIEW (终审) 
    ↓
FINISHED (已结束)
```

**请求示例:**
```bash
# 将赛事推进到初审阶段
curl -X PUT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"stage":"REVIEW"}' \
  http://localhost:6031/api/admin/competitions/1/stage
```

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "2024年浙江省医院品管圈大赛",
    "description": "提升医疗质量，推动持续改进",
    "stage": "REVIEW",
    "startDate": "2024-01-01 00:00:00",
    "endDate": "2024-12-31 23:59:59",
    "createdAt": "2024-01-01 10:00:00"
  },
  "message": null
}
```

---

## 4. 报名管理

### 4.1 提交报名（参赛者）

**接口:** `POST /api/registrations`  
**权限:** CONTESTANT  
**说明:** 参赛者提交报名信息，这是最复杂的表单

**请求参数:**
```json
{
  "competitionId": 1,
  "institutionId": 1,
  "projectName": "优化门诊预约流程品管圈",
  "contactPerson": "张医生",
  "contactPhone": "13800138000",
  "participantNames": "张医生,李护士,王技师",
  "mentorName": "陈主任",
  "mentorTitle": "主任医师",
  "activityType": "医疗类",
  "activityBackground": "门诊预约效率低下，患者等待时间长",
  "activityObjective": "将平均预约等待时间从30分钟缩短至10分钟",
  "activityProcess": "1.现状调查 2.原因分析 3.制定对策 4.实施改进 5.效果确认",
  "activityResult": "预约等待时间缩短67%，患者满意度提升至95%",
  "projectSummary": "通过优化预约流程，显著提升了门诊效率和患者满意度",
  "materialUrl": "https://example.com/materials/project1.zip"
}
```

**参数说明:**
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| competitionId | Long | 是 | 赛事ID |
| institutionId | Long | 是 | 机构ID |
| projectName | String | 是 | 项目名称（最多100字） |
| contactPerson | String | 是 | 联系人姓名 |
| contactPhone | String | 是 | 联系电话 |
| participantNames | String | 是 | 参与人员（多人用逗号分隔） |
| mentorName | String | 否 | 导师姓名 |
| mentorTitle | String | 否 | 导师职称 |
| activityType | String | 是 | 活动类型（从字典获取） |
| activityBackground | String | 是 | 活动背景（最多2000字） |
| activityObjective | String | 是 | 活动目标（最多500字） |
| activityProcess | String | 是 | 活动过程（最多2000字） |
| activityResult | String | 是 | 活动成果（最多1000字） |
| projectSummary | String | 是 | 项目总结（最多1000字） |
| materialUrl | String | 否 | 材料附件URL |

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 101,
    "competitionId": 1,
    "institutionId": 1,
    "institutionName": "浙江大学医学院附属第一医院",
    "projectName": "优化门诊预约流程品管圈",
    "contactPerson": "张医生",
    "contactPhone": "13800138000",
    "status": "PENDING",
    "submittedAt": "2026-02-06 18:40:00",
    "activityInfo": {
      "activityType": "医疗类",
      "activityBackground": "门诊预约效率低下，患者等待时间长",
      "activityObjective": "将平均预约等待时间从30分钟缩短至10分钟"
    }
  },
  "message": "报名成功"
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| id | Long | 报名ID | 后续查询和修改需要用到 |
| status | String | 审批状态 | **关键字段**：<br>- PENDING: 待审核<br>- APPROVED: 已通过<br>- REJECTED: 已驳回 |
| submittedAt | String | 提交时间 | 显示提交记录 |

### 4.2 获取我的报名列表（参赛者）

**接口:** `GET /api/registrations/my`  
**权限:** CONTESTANT  
**说明:** 查看当前用户的所有报名记录

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/registrations/my
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 5,
      "competitionId": 1,
      "institutionId": 1,
      "institutionName": "浙江大学医学院附属第一医院",
      "projectName": "护理质量持续改进",
      "contactPerson": "Contestant",
      "contactPhone": "13800000001",
      "status": "APPROVED",
      "reviewScore": 85.5,
      "submittedAt": "2024-02-01 10:00:00"
    }
  ],
  "message": null
}
```

### 4.3 获取待审核报名列表（组委会）

**接口:** `GET /api/admin/registrations`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 组委会查看所有报名，支持多条件筛选

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| competitionId | Long | 否 | 赛事ID |
| institutionId | Long | 否 | 机构ID |
| status | String | 否 | 审批状态：PENDING、APPROVED、REJECTED |

**请求示例:**
```bash
# 获取所有待审核报名
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/admin/registrations?status=PENDING"

# 获取某机构的所有报名
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/admin/registrations?institutionId=1"
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "competitionId": 1,
      "institutionId": 1,
      "institutionName": "浙江大学医学院附属第一医院",
      "projectName": "Sample Project 1",
      "contactPerson": "Contact 1",
      "contactPhone": "13800000001",
      "status": "APPROVED",
      "reviewScore": null,
      "submittedAt": "2024-01-15 10:00:00"
    }
    // ... 共33条报名记录
  ],
  "message": null
}
```

### 4.4 审批报名（组委会）

**接口:** `PUT /api/admin/registrations/{id}/status`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 审批通过或驳回报名

**请求参数:**
```json
{
  "status": "APPROVED",
  "rejectReason": ""
}
```

**参数说明:**
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| status | String | 是 | APPROVED（通过）或 REJECTED（驳回） |
| rejectReason | String | 驳回时必填 | 驳回原因，参赛者可见 |

**请求示例（通过）:**
```bash
curl -X PUT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status":"APPROVED"}' \
  http://localhost:6031/api/admin/registrations/1/status
```

**请求示例（驳回）:**
```bash
curl -X PUT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status":"REJECTED","rejectReason":"材料不完整，请补充活动数据"}' \
  http://localhost:6031/api/admin/registrations/1/status
```

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "APPROVED",
    "rejectReason": null
  },
  "message": "审批成功"
}
```

---

## 5. 评委管理

### 5.1 获取评委列表（组委会）

**接口:** `GET /api/admin/reviewers`  
**权限:** COMMITTEE、COMMITTEE_ADMIN、OPS  
**说明:** 获取评审专家池，支持多维度筛选

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| institutionId | Long | 否 | 按机构筛选 |
| reviewerGroupCode | String | 否 | 按初审分组筛选（如：A1、B1、B2） |
| interviewGroupCode | String | 否 | 按终审分组筛选 |
| expertBackground | String | 否 | 按专家背景筛选（MEDICAL、MANAGEMENT、NURSING） |

**请求示例:**
```bash
# 获取所有评委
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/admin/reviewers

# 获取医疗背景的评委
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/admin/reviewers?expertBackground=MEDICAL"

# 获取A1组的评委
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/admin/reviewers?reviewerGroupCode=A1"
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "phone": "13800000002",
      "name": "Reviewer",
      "title": "Title",
      "institutionId": 2,
      "institutionName": "浙江大学医学院附属第二医院",
      "reviewerGroupCode": null,
      "interviewGroupCode": null,
      "expertBackground": null
    },
    {
      "id": 6,
      "phone": "13800000021",
      "name": "评审专家A",
      "title": "主任医师",
      "institutionId": 2,
      "institutionName": "浙江大学医学院附属第二医院",
      "reviewerGroupCode": "A1",
      "interviewGroupCode": "A1",
      "expertBackground": "MEDICAL"
    }
    // ... 共16个评委
  ],
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|-----|------|
| id | Long | 评委ID | 分配评审任务时需要 |
| phone | String | 手机号 | 评委唯一标识 |
| name | String | 姓名 | 显示评委信息 |
| title | String | 职称 | 显示评委资质 |
| institutionId | Long | 机构ID | 避免利益冲突 |
| institutionName | String | 机构名称 | 显示评委单位 |
| reviewerGroupCode | String | 初审分组 | 按组分配任务 |
| interviewGroupCode | String | 终审分组 | 按组分配任务 |
| expertBackground | String | 专家背景 | **重要**：MEDICAL（医疗）、MANAGEMENT（管理）、NURSING（护理），用于均衡分组 |

**前端使用场景:**
```javascript
// 场景1: 展示评委池
const response = await fetch('http://localhost:6031/api/admin/reviewers', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: reviewers } = await response.json();

// 场景2: 按背景筛选评委，确保分组均衡
const medicalReviewers = await fetch(
  'http://localhost:6031/api/admin/reviewers?expertBackground=MEDICAL',
  { headers: { 'Authorization': `Bearer ${token}` } }
);

// 场景3: 获取某一组的评委
const groupA1 = await fetch(
  'http://localhost:6031/api/admin/reviewers?reviewerGroupCode=A1',
  { headers: { 'Authorization': `Bearer ${token}` } }
);
```

### 5.2 创建评委（组委会）

**接口:** `POST /api/admin/reviewers`  
**权限:** COMMITTEE、COMMITTEE_ADMIN、OPS  
**说明:** 添加新的评审专家

**请求参数:**
```json
{
  "phone": "13900000001",
  "name": "王教授",
  "title": "主任医师",
  "institutionId": 3,
  "reviewerGroupCode": "A1",
  "interviewGroupCode": "A1",
  "expertBackground": "MEDICAL"
}
```

**参数说明:**
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| phone | String | 是 | 手机号（唯一） |
| name | String | 是 | 姓名 |
| title | String | 否 | 职称 |
| institutionId | Long | 否 | 所属机构ID |
| reviewerGroupCode | String | 否 | 初审分组代码 |
| interviewGroupCode | String | 否 | 终审分组代码 |
| expertBackground | String | 否 | 专家背景：MEDICAL、MANAGEMENT、NURSING |

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "phone": "13900000001",
    "name": "王教授",
    "title": "主任医师",
    "role": "REVIEWER",
    "institution": {
      "id": 3,
      "name": "浙江省人民医院"
    },
    "reviewerGroupCode": "A1",
    "interviewGroupCode": "A1",
    "expertBackground": "MEDICAL",
    "createdAt": "2026-02-06 18:50:00"
  },
  "message": null
}
```

---

## 6. 评审管理

### 6.1 获取我的评审任务（评委）

**接口:** `GET /api/reviews/my-tasks`  
**权限:** REVIEWER  
**说明:** 评委查看分配给自己的评审任务

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/reviews/my-tasks
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "registrationId": 5,
      "projectName": "护理质量持续改进",
      "institutionName": "浙江大学医学院附属第一医院",
      "reviewType": "INITIAL",
      "score": 85.5,
      "comment": "项目设计合理，数据详实，效果显著",
      "reviewedAt": "2024-03-01 14:30:00"
    },
    {
      "id": 2,
      "registrationId": 8,
      "projectName": "门诊流程优化",
      "institutionName": "浙江省人民医院",
      "reviewType": "INITIAL",
      "score": null,
      "comment": null,
      "reviewedAt": null
    }
  ],
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| id | Long | 评审记录ID | 提交评分时需要 |
| registrationId | Long | 报名ID | 查看报名详情 |
| projectName | String | 项目名称 | 显示评审对象 |
| institutionName | String | 机构名称 | 显示项目单位 |
| reviewType | String | 评审类型 | INITIAL（初审）、FINAL（终审） |
| score | Double | 评分 | null表示未评分 |
| comment | String | 评语 | 评委意见 |
| reviewedAt | String | 评审时间 | null表示未完成 |

### 6.2 提交评审评分（评委）

**接口:** `POST /api/reviews/{id}/score`  
**权限:** REVIEWER  
**说明:** 评委对分配的项目进行评分

**请求参数:**
```json
{
  "score": 88.5,
  "comment": "项目主题明确，改进措施得当，成效显著。建议进一步量化成本效益分析。"
}
```

**参数说明:**
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| score | Double | 是 | 评分（0-100） |
| comment | String | 否 | 评审意见（最多500字） |

**请求示例:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"score":88.5,"comment":"项目主题明确，改进措施得当"}' \
  http://localhost:6031/api/reviews/2/score
```

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "registrationId": 8,
    "reviewerId": 3,
    "reviewType": "INITIAL",
    "score": 88.5,
    "comment": "项目主题明确，改进措施得当",
    "reviewedAt": "2026-02-06 19:00:00"
  },
  "message": "评审提交成功"
}
```

### 6.3 分配评审任务（组委会）

**接口:** `POST /api/admin/reviews/assign`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 将报名项目分配给评委进行评审

**请求参数:**
```json
{
  "registrationId": 10,
  "reviewerId": 6,
  "reviewType": "INITIAL"
}
```

**参数说明:**
| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| registrationId | Long | 是 | 报名ID |
| reviewerId | Long | 是 | 评委ID |
| reviewType | String | 是 | INITIAL（初审）或 FINAL（终审） |

**请求示例:**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"registrationId":10,"reviewerId":6,"reviewType":"INITIAL"}' \
  http://localhost:6031/api/admin/reviews/assign
```

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "id": 50,
    "registrationId": 10,
    "reviewerId": 6,
    "reviewerName": "评审专家A",
    "reviewType": "INITIAL",
    "score": null,
    "comment": null,
    "assignedAt": "2026-02-06 19:10:00"
  },
  "message": "分配成功"
}
```

### 6.4 获取评审汇总（组委会）

**接口:** `GET /api/admin/reviews/summary`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 查看所有项目的评审进度和得分

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| competitionId | Long | 否 | 赛事ID |
| reviewType | String | 否 | INITIAL、FINAL |

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/admin/reviews/summary?competitionId=1&reviewType=INITIAL"
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "registrationId": 5,
      "projectName": "护理质量持续改进",
      "institutionName": "浙江大学医学院附属第一医院",
      "reviewCount": 3,
      "completedCount": 3,
      "averageScore": 86.7,
      "maxScore": 90.0,
      "minScore": 82.5
    },
    {
      "registrationId": 8,
      "projectName": "门诊流程优化",
      "institutionName": "浙江省人民医院",
      "reviewCount": 3,
      "completedCount": 1,
      "averageScore": 88.5,
      "maxScore": 88.5,
      "minScore": 88.5
    }
  ],
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| registrationId | Long | 报名ID | 关联报名详情 |
| projectName | String | 项目名称 | 显示 |
| institutionName | String | 机构名称 | 显示 |
| reviewCount | Integer | 分配评委数 | 显示评审进度 |
| completedCount | Integer | 已完成评审数 | 显示进度百分比 |
| averageScore | Double | 平均分 | **重要**：用于排名 |
| maxScore | Double | 最高分 | 显示 |
| minScore | Double | 最低分 | 显示 |

### 6.5 获取评审排名（组委会）

**接口:** `GET /api/admin/reviews/ranking`  
**权限:** COMMITTEE、COMMITTEE_ADMIN  
**说明:** 按平均分排序的项目列表

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/admin/reviews/ranking?competitionId=1
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "registrationId": 8,
      "projectName": "门诊流程优化",
      "institutionName": "浙江省人民医院",
      "averageScore": 88.5,
      "completedCount": 1,
      "reviewCount": 3
    },
    {
      "rank": 2,
      "registrationId": 5,
      "projectName": "护理质量持续改进",
      "institutionName": "浙江大学医学院附属第一医院",
      "averageScore": 86.7,
      "completedCount": 3,
      "reviewCount": 3
    }
  ],
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|-----|------|
| rank | Integer | 排名 | 显示名次 |
| averageScore | Double | 平均分 | 排序依据 |

---

## 7. 统计数据

### 7.1 获取统计概览（组委会/运维）

**接口:** `GET /api/admin/stats/summary`  
**权限:** COMMITTEE、COMMITTEE_ADMIN、OPS  
**说明:** 获取赛事整体数据统计

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:6031/api/admin/stats/summary
```

**真实返回数据:**
```json
{
  "success": true,
  "data": {
    "totalRegistrations": 33,
    "pendingRegistrations": 0,
    "approvedRegistrations": 33,
    "rejectedRegistrations": 0,
    "totalReviewers": 16,
    "totalInstitutions": 33,
    "averageScore": 85.5,
    "completionRate": 100.0
  },
  "message": null
}
```

**返回字段说明:**
| 字段 | 类型 | 说明 | 用途 |
|-----|------|------|------|
| totalRegistrations | Integer | 总报名数 | 显示在仪表盘 |
| pendingRegistrations | Integer | 待审核数 | 显示待办事项 |
| approvedRegistrations | Integer | 已通过数 | 显示审核进度 |
| rejectedRegistrations | Integer | 已驳回数 | 显示审核情况 |
| totalReviewers | Integer | 评委总数 | 显示专家库规模 |
| totalInstitutions | Integer | 参与机构数 | 显示覆盖范围 |
| averageScore | Double | 平均得分 | 显示整体水平 |
| completionRate | Double | 完成率 | 显示评审进度 |

---

## 8. 系统管理

### 8.1 获取数据字典

**接口:** `GET /api/dictionaries`  
**权限:** 需要登录  
**说明:** 获取活动类型等字典数据

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| type | String | 否 | 字典类型：ACTIVITY_TYPE（活动类型） |

**请求示例:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:6031/api/dictionaries?type=ACTIVITY_TYPE"
```

**真实返回数据:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "type": "ACTIVITY_TYPE",
      "code": "MEDICAL",
      "label": "医疗类",
      "sortOrder": 1
    },
    {
      "id": 2,
      "type": "ACTIVITY_TYPE",
      "code": "NURSING",
      "label": "护理类",
      "sortOrder": 2
    },
    {
      "id": 3,
      "type": "ACTIVITY_TYPE",
      "code": "MANAGEMENT",
      "label": "管理类",
      "sortOrder": 3
    }
  ],
  "message": null
}
```

**前端使用示例:**
```javascript
// 获取活动类型字典用于下拉选择
const response = await fetch(
  'http://localhost:6031/api/dictionaries?type=ACTIVITY_TYPE',
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const { data: activityTypes } = await response.json();

// 渲染为选择器
<Select>
  {activityTypes.map(item => (
    <Option key={item.code} value={item.code}>
      {item.label}
    </Option>
  ))}
</Select>
```

---

## 附录A: 完整的前端开发流程示例

### 场景1: 参赛者报名流程

```javascript
// 步骤1: 用户登录
async function login() {
  const response = await fetch('http://localhost:6031/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: '13800138000',
      name: '张医生',
      title: '主治医师',
      role: 'CONTESTANT'
    })
  });
  const data = await response.json();
  localStorage.setItem('token', data.data.token);
  return data.data;
}

// 步骤2: 获取赛事列表
async function getCompetitions() {
  const token = localStorage.getItem('token');
  const response = await fetch(
    'http://localhost:6031/api/competitions?stage=REGISTER',
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return await response.json();
}

// 步骤3: 获取机构列表
async function getInstitutions() {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:6031/api/institutions', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 步骤4: 获取活动类型字典
async function getActivityTypes() {
  const token = localStorage.getItem('token');
  const response = await fetch(
    'http://localhost:6031/api/dictionaries?type=ACTIVITY_TYPE',
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return await response.json();
}

// 步骤5: 提交报名
async function submitRegistration(formData) {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:6031/api/registrations', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  });
  return await response.json();
}

// 步骤6: 查看我的报名
async function getMyRegistrations() {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:6031/api/registrations/my', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}
```

### 场景2: 组委会审批和分配评委流程

```javascript
// 步骤1: 组委会登录
async function committeeLogin() {
  const response = await fetch('http://localhost:6031/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: '13800000009',
      name: '组委会',
      title: '组委会主任',
      role: 'COMMITTEE'
    })
  });
  const data = await response.json();
  localStorage.setItem('token', data.data.token);
  return data.data;
}

// 步骤2: 获取待审批报名列表
async function getPendingRegistrations() {
  const token = localStorage.getItem('token');
  const response = await fetch(
    'http://localhost:6031/api/admin/registrations?status=PENDING',
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return await response.json();
}

// 步骤3: 审批报名
async function approveRegistration(registrationId) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `http://localhost:6031/api/admin/registrations/${registrationId}/status`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'APPROVED' })
    }
  );
  return await response.json();
}

// 步骤4: 推进赛事到评审阶段
async function updateCompetitionStage(competitionId) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `http://localhost:6031/api/admin/competitions/${competitionId}/stage`,
    {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ stage: 'REVIEW' })
    }
  );
  return await response.json();
}

// 步骤5: 获取评委池
async function getReviewers() {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:6031/api/admin/reviewers', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 步骤6: 分配评审任务
async function assignReview(registrationId, reviewerId) {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:6031/api/admin/reviews/assign', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      registrationId: registrationId,
      reviewerId: reviewerId,
      reviewType: 'INITIAL'
    })
  });
  return await response.json();
}

// 步骤7: 查看评审进度
async function getReviewSummary(competitionId) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `http://localhost:6031/api/admin/reviews/summary?competitionId=${competitionId}&reviewType=INITIAL`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return await response.json();
}

// 步骤8: 查看排名
async function getRanking(competitionId) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `http://localhost:6031/api/admin/reviews/ranking?competitionId=${competitionId}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return await response.json();
}
```

### 场景3: 评委评审流程

```javascript
// 步骤1: 评委登录
async function reviewerLogin() {
  const response = await fetch('http://localhost:6031/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone: '13800000021',
      name: '评审专家A',
      title: '主任医师',
      role: 'REVIEWER'
    })
  });
  const data = await response.json();
  localStorage.setItem('token', data.data.token);
  return data.data;
}

// 步骤2: 获取我的评审任务
async function getMyTasks() {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:6031/api/reviews/my-tasks', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
}

// 步骤3: 查看报名详情
async function getRegistrationDetail(registrationId) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `http://localhost:6031/api/registrations/${registrationId}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return await response.json();
}

// 步骤4: 提交评分
async function submitScore(reviewId, score, comment) {
  const token = localStorage.getItem('token');
  const response = await fetch(
    `http://localhost:6031/api/reviews/${reviewId}/score`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ score, comment })
    }
  );
  return await response.json();
}
```

---

## 附录B: 错误处理

### 统一错误响应格式

```json
{
  "success": false,
  "data": null,
  "message": "错误描述信息"
}
```

### 常见HTTP状态码

| 状态码 | 说明 | 处理方式 |
|-------|------|---------|
| 200 | 成功 | 正常处理返回数据 |
| 400 | 请求参数错误 | 显示message给用户，检查参数 |
| 401 | 未登录或token过期 | 跳转到登录页 |
| 403 | 权限不足 | 显示"无权限访问" |
| 404 | 资源不存在 | 显示"数据不存在" |
| 500 | 服务器错误 | 显示"系统错误，请稍后重试" |

### 错误处理示例

```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    // 处理HTTP错误
    if (response.status === 401) {
      // token过期，跳转登录
      localStorage.removeItem('token');
      window.location.href = '/login';
      return null;
    }
    
    if (response.status === 403) {
      alert('您没有权限执行此操作');
      return null;
    }
    
    const data = await response.json();
    
    // 处理业务错误
    if (!data.success) {
      alert(data.message || '操作失败');
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('API调用失败:', error);
    alert('网络错误，请检查连接');
    return null;
  }
}
```

---

## 附录C: 测试账号

| 角色 | 手机号 | 姓名 | 说明 |
|-----|--------|------|------|
| COMMITTEE | 13800000009 | Committee | 组委会，可审批、分配评委 |
| COMMITTEE_ADMIN | 13800000010 | CommitteeAdmin | 组委会管理员 |
| CONTESTANT | 13800000001 | Contestant | 参赛者，可报名 |
| REVIEWER | 13800000021 | 评审专家A | 评委，可评审 |
| OPS | 13800000051 | OPS | 运维，可查看所有数据 |

---

## 附录D: 数据库信息（开发/测试环境）

- **主库:** d_hos_pinguan_traegj_20260205
- **测试库2:** d_hos_pinguan_traegj_20260205-2
- **测试库3:** d_hos_pinguan_traegj_20260205-3

可通过系统管理界面切换数据源，用于测试不同赛事阶段。

---

## 附录E: Swagger文档地址

在线API文档: `http://localhost:6031/swagger`

可在Swagger页面直接测试所有接口。

---

**文档结束**

如有疑问，请联系后端开发团队。
