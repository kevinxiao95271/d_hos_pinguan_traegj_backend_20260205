# 评审专家管理API - 运维使用指南

## 概述

运维(OPS)角色可以完整管理评审专家，包括查询、新增、修改、删除等操作。

## 数据来源说明

评委数据存储在 `user_accounts` 表中，通过 `role` 字段区分用户类型：

| 数据库表 | Entity类 | 角色标识 |
|---------|---------|---------|
| user_accounts | UserAccount | role = 'REVIEWER' |

**字段映射关系**：

| API字段 | 数据库字段 | 说明 |
|---------|-----------|------|
| id | id | 评委ID |
| phone | phone | 手机号（登录账号） |
| name | name | 姓名 |
| title | title | 职称 |
| institutionId | institution_id | 所属机构ID |
| institutionName | - | 从institutions表JOIN获取 |
| reviewerGroupCode | reviewer_group_code | 书审分组代码 |
| interviewGroupCode | interview_group_code | 面谈分组代码 |
| expertBackground | expert_background | 专家背景/专业领域 |
| currentLoad | - | 实时计算（COUNT review_tasks） |

**实际数据示例**（来自数据库）：
```
ID: 2
  手机号: 13900000001
  姓名: 王建国
  职称: Test Title
  角色: REVIEWER
  机构ID: None
  书审分组: A1
  面谈分组: A1
  专家背景: MEDICAL
```

## 权限说明

以下角色可以访问评审专家管理接口：
- ✅ OPS (运维)
- ✅ COMMITTEE (组委会)
- ✅ COMMITTEE_ADMIN (组委会管理员)

## API接口列表

### 1. 评委列表

**接口**: `GET /api/admin/reviewers`

**权限**: OPS / COMMITTEE / COMMITTEE_ADMIN

**参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| competitionId | Long | 否 | 赛事ID (当前未使用) |
| institutionId | Long | 否 | 机构ID筛选 |
| reviewerGroupCode | String | 否 | 评委分组代码筛选 |
| interviewGroupCode | String | 否 | 面谈分组代码筛选 |
| expertBackground | String | 否 | 专家背景筛选 |

**响应示例**:
```json
{
  "success": true,
  "message": "操作成功",
  "data": [
    {
      "id": 1,
      "phone": "13800138001",
      "name": "张医生",
      "title": "主任医师",
      "institutionId": 10,
      "institutionName": "浙江省人民医院",
      "reviewerGroupCode": "A",
      "interviewGroupCode": "I1",
      "expertBackground": "医疗质量管理",
      "currentLoad": 5
    }
  ]
}
```

**字段说明**:
- `id`: 评委ID
- `phone`: 手机号（登录账号）
- `name`: 姓名
- `title`: 职称
- `institutionId`: 所属机构ID
- `institutionName`: 所属机构名称
- `reviewerGroupCode`: 书审分组代码
- `interviewGroupCode`: 面谈分组代码
- `expertBackground`: 专家背景/专业领域
- `currentLoad`: 当前负荷（已分配的评审任务数）

### 2. 评委详情

**接口**: `GET /api/admin/reviewers/{id}`

**权限**: OPS / COMMITTEE / COMMITTEE_ADMIN

**路径参数**:
- `id`: 评委ID

**响应示例**:
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "id": 1,
    "phone": "13800138001",
    "name": "张医生",
    "title": "主任医师",
    "institutionId": 10,
    "reviewerGroupCode": "A",
    "interviewGroupCode": "I1",
    "expertBackground": "医疗质量管理",
    "role": "REVIEWER",
    "createdAt": "2026-01-15T10:30:00"
  }
}
```

### 3. 新增评委

**接口**: `POST /api/admin/reviewers`

**权限**: OPS / COMMITTEE / COMMITTEE_ADMIN

**请求体**:
```json
{
  "phone": "13800138002",
  "name": "李医生",
  "title": "副主任医师",
  "institutionId": 10,
  "reviewerGroupCode": "B",
  "interviewGroupCode": "I2",
  "expertBackground": "护理质量管理"
}
```

**字段说明**:
| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| phone | String | 是 | 手机号（11位，作为登录账号） |
| name | String | 是 | 姓名 |
| title | String | 否 | 职称 |
| institutionId | Long | 否 | 所属机构ID |
| reviewerGroupCode | String | 否 | 书审分组代码 |
| interviewGroupCode | String | 否 | 面谈分组代码 |
| expertBackground | String | 否 | 专家背景/专业领域 |

**响应示例**:
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "id": 100,
    "phone": "13800138002",
    "name": "李医生",
    "title": "副主任医师",
    "institutionId": 10,
    "reviewerGroupCode": "B",
    "interviewGroupCode": "I2",
    "expertBackground": "护理质量管理",
    "role": "REVIEWER",
    "createdAt": "2026-02-11T15:30:00"
  }
}
```

