# 后端API修复报告

**日期:** 2026-02-06 20:15  
**版本:** v1.1  
**服务地址:** http://localhost:6031

---

## ✅ 已修复的API

### 1. ⭐ 评委端 - 我的任务列表

**新接口:**
```
GET /api/reviews/my-tasks
```

**特点:**
- ✅ 自动从token获取当前评委ID
- ✅ 无需传递reviewerId参数
- ✅ 返回当前登录评委的所有评审任务

**前端代码示例:**
```javascript
// 之前（400错误）
const tasks = await fetch('/api/reviews/tasks?reviewerId=???');  // ❌ 不知道reviewerId

// 现在（正常工作）
const tasks = await fetch('/api/reviews/my-tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
});  // ✅ 自动获取
```

---

### 2. ⭐ 参赛者端 - 我的报名列表

**新接口:**
```
GET /api/registrations/my
```

**特点:**
- ✅ 自动从token获取当前参赛者ID
- ✅ 无需传递applicantId参数
- ✅ 返回当前登录参赛者的所有报名记录

**前端代码示例:**
```javascript
// 之前（400错误）
const regs = await fetch('/api/registrations/by-applicant?applicantId=???');  // ❌ 不知道applicantId

// 现在（正常工作）
const regs = await fetch('/api/registrations/my', {
  headers: { 'Authorization': `Bearer ${token}` }
});  // ✅ 自动获取
```

**测试结果:** ✅ 已验证，正常返回0个报名（新用户无报名记录）

---

## 📋 完整的评委端API

### 评委端必需的4个API

| API | 说明 | 状态 |
|-----|------|------|
| `GET /api/reviews/my-tasks` | 我的评审任务列表 | ✅ 已修复 |
| `GET /api/registrations/{id}` | 查看报名详情 | ✅ 正常 |
| `POST /api/reviews/scores` | 提交评分 | ✅ 正常 |
| `GET /api/reviews/scores/{taskId}` | 查看已提交的评分 | ✅ 正常 |

### 评委工作流程

```
1. 登录
   POST /api/auth/login
   { "phone":"13800000021", "name":"李明华", "role":"REVIEWER" }
   
2. 获取我的任务
   GET /api/reviews/my-tasks
   返回: [{ id, registrationId, projectName, status, ... }]
   
3. 查看项目详情
   GET /api/registrations/{registrationId}
   返回: { projectName, members, activity, summary, ... }
   
4. 提交评分
   POST /api/reviews/scores
   {
     "reviewTaskId": 101,
     "scores": {
       "theme": 90,
       "process": 85,
       "method": 88,
       "result": 92,
       "innovation": 87
     },
     "comments": "项目主题明确...",
     "suggestions": "建议..."
   }
```

---

## 📝 完整的参赛者端API

### 参赛者端必需的API

| API | 说明 | 状态 |
|-----|------|------|
| `GET /api/registrations/my` | 我的报名列表 | ✅ 已修复 |
| `POST /api/registrations` | 创建报名 | ✅ 正常 |
| `PUT /api/registrations/{id}/members` | 提交成员信息 | ✅ 正常 |
| `PUT /api/registrations/{id}/activity` | 提交活动说明 | ✅ 正常 |
| `PUT /api/registrations/{id}/summary` | 提交项目总结 | ✅ 正常 |
| `POST /api/registrations/{id}/materials` | 上传材料 | ✅ 正常 |
| `POST /api/registrations/{id}/submit` | 提交报名 | ✅ 正常 |
| `GET /api/registrations/{id}` | 查看报名详情 | ✅ 正常 |
| `GET /api/registrations/{id}/review-results` | 查看评审结果 | ✅ 正常 |

### 参赛者工作流程

```
1. 登录
   POST /api/auth/login
   { "phone":"13900000001", "name":"张医生", "role":"CONTESTANT" }
   
2. 查看我的报名
   GET /api/registrations/my
   
3. 创建新报名（草稿）
   POST /api/registrations
   {
     "competitionId": 21,
     "institutionId": 1,
     "projectName": "优化门诊预约流程",
     "projectType": "医疗类",
     "contactName": "张医生",
     "contactPhone": "13900000001",
     "contactEmail": "zhang@hospital.com"
   }
   返回: { id: 100, status: "DRAFT" }
   
4. 填写详细信息（可分步保存）
   PUT /api/registrations/100/members
   PUT /api/registrations/100/activity
   PUT /api/registrations/100/summary
   
5. 上传材料
   POST /api/registrations/100/materials
   
6. 提交审核
   POST /api/registrations/100/submit
   返回: { id: 100, status: "PENDING_REVIEW" }
```

---

## 🎨 前端页面建议

### 评委端需要实现的页面

#### 1. 任务列表页 (`/reviewer/tasks`)
```vue
<template>
  <div>
    <h2>我的评审任务</h2>
    <Table :data="tasks">
      <Column prop="projectName" label="项目名称"/>
      <Column prop="institutionName" label="机构"/>
      <Column prop="status" label="状态"/>
      <Column label="操作">
        <Button @click="goToReview(row.id)">去评审</Button>
      </Column>
    </Table>
  </div>
</template>

<script>
export default {
  async mounted() {
    const res = await fetch('/api/reviews/my-tasks', {
      headers: { 'Authorization': `Bearer ${this.$token}` }
    });
    this.tasks = (await res.json()).data;
  }
}
</script>
```

