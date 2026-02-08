# 前端开发指引 - 分场景API调用

## 📋 概述

本文档详细说明4个场景下如何调用API获取报名详情，包括所有Label字段。

所有场景的详情接口都返回完整的4个Label字段：
- `subjectTypeLabel` - 主题类型标签
- `methodLabel` - 运用手法标签  
- `experienceImproveLabel` - 改善就医环境标签
- `qualityTopicLabel` - 医疗质量相关主题标签

---

## 场景1: 参赛者 - 我的报名

### 用户角色
参赛者 (CONTESTANT)

### 页面路径
`/contestant/my-registrations` → 点击查看详情

### API调用流程

#### 步骤1: 登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "phone": "13800000001",
  "name": "张三",
  "role": "CONTESTANT"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### 步骤2: 获取我的报名列表
```http
GET /api/registrations/my
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "id": 119,
      "projectName": "康复流程改进-14",
      "groupType": "COMPREHENSIVE",
      "groupCode": "B2",
      "status": "APPROVED",
      "institutionId": 14,
      "institutionName": "浙江大学医学院附属口腔医院",
      "institutionLevel": "三级甲等",
      "competitionId": 23,
      "competitionName": "2023年度品管圈大赛",
      "submittedAt": "2026-02-05T10:00:00",
      "createdAt": "2026-02-05T09:00:00"
    }
  ]
}
```

#### 步骤3: 查看报名详情
```http
GET /api/registrations/{id}
Authorization: Bearer {token}
```

**响应:** 见"通用详情响应格式"

### 前端实现示例 (Vue 3)

```vue
<template>
  <div class="my-registrations">
    <el-table :data="registrations" @row-click="viewDetail">
      <el-table-column prop="projectName" label="项目名称" />
      <el-table-column prop="institutionName" label="机构名称" />
      <el-table-column prop="status" label="状态" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const registrations = ref([])

onMounted(async () => {
  const response = await axios.get('/api/registrations/my')
  registrations.value = response.data.data
})

const viewDetail = (row) => {
  router.push(`/contestant/registration/${row.id}`)
}
</script>
```

---

## 场景2: 组委会管理员 - 书审分组项目列表

### 用户角色
组委会管理员 (COMMITTEE_ADMIN)

### 页面路径
`/admin/book-review-groups` → 点击查看详情

### API调用流程

#### 步骤1: 登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "phone": "13800000041",
  "name": "CommitteeAdmin A",
  "role": "COMMITTEE_ADMIN"
}
```

#### 步骤2: 获取书审分组列表
```http
GET /api/admin/registrations/interview-groups?competitionId=23
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "groupName": "A1",
      "items": [
        {
          "id": 119,
          "projectName": "康复流程改进-14",
          "institutionName": "浙江大学医学院附属口腔医院",
          "institutionLevel": "三级甲等",
          "groupType": "COMPREHENSIVE",
          "groupCode": "A1"
        }
      ]
    }
  ]
}
```

**注意:** 如果返回空数组，可以尝试以下备用接口：
- `/api/admin/registrations/final-groups?competitionId=23`

#### 步骤3: 查看项目详情
```http
GET /api/registrations/{id}
Authorization: Bearer {token}
```

**响应:** 见"通用详情响应格式"

### 前端实现示例 (Vue 3)

```vue
<template>
  <div class="book-review-groups">
    <el-collapse v-model="activeGroups">
      <el-collapse-item 
        v-for="group in groups" 
        :key="group.groupName"
        :name="group.groupName"
        :title="`${group.groupName} (${group.items.length}个项目)`"
      >
        <el-table :data="group.items" @row-click="viewDetail">
          <el-table-column prop="projectName" label="项目名称" />
          <el-table-column prop="institutionName" label="机构名称" />
          <el-table-column prop="institutionLevel" label="机构等级" />
        </el-table>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const groups = ref([])
const activeGroups = ref([])

