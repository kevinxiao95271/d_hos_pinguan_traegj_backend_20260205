# 入围管理API废弃与替换说明

**文档日期**: 2026-02-07  
**影响范围**: 入围管理页面 - 项目详情展示

---

## 📋 变更总览

### 新增API
```
GET /api/registrations/{registrationId}/reviewer-scores?stage={BOOK|INTERVIEW|FINAL}
```
**功能**: 返回指定项目每个评委的详细评分记录

---

## ❌ 被废弃的API

### API 1: GET /api/admin/reviews/feedback

**废弃原因**: 新API完全覆盖并超越了此API的功能

#### 原API功能
```
GET /api/admin/reviews/feedback?competitionId={id}&stage={stage}
```

**返回内容**:
```json
{
  "code": 200,
  "data": [
    {
      "registrationId": 106,
      "projectName": "护理质量持续改进",
      "institutionName": "浙江大学医学院附属第一医院",
      "stage": "BOOK",
      "reviewerId": 21,
      "reviewerName": "张三",
      "total": 88,           // ✅ 有总分
      "highlight": "...",     // ✅ 有亮点
      "weakness": "..."       // ✅ 有改进建议
    }
  ]
}
```

**不足**:
- ❌ 缺少分项评分（plan, problem, action等7个维度）
- ❌ 缺少评委单位、职称
- ❌ 缺少评审时间
- ❌ 需要按赛事ID查询，无法直接按项目ID查询
- ❌ 返回所有项目的数据，需要前端筛选

#### 新API功能
```
GET /api/registrations/{registrationId}/reviewer-scores?stage=BOOK
```

**返回内容**:
```json
{
  "code": 200,
  "data": [
    {
      "stage": "BOOK",
      "reviewerId": 21,
      "reviewerName": "张三",
      "reviewerTitle": "主任医师",                    // ✅ 新增
      "reviewerInstitutionName": "浙江大学医学院附属第一医院",  // ✅ 新增
      "reviewerInstitutionLevel": "三级甲等",          // ✅ 新增
      "scores": {                                     // ✅ 新增
        "plan": 18,
        "problem": 17,
        "action": 19,
        "success": 18,
        "review": 16,
        "operation": 0,
        "presentation": 0,
        "total": 88
      },
      "highlight": "项目主题明确...",
      "weakness": "建议进一步...",
      "submittedAt": "2026-02-05T14:30:00"           // ✅ 新增
    }
  ]
}
```

**优势**:
- ✅ 包含7个维度的分项评分
- ✅ 包含评委完整信息（姓名、职称、单位、等级）
- ✅ 包含评审时间
- ✅ 直接按项目ID查询，无需筛选
- ✅ 支持按stage过滤
- ✅ 数据结构更清晰（scores对象）

**替换方案**: 直接使用新API替换

---

## ⚠️ 可以选择性废弃的API

### API 2: GET /api/registrations/{id}/review-details

**状态**: 建议保留用于特定场景，或根据前端需求决定

#### 原API功能
```
GET /api/registrations/{registrationId}/review-details
```

**返回内容**:
```json
{
  "code": 200,
  "data": [
    {
      "stage": "BOOK",
      "taskCount": 2,
      "scoredCount": 1,
      "avgPlan": 18.0,       // 平均分
      "avgProblem": 17.0,    // 平均分
      "avgAction": 19.0,     // 平均分
      "avgSuccess": 18.0,    // 平均分
      "avgReview": 16.0,     // 平均分
      "avgOperation": 0.0,   // 平均分
      "avgPresentation": 0.0,// 平均分
      "avgTotal": 88.0,      // 平均分
      "highlights": [        // 所有评委评语合并
        "项目主题明确...",
        "数据详实..."
      ],
      "weaknesses": [        // 所有评委评语合并
        "建议进一步...",
        "建议补充..."
      ]
    }
  ]
}
```

**优点**:
- ✅ 返回汇总平均分，适合快速查看总体情况
- ✅ 返回taskCount和scoredCount，了解评审进度
- ✅ 数据量小，响应快

**不足**:
- ❌ 无法区分每个评委的评分
- ❌ 无法区分评语是哪个评委的
- ❌ 没有评委信息

#### 使用场景对比

**场景A: 只需要看平均分和汇总评语**
- 推荐使用：**原API** `GET /api/registrations/{id}/review-details`
- 理由：数据量小，响应快，信息足够

**场景B: 需要看每个评委的详细评分**
- 推荐使用：**新API** `GET /api/registrations/{id}/reviewer-scores`
- 理由：信息完整，可以展示每个评委的独立记录