**注意事项**:
1. 手机号必须唯一，不能重复
2. 新增评委的默认密码通常为手机号后6位或统一密码
3. 评委角色自动设置为 REVIEWER

### 4. 更新评委

**接口**: `PUT /api/admin/reviewers/{id}`

**权限**: OPS / COMMITTEE / COMMITTEE_ADMIN

**路径参数**:
- `id`: 评委ID

**请求体**:
```json
{
  "phone": "13800138002",
  "name": "李医生",
  "title": "主任医师",
  "institutionId": 10,
  "reviewerGroupCode": "A",
  "interviewGroupCode": "I1",
  "expertBackground": "医疗质量管理、护理质量管理"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "id": 100,
    "phone": "13800138002",
    "name": "李医生",
    "title": "主任医师",
    "institutionId": 10,
    "reviewerGroupCode": "A",
    "interviewGroupCode": "I1",
    "expertBackground": "医疗质量管理、护理质量管理",
    "role": "REVIEWER",
    "createdAt": "2026-02-11T15:30:00"
  }
}
```

**注意事项**:
1. 可以修改评委的所有信息
2. 修改手机号时需确保新手机号未被使用
3. 修改分组代码会影响评审任务分配

### 5. 删除评委

**接口**: `DELETE /api/admin/reviewers/{id}`

**权限**: OPS / COMMITTEE / COMMITTEE_ADMIN

**路径参数**:
- `id`: 评委ID

**响应示例**:
```json
{
  "success": true,
  "message": "操作成功",
  "data": null
}
```

**注意事项**:
1. ⚠️ 删除操作不可恢复
2. ⚠️ 如果评委已有评审任务，建议先处理任务再删除
3. 建议使用软删除（禁用账号）而非物理删除

### 6. 评委列表（兼容路径）

**接口**: `GET /api/admin/reviewers/list`

**说明**: 与 `GET /api/admin/reviewers` 功能完全相同，提供兼容性支持

## 使用场景

### 场景1: 批量导入评委

1. 准备评委数据（Excel/CSV）
2. 逐条调用新增接口
3. 记录导入结果

```bash
# 示例：使用curl批量导入
for reviewer in $(cat reviewers.json | jq -c '.[]'); do
  curl -X POST http://localhost:6031/api/admin/reviewers \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$reviewer"
done
```

### 场景2: 按机构查询评委

```bash
# 查询某个机构的所有评委
curl "http://localhost:6031/api/admin/reviewers?institutionId=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 场景3: 按分组查询评委

```bash
# 查询A组的所有评委
curl "http://localhost:6031/api/admin/reviewers?reviewerGroupCode=A" \
  -H "Authorization: Bearer $TOKEN"
```

### 场景4: 查看评委负荷

```bash
# 查询所有评委及其当前负荷
curl "http://localhost:6031/api/admin/reviewers" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data[] | {name, currentLoad}'
```

### 场景5: 更新评委分组

```bash
# 将评委从A组调整到B组
curl -X PUT http://localhost:6031/api/admin/reviewers/100 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138002",
    "name": "李医生",
    "title": "主任医师",
    "institutionId": 10,
    "reviewerGroupCode": "B",
    "interviewGroupCode": "I2",
    "expertBackground": "医疗质量管理"
  }'
