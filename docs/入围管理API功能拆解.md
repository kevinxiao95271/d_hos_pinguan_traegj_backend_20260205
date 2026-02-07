# 入围管理API功能拆解文档

## 概述

本文档详细说明入围管理页面所需的所有API，包括调用路径、参数、返回JSON结构，以及各API如何组合实现功能点。

---

## API列表

### 1. 获取书审排名

**功能**: 获取指定赛事的书审阶段评分排名

**请求**
```
GET /api/admin/reviews/rankings
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| competitionId | Long | 是 | 赛事ID |
| stage | String | 是 | 评审阶段，固定值: `BOOK` |
| groupType | String | 否 | 组别筛选: `BASIC`/`ADVANCED`/`COMPREHENSIVE` |

**请求头**
```
Authorization: Bearer {token}
```

**返回JSON结构**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "rank": 1,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第一医院",
      "groupType": "BASIC",
      "stage": "BOOK",
      "avgTotal": 88.0
    }
  ]
}
```

**返回字段说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| rank | Integer | 排名（1,2,3...） |
| registrationId | Long | 报名ID |
| projectName | String | 项目名称 |
| institutionName | String | 医疗机构名称 |
| groupType | String | 组别: BASIC(基层组), ADVANCED(进阶组), COMPREHENSIVE(综合组) |
| stage | String | 评审阶段: BOOK |
| avgTotal | Double | 书审平均总分 |

---

### 2. 获取面谈排名

**功能**: 获取指定赛事的面谈阶段评分排名

**请求**
```
GET /api/admin/reviews/rankings
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| competitionId | Long | 是 | 赛事ID |
| stage | String | 是 | 评审阶段，固定值: `INTERVIEW` |
| groupType | String | 否 | 组别筛选: `BASIC`/`ADVANCED`/`COMPREHENSIVE` |

**请求头**
```
Authorization: Bearer {token}
```

**返回JSON结构**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "rank": 1,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第一医院",
      "groupType": "BASIC",
      "stage": "INTERVIEW",
      "avgTotal": 85.5
    }
  ]
}
```

**返回字段说明**（同书审排名，stage字段为INTERVIEW）

**特殊说明**: 
- 如果某个项目还未进行面谈评审，该API返回的数据中不会包含该项目
- 返回空数组`[]`表示暂无面谈评分数据

---

### 3. 获取项目详细评分

**功能**: 获取指定项目在各阶段的详细评分（含亮点和改进建议）

**请求**
```
GET /api/registrations/{registrationId}/review-details
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| registrationId | Long | 是 | 报名ID（路径参数） |

**请求头**
```
Authorization: Bearer {token}
```

**返回JSON结构**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "stage": "BOOK",
      "taskCount": 2,
      "scoredCount": 1,
      "avgPlan": 18.0,
      "avgProblem": 17.0,
      "avgAction": 19.0,
      "avgSuccess": 18.0,
      "avgReview": 16.0,
      "avgOperation": 0.0,
      "avgPresentation": 0.0,
      "avgTotal": 88.0,
      "highlights": [
        "项目主题明确，改进措施得当，成效显著。实施过程规范，数据收集完整，对比分析清晰。团队协作良好。"
      ],
      "weaknesses": [
        "建议进一步量化成本效益分析。可以增加更多的跨部门协作案例。持续改进机制可以更完善。"
      ]
    },
    {
      "stage": "INTERVIEW",
      "taskCount": 0,
      "scoredCount": 0,
      "avgPlan": null,
      "avgProblem": null,
      "avgAction": null,
      "avgSuccess": null,
      "avgReview": null,
      "avgOperation": null,
      "avgPresentation": null,
      "avgTotal": null,
      "highlights": [],
      "weaknesses": []
    },
    {
      "stage": "FINAL",
      "taskCount": 0,
      "scoredCount": 0,
      "avgPlan": null,
      "avgProblem": null,
      "avgAction": null,
      "avgSuccess": null,
      "avgReview": null,
      "avgOperation": null,
      "avgPresentation": null,
      "avgTotal": null,
      "highlights": [],
      "weaknesses": []
    }
  ]
}
```

