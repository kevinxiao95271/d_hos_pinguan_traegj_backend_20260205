# 项目负责人职称统计 - API参数变更清单

## 变更概述

本次功能新增只涉及1个API的响应字段变更，不涉及任何请求参数的变更。

---

## 受影响的API列表

### ✅ 只有1个API受影响

| API | 方法 | 路径 | 变更类型 | 影响范围 |
|-----|------|------|---------|---------|
| 报名统计 | GET | `/api/admin/stats/summary` | 响应新增字段 | 响应体 |

---

## API详细变更

### API 1: 报名统计接口

#### 基本信息

- **接口名称**: 报名统计
- **接口路径**: `GET /api/admin/stats/summary`
- **权限要求**: 管理员（COMMITTEE角色）
- **变更类型**: 响应新增字段

#### 请求参数

❌ **无变更**

| 参数名 | 类型 | 必填 | 说明 | 变更状态 |
|--------|------|------|------|---------|
| competitionId | Long | 否 | 赛事ID，不传则返回最新赛事 | 无变更 |

#### 请求示例

```bash
# 查询最新赛事统计（无变更）
GET /api/admin/stats/summary

# 查询指定赛事统计（无变更）
GET /api/admin/stats/summary?competitionId=21
```

#### 响应参数变更

✅ **新增1个字段**

| 字段路径 | 类型 | 变更类型 | 说明 |
|---------|------|---------|------|
| `data.leaderTitleCounts` | `Map<String, Integer>` | 新增 | 项目负责人职称分布统计 |

#### 响应字段完整列表

| 字段名 | 类型 | 说明 | 变更状态 |
|--------|------|------|---------|
| competitionId | Long | 赛事ID | 无变更 |
| competitionName | String | 赛事名称 | 无变更 |
| registrationCount | Integer | 报名总数 | 无变更 |
| toolTypeCount | Integer | 品管工具类型数 | 无变更 |
| reviewerCount | Integer | 评委总数 | 无变更 |
| reviewerInstitutionCount | Integer | 评委机构数 | 无变更 |
| bookReviewTaskCount | Integer | 书审任务总数 | 无变更 |
| bookReviewUnscoredCount | Integer | 书审未评分数 | 无变更 |
| regionCounts | Map<String, Integer> | 地区分布 | 无变更 |
| subjectTypeCounts | Map<String, Integer> | 主题类型分布 | 无变更 |
| methodCounts | Map<String, Integer> | 品管工具分布 | 无变更 |
| **leaderTitleCounts** | **Map<String, Integer>** | **项目负责人职称分布** | **新增** |
| avgPlan | Double | 计划平均分 | 无变更 |
| avgProblem | Double | 问题平均分 | 无变更 |
| avgAction | Double | 行动平均分 | 无变更 |
| avgSuccess | Double | 成功平均分 | 无变更 |
| avgReview | Double | 评审平均分 | 无变更 |
| avgOperation | Double | 操作平均分 | 无变更 |
| avgPresentation | Double | 展示平均分 | 无变更 |

#### 新增字段详细说明

**字段名**: `leaderTitleCounts`

**类型**: `Map<String, Integer>` / `Object` / `Record<string, number>`

**说明**: 项目负责人职称分布统计

**数据结构**:
```typescript
{
  [职称名称: string]: 项目数量: number
}
```

**示例值**:
```json
{
  "主管护师": 19,
  "主治医师": 10,
  "药师": 9,
  "技师": 4,
  "医师": 3,
  "未知": 1
}
```

**可能的职称值**:
- 主管护师
- 主治医师
- 药师
- 技师
- 医师
- 护师
- 康复治疗师
- 未知（职称为空时）
- 其他任意职称名称

**数据来源**:
- 表: `registration_members`
- 字段: `title`
- 筛选条件: `role = 'PARTICIPANT'`

**统计规则**:
1. 每个报名项目只统计一个负责人
2. 如果项目有多个PARTICIPANT，只统计第一个
3. 职称为空或null时，统计为"未知"
4. 职称名称使用数据库原始值，不做转换

**特殊情况**:
- 如果赛事没有报名项目，返回空对象 `{}`
- 如果所有项目都没有负责人，返回空对象 `{}`
- 职称总数可能小于报名总数（有些项目没有负责人）

#### 响应示例对比

**变更前**:
```json
{
  "success": true,
  "data": {
    "competitionId": 21,
    "competitionName": "2026浙江品管大赛",
    "registrationCount": 46,
    "toolTypeCount": 22,
    "reviewerCount": 21,
    "reviewerInstitutionCount": 11,
    "bookReviewTaskCount": 6,
    "bookReviewUnscoredCount": 5,
    "regionCounts": {
      "杭州": 18,
      "舟山": 15,
      "宁波": 3
    },
    "subjectTypeCounts": {
      "病人照护": 10,
      "医疗信息": 8,
      "其他": 6
    },
    "methodCounts": {
      "流程改造": 8,
      "品管圈-课题达成": 7,
      "PDCA": 6
    },
    "avgPlan": 18.0,
    "avgProblem": 17.0,
    "avgAction": 19.0,
    "avgSuccess": 18.0,
    "avgReview": 16.0,
    "avgOperation": 0.0,
    "avgPresentation": 0.0
  },
  "message": null
}
```

