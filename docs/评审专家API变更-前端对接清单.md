# 评审专家API变更 - 前端对接清单

## 变更时间

2026-02-11

## 变更原因

删除评审专家的分组限制（reviewerGroupCode, interviewGroupCode），因为：
- 评审专家没有固定分组
- 评审专家可以评审任何分组的项目
- 分配基于专业背景（expertBackground）而非分组

---

## API变更详情

### 1. 评委列表接口

#### 端点1: GET /api/admin/reviewers

**请求参数变更**:

| 参数 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| competitionId | 可选 | 可选 | 无变化 |
| institutionId | 可选 | 可选 | 无变化 |
| reviewerGroupCode | 可选 | ❌ 删除 | 删除此参数 |
| interviewGroupCode | 可选 | ❌ 删除 | 删除此参数 |
| expertBackground | 可选 | 可选 | 无变化 |

**请求示例**:

```javascript
// 修改前
GET /api/admin/reviewers?institutionId=10&reviewerGroupCode=A1&interviewGroupCode=B2&expertBackground=临床医学

// 修改后
GET /api/admin/reviewers?institutionId=10&expertBackground=临床医学
```

**响应数据变更**:

```json
// 修改前
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "phone": "13800138000",
      "name": "张三",
      "title": "主任医师",
      "institutionId": 10,
      "institutionName": "浙江大学医学院附属第一医院",
      "reviewerGroupCode": "A1",        // ❌ 删除
      "interviewGroupCode": "B2",       // ❌ 删除
      "expertBackground": "临床医学",
      "currentLoad": 5
    }
  ]
}

// 修改后
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "phone": "13800138000",
      "name": "张三",
      "title": "主任医师",
      "institutionId": 10,
      "institutionName": "浙江大学医学院附属第一医院",
      "expertBackground": "临床医学",   // ✅ 保留
      "currentLoad": 5
    }
  ]
}
```

---

#### 端点2: GET /api/admin/reviewers/list

**说明**: 兼容路径，变更与端点1相同

**请求参数变更**: 同端点1

**响应数据变更**: 同端点1

---

### 2. 评审任务相关接口

#### 端点3: GET /api/admin/reviews/reviewers

**请求参数变更**:

| 参数 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| institutionId | 可选 | 可选 | 无变化 |
| reviewerGroupCode | 可选 | ❌ 删除 | 删除此参数 |
| interviewGroupCode | 可选 | ❌ 删除 | 删除此参数 |
| expertBackground | 可选 | 可选 | 无变化 |

**请求示例**:

```javascript
// 修改前
GET /api/admin/reviews/reviewers?institutionId=10&reviewerGroupCode=A1&expertBackground=临床医学

// 修改后
GET /api/admin/reviews/reviewers?institutionId=10&expertBackground=临床医学
```

**响应数据变更**: 同端点1

---

#### 端点4: GET /api/admin/reviews/book-scores

**请求参数变更**:

| 参数 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| competitionId | 必填 | 必填 | 无变化 |
| status | 可选 | 可选 | 无变化 |
| reviewerId | 可选 | 可选 | 无变化 |
| institutionId | 可选 | 可选 | 无变化 |
| groupType | 可选 | 可选 | 无变化 |
| reviewerGroupCode | 可选 | ❌ 删除 | 删除此参数 |

**请求示例**:

```javascript
// 修改前
GET /api/admin/reviews/book-scores?competitionId=21&status=SCORED&reviewerGroupCode=A1&groupType=BASIC

// 修改后
GET /api/admin/reviews/book-scores?competitionId=21&status=SCORED&groupType=BASIC
```

**响应数据变更**: 无变化（BookScoreItem不包含评委分组信息）

---

## 前端代码修改指南

### Vue 3 示例

#### 修改前

