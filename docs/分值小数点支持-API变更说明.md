# 分值小数点支持 - API变更说明

## 变更概述

**生效日期**: 2026-02-10  
**变更类型**: 字段类型变更  
**影响范围**: 6个API接口

所有评分相关字段从**整数**改为**小数**（支持1位小数）

---

## 数据类型变更

### 变更前
```json
{
  "plan": 18,           // Integer 整数
  "problem": 17,        // Integer 整数
  "action": 19,         // Integer 整数
  "total": 88           // Integer 整数
}
```

### 变更后
```json
{
  "plan": 18.5,         // Double 小数（1位）
  "problem": 17.8,      // Double 小数（1位）
  "action": 19.2,       // Double 小数（1位）
  "total": 93.0         // Double 小数（1位）
}
```

---

## 涉及的API接口

### 1. 提交评分

**接口**: `POST /api/reviews/scores`

**请求体变更**:
```json
{
  "reviewTaskId": 101,
  "plan": 18.5,          // 改为小数，支持0.1精度
  "problem": 17.8,       // 改为小数
  "action": 19.2,        // 改为小数
  "success": 14.5,       // 改为小数
  "review": 9.8,         // 改为小数
  "operation": 9.5,      // 改为小数
  "presentation": 4.7,   // 改为小数
  "highlight": "优点",
  "weakness": "缺点"
}
```

**响应体变更**:
```json
{
  "success": true,
  "data": {
    "id": 49,
    "plan": 18.5,        // 返回小数
    "problem": 17.8,     // 返回小数
    "action": 19.2,      // 返回小数
    "success": 14.5,
    "review": 9.8,
    "operation": 9.5,
    "presentation": 4.7,
    "total": 94.0,       // 自动计算的总分
    "highlight": "优点",
    "weakness": "缺点",
    "submittedAt": "2026-02-10T17:00:00"
  }
}
```

**校验规则**:
- 每个分值字段: 0.0 ~ 100.0
- 支持1位小数（如 8.5）
- 总分自动计算

---

### 2. 查询评分详情

**接口**: `GET /api/reviews/scores/{reviewTaskId}`

**响应体变更**:
```json
{
  "success": true,
  "data": {
    "id": 49,
    "plan": 18.5,        // 小数类型
    "problem": 17.8,
    "action": 19.2,
    "success": 14.5,
    "review": 9.8,
    "operation": 9.5,
    "presentation": 4.7,
    "total": 94.0,
    "highlight": "优点",
    "weakness": "缺点",
    "submittedAt": "2026-02-10T17:00:00"
  }
}
```

---

### 3. 阶段评分汇总

**接口**: `GET /api/reviews/summary`

**参数**: 
- `competitionId`: 赛事ID
- `stage`: 评审阶段

**响应体变更**:
```json
{
  "success": true,
  "data": [
    {
      "registrationId": 101,
      "projectName": "项目A",
      "institutionName": "某医院",
      "groupType": "GENERAL",
      "stage": "BOOK",
      "avgTotal": 88.5,      // 平均总分，小数类型
      "scoresCount": 3
    }
  ]
}
```

---

### 4. 阶段评分排名

**接口**: `GET /api/reviews/rankings`

**参数**:
- `competitionId`: 赛事ID
- `stage`: 评审阶段
- `groupType`: 组别（可选）

**响应体变更**:
```json
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "registrationId": 101,
      "projectName": "项目A",
      "institutionName": "某医院",
      "groupType": "GENERAL",
      "stage": "BOOK",
      "avgTotal": 92.5       // 平均总分，小数类型
    }
  ]
}
```

---

### 5. 报名评审详情

**接口**: `GET /api/registrations/{id}/review-details`

**响应体变更**:
```json
{
  "success": true,
  "data": [
    {
      "stage": "BOOK",
      "taskCount": 3,
      "scoredCount": 3,
      "avgPlan": 18.5,           // 平均分，小数类型
      "avgProblem": 17.8,        // 平均分，小数类型
      "avgAction": 19.2,         // 平均分，小数类型
      "avgSuccess": 14.5,
      "avgReview": 9.8,
      "avgOperation": 9.5,
      "avgPresentation": 4.7,
      "avgTotal": 94.0,          // 平均总分，小数类型
      "highlights": ["优点1", "优点2"],
      "weaknesses": ["缺点1", "缺点2"]
    }
  ]
}
```