**返回字段说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| stage | String | 评审阶段: BOOK/INTERVIEW/FINAL |
| taskCount | Integer | 分配的评审任务数 |
| scoredCount | Integer | 已完成评审数 |
| avgPlan | Double | 计划维度平均分（满分20） |
| avgProblem | Double | 问题维度平均分（满分20） |
| avgAction | Double | 行动维度平均分（满分20） |
| avgSuccess | Double | 成效维度平均分（满分15） |
| avgReview | Double | 回顾维度平均分（满分10） |
| avgOperation | Double | 运作维度平均分（满分10） |
| avgPresentation | Double | 展示维度平均分（满分5） |
| avgTotal | Double | 总分平均分（满分100） |
| highlights | Array[String] | 评委给出的亮点（所有评委的汇总） |
| weaknesses | Array[String] | 评委给出的改进建议（所有评委的汇总） |

**特殊说明**:
- 始终返回3个阶段的数据（BOOK, INTERVIEW, FINAL）
- 如果某个阶段未评审，所有avg字段为null，数组为空
- `taskCount=0 && scoredCount=0` 表示该阶段未分配任务

---

### 4. 获取入围名单（按条件筛选）

**功能**: 根据分数线或数量限制获取入围项目列表

**请求**
```
GET /api/admin/reviews/shortlist
```

**请求参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| competitionId | Long | 是 | 赛事ID |
| stage | String | 是 | 评审阶段: `BOOK`/`INTERVIEW` |
| groupType | String | 否 | 组别筛选 |
| limit | Integer | 否 | 限制入围数量（前N名） |
| minAvgTotal | Double | 否 | 最低分数线 |

**请求头**
```
Authorization: Bearer {token}
```

**返回JSON结构**（同rankings API）
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "rank": 1,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第一医院",
      "groupType": "BASIC",
      "stage": "BOOK",
      "avgTotal": 88.0
    }
  ]
}
```

**参数使用说明**:
- `limit=10`: 返回前10名
- `minAvgTotal=80`: 返回总分≥80分的项目
- 同时指定`limit`和`minAvgTotal`时，取交集（既要在前N名，又要≥最低分）
- 按`avgTotal`降序排序，`rank`字段从1开始

---

## 功能点拆解

### 功能点1: 综合排名展示

**目标**: 显示所有项目的书审得分、面谈得分、综合得分和综合排名

**使用的API**:
1. `GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK` - 获取书审排名
2. `GET /api/admin/reviews/rankings?competitionId=21&stage=INTERVIEW` - 获取面谈排名

**数据处理逻辑**:
```
1. 调用API获取书审数据 -> bookList
2. 调用API获取面谈数据 -> interviewList
3. 按registrationId合并两个列表:
   - 创建Map: registrationId -> {bookScore, interviewScore}
4. 计算综合得分:
   compositeScore = bookScore × 书审权重% + interviewScore × 面谈权重%
5. 按compositeScore降序排序
6. 重新分配rank（1,2,3...）
```

**返回数据结构** (处理后):
```json
[
  {
    "rank": 1,
    "registrationId": 106,
    "projectName": "护理交接班规范化-1",
    "institutionName": "浙江大学医学院附属第一医院",
    "groupType": "BASIC",
    "bookScore": 88.0,
    "interviewScore": 85.5,
    "compositeScore": 86.75,
    "status": "completed"
  }
]
```

**状态说明**:
- `status="completed"`: 已完成书审和面谈
- `status="pending_interview"`: 只有书审，待面谈

---

### 功能点2: 入围策略配置

**目标**: 根据权重、比例、分数线自动计算入围名单

**使用的API**:
无需额外API，基于功能点1的综合排名数据计算

**计算逻辑**:
```
输入:
- 综合排名列表（功能点1的结果）
- 书审权重%
- 面谈权重%
- 入围比例%（如30%）
- 最低分数线（可选）

