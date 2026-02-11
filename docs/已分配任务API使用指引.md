# 已分配任务API使用指引

## 概述

本文档提供书审和面谈环节已分配任务的API使用指引，包括接口说明、参数详解、返回数据格式和前端代码示例。

## API接口

### 查询已分配任务列表

**接口地址**: `GET /api/admin/reviews/tasks`

**权限要求**: 需要管理员权限（COMMITTEE_ADMIN）

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| competitionId | Long | 是 | 竞赛ID |
| stage | String | 否 | 评审环节：BOOK(书审)、INTERVIEW(面谈)、FINAL(终审) |
| status | String | 否 | 任务状态：PENDING(待确认)、CONFIRMED(已确认)、SCORED(已评分)、RETURNED(已退回) |

**返回数据**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "stage": "BOOK",
      "status": "CONFIRMED",
      "createdAt": "2025-01-15T10:30:00",
      "registrationId": 100,
      "projectName": "基于AI的医疗质量改进项目",
      "institutionName": "浙江省人民医院",
      "groupType": "COMPREHENSIVE",
      "groupCode": "B1",
      "reviewerId": 5,
      "reviewerName": "张医生",
      "reviewerTitle": "主任医师",
      "reviewerInstitutionName": "浙江大学医学院附属第一医院",
      "reviewerGroupCode": null,
      "interviewGroupCode": null,
      "expertBackground": "临床医学"
    }
  ],
  "message": null
}
```

## 使用场景

### 场景1: 书审环节任务管理

#### 1.1 查询所有书审任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=BOOK
```

**用途**: 查看本届竞赛所有书审任务的分配情况

#### 1.2 查询待确认的书审任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=BOOK&status=PENDING
```

**用途**: 查看哪些书审任务还未被评委确认

#### 1.3 查询已确认的书审任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=BOOK&status=CONFIRMED
```

**用途**: 查看评委已确认但尚未评分的书审任务

#### 1.4 查询已评分的书审任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=BOOK&status=SCORED
```

**用途**: 查看已完成评分的书审任务

### 场景2: 面谈环节任务管理

#### 2.1 查询所有面谈任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=INTERVIEW
```

**用途**: 查看本届竞赛所有面谈任务的分配情况

#### 2.2 查询待确认的面谈任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=INTERVIEW&status=PENDING
```

**用途**: 查看哪些面谈任务还未被评委确认

#### 2.3 查询已确认的面谈任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=INTERVIEW&status=CONFIRMED
```

**用途**: 查看评委已确认但尚未评分的面谈任务

#### 2.4 查询已评分的面谈任务

```http
GET /api/admin/reviews/tasks?competitionId=21&stage=INTERVIEW&status=SCORED
```

**用途**: 查看已完成评分的面谈任务

### 场景3: 跨环节任务查询

#### 3.1 查询所有环节的所有任务

```http
GET /api/admin/reviews/tasks?competitionId=21
```

**用途**: 查看本届竞赛所有评审任务（书审+面谈+终审）

#### 3.2 查询所有环节的待确认任务

```http
GET /api/admin/reviews/tasks?competitionId=21&status=PENDING
```

**用途**: 查看所有环节中待确认的任务

## 返回字段详解

### 任务基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Long | 任务ID，唯一标识 |
| stage | String | 评审环节：BOOK(书审)、INTERVIEW(面谈)、FINAL(终审) |
| status | String | 任务状态：PENDING(待确认)、CONFIRMED(已确认)、SCORED(已评分)、RETURNED(已退回) |
| createdAt | DateTime | 任务创建时间 |

### 报名项目信息

| 字段 | 类型 | 说明 |
|------|------|------|
| registrationId | Long | 报名ID |
| projectName | String | 项目名称 |
| institutionName | String | 参赛机构名称 |
| groupType | String | 组别类型：BASIC(基层组)、COMPREHENSIVE(综合组)、ADVANCED(进阶组) |
| groupCode | String | 组别代码，如 A1, B2, C3 |

### 评委信息