```vue
<template>
  <div>
    <!-- 筛选条件 -->
    <el-form :inline="true">
      <el-form-item label="机构">
        <el-select v-model="filters.institutionId">
          <el-option label="全部" :value="null" />
          <!-- 机构选项 -->
        </el-select>
      </el-form-item>
      
      <!-- ❌ 删除这两个筛选条件 -->
      <el-form-item label="书审分组">
        <el-select v-model="filters.reviewerGroupCode">
          <el-option label="全部" :value="null" />
          <el-option label="A1" value="A1" />
          <el-option label="B2" value="B2" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="面谈分组">
        <el-select v-model="filters.interviewGroupCode">
          <el-option label="全部" :value="null" />
          <el-option label="A1" value="A1" />
          <el-option label="B2" value="B2" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="专业背景">
        <el-select v-model="filters.expertBackground">
          <el-option label="全部" :value="null" />
          <el-option label="临床医学" value="临床医学" />
          <el-option label="护理学" value="护理学" />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="loadReviewers">查询</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 评委列表 -->
    <el-table :data="reviewers">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="title" label="职称" />
      <el-table-column prop="institutionName" label="所属机构" />
      <!-- ❌ 删除这两列 -->
      <el-table-column prop="reviewerGroupCode" label="书审分组" />
      <el-table-column prop="interviewGroupCode" label="面谈分组" />
      <el-table-column prop="expertBackground" label="专业背景" />
      <el-table-column prop="currentLoad" label="当前负荷" />
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const filters = ref({
  institutionId: null,
  reviewerGroupCode: null,      // ❌ 删除
  interviewGroupCode: null,      // ❌ 删除
  expertBackground: null
});

const reviewers = ref([]);

const loadReviewers = async () => {
  const params = new URLSearchParams();
  if (filters.value.institutionId) params.append('institutionId', filters.value.institutionId);
  if (filters.value.reviewerGroupCode) params.append('reviewerGroupCode', filters.value.reviewerGroupCode);      // ❌ 删除
  if (filters.value.interviewGroupCode) params.append('interviewGroupCode', filters.value.interviewGroupCode);  // ❌ 删除
  if (filters.value.expertBackground) params.append('expertBackground', filters.value.expertBackground);
  
  const response = await fetch(`/api/admin/reviewers?${params}`);
  const result = await response.json();
  reviewers.value = result.data;
};
</script>
```

#### 修改后

```vue
<template>
  <div>
    <!-- 筛选条件 -->
    <el-form :inline="true">
      <el-form-item label="机构">
        <el-select v-model="filters.institutionId">
          <el-option label="全部" :value="null" />
          <!-- 机构选项 -->
        </el-select>
      </el-form-item>
      
      <!-- ✅ 只保留专业背景筛选 -->
      <el-form-item label="专业背景">
        <el-select v-model="filters.expertBackground">
          <el-option label="全部" :value="null" />
          <el-option label="临床医学" value="临床医学" />
          <el-option label="护理学" value="护理学" />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="loadReviewers">查询</el-button>
      </el-form-item>
    </el-form>
    
    <!-- 评委列表 -->
    <el-table :data="reviewers">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="phone" label="手机号" />
      <el-table-column prop="title" label="职称" />
      <el-table-column prop="institutionName" label="所属机构" />
      <!-- ✅ 只保留专业背景列 -->
      <el-table-column prop="expertBackground" label="专业背景" />
      <el-table-column prop="currentLoad" label="当前负荷" />
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const filters = ref({
  institutionId: null,
  expertBackground: null  // ✅ 只保留expertBackground
});

const reviewers = ref([]);

const loadReviewers = async () => {
  const params = new URLSearchParams();
  if (filters.value.institutionId) params.append('institutionId', filters.value.institutionId);
  if (filters.value.expertBackground) params.append('expertBackground', filters.value.expertBackground);
  
  const response = await fetch(`/api/admin/reviewers?${params}`);
  const result = await response.json();
  reviewers.value = result.data;
};
</script>
```

---

### React 示例

#### 修改前

