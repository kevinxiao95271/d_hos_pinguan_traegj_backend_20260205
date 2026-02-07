# 报名竞赛ID返回问题修复

> 修复时间：2026-02-06  
> 问题：前端无法判断用户已报名哪些赛事

---

## 🔍 问题诊断

### 用户发现的问题

前端显示"我的报名"列表时，能看到报名记录，但**所有赛事都显示"立即报名"按钮**，包括已经报过名的赛事。

### 根本原因

**API返回的报名数据中 `competitionId` 字段为 `null`**

```json
{
  "id": 116,
  "projectName": "门诊预约体验提升-11",
  "competitionId": null,  // ❌ 问题：应该是21，实际是null
  "status": "APPROVED"
}
```

### 技术原因

`Registration` 实体类中：
- `competition` 字段被标记为 `@JsonIgnore`
- 导致序列化时不返回竞赛信息
- 数据库中 `competition_id` 有值（21），但API不返回

---

## ✅ 修复方案

### 修改 Registration.java

添加了 `competitionId`、`institutionId`、`applicantId` 三个字段：

```java
@Column(name = "competition_id", insertable = false, updatable = false)
private Long competitionId;

@Column(name = "institution_id", insertable = false, updatable = false)
private Long institutionId;

@Column(name = "applicant_id", insertable = false, updatable = false)
private Long applicantId;
```

**说明**：
- `insertable = false, updatable = false`：这些字段是只读的，通过关联对象（`competition`、`institution`、`applicant`）来管理
- 这样既保留了JPA的关联关系，又能在JSON序列化时返回ID值

---

## 📊 修复前后对比

### 修复前

```json
GET /api/registrations/my

{
  "code": 200,
  "data": [
    {
      "id": 116,
      "projectName": "门诊预约体验提升-11",
      "competitionId": null,     // ❌ 空值
      "institutionId": null,     // ❌ 空值
      "applicantId": null,       // ❌ 空值
      "status": "APPROVED"
    }
  ]
}
```

**影响**：
- 前端无法知道这个报名属于哪个赛事
- 无法判断赛事是否已报名
- 所有赛事都显示"立即报名"

### 修复后

```json
GET /api/registrations/my

{
  "code": 200,
  "data": [
    {
      "id": 116,
      "projectName": "门诊预约体验提升-11",
      "competitionId": 21,       // ✅ 正确返回赛事ID
      "institutionId": 11,       // ✅ 正确返回机构ID
      "applicantId": 127,        // ✅ 正确返回申请人ID
      "status": "APPROVED"
    }
  ]
}
```

**效果**：
- 前端可以知道报名属于赛事21
- 可以判断赛事21已报名
- 赛事21显示"查看报名"，其他赛事显示"立即报名"

---

## 🎯 前端使用指引

### 1. 获取用户报名列表

```javascript
const myRegistrations = await axios.get('/api/registrations/my')
const registeredCompetitionIds = myRegistrations.data.data.map(r => r.competitionId)
// 例如：[21]
```

### 2. 判断赛事是否已报名

```javascript
const competitions = await axios.get('/api/competitions')

competitions.data.data.forEach(competition => {
  const isRegistered = registeredCompetitionIds.includes(competition.id)
  
  if (isRegistered) {
    // 显示"查看报名"按钮
    competition.buttonText = '查看报名'
    competition.buttonAction = () => viewRegistration(competition.id)
  } else {
    // 显示"立即报名"按钮
    competition.buttonText = '立即报名'
    competition.buttonAction = () => createRegistration(competition.id)
  }
})
```

### 3. Vue示例代码