onMounted(async () => {
  const competitionId = 23
  const response = await axios.get(
    `/api/admin/registrations/interview-groups?competitionId=${competitionId}`
  )
  groups.value = response.data.data
  
  // 默认展开第一组
  if (groups.value.length > 0) {
    activeGroups.value = [groups.value[0].groupName]
  }
})

const viewDetail = (row) => {
  router.push(`/admin/registration/${row.id}`)
}
</script>
```

---

## 场景3: 组委会管理员 - 筛选项目列表

### 用户角色
组委会管理员 (COMMITTEE_ADMIN)

### 页面路径
`/admin/registrations` → 筛选 → 点击查看详情

### API调用流程

#### 步骤1: 登录
同场景2

#### 步骤2: 筛选项目列表
```http
GET /api/admin/registrations/filter?competitionId=23&groupType=COMPREHENSIVE&projectName=康复
Authorization: Bearer {token}
```

**查询参数:**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| competitionId | Long | 是 | 赛事ID |
| groupType | String | 否 | 组别类型 (COMPREHENSIVE/SPECIALIZED) |
| groupCode | String | 否 | 分组代码 (如 A1, B2) |
| projectName | String | 否 | 项目名称（模糊搜索） |
| institutionName | String | 否 | 机构名称（模糊搜索） |
| methodCode | String | 否 | 运用手法代码 |
| subjectTypeCode | String | 否 | 主题类型代码 |

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "id": 119,
      "projectName": "康复流程改进-14",
      "institutionName": "浙江大学医学院附属口腔医院",
      "groupType": "COMPREHENSIVE",
      "groupCode": "B2",
      "subjectTypeCode": "subject_type_6",
      "subjectTypeLabel": "满意度",
      "methodCode": "method_15",
      "methodLabel": "流程改造"
    }
  ]
}
```

**注意:** 筛选列表中已包含 `subjectTypeLabel` 和 `methodLabel`，可以直接显示。

#### 步骤3: 查看项目详情
```http
GET /api/registrations/{id}
Authorization: Bearer {token}
```

**响应:** 见"通用详情响应格式"

### 前端实现示例 (Vue 3)

```vue
<template>
  <div class="registration-filter">
    <!-- 筛选表单 -->
    <el-form :model="filterForm" inline>
      <el-form-item label="项目名称">
        <el-input v-model="filterForm.projectName" placeholder="输入项目名称" />
      </el-form-item>
      <el-form-item label="机构名称">
        <el-input v-model="filterForm.institutionName" placeholder="输入机构名称" />
      </el-form-item>
      <el-form-item label="组别">
        <el-select v-model="filterForm.groupType" placeholder="选择组别">
          <el-option label="综合组" value="COMPREHENSIVE" />
          <el-option label="专科组" value="SPECIALIZED" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">搜索</el-button>
        <el-button @click="reset">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 结果列表 -->
    <el-table :data="projects" @row-click="viewDetail">
      <el-table-column prop="projectName" label="项目名称" />
      <el-table-column prop="institutionName" label="机构名称" />
      <el-table-column prop="groupCode" label="分组" />
      <el-table-column prop="subjectTypeLabel" label="主题类型" />
      <el-table-column prop="methodLabel" label="运用手法" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const projects = ref([])
const filterForm = ref({
  competitionId: 23,
  projectName: '',
  institutionName: '',
  groupType: ''
})

const search = async () => {
  const params = new URLSearchParams()
  params.append('competitionId', filterForm.value.competitionId)
  
  if (filterForm.value.projectName) {
    params.append('projectName', filterForm.value.projectName)
  }
  if (filterForm.value.institutionName) {
    params.append('institutionName', filterForm.value.institutionName)
  }
  if (filterForm.value.groupType) {
    params.append('groupType', filterForm.value.groupType)
  }
  
  const response = await axios.get(`/api/admin/registrations/filter?${params}`)
  projects.value = response.data.data
}

const reset = () => {
  filterForm.value = {
    competitionId: 23,
    projectName: '',
    institutionName: '',
    groupType: ''
  }
  search()
}

const viewDetail = (row) => {
  router.push(`/admin/registration/${row.id}`)
}

onMounted(() => {
  search()
})
</script>
```