计算:
1. 重新计算compositeScore（如果权重改变）
2. 重新排序
3. 计算入围数量: count = Math.floor(总数 × 入围比例%)
4. 取前count名
5. 如果设置了最低分数线，过滤掉 < 分数线的项目
6. 标记入围状态: isShortlisted = true/false
```

**处理后数据结构**:
```json
[
  {
    "rank": 1,
    "registrationId": 106,
    "projectName": "护理交接班规范化-1",
    "compositeScore": 86.75,
    "isShortlisted": true,
    "shortlistType": "auto"
  }
]
```

---

### 功能点3: 个别增补/取消

**目标**: 手动标记某个项目为入围或取消入围

**使用的API**:
无需新API，在客户端维护增补/取消状态

**数据处理逻辑**:
```
1. 基于功能点2的入围列表
2. 手动增补:
   - 找到未入围的项目
   - 设置: isShortlisted = true, shortlistType = "manual_add"
3. 手动取消:
   - 找到已入围的项目（自动或增补）
   - 设置: isShortlisted = false, shortlistType = "manual_remove"
4. 状态区分:
   - shortlistType = "auto": 自动入围
   - shortlistType = "manual_add": 手动增补
   - shortlistType = "manual_remove": 手动取消
   - shortlistType = null: 未入围
```

**处理后数据结构**:
```json
[
  {
    "rank": 1,
    "registrationId": 106,
    "projectName": "护理交接班规范化-1",
    "compositeScore": 86.75,
    "isShortlisted": true,
    "shortlistType": "auto"
  },
  {
    "rank": 11,
    "registrationId": 120,
    "projectName": "信息系统提效-15",
    "compositeScore": 75.50,
    "isShortlisted": true,
    "shortlistType": "manual_add"
  }
]
```

---

### 功能点4: 按组别筛选

**目标**: 按组别（基层组/进阶组/综合组）分别查看排名和入围情况

**使用的API**:
1. `GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK&groupType=BASIC`
2. `GET /api/admin/reviews/rankings?competitionId=21&stage=INTERVIEW&groupType=BASIC`

**数据处理逻辑**:
```
方式1: API筛选（推荐）
- 调用API时传入groupType参数
- 后端直接返回指定组别的数据
- 按功能点1处理

方式2: 客户端筛选
- 获取全部数据（不传groupType）
- 客户端过滤: data.filter(item => item.groupType === 'BASIC')
```

**组别枚举值**:
- `BASIC` - 基层组
- `ADVANCED` - 进阶组
- `COMPREHENSIVE` - 综合组

---

### 功能点5: 查看项目详情

**目标**: 点击项目查看详细评分和评委意见

**使用的API**:
`GET /api/registrations/{registrationId}/review-details`

**数据展示**:
```
书审阶段:
  - 各维度得分（计划、问题、行动、成效、回顾、运作、展示）
  - 总分
  - 评委亮点
  - 评委改进建议

面谈阶段:
  - 同上

决赛阶段:
  - 同上（如果有）
```

---

### 功能点6: 统计信息

**目标**: 显示总数、已完成数、入围数等统计

**使用的API**:
无需额外API，基于功能点1的数据统计

**统计逻辑**:
```javascript
const stats = {
  totalProjects: data.length,
  completedBook: data.filter(p => p.bookScore !== null).length,
  completedInterview: data.filter(p => p.interviewScore !== null).length,
  completedBoth: data.filter(p => p.status === 'completed').length,
  shortlisted: data.filter(p => p.isShortlisted).length,
  shortlistedAuto: data.filter(p => p.shortlistType === 'auto').length,
  shortlistedManual: data.filter(p => p.shortlistType === 'manual_add').length,
  removedManual: data.filter(p => p.shortlistType === 'manual_remove').length
}
```

---

### 功能点7: 导出入围名单

**目标**: 导出CSV格式的入围名单

**使用的API**:
无需额外API，基于功能点2的入围列表生成CSV

**CSV格式**:
```csv
综合排名,项目名称,医疗机构,组别,书审得分,面谈得分,综合得分,入围状态
1,护理交接班规范化-1,浙江大学医学院附属第一医院,基层组,88.00,85.50,86.75,入围
2,门诊预约体验提升-11,嘉兴市第一医院,综合组,87.00,84.00,85.50,入围
...
```

---

## API调用流程示例

### 场景1: 页面初始加载

```
1. 调用 GET /api/admin/reviews/rankings?competitionId=21&stage=BOOK
   -> 获取书审数据