```vue
<template>
  <div v-for="competition in competitions" :key="competition.id">
    <h3>{{ competition.name }}</h3>
    <el-button 
      :type="isRegistered(competition.id) ? 'success' : 'primary'"
      @click="handleAction(competition.id)"
    >
      {{ isRegistered(competition.id) ? '查看报名' : '立即报名' }}
    </el-button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const competitions = ref([])
const myRegistrations = ref([])

const isRegistered = (competitionId) => {
  return myRegistrations.value.some(r => r.competitionId === competitionId)
}

const handleAction = (competitionId) => {
  if (isRegistered(competitionId)) {
    // 查看报名
    const registration = myRegistrations.value.find(r => r.competitionId === competitionId)
    router.push(`/contestant/registration/${registration.id}`)
  } else {
    // 立即报名
    router.push(`/contestant/register?competitionId=${competitionId}`)
  }
}

onMounted(async () => {
  // 同时加载赛事列表和我的报名
  const [comps, regs] = await Promise.all([
    axios.get('/api/competitions'),
    axios.get('/api/registrations/my')
  ])
  competitions.value = comps.data.data
  myRegistrations.value = regs.data.data
})
</script>
```

---

## ✅ 测试验证

### 测试脚本

```bash
python scripts/check_registration_competition_id.py
```

### 测试结果

```
✅ 数据库数据正常
  - 总报名数: 38
  - 有竞赛ID: 38 (100%)
  - 无竞赛ID: 0 (0%)

✅ API返回正常
  - 报名ID 116: 门诊预约体验提升-11
  - 竞赛ID: 21 ✅ (之前是null)
  - 状态: APPROVED
```

### 测试账号

使用推荐测试账号验证：

| 姓名 | 手机号 | 已报名赛事 | 报名ID |
|------|--------|-----------|--------|
| 参赛者11 | 13966000011 | 赛事21 | 116 |
| 参赛者12 | 13966000012 | 赛事21 | 117 |
| 参赛者13 | 13966000013 | 赛事21 | 118 |

登录后：
- 调用 `GET /api/registrations/my`
- 应该看到 `competitionId: 21`
- 前端可以判断赛事21已报名

---

## 📝 影响范围

### 影响的API

1. **GET /api/registrations/my** ⭐ 主要影响
   - 返回 `competitionId`、`institutionId`、`applicantId`
   
2. **GET /api/registrations** 
   - 按赛事查询报名列表
   - 也会返回这些ID字段

3. **GET /api/registrations/{id}**
   - 报名详情
   - 返回完整的 `registration` 对象（包含ID字段）

### 不影响的功能

- ✅ 创建报名：后端仍然通过关联对象保存
- ✅ 更新报名：后端仍然通过关联对象更新
- ✅ 数据库结构：无需修改

---

## ⚠️ 注意事项

1. **字段是只读的**
   - `competitionId`、`institutionId`、`applicantId` 仅用于展示
   - 不能通过这些字段修改关联关系
   - 必须通过 `competition`、`institution`、`applicant` 对象操作

2. **向后兼容**
   - 旧的关联对象字段仍然存在
   - 新增的ID字段不影响现有功能
   - 纯粹是为了API返回方便

3. **前端必须使用**
   - 前端现在可以通过 `competitionId` 判断已报名赛事
   - 必须实现报名状态的判断逻辑
   - 避免用户重复报名同一赛事

---

## 🎉 修复完成

### 问题

- ❌ API返回的 `competitionId` 为 `null`
- ❌ 前端无法判断已报名赛事
- ❌ 所有赛事都显示"立即报名"

### 解决

- ✅ API正确返回 `competitionId`
- ✅ 前端可以判断已报名赛事
- ✅ 已报名赛事显示"查看报名"

### 后续

- 📋 前端需要实现报名状态判断逻辑
- 📋 避免用户重复报名同一赛事
- 📋 提供更好的用户体验

---

## 📅 修复记录

- **修复日期**：2026-02-06
- **修复内容**：添加 `competitionId`、`institutionId`、`applicantId` 字段
- **影响文件**：`src/main/java/com/trae/pinguan/domain/entity/Registration.java`
- **测试状态**：✅ 已验证通过
- **部署状态**：✅ 已重启服务器

**修复完成，API现在正确返回竞赛ID！** 🎉