**场景C: 需要同时看平均分和每个评委评分**
- 方案1：调用两个API
  - `GET /api/registrations/{id}/review-details` 获取平均分
  - `GET /api/registrations/{id}/reviewer-scores` 获取每个评委评分
- 方案2：只调用新API，前端自己计算平均分
  - `GET /api/registrations/{id}/reviewer-scores`
  - 前端计算平均值

**建议**:
- 如果前端只需要展示每个评委的详细评分（新需求），可以**废弃**原API
- 如果前端还需要快速查看平均分汇总，可以**保留**原API
- 推荐方案：**保留原API**，两个API各有用途

---

## ✅ 继续保留的API

### API 3: GET /api/admin/reviews/rankings

**状态**: **保留**

**原因**: 
- ✅ 用于排行榜和列表页展示
- ✅ 返回所有项目的排名和平均分
- ✅ 支持按组别、阶段筛选
- ✅ 新API无法替代（新API是针对单个项目的详情）

**使用场景**: 入围管理列表页、排行榜、综合排名计算

```
GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK&groupType=BASIC
```

**不受影响**，继续使用。

---

### API 4: GET /api/admin/reviews/shortlist

**状态**: **保留**

**原因**:
- ✅ 用于入围名单筛选（按比例、按分数线）
- ✅ 新API无法替代

**使用场景**: 入围策略配置、入围名单生成

```
GET /api/admin/reviews/shortlist?competitionId=21&stage=BOOK&limit=10&minAvgTotal=80
```

**不受影响**，继续使用。

---

## 📊 API对比总结表

| API | 状态 | 原因 | 替换方案 |
|-----|------|------|---------|
| **GET /api/admin/reviews/feedback** | ❌ **废弃** | 新API完全覆盖且功能更强 | 使用新API `GET /api/registrations/{id}/reviewer-scores` |
| **GET /api/registrations/{id}/review-details** | ⚠️ **可选废弃** | 根据前端需求决定是否保留 | 可用新API替代，或保留与新API并存 |
| **GET /api/admin/reviews/rankings** | ✅ **保留** | 用于列表页排名，无替代 | 无需替换 |
| **GET /api/admin/reviews/shortlist** | ✅ **保留** | 用于入围筛选，无替代 | 无需替换 |
| **GET /api/registrations/{id}/reviewer-scores** | ✨ **新增** | 新功能：展示每个评委详情 | - |

---

## 🔄 迁移方案

### 方案A: 激进方案（简化API）

**废弃API**:
1. ❌ `GET /api/admin/reviews/feedback`
2. ❌ `GET /api/registrations/{id}/review-details`

**替换方案**:
- 统一使用新API `GET /api/registrations/{id}/reviewer-scores`
- 前端需要平均分时，自己计算：
  ```javascript
  const avgTotal = reviewerScores.reduce((sum, r) => sum + r.scores.total, 0) / reviewerScores.length;
  ```

**优点**:
- ✅ API更少，维护简单
- ✅ 数据结构统一

**缺点**:
- ❌ 前端需要自己计算平均分
- ❌ 数据量可能比原API大（返回每个评委详情）
- ❌ 前端改动较大

---

### 方案B: 保守方案（共存）（推荐）⭐

**废弃API**:
1. ❌ `GET /api/admin/reviews/feedback` - 功能被新API完全覆盖

**保留API**:
1. ✅ `GET /api/registrations/{id}/review-details` - 用于快速查看平均分
2. ✅ `GET /api/admin/reviews/rankings` - 用于列表页排名
3. ✅ `GET /api/admin/reviews/shortlist` - 用于入围筛选

**新增API**:
1. ✨ `GET /api/registrations/{id}/reviewer-scores` - 用于查看每个评委详情

**使用场景划分**:
```
入围管理列表页:
  └─ GET /api/admin/reviews/rankings
     返回：所有项目的排名和平均分

项目详情弹窗 - 汇总信息:
  └─ GET /api/registrations/{id}/review-details
     返回：各维度平均分、评语汇总

项目详情弹窗 - 评委详情:
  └─ GET /api/registrations/{id}/reviewer-scores
     返回：每个评委的详细评分和信息

入围名单筛选:
  └─ GET /api/admin/reviews/shortlist
     返回：符合条件的入围项目
```

**优点**:
- ✅ 向下兼容，前端改动最小
- ✅ 每个API职责明确
- ✅ 可以根据场景选择最合适的API

**缺点**:
- ⚠️ API数量较多，需要维护

---

## 📱 前端调用变更

### 旧的调用方式（被废弃）

```javascript
// ❌ 废弃：查看项目的评委反馈
const response = await axios.get(
  '/api/admin/reviews/feedback',
  {
    params: { competitionId: 21, stage: 'BOOK' },
    headers: { Authorization: `Bearer ${token}` }
  }
);

// 需要筛选出当前项目
const projectFeedback = response.data.data.filter(
  item => item.registrationId === 106
);
```

