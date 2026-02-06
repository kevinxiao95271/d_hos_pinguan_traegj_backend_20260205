# API最终测试文档

**日期:** 2026-02-06 20:25  
**版本:** v1.2 - 最终修复版

---

## ✅ 最终修复说明

### 问题1: 评委端API路径错误

**错误路径:** `GET /api/reviews/tasks` ❌  
**正确路径:** `GET /api/reviews/my-tasks` ✅

**说明:** 前端使用了错误的路径，应该使用 `my-tasks` 而不是 `tasks`

---

### 问题2: 报名创建API参数问题

**之前（400错误）:**
```json
{
  "competitionId": 21,
  "projectName": "测试项目",
  "groupType": "BASIC",
  "institutionId": 1,
  "applicantId": 150  // ❌ 前端不知道当前用户ID
}
```

**现在（已修复）:**
```json
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "测试项目",
  "groupType": "BASIC"
  // ✅ applicantId自动从token获取，不需要传
}
```

---

## 📋 完整的API使用说明

### 1. 评委端 - 我的任务列表

**接口:** `GET /api/reviews/my-tasks`

**请求示例:**
```bash
curl -X GET http://localhost:6031/api/reviews/my-tasks \
  -H "Authorization: Bearer <token>"
```

**返回示例:**
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

**前端代码:**
```javascript
const response = await fetch('/api/reviews/my-tasks', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: tasks } = await response.json();
```

**注意事项:**
- ✅ 路径是 `/api/reviews/my-tasks` 不是 `/api/reviews/tasks`
- ✅ 自动从token获取当前评委ID
- ✅ 如果没有分配任务，返回空数组 `[]`

---

### 2. 参赛者端 - 创建报名

**接口:** `POST /api/registrations`

**必填参数（3个）:**

| 参数 | 类型 | 说明 | 示例 |
|-----|------|------|------|
| competitionId | Long | 赛事ID | 21 |
| institutionId | Long | 机构ID | 1 |
| projectName | String | 项目名称 | "优化门诊预约流程" |
| groupType | String | 组别类型 | "BASIC" 或 "ADVANCED" |

**请求示例:**
```bash
curl -X POST http://localhost:6031/api/registrations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "competitionId": 21,
    "institutionId": 1,
    "projectName": "优化门诊预约流程品管圈",
    "groupType": "BASIC"
  }'
```

**返回示例:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "competitionId": 21,
    "institutionId": 1,
    "projectName": "优化门诊预约流程品管圈",
    "groupType": "BASIC",
    "status": "DRAFT",
    "createdAt": "2026-02-06T10:00:00"
  }
}
```

**前端代码:**
```javascript
const response = await fetch('/api/registrations', {
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
});
const { data: registration } = await response.json();
const registrationId = registration.id;  // 保存ID，后续步骤需要
```

**注意事项:**
- ✅ `applicantId` 不需要传，自动从token获取
- ✅ `status` 不需要传，自动设置为 `DRAFT`
- ✅ `groupType` 有效值：`BASIC`（基础组）、`ADVANCED`（高级组）
- ✅ 创建后返回的 `id` 要保存，后续步骤需要用到

---

### 3. 参赛者端 - 完整报名流程

#### 步骤1: 创建报名（草稿）
```javascript
POST /api/registrations
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "优化门诊预约流程品管圈",
  "groupType": "BASIC"
}
// 返回: { id: 100, status: "DRAFT" }
```

#### 步骤2: 提交成员信息
```javascript
PUT /api/registrations/100/members
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

#### 步骤3: 提交活动说明
```javascript
PUT /api/registrations/100/activity
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

#### 步骤4: 提交项目总结
```javascript
PUT /api/registrations/100/summary
{
  "background": "门诊预约效率低下...",
  "objective": "缩短预约等待时间...",
  "process": "1.现状调查 2.原因分析...",
  "result": "效率提升67%...",
  "conclusion": "项目取得显著成效..."
}
```

#### 步骤5: 上传材料（可选）
```javascript
POST /api/registrations/100/materials
FormData:
  type: "PROJECT_PLAN"
  file: <file binary>