```jsx
import { useState, useEffect } from 'react';
import { Table, Select, Button, Form } from 'antd';

const ReviewerList = () => {
  const [filters, setFilters] = useState({
    institutionId: null,
    reviewerGroupCode: null,      // ❌ 删除
    interviewGroupCode: null,      // ❌ 删除
    expertBackground: null
  });
  
  const [reviewers, setReviewers] = useState([]);
  
  const columns = [
    { title: '姓名', dataIndex: 'name' },
    { title: '手机号', dataIndex: 'phone' },
    { title: '职称', dataIndex: 'title' },
    { title: '所属机构', dataIndex: 'institutionName' },
    { title: '书审分组', dataIndex: 'reviewerGroupCode' },      // ❌ 删除
    { title: '面谈分组', dataIndex: 'interviewGroupCode' },      // ❌ 删除
    { title: '专业背景', dataIndex: 'expertBackground' },
    { title: '当前负荷', dataIndex: 'currentLoad' }
  ];
  
  const loadReviewers = async () => {
    const params = new URLSearchParams();
    if (filters.institutionId) params.append('institutionId', filters.institutionId);
    if (filters.reviewerGroupCode) params.append('reviewerGroupCode', filters.reviewerGroupCode);      // ❌ 删除
    if (filters.interviewGroupCode) params.append('interviewGroupCode', filters.interviewGroupCode);  // ❌ 删除
    if (filters.expertBackground) params.append('expertBackground', filters.expertBackground);
    
    const response = await fetch(`/api/admin/reviewers?${params}`);
    const result = await response.json();
    setReviewers(result.data);
  };
  
  return (
    <div>
      <Form layout="inline">
        <Form.Item label="机构">
          <Select 
            value={filters.institutionId}
            onChange={value => setFilters({...filters, institutionId: value})}
          >
            <Select.Option value={null}>全部</Select.Option>
          </Select>
        </Form.Item>
        
        {/* ❌ 删除这两个筛选条件 */}
        <Form.Item label="书审分组">
          <Select 
            value={filters.reviewerGroupCode}
            onChange={value => setFilters({...filters, reviewerGroupCode: value})}
          >
            <Select.Option value={null}>全部</Select.Option>
            <Select.Option value="A1">A1</Select.Option>
          </Select>
        </Form.Item>
        
        <Form.Item label="面谈分组">
          <Select 
            value={filters.interviewGroupCode}
            onChange={value => setFilters({...filters, interviewGroupCode: value})}
          >
            <Select.Option value={null}>全部</Select.Option>
            <Select.Option value="B2">B2</Select.Option>
          </Select>
        </Form.Item>
        
        <Form.Item label="专业背景">
          <Select 
            value={filters.expertBackground}
            onChange={value => setFilters({...filters, expertBackground: value})}
          >
            <Select.Option value={null}>全部</Select.Option>
            <Select.Option value="临床医学">临床医学</Select.Option>
          </Select>
        </Form.Item>
        
        <Form.Item>
          <Button type="primary" onClick={loadReviewers}>查询</Button>
        </Form.Item>
      </Form>
      
      <Table columns={columns} dataSource={reviewers} rowKey="id" />
    </div>
  );
};
```

#### 修改后

```jsx
import { useState, useEffect } from 'react';
import { Table, Select, Button, Form } from 'antd';

const ReviewerList = () => {
  const [filters, setFilters] = useState({
    institutionId: null,
    expertBackground: null  // ✅ 只保留expertBackground
  });
  
  const [reviewers, setReviewers] = useState([]);
  
  const columns = [
    { title: '姓名', dataIndex: 'name' },
    { title: '手机号', dataIndex: 'phone' },
    { title: '职称', dataIndex: 'title' },
    { title: '所属机构', dataIndex: 'institutionName' },
    // ✅ 只保留专业背景列
    { title: '专业背景', dataIndex: 'expertBackground' },
    { title: '当前负荷', dataIndex: 'currentLoad' }
  ];
  
  const loadReviewers = async () => {
    const params = new URLSearchParams();
    if (filters.institutionId) params.append('institutionId', filters.institutionId);
    if (filters.expertBackground) params.append('expertBackground', filters.expertBackground);
    
    const response = await fetch(`/api/admin/reviewers?${params}`);
    const result = await response.json();
    setReviewers(result.data);
  };
  
  return (
    <div>
      <Form layout="inline">
        <Form.Item label="机构">
          <Select 
            value={filters.institutionId}
            onChange={value => setFilters({...filters, institutionId: value})}
          >
            <Select.Option value={null}>全部</Select.Option>
          </Select>
        </Form.Item>
        
        {/* ✅ 只保留专业背景筛选 */}
        <Form.Item label="专业背景">
          <Select 
            value={filters.expertBackground}
            onChange={value => setFilters({...filters, expertBackground: value})}
          >
            <Select.Option value={null}>全部</Select.Option>
            <Select.Option value="临床医学">临床医学</Select.Option>
            <Select.Option value="护理学">护理学</Select.Option>
          </Select>
        </Form.Item>
        
        <Form.Item>
          <Button type="primary" onClick={loadReviewers}>查询</Button>
        </Form.Item>
      </Form>
      
      <Table columns={columns} dataSource={reviewers} rowKey="id" />
    </div>
  );
};
```