---

## 场景4: 评委 - 查看评审任务

### 用户角色
评委 (REVIEWER)

### 页面路径
`/reviewer/my-tasks` → 点击查看详情

### API调用流程

#### 步骤1: 登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "phone": "13900000001",
  "name": "李明华",
  "role": "REVIEWER"
}
```

#### 步骤2: 获取评审任务列表
```http
GET /api/reviews/my-tasks?competitionId=23
Authorization: Bearer {token}
```

**响应:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "registrationId": 119,
      "projectName": "康复流程改进-14",
      "reviewStage": "BOOK_REVIEW",
      "status": "PENDING"
    }
  ]
}
```

#### 步骤3: 查看项目详情
```http
GET /api/registrations/{registrationId}
Authorization: Bearer {token}
```

**响应:** 见"通用详情响应格式"

### 前端实现示例 (Vue 3)

```vue
<template>
  <div class="reviewer-tasks">
    <el-table :data="tasks" @row-click="viewDetail">
      <el-table-column prop="projectName" label="项目名称" />
      <el-table-column prop="reviewStage" label="评审阶段">
        <template #default="{ row }">
          {{ getReviewStageLabel(row.reviewStage) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            size="small"
            @click.stop="startReview(row)"
          >
            {{ row.status === 'PENDING' ? '开始评审' : '查看详情' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const tasks = ref([])

onMounted(async () => {
  const competitionId = 23
  const response = await axios.get(`/api/reviews/my-tasks?competitionId=${competitionId}`)
  tasks.value = response.data.data
})

const viewDetail = (row) => {
  router.push(`/reviewer/registration/${row.registrationId}`)
}

const startReview = (row) => {
  router.push(`/reviewer/review/${row.id}`)
}

const getReviewStageLabel = (stage) => {
  const labels = {
    'BOOK_REVIEW': '书审',
    'INTERVIEW': '面谈',
    'FINAL': '决赛'
  }
  return labels[stage] || stage
}

const getStatusLabel = (status) => {
  const labels = {
    'PENDING': '待评审',
    'IN_PROGRESS': '评审中',
    'SCORED': '已评分'
  }
  return labels[status] || status
}

const getStatusType = (status) => {
  const types = {
    'PENDING': 'warning',
    'IN_PROGRESS': 'primary',
    'SCORED': 'success'
  }
  return types[status] || 'info'
}
</script>
```

---

## 通用详情响应格式

所有场景的详情接口 `GET /api/registrations/{id}` 返回相同的数据结构：

```json
{
  "success": true,
  "data": {
    "registration": {
      "id": 119,
      "projectName": "康复流程改进-14",
      "groupType": "COMPREHENSIVE",
      "groupCode": "B2",
      "status": "APPROVED",
      "submittedAt": "2026-02-05T10:00:00",
      "createdAt": "2026-02-05T09:00:00"
    },
    "institution": {
      "id": 14,
      "name": "浙江大学医学院附属口腔医院",
      "code": "INST014",
      "region": "杭州",
      "level": "三级甲等"
    },
    "activityInfo": {
      "theme": "项目主题119",
      "keywords": "质量,改进",
      "subjectTypeCode": "subject_type_6",
      "subjectTypeLabel": "满意度",
      "methodCode": "method_15",
      "methodLabel": "流程改造",
      "experienceImproveCode": "outpatient_process",
      "experienceImproveLabel": "门诊就诊流程更加优化",
      "qualityTopicCode": "surgery_mortality",
      "qualityTopicLabel": "降低住院患者围手术期死亡率",
      "avgWorkYears": 7,
      "avgAge": 32,
      "crossDepartment": true,
      "relatedToDigitalAi": false
    },
    "projectSummary": {
      "theme": "项目摘要主题",
      "plan": "计划内容...",
      "problem": "问题结构与对策措施探讨...",
      "action": "对策行动过程...",
      "success": "成果表现...",
      "discussion": "讨论总结...",
      "operation": "运作内容...",
      "presentation": "展示内容..."
    },
    "members": [
      {
        "id": 1,
        "role": "LEADER",
        "name": "张三",
        "title": "主任医师",
        "department": "内科"
      }
    ],
    "materials": [
      {
        "id": 1,
        "fileName": "项目材料.pdf",
        "fileUrl": "/uploads/xxx.pdf",
        "fileType": "PDF",
        "uploadedAt": "2026-02-05T09:30:00"
      }
    ]
  }
}
```