```

#### 步骤6: 提交审核
```javascript
POST /api/registrations/100/submit
// 返回: { id: 100, status: "PENDING_REVIEW" }
```

---

## 🔍 GroupType 说明

| 值 | 说明 | 适用对象 |
|----|------|---------|
| `BASIC` | 基础组 | 初次参赛或基础项目 |
| `ADVANCED` | 高级组 | 有经验的团队或复杂项目 |

**前端选择器:**
```vue
<Select v-model="form.groupType">
  <Option value="BASIC">基础组</Option>
  <Option value="ADVANCED">高级组</Option>
</Select>
```

---

## 📊 报名状态流转

```
DRAFT (草稿)
  - 可以编辑
  - 可以随时保存各部分
  - 可以提交审核
  ↓ POST /{id}/submit
PENDING_REVIEW (待审核)
  - 不可编辑
  - 等待组委会审核
  ↓ 组委会审核
APPROVED (已通过)
  - 不可编辑
  - 可以查看评审结果
  
REJECTED (已驳回)
  - 可以退回DRAFT重新编辑
  - 可以查看驳回原因
```

---

## 🎯 前端表单验证

### 创建报名表单
```javascript
const rules = {
  competitionId: [
    { required: true, message: '请选择赛事' }
  ],
  institutionId: [
    { required: true, message: '请选择机构' }
  ],
  projectName: [
    { required: true, message: '请输入项目名称' },
    { max: 100, message: '项目名称不能超过100字' }
  ],
  groupType: [
    { required: true, message: '请选择组别' }
  ]
};
```

### 活动说明表单
```javascript
const activityRules = {
  theme: [
    { required: true, message: '请输入主题' }
  ],
  keywords: [
    { required: true, message: '请输入关键词' }
  ],
  subjectTypeCode: [
    { required: true, message: '请选择主体类型' }
  ],
  methodCode: [
    { required: true, message: '请选择方法' }
  ],
  // ... 其他必填字段
};
```

---

## 🔑 测试数据

### 获取赛事列表
```bash
GET /api/competitions
```
返回: `[{ id: 21, name: "2026浙江品管大赛", stage: "BOOK_REVIEW" }]`

### 获取机构列表
```bash
GET /api/institutions
```
返回: `[{ id: 1, name: "浙江大学医学院附属第一医院", code: "INS-0001" }]`（共33个）

---

## ⚠️ 常见错误

### 错误1: 400 - 参数校验失败

**原因:** 缺少必填参数或参数类型错误

**解决:**
```javascript
// ❌ 错误
{
  "competitionId": "21",  // 字符串，应该是数字
  "projectName": ""       // 空字符串，不能为空
}

// ✅ 正确
{
  "competitionId": 21,    // 数字
  "institutionId": 1,     // 必填
  "projectName": "xxx",   // 非空字符串
  "groupType": "BASIC"    // 必填
}
```

### 错误2: 401 - 未登录

**原因:** token缺失或过期

**解决:**
```javascript
// 检查token
const token = localStorage.getItem('token');
if (!token) {
  router.push('/login');
  return;
}

// 401错误时重新登录
if (response.status === 401) {
  localStorage.removeItem('token');
  router.push('/login');
}
```

### 错误3: 404 - 接口不存在

**原因:** 路径错误

**解决:**
```javascript
// ❌ 错误路径
'/api/reviews/tasks'              // 缺少 my-
'/api/registrations/by-applicant' // 应该用 my

