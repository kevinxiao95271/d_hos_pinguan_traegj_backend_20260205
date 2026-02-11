# 项目负责人职称统计 - API变更说明

## 变更概述

在报名统计API的响应中，新增了 `leaderTitleCounts` 字段，用于统计项目负责人的职称分布。

---

## 受影响的API

### API 1: GET /api/admin/stats/summary

**接口路径**: `/api/admin/stats/summary`

**请求方法**: GET

**请求参数**: 
- `competitionId` (可选): Long - 赛事ID，不传则返回最新赛事的统计

**权限要求**: 需要管理员权限（COMMITTEE角色）

---

## 响应变更详情

### 变更前的响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "competitionId": 23,
    "competitionName": "2023年度品管大赛",
    "registrationCount": 46,
    "toolTypeCount": 3,
    "reviewerCount": 15,
    "reviewerInstitutionCount": 10,
    "bookReviewTaskCount": 50,
    "bookReviewUnscoredCount": 5,
    "regionCounts": {
      "浙江省": 20,
      "江苏省": 15,
      "上海市": 11
    },
    "subjectTypeCounts": {
      "护理": 25,
      "医疗": 15,
      "药学": 6
    },
    "methodCounts": {
      "品管圈": 30,
      "PDCA": 10,
      "六西格玛": 6
    },
    "avgPlan": 8.5,
    "avgProblem": 8.3,
    "avgAction": 8.7,
    "avgSuccess": 8.6,
    "avgReview": 8.4,
    "avgOperation": 8.2,
    "avgPresentation": 8.8
  }
}
```

### 变更后的响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "competitionId": 23,
    "competitionName": "2023年度品管大赛",
    "registrationCount": 46,
    "toolTypeCount": 3,
    "reviewerCount": 15,
    "reviewerInstitutionCount": 10,
    "bookReviewTaskCount": 50,
    "bookReviewUnscoredCount": 5,
    "regionCounts": {
      "浙江省": 20,
      "江苏省": 15,
      "上海市": 11
    },
    "subjectTypeCounts": {
      "护理": 25,
      "医疗": 15,
      "药学": 6
    },
    "methodCounts": {
      "品管圈": 30,
      "PDCA": 10,
      "六西格玛": 6
    },
    "leaderTitleCounts": {           // ← 新增字段
      "主管护师": 40,
      "药师": 28,
      "技师": 21,
      "护师": 15,
      "主治医师": 15,
      "医师": 13,
      "康复治疗师": 3
    },
    "avgPlan": 8.5,
    "avgProblem": 8.3,
    "avgAction": 8.7,
    "avgSuccess": 8.6,
    "avgReview": 8.4,
    "avgOperation": 8.2,
    "avgPresentation": 8.8
  }
}
```

---

## 新增字段说明

### leaderTitleCounts

**类型**: `Map<String, Integer>` / `Object`

**说明**: 项目负责人职称分布统计

**数据结构**:
- Key: 职称名称（String）
- Value: 该职称的项目数量（Integer）

**可能的职称值**:
- 主管护师
- 药师
- 技师
- 护师
- 主治医师
- 医师
- 康复治疗师
- 未知（当职称为空时）

**数据来源**:
- 表: `registration_members`
- 字段: `title`
- 筛选条件: `role = 'PARTICIPANT'`（项目负责人）

**统计规则**:
1. 每个报名项目只统计一个负责人（PARTICIPANT角色）
2. 如果项目有多个PARTICIPANT，只统计第一个
3. 如果职称为空或null，统计为"未知"
4. 职称名称直接使用数据库中的值，不做转换

---

## 兼容性说明

### 向后兼容性

✅ **完全向后兼容**

- 只是新增字段，不影响现有字段
- 现有字段的类型、名称、含义均未改变
- 旧版前端可以正常使用，只是不显示新字段

### 前端适配建议

#### 1. 可选适配（推荐）

前端可以选择性地使用新字段：

```javascript
// 检查字段是否存在
if (data.leaderTitleCounts) {
  // 显示项目负责人职称分布饼图
  renderLeaderTitleChart(data.leaderTitleCounts);
}
```

#### 2. 立即适配

直接使用新字段，不做兼容性检查：

```javascript
// 直接使用（假设后端已更新）
renderLeaderTitleChart(data.leaderTitleCounts);
```

---

## TypeScript 类型定义

### 更新前

```typescript
interface StatsSummaryResponse {
  competitionId: number;
  competitionName: string;
  registrationCount: number;
  toolTypeCount: number;
  reviewerCount: number;
  reviewerInstitutionCount: number;
  bookReviewTaskCount: number;
  bookReviewUnscoredCount: number;
  regionCounts: Record<string, number>;
  subjectTypeCounts: Record<string, number>;
  methodCounts: Record<string, number>;
  avgPlan: number;
  avgProblem: number;
  avgAction: number;
  avgSuccess: number;
  avgReview: number;
  avgOperation: number;
  avgPresentation: number;
}
```