| 字段 | 类型 | 说明 |
|------|------|------|
| reviewerId | Long | 评委ID |
| reviewerName | String | 评委姓名 |
| reviewerTitle | String | 评委职称 |
| reviewerInstitutionName | String | 评委所在机构 |
| expertBackground | String | 专业背景（评委分配的关键依据） |
| reviewerGroupCode | String | 书审分组代码（已废弃，始终为null） |
| interviewGroupCode | String | 面谈分组代码（已废弃，始终为null） |

## 前端代码示例

### Vue 3 + Composition API

```vue
<template>
  <div class="review-tasks">
    <h2>{{ stageTitle }}任务列表</h2>
    
    <!-- 状态筛选 -->
    <div class="filters">
      <select v-model="selectedStatus" @change="loadTasks">
        <option value="">全部状态</option>
        <option value="PENDING">待确认</option>
        <option value="CONFIRMED">已确认</option>
        <option value="SCORED">已评分</option>
        <option value="RETURNED">已退回</option>
      </select>
    </div>
    
    <!-- 任务列表 -->
    <div class="task-list">
      <div v-for="task in tasks" :key="task.id" class="task-item">
        <div class="task-header">
          <span class="task-id">#{{ task.id }}</span>
          <span :class="['status', task.status.toLowerCase()]">
            {{ statusText[task.status] }}
          </span>
        </div>
        
        <div class="task-body">
          <h3>{{ task.projectName }}</h3>
          <p class="institution">{{ task.institutionName }}</p>
          <p class="group">{{ groupTypeText[task.groupType] }} - {{ task.groupCode }}</p>
        </div>
        
        <div class="task-footer">
          <div class="reviewer-info">
            <span class="reviewer-name">{{ task.reviewerName }}</span>
            <span class="reviewer-title">{{ task.reviewerTitle }}</span>
            <span class="reviewer-institution">{{ task.reviewerInstitutionName }}</span>
            <span class="expert-background">{{ task.expertBackground }}</span>
          </div>
          <div class="task-time">
            {{ formatDate(task.createdAt) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  competitionId: {
    type: Number,
    required: true
  },
  stage: {
    type: String,
    required: true,
    validator: (value) => ['BOOK', 'INTERVIEW', 'FINAL'].includes(value)
  }
})

const tasks = ref([])
const selectedStatus = ref('')

const stageTitle = computed(() => {
  const titles = {
    'BOOK': '书审',
    'INTERVIEW': '面谈',
    'FINAL': '终审'
  }
  return titles[props.stage] || ''
})

const statusText = {
  'PENDING': '待确认',
  'CONFIRMED': '已确认',
  'SCORED': '已评分',
  'RETURNED': '已退回'
}

const groupTypeText = {
  'BASIC': '基层组',
  'COMPREHENSIVE': '综合组',
  'ADVANCED': '进阶组'
}

const loadTasks = async () => {
  try {
    const params = {
      competitionId: props.competitionId,
      stage: props.stage
    }
    
    if (selectedStatus.value) {
      params.status = selectedStatus.value
    }
    
    const response = await axios.get('/api/admin/reviews/tasks', { params })
    
    if (response.data.success) {
      tasks.value = response.data.data
    }
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.review-tasks {
  padding: 20px;
}

.filters {
  margin-bottom: 20px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.task-list {
  display: grid;
  gap: 16px;
}

.task-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  background: white;
}

.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.task-id {
  font-weight: bold;
  color: #666;
}

.status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status.pending {
  background: #fff3cd;
  color: #856404;
}

.status.confirmed {
  background: #d1ecf1;
  color: #0c5460;
}

.status.scored {
  background: #d4edda;
  color: #155724;
}

.status.returned {
  background: #f8d7da;
  color: #721c24;
}

.task-body h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.task-body p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

.task-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reviewer-info {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #666;
}

.reviewer-name {
  font-weight: bold;
  color: #333;
}

.task-time {
  font-size: 12px;
  color: #999;
}
</style>
```

### React + Hooks