// ✅ 正确路径
'/api/reviews/my-tasks'
'/api/registrations/my'
```

---

## 📱 完整的前端示例

### 评委端 - 任务列表页
```vue
<template>
  <div class="reviewer-tasks">
    <h2>我的评审任务</h2>
    
    <div v-if="loading">加载中...</div>
    
    <div v-else-if="tasks.length === 0">
      暂无评审任务
    </div>
    
    <Table v-else :data="tasks">
      <Column prop="projectName" label="项目名称"/>
      <Column prop="institutionName" label="机构"/>
      <Column prop="stage" label="阶段">
        <template #default="{ row }">
          <span v-if="row.stage === 'BOOK_REVIEW'">书面评审</span>
          <span v-else-if="row.stage === 'INTERVIEW'">现场答辩</span>
        </template>
      </Column>
      <Column prop="status" label="状态">
        <template #default="{ row }">
          <Tag v-if="row.status === 'PENDING'" type="warning">待评审</Tag>
          <Tag v-else-if="row.status === 'COMPLETED'" type="success">已完成</Tag>
        </template>
      </Column>
      <Column label="操作">
        <template #default="{ row }">
          <Button @click="goToReview(row.id)">去评审</Button>
        </template>
      </Column>
    </Table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tasks: [],
      loading: false
    };
  },
  
  async mounted() {
    await this.loadTasks();
  },
  
  methods: {
    async loadTasks() {
      this.loading = true;
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/reviews/my-tasks', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.status === 401) {
          this.$router.push('/login');
          return;
        }
        
        const { data } = await response.json();
        this.tasks = data;
      } catch (error) {
        this.$message.error('加载失败');
      } finally {
        this.loading = false;
      }
    },
    
    goToReview(taskId) {
      this.$router.push(`/reviewer/review/${taskId}`);
    }
  }
};
</script>
```

### 参赛者端 - 创建报名页
```vue
<template>
  <div class="create-registration">
    <h2>创建报名</h2>
    
    <Form :model="form" :rules="rules" ref="form">
      <FormItem label="选择赛事" prop="competitionId">
        <Select v-model="form.competitionId">
          <Option v-for="comp in competitions" 
                  :key="comp.id" 
                  :value="comp.id">
            {{ comp.name }}
          </Option>
        </Select>
      </FormItem>
      
      <FormItem label="选择机构" prop="institutionId">
        <Select v-model="form.institutionId">
          <Option v-for="inst in institutions" 
                  :key="inst.id" 
                  :value="inst.id">
            {{ inst.name }}
          </Option>
        </Select>
      </FormItem>
      
      <FormItem label="项目名称" prop="projectName">
        <Input v-model="form.projectName" 
               placeholder="请输入项目名称（最多100字）"
               maxlength="100"
               show-word-limit/>
      </FormItem>
      
      <FormItem label="参赛组别" prop="groupType">
        <Radio v-model="form.groupType" value="BASIC">基础组</Radio>
        <Radio v-model="form.groupType" value="ADVANCED">高级组</Radio>
      </FormItem>
      
      <FormItem>
        <Button type="primary" @click="submit" :loading="submitting">
          创建报名
        </Button>
      </FormItem>
    </Form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        competitionId: null,
        institutionId: null,
        projectName: '',
        groupType: 'BASIC'
      },
      rules: {
        competitionId: [
          { required: true, message: '请选择赛事' }
        ],
        institutionId: [
          { required: true, message: '请选择机构' }
        ],
        projectName: [
          { required: true, message: '请输入项目名称' },
          { max: 100, message: '项目名称不能超过100字' }
        ],
        groupType: [
          { required: true, message: '请选择组别' }
        ]
      },
      competitions: [],
      institutions: [],
      submitting: false
    };
  },
  
  async mounted() {
    await this.loadOptions();
  },
  
  methods: {
    async loadOptions() {
      const token = localStorage.getItem('token');
      
      // 加载赛事列表
      const compResp = await fetch('/api/competitions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.competitions = (await compResp.json()).data;
      
      // 加载机构列表
      const instResp = await fetch('/api/institutions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      this.institutions = (await instResp.json()).data;
    },
    
    async submit() {
      this.$refs.form.validate(async (valid) => {
        if (!valid) return;
        
        this.submitting = true;
        try {
          const token = localStorage.getItem('token');
          const response = await fetch('/api/registrations', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(this.form)
          });
          
          if (response.status === 401) {
            this.$router.push('/login');
            return;
          }
          
          const { data } = await response.json();
          this.$message.success('创建成功');
          
          // 跳转到编辑页面继续填写
          this.$router.push(`/contestant/registration/edit/${data.id}`);
        } catch (error) {
          this.$message.error('创建失败');
        } finally {
          this.submitting = false;
        }
      });
    }
  }
};
</script>
```

---

## 📞 技术支持

**Swagger文档:** http://localhost:6031/swagger  
**测试脚本:** `python scripts/test_fixed_apis.py`

---

**所有API已最终修复完成！** 🎉