**变更后**:
```json
{
  "success": true,
  "data": {
    "competitionId": 21,
    "competitionName": "2026浙江品管大赛",
    "registrationCount": 46,
    "toolTypeCount": 22,
    "reviewerCount": 21,
    "reviewerInstitutionCount": 11,
    "bookReviewTaskCount": 6,
    "bookReviewUnscoredCount": 5,
    "regionCounts": {
      "杭州": 18,
      "舟山": 15,
      "宁波": 3
    },
    "subjectTypeCounts": {
      "病人照护": 10,
      "医疗信息": 8,
      "其他": 6
    },
    "methodCounts": {
      "流程改造": 8,
      "品管圈-课题达成": 7,
      "PDCA": 6
    },
    "leaderTitleCounts": {           // ← 新增字段
      "主管护师": 19,
      "主治医师": 10,
      "药师": 9,
      "技师": 4,
      "医师": 3,
      "未知": 1
    },
    "avgPlan": 18.0,
    "avgProblem": 17.0,
    "avgAction": 19.0,
    "avgSuccess": 18.0,
    "avgReview": 16.0,
    "avgOperation": 0.0,
    "avgPresentation": 0.0
  },
  "message": null
}
```

---

## 参数类型变更汇总

### 请求参数变更

❌ **无任何请求参数变更**

| API | 参数名 | 变更前类型 | 变更后类型 | 变更说明 |
|-----|--------|-----------|-----------|---------|
| - | - | - | - | 无变更 |

### 响应参数变更

✅ **只有1个响应字段新增**

| API | 字段路径 | 变更前类型 | 变更后类型 | 变更说明 |
|-----|---------|-----------|-----------|---------|
| GET /api/admin/stats/summary | data.leaderTitleCounts | 不存在 | Map<String, Integer> | 新增字段 |

---

## 兼容性分析

### 向后兼容性

✅ **完全向后兼容**

**原因**:
1. 只是新增字段，不影响现有字段
2. 现有字段的类型、名称、含义均未改变
3. 请求参数完全不变
4. 旧版前端可以正常使用，只是不显示新字段

### 前端适配要求

#### 必须适配

❌ **无强制适配要求**

#### 可选适配

✅ **可选择性使用新字段**

```typescript
// 检查字段是否存在
if (data.leaderTitleCounts) {
  // 显示项目负责人职称分布饼图
  renderLeaderTitleChart(data.leaderTitleCounts);
}
```

---

## TypeScript 类型定义变更

### 变更前

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

### 变更后

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

## 测试建议

### 1. 接口测试

```bash
# 测试最新赛事
curl -X GET "http://localhost:6031/api/admin/stats/summary" \
  -H "Authorization: Bearer {token}"

# 测试指定赛事
curl -X GET "http://localhost:6031/api/admin/stats/summary?competitionId=21" \
  -H "Authorization: Bearer {token}"
```

### 2. 字段验证

```javascript
// 验证新字段存在
console.assert(data.leaderTitleCounts !== undefined);
console.assert(typeof data.leaderTitleCounts === 'object');

// 验证数据类型
Object.entries(data.leaderTitleCounts).forEach(([title, count]) => {
  console.assert(typeof title === 'string');
  console.assert(typeof count === 'number');
  console.assert(count >= 0);
});
```

### 3. 边界测试

- 测试没有报名项目的赛事（应返回空对象 `{}`）
- 测试所有项目都没有负责人的赛事（应返回空对象 `{}`）
- 测试职称为空的项目（应统计为"未知"）

---

## 部署检查清单

### 部署前

- [x] 代码编译通过
- [x] 单元测试通过
- [x] 接口测试通过
- [x] 文档更新完成

### 部署后

- [ ] 验证API响应包含新字段
- [ ] 验证数据统计准确性
- [ ] 验证旧版前端正常工作
- [ ] 验证新版前端正确显示

---

## 常见问题

### Q1: 这次变更会影响多少个API？

A: 只影响1个API：`GET /api/admin/stats/summary`

### Q2: 请求参数有变化吗？

A: 没有。请求参数完全不变。

### Q3: 响应参数类型有变化吗？

A: 没有。只是新增了1个字段，现有字段的类型都没有变化。

### Q4: 旧版前端需要强制升级吗？

A: 不需要。新增字段不影响现有功能，旧版前端可以继续使用。

### Q5: 如何验证新字段是否生效？

A: 调用API后检查响应中是否包含 `leaderTitleCounts` 字段。

---

## 总结

### 变更范围

- **受影响API数量**: 1个
- **请求参数变更**: 0个
- **响应参数变更**: 1个（新增）
- **参数类型变更**: 0个

### 兼容性

- **向后兼容**: ✅ 是
- **强制升级**: ❌ 否
- **影响范围**: 最小

### 风险评估

- **风险等级**: 低
- **影响范围**: 仅统计API
- **回滚难度**: 低

---

**文档版本**: 1.0  
**更新时间**: 2026-02-11  
**变更类型**: 新增功能（向后兼容）