2. 调用 GET /api/admin/reviews/rankings?competitionId=21&stage=INTERVIEW
   -> 获取面谈数据

3. 客户端合并数据，计算综合得分和排名

4. 显示综合排名列表
```

### 场景2: 调整权重后重新计算

```
1. 用户修改权重: 书审60%, 面谈40%

2. 无需调用API，直接用已有数据重新计算:
   compositeScore = bookScore × 0.6 + interviewScore × 0.4

3. 重新排序并更新rank

4. 刷新显示
```

### 场景3: 设置入围比例30%

```
1. 基于当前综合排名（功能点1的结果）

2. 计算入围数量:
   count = Math.floor(completedBoth × 0.3)
   
3. 标记前count名为入围:
   data.forEach((item, index) => {
     item.isShortlisted = (index < count && item.status === 'completed')
     item.shortlistType = item.isShortlisted ? 'auto' : null
   })

4. 刷新显示
```

### 场景4: 手动增补第11名

```
1. 找到排名11的项目

2. 修改状态:
   item.isShortlisted = true
   item.shortlistType = 'manual_add'

3. 刷新显示（该项目显示"入围（增补）"标识）
```

### 场景5: 查看项目详情

```
1. 用户点击项目ID=106

2. 调用 GET /api/registrations/106/review-details

3. 弹窗/侧边栏显示:
   - 书审各维度得分
   - 面谈各维度得分
   - 评委意见（亮点+改进建议）
```

---

## 数据测试结果

### 当前测试环境数据

**赛事ID**: 21 (2026浙江品管大赛)

**书审数据**:
- 项目数: 1
- 项目ID: 106
- 项目名称: 护理交接班规范化-1
- 书审得分: 88.0

**面谈数据**:
- 项目数: 0
- 状态: 待评审

**结论**: 
- 目前只有书审数据，无法计算综合排名
- 待面谈评审完成后，可使用上述API和逻辑计算综合排名

---

## 注意事项

1. **权重计算**: 
   - 书审权重 + 面谈权重 = 100%
   - 默认各50%
   - 可调整为任意比例（如60% + 40%）

2. **入围比例**:
   - 只能对已完成书审和面谈的项目设置入围
   - 待面谈的项目不参与入围计算

3. **组别筛选**:
   - 可以全局入围（所有组别一起排名）
   - 也可以分组入围（每个组别单独排名和入围）

4. **手动增补/取消**:
   - 客户端维护状态，不需要调用后端API
   - 可以考虑后续增加持久化API保存手动操作

5. **数据刷新**:
   - 评委打分后，需要重新调用rankings API获取最新数据
   - 建议提供"刷新"按钮

---

## 总结

**核心API（3个）**:
1. `GET /api/admin/reviews/rankings` - 获取排名（书审/面谈）
2. `GET /api/registrations/{id}/review-details` - 获取详细评分
3. `GET /api/admin/reviews/shortlist` - 获取入围名单（可选，可用rankings代替）

**核心功能点（7个）**:
1. 综合排名展示 - 合并书审和面谈数据
2. 入围策略配置 - 权重、比例、分数线
3. 个别增补/取消 - 手动调整入围状态
4. 按组别筛选 - 支持分组查看
5. 查看项目详情 - 详细评分和评委意见
6. 统计信息 - 实时统计各项指标
7. 导出入围名单 - CSV格式导出

**数据流向**:
```
后端API -> 原始数据(书审+面谈) -> 客户端合并计算 -> 综合排名 -> 入围策略 -> 手动调整 -> 最终入围名单
```