#### 2. 评审打分页 (`/reviewer/review/:taskId`)
```vue
<template>
  <div>
    <!-- 项目详情展示 -->
    <ProjectDetail :data="project"/>
    
    <!-- 评分表单 -->
    <Form>
      <FormItem label="主题选择 (0-100)">
        <Input v-model="scores.theme" type="number"/>
      </FormItem>
      <FormItem label="活动过程 (0-100)">
        <Input v-model="scores.process" type="number"/>
      </FormItem>
      <!-- ... 其他维度 ... -->
      <FormItem label="评审意见">
        <Textarea v-model="comments"/>
      </FormItem>
      <Button @click="submitScore">提交评分</Button>
    </Form>
  </div>
</template>
```

### 参赛者端需要实现的页面

#### 1. 我的报名列表 (`/contestant/registrations`)
```vue
<template>
  <div>
    <Button @click="createNew">新建报名</Button>
    <Table :data="registrations">
      <Column prop="projectName" label="项目名称"/>
      <Column prop="status" label="状态">
        <span v-if="row.status === 'DRAFT'">草稿</span>
        <span v-else-if="row.status === 'PENDING_REVIEW'">待审核</span>
        <span v-else-if="row.status === 'APPROVED'">已通过</span>
      </Column>
      <Column label="操作">
        <Button v-if="row.status === 'DRAFT'" @click="editDraft(row.id)">继续编辑</Button>
        <Button @click="viewDetail(row.id)">查看详情</Button>
      </Column>
    </Table>
  </div>
</template>

<script>
export default {
  async mounted() {
    const res = await fetch('/api/registrations/my', {
      headers: { 'Authorization': `Bearer ${this.$token}` }
    });
    this.registrations = (await res.json()).data;
  }
}
</script>
```

#### 2. 报名表单页 (`/contestant/registration/create`)
```vue
<template>
  <div>
    <Steps :current="step">
      <Step title="基本信息"/>
      <Step title="成员信息"/>
      <Step title="活动说明"/>
      <Step title="项目总结"/>
      <Step title="上传材料"/>
    </Steps>
    
    <!-- Step 1: 基本信息 -->
    <Form v-if="step === 0">
      <FormItem label="选择赛事">
        <Select v-model="form.competitionId"/>
      </FormItem>
      <FormItem label="选择机构">
        <Select v-model="form.institutionId"/>
      </FormItem>
      <FormItem label="项目名称">
        <Input v-model="form.projectName"/>
      </FormItem>
      <Button @click="saveAndNext">保存并继续</Button>
    </Form>
    
    <!-- Step 2-5: 其他步骤 ... -->
    
    <!-- 最后一步：提交 -->
    <Button @click="submitRegistration">提交审核</Button>
  </div>
</template>

<script>
export default {
  methods: {
    async saveAndNext() {
      // 第一步：创建报名
      if (!this.registrationId) {
        const res = await fetch('/api/registrations', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.$token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.form)
        });
        this.registrationId = (await res.json()).data.id;
      }
      
      // 后续步骤：更新各部分
      await fetch(`/api/registrations/${this.registrationId}/members`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${this.$token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ members: this.members })
      });
      
      this.step++;
    },
    
    async submitRegistration() {
      await fetch(`/api/registrations/${this.registrationId}/submit`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${this.$token}` }
      });
      this.$router.push('/contestant/registrations');
    }
  }
}
</script>
```

---

## 🔑 测试账号

### 评委（16个可用账号）

| 手机号 | 姓名 | 职称 | 背景 |
|--------|------|------|------|
| 13800000002 | 王建国 | 主任医师 | 医疗 |
| 13800000021 | 李明华 | 主任医师 | 医疗 |
| 13800000022 | 张秀英 | 护理部主任 | 护理 |
| 13800002001 | 陈卫东 | 副主任医师 | 医疗 |
| 13800002002 | 刘芳 | 主任护师 | 护理 |

**使用方式:**
```javascript
const login = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13800000021',
    name: '李明华',  // 可以任意填，不影响数据
    role: 'REVIEWER'
  })
});
```

### 参赛者（任意注册）

```javascript
const login = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13900000001',  // 任意11位手机号
    name: '张医生',         // 任意姓名
    role: 'CONTESTANT'
  })
});
// 首次登录会自动创建账号
```

---

## ⚠️ 重要提醒

### 1. Token管理
```javascript
// 登录后保存token
localStorage.setItem('token', loginData.data.token);

// 所有请求都带token
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}

// 401错误时跳转登录
if (response.status === 401) {
  localStorage.removeItem('token');
  router.push('/login');
}
```

### 2. 报名状态流转
```
DRAFT (草稿，可编辑)
  ↓ POST /api/registrations/{id}/submit
PENDING_REVIEW (待审核，不可编辑)
  ↓ 组委会审核
APPROVED (通过) / REJECTED (驳回)
  ↓ 驳回后可退回DRAFT重新编辑
DRAFT (重新编辑)
```

### 3. 草稿保存
- 创建报名时自动保存为DRAFT状态
- 填写过程中可随时调用PUT接口更新各部分
- 只有调用`POST /{id}/submit`后才会变为待审核状态

---

## 📞 联系方式

**后端开发:** 已修复所有必需API  
**Swagger文档:** http://localhost:6031/swagger  
**测试脚本:** `python scripts/test_fixed_apis.py`

---

## 📚 详细文档

1. **API修复文档.md** - 完整的API使用说明
2. **API开发指引文档.md** - 全面的API参考手册
3. **前端开发QuickStart.md** - 前端快速上手指南

---

**修复完成！所有必需API已就绪，可以开始前端开发。** 🎉