---

## 通用详情页面组件

```vue
<template>
  <div class="registration-detail" v-if="detail">
    <!-- 基本信息 -->
    <el-card class="section">
      <template #header>
        <h3>基本信息</h3>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="项目名称">
          {{ detail.registration.projectName }}
        </el-descriptions-item>
        <el-descriptions-item label="机构名称">
          {{ detail.institution.name }}
        </el-descriptions-item>
        <el-descriptions-item label="机构等级">
          {{ detail.institution.level }}
        </el-descriptions-item>
        <el-descriptions-item label="所在地区">
          {{ detail.institution.region }}
        </el-descriptions-item>
        <el-descriptions-item label="组别">
          {{ detail.registration.groupType === 'COMPREHENSIVE' ? '综合组' : '专科组' }}
        </el-descriptions-item>
        <el-descriptions-item label="分组">
          {{ detail.registration.groupCode || '未分组' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 活动信息 -->
    <el-card class="section" v-if="detail.activityInfo">
      <template #header>
        <h3>活动信息</h3>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="活动主题" :span="2">
          {{ detail.activityInfo.theme }}
        </el-descriptions-item>
        <el-descriptions-item label="关键词" :span="2">
          {{ detail.activityInfo.keywords }}
        </el-descriptions-item>
        
        <!-- 4个Label字段 -->
        <el-descriptions-item label="主题类型">
          {{ detail.activityInfo.subjectTypeLabel || detail.activityInfo.subjectTypeCode || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="运用手法">
          {{ detail.activityInfo.methodLabel || detail.activityInfo.methodCode || '未填写' }}
        </el-descriptions-item>
        <el-descriptions-item label="改善就医环境">
          {{ getExperienceImproveDisplay(detail.activityInfo) }}
        </el-descriptions-item>
        <el-descriptions-item label="医疗质量相关主题">
          {{ getQualityTopicDisplay(detail.activityInfo) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="平均工作年限">
          {{ detail.activityInfo.avgWorkYears }} 年
        </el-descriptions-item>
        <el-descriptions-item label="平均年龄">
          {{ detail.activityInfo.avgAge }} 岁
        </el-descriptions-item>
        <el-descriptions-item label="是否跨部门">
          <el-tag :type="detail.activityInfo.crossDepartment ? 'success' : 'info'">
            {{ detail.activityInfo.crossDepartment ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否与数字化/AI相关">
          <el-tag :type="detail.activityInfo.relatedToDigitalAi ? 'success' : 'info'">
            {{ detail.activityInfo.relatedToDigitalAi ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 项目摘要 -->
    <el-card class="section" v-if="detail.projectSummary">
      <template #header>
        <h3>项目摘要</h3>
      </template>
      <div class="summary-content">
        <div class="summary-item" v-if="detail.projectSummary.plan">
          <h4>计划</h4>
          <p>{{ detail.projectSummary.plan }}</p>
        </div>
        <div class="summary-item" v-if="detail.projectSummary.problem">
          <h4>问题结构与对策措施探讨</h4>
          <p>{{ detail.projectSummary.problem }}</p>
        </div>
        <div class="summary-item" v-if="detail.projectSummary.action">
          <h4>对策行动过程</h4>
          <p>{{ detail.projectSummary.action }}</p>
        </div>
        <div class="summary-item" v-if="detail.projectSummary.success">
          <h4>成果表现</h4>
          <p>{{ detail.projectSummary.success }}</p>
        </div>
        <div class="summary-item" v-if="detail.projectSummary.discussion">
          <h4>讨论总结</h4>
          <p>{{ detail.projectSummary.discussion }}</p>
        </div>
        <div class="summary-item" v-if="detail.projectSummary.operation">
          <h4>运作</h4>
          <p>{{ detail.projectSummary.operation }}</p>
        </div>
        <div class="summary-item" v-if="detail.projectSummary.presentation">
          <h4>展示</h4>
          <p>{{ detail.projectSummary.presentation }}</p>
        </div>
      </div>
    </el-card>

    <!-- 团队成员 -->
    <el-card class="section" v-if="detail.members && detail.members.length > 0">
      <template #header>
        <h3>团队成员</h3>
      </template>
      <el-table :data="detail.members" border>
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            {{ getMemberRoleLabel(row.role) }}
          </template>
        </el-table-column>
        <el-table-column prop="title" label="职称" />
        <el-table-column prop="department" label="科室" />
      </el-table>
    </el-card>

    <!-- 材料文件 -->
    <el-card class="section" v-if="detail.materials && detail.materials.length > 0">
      <template #header>
        <h3>材料文件</h3>
      </template>
      <el-table :data="detail.materials" border>
        <el-table-column prop="fileName" label="文件名" />
        <el-table-column prop="fileType" label="类型" />
        <el-table-column label="操作">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="downloadFile(row)">
              下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const detail = ref(null)

onMounted(async () => {
  const registrationId = route.params.id
  const response = await axios.get(`/api/registrations/${registrationId}`)
  detail.value = response.data.data
})

// 处理"其他"选项
const getExperienceImproveDisplay = (activityInfo) => {
  if (!activityInfo.experienceImproveCode) {
    return '未填写'
  }
  
  if (activityInfo.experienceImproveCode === 'other') {
    return activityInfo.experienceImproveOther || '其他'
  }
  
  return activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode
}

const getQualityTopicDisplay = (activityInfo) => {
  if (!activityInfo.qualityTopicCode) {
    return '未填写'
  }
  
  if (activityInfo.qualityTopicCode === 'other') {
    return activityInfo.qualityTopicOther || '其他'
  }
  
  return activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode
}

const getMemberRoleLabel = (role) => {
  const labels = {
    'LEADER': '圈长',
    'FACILITATOR': '辅导员',
    'MEMBER': '圈员'
  }
  return labels[role] || role
}

const downloadFile = (file) => {
  window.open(file.fileUrl, '_blank')
}
</script>

<style scoped>
.section {
  margin-bottom: 20px;
}

.summary-content {
  padding: 10px;
}

.summary-item {
  margin-bottom: 20px;
}

.summary-item h4 {
  color: #409EFF;
  margin-bottom: 10px;
  font-size: 16px;
}

.summary-item p {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.8;
  color: #606266;
}
</style>
```

---

## 测试账号

| 角色 | 手机号 | 姓名 | 角色代码 |
|------|--------|------|----------|
| 参赛者 | 13800000001 | 张三 | CONTESTANT |
| 组委会管理员 | 13800000041 | CommitteeAdmin A | COMMITTEE_ADMIN |
| 评委 | 13900000001 | 李明华 | REVIEWER |

---

## 测试结果

✅ 所有4个场景测试通过
- 场景1: 参赛者 - 我的报名 ✅
- 场景2: 组委会管理员 - 书审分组项目列表 ✅
- 场景3: 组委会管理员 - 筛选项目列表 ✅
- 场景4: 评委 - 查看评审任务 ✅

所有场景都能正确返回4个Label字段。

---

**文档更新时间**: 2026-02-09  
**测试状态**: ✅ 全部通过  
**应用状态**: ✅ 运行正常（端口6031）