---

## TypeScript 类型定义

### 修改前

```typescript
// 评委列表项
interface ReviewerListItem {
  id: number;
  phone: string;
  name: string;
  title: string;
  institutionId: number | null;
  institutionName: string | null;
  reviewerGroupCode: string | null;      // ❌ 删除
  interviewGroupCode: string | null;      // ❌ 删除
  expertBackground: string | null;
  currentLoad: number;
}

// 筛选条件
interface ReviewerFilters {
  institutionId?: number;
  reviewerGroupCode?: string;            // ❌ 删除
  interviewGroupCode?: string;            // ❌ 删除
  expertBackground?: string;
}
```

### 修改后

```typescript
// 评委列表项
interface ReviewerListItem {
  id: number;
  phone: string;
  name: string;
  title: string;
  institutionId: number | null;
  institutionName: string | null;
  expertBackground: string | null;       // ✅ 保留
  currentLoad: number;
}

// 筛选条件
interface ReviewerFilters {
  institutionId?: number;
  expertBackground?: string;             // ✅ 保留
}
```

---

## 测试建议

### 1. 接口测试

```bash
# 测试评委列表接口
curl -X GET "http://localhost:8080/api/admin/reviewers?institutionId=10&expertBackground=临床医学" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 测试书审得分列表接口
curl -X GET "http://localhost:8080/api/admin/reviews/book-scores?competitionId=21&status=SCORED&groupType=BASIC" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 前端测试清单

- [ ] 评委列表页面：删除分组筛选条件
- [ ] 评委列表页面：删除分组显示列
- [ ] 书审得分页面：删除reviewerGroupCode筛选
- [ ] 评审任务分配页面：确认不依赖分组信息
- [ ] TypeScript类型定义：更新接口类型
- [ ] 单元测试：更新相关测试用例

---

## 常见问题

### Q1: 为什么要删除分组字段？

A: 因为评审专家没有固定分组，可以评审任何分组的项目。分组限制是错误的设计。

### Q2: 如何筛选特定专业的评委？

A: 使用`expertBackground`参数，例如：`?expertBackground=临床医学`

### Q3: 旧的API调用会报错吗？

A: 不会报错，但`reviewerGroupCode`和`interviewGroupCode`参数会被忽略。

### Q4: 数据库中的字段会删除吗？

A: 暂时不删除，只是不再使用。未来版本可能会删除。

---

## 总结

### 删除的参数

- ❌ `reviewerGroupCode` - 书审分组代码
- ❌ `interviewGroupCode` - 面谈分组代码

### 删除的响应字段

- ❌ `reviewerGroupCode` - 书审分组代码
- ❌ `interviewGroupCode` - 面谈分组代码

### 保留的字段

- ✅ `expertBackground` - 专业背景（这才是分配的关键依据）
- ✅ `institutionId` - 所属机构
- ✅ `currentLoad` - 当前负荷

---

**文档版本**: 1.0  
**更新时间**: 2026-02-11  
**状态**: ✅ 已完成