---

### 6. 统计汇总

**接口**: `GET /api/admin/stats/summary`

**参数**:
- `competitionId`: 赛事ID（可选，不传则使用最新赛事）

**响应体变更**:
```json
{
  "success": true,
  "data": {
    "competitionId": 21,
    "competitionName": "2026浙江品管大赛",
    "registrationCount": 45,
    "avgPlan": 18.5,           // 平均分，小数类型
    "avgProblem": 17.8,        // 平均分，小数类型
    "avgAction": 19.2,         // 平均分，小数类型
    "avgSuccess": 14.5,
    "avgReview": 9.8,
    "avgOperation": 9.5,
    "avgPresentation": 4.7,
    "regionCounts": {...},
    "subjectTypeCounts": {...},
    "methodCounts": {...},
    "leaderTitleCounts": {...}
  }
}
```

---

## 前端适配要点

### 1. 输入框配置

```html
<!-- 支持小数输入 -->
<input 
  type="number" 
  step="0.1"           <!-- 步长0.1 -->
  min="0" 
  max="100"
  placeholder="请输入分值（如 8.5）"
/>
```

### 2. 数据类型处理

```javascript
// JavaScript中接收到的分值是number类型
const score = response.data.plan;  // 18.5 (number)

// 显示时保留1位小数
const displayScore = score.toFixed(1);  // "18.5"
```

### 3. 表单验证

```javascript
// 验证分值范围和精度
function validateScore(value) {
  const num = parseFloat(value);
  
  // 范围检查
  if (num < 0 || num > 100) {
    return "分值必须在0-100之间";
  }
  
  // 精度检查（最多1位小数）
  if (!/^\d+(\.\d{1})?$/.test(value)) {
    return "分值最多保留1位小数";
  }
  
  return null;  // 验证通过
}
```

### 4. 总分计算

```javascript
// 前端计算总分（用于实时显示）
function calculateTotal(scores) {
  const total = scores.plan + scores.problem + scores.action +
                scores.success + scores.review + scores.operation +
                scores.presentation;
  
  // 保留1位小数
  return Math.round(total * 10) / 10;
}
```

### 5. 显示格式化

```javascript
// 统一显示格式
function formatScore(score) {
  if (score === null || score === undefined) {
    return '-';
  }
  return score.toFixed(1);  // 始终显示1位小数
}

// 示例
formatScore(18.5)  // "18.5"
formatScore(18.0)  // "18.0"
formatScore(18)    // "18.0"
```

---

## 兼容性说明

### 向后兼容
- ✅ 现有整数分值自动转换为小数（8 → 8.0）
- ✅ API响应格式不变，只是数据类型变化
- ✅ 整数输入仍然有效（18 等同于 18.0）

### 不兼容情况
- ❌ 如果前端强制类型检查为Integer，需要改为Number
- ❌ 如果前端输入框禁止小数，需要修改配置

---

## 测试建议

### 测试用例

1. **提交整数分值**: 18, 17, 19 → 应该成功
2. **提交小数分值**: 18.5, 17.8, 19.2 → 应该成功
3. **提交2位小数**: 18.75 → 应该被四舍五入或拒绝
4. **边界值测试**: 0.0, 100.0, 0.1, 99.9 → 应该成功
5. **非法值测试**: -1, 101, "abc" → 应该拒绝

### 验证点

- [ ] 输入框支持小数输入
- [ ] 分值显示保留1位小数
- [ ] 总分计算正确
- [ ] 排名和统计显示正确
- [ ] 表单验证正确

---

## 常见问题

### Q1: 为什么选择1位小数而不是2位？
A: 1位小数精度已经足够（0.1分），且无需格式化转换，代码更简单。

### Q2: 现有数据会受影响吗？
A: 不会。现有整数数据自动转换为小数格式（8 → 8.0）。

### Q3: 前端需要做格式化吗？
A: 建议使用 `toFixed(1)` 统一显示格式，但不是必须的。

### Q4: 总分如何计算？
A: 后端自动计算7个分项之和，前端无需计算（但可以实时显示）。

---

**更新时间**: 2026-02-10  
**文档版本**: v1.0  
**联系人**: 后端开发团队