### 更新后

```typescript
interface StatsSummaryResponse {
  competitionId: number;
  competitionName: string;
  registrationCount: number;
  toolTypeCount: number;
  reviewerCount: number;
  reviewerInstitutionCount: number;
  bookReviewTaskCount: number;
  bookReviewUnscoredCount: number;
  regionCounts: Record<string, number>;
  subjectTypeCounts: Record<string, number>;
  methodCounts: Record<string, number>;
  leaderTitleCounts: Record<string, number>;  // ← 新增
  avgPlan: number;
  avgProblem: number;
  avgAction: number;
  avgSuccess: number;
  avgReview: number;
  avgOperation: number;
  avgPresentation: number;
}
```

---

## 变更影响范围

### 后端变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `StatsSummaryResponse.java` | 修改 | 添加 `leaderTitleCounts` 字段 |
| `StatsService.java` | 修改 | 添加统计逻辑，注入 `RegistrationMemberRepository` |

### 前端影响

| 影响范围 | 影响程度 | 说明 |
|---------|---------|------|
| API调用 | 无影响 | 请求参数和URL完全不变 |
| 响应解析 | 无影响 | 只是多了一个字段，不影响现有字段解析 |
| 类型定义 | 需更新 | 如果使用TypeScript，建议更新接口定义 |
| UI展示 | 可选 | 可以选择是否展示新的职称分布图表 |

---

## 测试建议

### 1. 接口测试

```bash
# 测试脚本
curl -X GET "http://localhost:6031/api/admin/stats/summary?competitionId=23" \
  -H "Authorization: Bearer {token}"
```

### 2. 字段验证

验证响应中包含 `leaderTitleCounts` 字段：

```javascript
const response = await fetch('/api/admin/stats/summary?competitionId=23');
const data = await response.json();

console.assert(data.data.leaderTitleCounts !== undefined, 
  'leaderTitleCounts字段应该存在');
console.assert(typeof data.data.leaderTitleCounts === 'object', 
  'leaderTitleCounts应该是对象类型');
```

### 3. 数据验证

验证统计数据的准确性：

```javascript
// 验证总数是否匹配
const totalLeaders = Object.values(data.data.leaderTitleCounts)
  .reduce((sum, count) => sum + count, 0);
  
console.log(`项目负责人总数: ${totalLeaders}`);
console.log(`报名项目总数: ${data.data.registrationCount}`);
// 注意：totalLeaders 可能小于 registrationCount（如果有项目没有负责人）
```

---

## 常见问题

### Q1: 为什么 leaderTitleCounts 的总数可能小于 registrationCount？

A: 因为有些项目可能没有设置PARTICIPANT角色的成员，这些项目不会被统计到职称分布中。

### Q2: "未知"职称是什么意思？

A: 当项目负责人的职称字段为空或null时，会被统计为"未知"。

### Q3: 如果一个项目有多个PARTICIPANT角色的成员，如何统计？

A: 只统计第一个PARTICIPANT角色的成员，避免重复统计。

### Q4: 旧版前端不更新会有问题吗？

A: 不会有问题。新增字段不影响现有功能，旧版前端可以正常使用，只是看不到新的职称分布图表。

### Q5: 职称名称会标准化吗？

A: 不会。职称名称直接使用数据库中的原始值，保持数据的真实性。

---

## 部署注意事项

### 1. 部署顺序

建议按以下顺序部署：

1. ✅ 先部署后端（新增字段）
2. ✅ 再部署前端（使用新字段）

这样可以保证前端部署时，后端已经支持新字段。

### 2. 回滚方案

如果需要回滚：

- 后端回滚：删除 `leaderTitleCounts` 字段即可
- 前端回滚：移除相关图表展示代码

### 3. 灰度发布

可以先在测试环境验证，确认无误后再发布到生产环境。

---

## 总结

### 变更的API

✅ **只有1个API受影响**: `GET /api/admin/stats/summary`

### 参数变更

❌ **请求参数无变更**
- URL路径不变
- 查询参数不变
- 请求头不变
- 请求体不变（GET请求无请求体）

### 响应变更

✅ **响应体新增1个字段**: `leaderTitleCounts`
- 类型: `Map<String, Integer>` / `Object`
- 位置: 在 `methodCounts` 之后，`avgPlan` 之前
- 必填: 是（总是返回，可能为空对象 `{}`）

### 兼容性

✅ **完全向后兼容**
- 不影响现有字段
- 不影响现有功能
- 旧版前端可正常使用

---

**文档版本**: 1.0  
**更新时间**: 2026-02-09  
**变更类型**: 新增功能（向后兼容）