### 新的调用方式（推荐）

```javascript
// ✅ 新API：直接获取项目的评委详细评分
const response = await axios.get(
  '/api/registrations/106/reviewer-scores',
  {
    params: { stage: 'BOOK' },  // 可选
    headers: { Authorization: `Bearer ${token}` }
  }
);

const reviewerScores = response.data.data;

// 展示每个评委的详细记录
reviewerScores.forEach(reviewer => {
  console.log(`评委：${reviewer.reviewerName}（${reviewer.reviewerInstitutionName}）`);
  console.log(`总分：${reviewer.scores.total}`);
  console.log(`计划：${reviewer.scores.plan}分`);
  console.log(`问题：${reviewer.scores.problem}分`);
  console.log(`行动：${reviewer.scores.action}分`);
  console.log(`成效：${reviewer.scores.success}分`);
  console.log(`回顾：${reviewer.scores.review}分`);
  console.log(`亮点：${reviewer.highlight}`);
  console.log(`改进建议：${reviewer.weakness}`);
  console.log(`评审时间：${reviewer.submittedAt}`);
});
```

### 如果需要平均分（前端计算）

```javascript
// 获取所有评委评分
const response = await axios.get(`/api/registrations/106/reviewer-scores`);
const reviewerScores = response.data.data;

// 按阶段分组
const bookReviewers = reviewerScores.filter(r => r.stage === 'BOOK');

// 计算平均分
const avgScores = {
  plan: bookReviewers.reduce((sum, r) => sum + r.scores.plan, 0) / bookReviewers.length,
  problem: bookReviewers.reduce((sum, r) => sum + r.scores.problem, 0) / bookReviewers.length,
  action: bookReviewers.reduce((sum, r) => sum + r.scores.action, 0) / bookReviewers.length,
  success: bookReviewers.reduce((sum, r) => sum + r.scores.success, 0) / bookReviewers.length,
  review: bookReviewers.reduce((sum, r) => sum + r.scores.review, 0) / bookReviewers.length,
  operation: bookReviewers.reduce((sum, r) => sum + r.scores.operation, 0) / bookReviewers.length,
  presentation: bookReviewers.reduce((sum, r) => sum + r.scores.presentation, 0) / bookReviewers.length,
  total: bookReviewers.reduce((sum, r) => sum + r.scores.total, 0) / bookReviewers.length
};

console.log(`书审平均总分：${avgScores.total.toFixed(1)}`);
```

---

## 📝 推荐执行步骤

### 第一阶段：新增API（不影响现有功能）

1. ✅ 实现新API `GET /api/registrations/{id}/reviewer-scores`
2. ✅ 编写测试脚本验证
3. ✅ 提供前端API文档

### 第二阶段：前端迁移

1. 前端新增"评委详情"展示功能，调用新API
2. 保留原有"汇总信息"展示，继续使用 `/review-details`
3. 如果前端决定完全使用新API，移除对 `/review-details` 的调用

### 第三阶段：清理废弃API

1. ❌ 标记 `GET /api/admin/reviews/feedback` 为废弃（@Deprecated）
2. ⏳ 观察一段时间，确认无调用
3. ❌ 移除废弃API的Controller方法和Service方法

---

## 🎯 最终建议

### 推荐方案：**方案B（保守方案）**

**立即废弃**:
- ❌ `GET /api/admin/reviews/feedback`

**继续保留**:
- ✅ `GET /api/registrations/{id}/review-details` - 汇总平均分
- ✅ `GET /api/admin/reviews/rankings` - 排行榜
- ✅ `GET /api/admin/reviews/shortlist` - 入围筛选

**新增**:
- ✨ `GET /api/registrations/{id}/reviewer-scores` - 评委详细评分

**理由**:
1. 向下兼容，前端可以渐进式迁移
2. 每个API职责清晰，各有用途
3. 保留 `/review-details` 用于快速查看平均分（数据量小，响应快）
4. 新API专注于展示每个评委的详细记录

---

## 📋 总结

| 项目 | 内容 |
|------|------|
| **废弃API数量** | 1个 |
| **废弃的API** | `GET /api/admin/reviews/feedback` |
| **替换方案** | `GET /api/registrations/{id}/reviewer-scores` |
| **保留API数量** | 3个 |
| **新增API数量** | 1个 |
| **前端影响** | 小（渐进式迁移） |
| **推荐方案** | 方案B（保守方案，API共存） |

---

**文档编写人**: AI Assistant  
**文档日期**: 2026-02-07  
**文档版本**: v1.0