```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ReviewTasks.css';

const ReviewTasks = ({ competitionId, stage }) => {
  const [tasks, setTasks] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState('');
  
  const stageTitle = {
    'BOOK': '书审',
    'INTERVIEW': '面谈',
    'FINAL': '终审'
  }[stage] || '';
  
  const statusText = {
    'PENDING': '待确认',
    'CONFIRMED': '已确认',
    'SCORED': '已评分',
    'RETURNED': '已退回'
  };
  
  const groupTypeText = {
    'BASIC': '基层组',
    'COMPREHENSIVE': '综合组',
    'ADVANCED': '进阶组'
  };
  
  const loadTasks = async () => {
    try {
      const params = {
        competitionId,
        stage
      };
      
      if (selectedStatus) {
        params.status = selectedStatus;
      }
      
      const response = await axios.get('/api/admin/reviews/tasks', { params });
      
      if (response.data.success) {
        setTasks(response.data.data);
      }
    } catch (error) {
      console.error('加载任务失败:', error);
    }
  };
  
  useEffect(() => {
    loadTasks();
  }, [competitionId, stage, selectedStatus]);
  
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };
  
  return (
    <div className="review-tasks">
      <h2>{stageTitle}任务列表</h2>
      
      <div className="filters">
        <select 
          value={selectedStatus} 
          onChange={(e) => setSelectedStatus(e.target.value)}
        >
          <option value="">全部状态</option>
          <option value="PENDING">待确认</option>
          <option value="CONFIRMED">已确认</option>
          <option value="SCORED">已评分</option>
          <option value="RETURNED">已退回</option>
        </select>
      </div>
      
      <div className="task-list">
        {tasks.map(task => (
          <div key={task.id} className="task-item">
            <div className="task-header">
              <span className="task-id">#{task.id}</span>
              <span className={`status ${task.status.toLowerCase()}`}>
                {statusText[task.status]}
              </span>
            </div>
            
            <div className="task-body">
              <h3>{task.projectName}</h3>
              <p className="institution">{task.institutionName}</p>
              <p className="group">
                {groupTypeText[task.groupType]} - {task.groupCode}
              </p>
            </div>
            
            <div className="task-footer">
              <div className="reviewer-info">
                <span className="reviewer-name">{task.reviewerName}</span>
                <span className="reviewer-title">{task.reviewerTitle}</span>
                <span className="reviewer-institution">
                  {task.reviewerInstitutionName}
                </span>
                <span className="expert-background">
                  {task.expertBackground}
                </span>
              </div>
              <div className="task-time">
                {formatDate(task.createdAt)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ReviewTasks;
```

## 常见问题

### Q1: reviewerGroupCode 和 interviewGroupCode 为什么总是null？

A: 这两个字段已废弃。评审专家不再有固定分组，可以评审任何分组的项目。评委分配主要基于 `expertBackground`（专业背景）字段。

### Q2: 如何判断一个评委的工作负荷？

A: 统计该评委在指定环节的任务数量。可以按 `reviewerId` 和 `stage` 分组统计。

### Q3: 如何查看某个项目被分配给了哪些评委？

A: 按 `registrationId` 筛选任务列表，可以看到该项目在不同环节被分配给的所有评委。

### Q4: stage参数可以不传吗？

A: 可以。不传stage参数时，会返回所有环节的任务。这在需要查看整体任务分配情况时很有用。

## 注意事项

1. **权限控制**: 该接口需要管理员权限，前端需要在请求头中携带有效的JWT token
2. **数据量**: 如果任务数量很大，建议前端实现分页或虚拟滚动
3. **实时更新**: 任务状态可能会变化，建议定期刷新或使用WebSocket实时更新
4. **错误处理**: 注意处理网络错误和权限错误，给用户友好的提示

## 相关文档

- [评审任务API变更说明](./评审任务API变更说明.md)
- [评审专家分组字段删除说明](./评审专家分组字段删除说明.md)
- [评审专家API变更-前端对接清单](./评审专家API变更-前端对接清单.md)