```

## 数据字典

### 评委分组代码 (reviewerGroupCode)

书审阶段的分组代码，用于评审任务分配：
- A, B, C, D, E, F, G, H, I, J...
- 根据实际需要设置

### 面谈分组代码 (interviewGroupCode)

面谈阶段的分组代码：
- I1, I2, I3, I4...
- 根据面谈场次设置

### 专家背景 (expertBackground)

评委的专业领域，可选值：
- 医疗质量管理
- 护理质量管理
- 医技质量管理
- 药学质量管理
- 医院管理
- 其他

## 前端集成示例

### Vue 3 示例

```vue
<template>
  <div>
    <!-- 评委列表 -->
    <el-table :data="reviewers" border>
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="title" label="职称" />
      <el-table-column prop="institutionName" label="所属机构" />
      <el-table-column prop="reviewerGroupCode" label="书审分组" />
      <el-table-column prop="currentLoad" label="当前负荷" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button @click="editReviewer(row)">编辑</el-button>
          <el-button type="danger" @click="deleteReviewer(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑评委' : '新增评委'">
      <el-form :model="form" label-width="120px">
        <el-form-item label="手机号" required>
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="职称">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="所属机构">
          <el-select v-model="form.institutionId">
            <el-option v-for="inst in institutions" :key="inst.id" 
              :label="inst.name" :value="inst.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="书审分组">
          <el-input v-model="form.reviewerGroupCode" />
        </el-form-item>
        <el-form-item label="面谈分组">
          <el-input v-model="form.interviewGroupCode" />
        </el-form-item>
        <el-form-item label="专家背景">
          <el-input v-model="form.expertBackground" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveReviewer">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const reviewers = ref([]);
const institutions = ref([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const form = ref({
  phone: '',
  name: '',
  title: '',
  institutionId: null,
  reviewerGroupCode: '',
  interviewGroupCode: '',
  expertBackground: ''
});

// 加载评委列表
async function loadReviewers() {
  const response = await axios.get('/api/admin/reviewers');
  if (response.data.success) {
    reviewers.value = response.data.data;
  }
}

// 新增评委
function addReviewer() {
  isEdit.value = false;
  form.value = {
    phone: '',
    name: '',
    title: '',
    institutionId: null,
    reviewerGroupCode: '',
    interviewGroupCode: '',
    expertBackground: ''
  };
  dialogVisible.value = true;
}

// 编辑评委
function editReviewer(reviewer) {
  isEdit.value = true;
  form.value = { ...reviewer };
  dialogVisible.value = true;
}

// 保存评委
async function saveReviewer() {
  try {
    if (isEdit.value) {
      await axios.put(`/api/admin/reviewers/${form.value.id}`, form.value);
    } else {
      await axios.post('/api/admin/reviewers', form.value);
    }
    dialogVisible.value = false;
    loadReviewers();
  } catch (error) {
    console.error('保存失败:', error);
  }
}

// 删除评委
async function deleteReviewer(id) {
  if (confirm('确定要删除这个评委吗？')) {
    await axios.delete(`/api/admin/reviewers/${id}`);
    loadReviewers();
  }
}

onMounted(() => {
  loadReviewers();
});
</script>
```

## 测试脚本

创建测试脚本验证API功能：

```bash
# scripts/test_reviewer_management.py
python scripts/test_reviewer_management.py
```

## 常见问题

### Q1: 运维角色无法访问评委管理接口？

**A**: 检查以下几点：
1. 确认用户角色是否为 OPS
2. 确认JWT token是否有效
3. 确认请求头中是否包含 `Authorization: Bearer {token}`

### Q2: 新增评委时提示手机号已存在？

**A**: 手机号是唯一标识，不能重复。请检查：
1. 该手机号是否已被其他用户使用
2. 是否需要更新现有评委而非新增

### Q3: 删除评委后能否恢复？

**A**: 当前删除是物理删除，无法恢复。建议：
1. 删除前做好数据备份
2. 考虑使用禁用功能代替删除
3. 如需恢复，联系数据库管理员

### Q4: 如何批量导入评委？

**A**: 
1. 准备JSON格式的评委数据
2. 使用脚本循环调用新增接口
3. 或者联系开发人员添加批量导入接口

## 总结

✅ **运维OPS角色完全支持评审专家管理**

现有API提供了完整的CRUD功能：
- ✅ 查询评委列表（支持多条件筛选）
- ✅ 查看评委详情
- ✅ 新增评委
- ✅ 更新评委信息
- ✅ 删除评委

运维人员可以通过这些接口完成所有评审专家的管理工作。

---

**文档版本**: 1.0  
**更新时间**: 2026-02-11  
**适用角色**: OPS / COMMITTEE / COMMITTEE_ADMIN
