# 报名统计接口 - 完整字段说明

## API接口

```
GET /api/admin/stats/summary
GET /api/admin/stats/summary/{competitionId}
```

## 响应格式

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

## 返回字段说明

### 基础信息

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| competitionId | Long | 赛事ID | 21 |
| competitionName | String | 赛事名称 | "2025年度品管圈大赛" |

### 统计数据

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| registrationCount | Integer | 报名项目总数 | 992 |
| institutionCount | Integer | 报名机构总数(去重) | 289 |
| toolTypeCount | Integer | 使用的品管工具种类数 | 15 |
| reviewerCount | Integer | 评委总数 | 50 |
| reviewerInstitutionCount | Integer | 评委所属机构数(去重) | 45 |
| bookReviewTaskCount | Integer | 书审任务总数 | 100 |
| bookReviewUnscoredCount | Integer | 书审未评分数 | 20 |

### 分布统计 (Map对象)

#### regionCounts (Map<String, Integer>)
地区分布统计

```json
{
  "杭州市": 150,
  "宁波市": 120,
  "温州市": 100,
  "其他": 50
}
```

#### subjectTypeCounts (Map<String, Integer>)
主题类型分布统计

```json
{
  "医疗质量": 200,
  "护理质量": 150,
  "医技质量": 100
}
```

#### methodCounts (Map<String, Integer>)
品管工具分布统计

```json
{
  "PDCA": 300,
  "QCC": 200,
  "RCA": 150,
  "FMEA": 100
}
```

#### leaderTitleCounts (Map<String, Integer>)
项目负责人职称分布统计

```json
{
  "主任医师": 100,
  "副主任医师": 150,
  "主治医师": 200,
  "主任护师": 80,
  "副主任护师": 120,
  "主管护师": 150,
  "其他": 192
}
```

### 组别统计 (groupTypeStats)

**类型**: List<GroupTypeStats>

**说明**: 基层组、综合组、进阶组的详细统计数据

#### GroupTypeStats 对象结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| groupType | String | 组别类型枚举 | "BASIC", "COMPREHENSIVE", "ADVANCED" |
| groupTypeName | String | 组别中文名称 | "基层组", "综合组", "进阶组" |
| institutionCount | Integer | 该组别的机构数 | 112 |
| projectCount | Integer | 该组别的项目数 | 250 |
| projectPercentage | Double | 项目占比(%) | 25.2 |
| avgProjectsPerInstitution | Double | 平均项目/机构 | 2.23 |

**示例数据**:

```json
"groupTypeStats": [
  {
    "groupType": "BASIC",
    "groupTypeName": "基层组",
    "institutionCount": 112,
    "projectCount": 250,
    "projectPercentage": 25.2,
    "avgProjectsPerInstitution": 2.23
  },
  {
    "groupType": "COMPREHENSIVE",
    "groupTypeName": "综合组",
    "institutionCount": 183,
    "projectCount": 644,
    "projectPercentage": 64.9,
    "avgProjectsPerInstitution": 3.52
  },
  {
    "groupType": "ADVANCED",
    "groupTypeName": "进阶组",
    "institutionCount": 60,
    "projectCount": 98,
    "projectPercentage": 9.9,
    "avgProjectsPerInstitution": 1.63
  }
]
```

### 平均分数统计

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| avgPlan | Double | 计划阶段平均分 | 8.5 |
| avgProblem | Double | 问题分析平均分 | 8.2 |
| avgAction | Double | 行动实施平均分 | 8.8 |
| avgSuccess | Double | 成果评价平均分 | 8.6 |
| avgReview | Double | 总结反思平均分 | 8.4 |
| avgOperation | Double | 操作规范平均分 | 8.7 |
| avgPresentation | Double | 展示效果平均分 | 8.3 |

## 完整响应示例

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "competitionId": 21,
    "competitionName": "2025年度品管圈大赛",
    "registrationCount": 992,
    "institutionCount": 289,
    "toolTypeCount": 15,
    "reviewerCount": 50,
    "reviewerInstitutionCount": 45,
    "bookReviewTaskCount": 100,
    "bookReviewUnscoredCount": 20,
    "regionCounts": {
      "杭州市": 150,
      "宁波市": 120,
      "温州市": 100,
      "其他": 622
    },
    "subjectTypeCounts": {
      "医疗质量": 200,
      "护理质量": 150,
      "医技质量": 100,
      "其他": 542
    },
    "methodCounts": {
      "PDCA": 300,
      "QCC": 200,
      "RCA": 150,
      "FMEA": 100,
      "其他": 242
    },
    "leaderTitleCounts": {
      "主任医师": 100,
      "副主任医师": 150,
      "主治医师": 200,
      "主任护师": 80,
      "副主任护师": 120,
      "主管护师": 150,
      "其他": 192
    },
    "groupTypeStats": [
      {
        "groupType": "BASIC",
        "groupTypeName": "基层组",
        "institutionCount": 112,
        "projectCount": 250,
        "projectPercentage": 25.2,
        "avgProjectsPerInstitution": 2.23
      },
      {
        "groupType": "COMPREHENSIVE",
        "groupTypeName": "综合组",
        "institutionCount": 183,
        "projectCount": 644,
        "projectPercentage": 64.9,
        "avgProjectsPerInstitution": 3.52
      },
      {
        "groupType": "ADVANCED",
        "groupTypeName": "进阶组",
        "institutionCount": 60,
        "projectCount": 98,
        "projectPercentage": 9.9,
        "avgProjectsPerInstitution": 1.63
      }
    ],
    "avgPlan": 8.5,
    "avgProblem": 8.2,
    "avgAction": 8.8,
    "avgSuccess": 8.6,
    "avgReview": 8.4,
    "avgOperation": 8.7,
    "avgPresentation": 8.3
  }
}
```

## 前端展示建议

### 1. 总览卡片

```
┌─────────────────────────────────────────┐
│  报名统计总览                            │
├─────────────────────────────────────────┤
│  总项目数: 992                           │
│  总机构数: 289 (已报名成功)              │
│  品管工具: 15 种                         │
│  评委人数: 50 人 (来自 45 个机构)        │
└─────────────────────────────────────────┘
```

### 2. 组别统计表格

```
组别       机构数    项目数    项目占比    平均项目/机构
─────────────────────────────────────────────────
基层组     112       250       25.2%       2.23
综合组     183       644       64.9%       3.52
进阶组     60        98        9.9%        1.63
```

### 3. 分布图表

- 地区分布: 地图热力图或柱状图
- 主题类型: 饼图
- 品管工具: 横向柱状图
- 职称分布: 饼图或柱状图

### 4. 评分统计

```
评分维度统计 (平均分)
─────────────────────
计划阶段: 8.5 ████████▌
问题分析: 8.2 ████████▏
行动实施: 8.8 ████████▊
成果评价: 8.6 ████████▌
总结反思: 8.4 ████████▍
操作规范: 8.7 ████████▋
展示效果: 8.3 ████████▎
```

## 数据说明

1. **institutionCount**: 去重后的机构总数，一个机构报多个项目只计数一次
2. **groupTypeStats**: 数组按顺序返回基层组、综合组、进阶组
3. **projectPercentage**: 保留1位小数，单位为百分比
4. **avgProjectsPerInstitution**: 保留2位小数
5. **Map类型字段**: 键为分类名称，值为该分类的项目数量
6. **平均分字段**: 保留1位小数，满分10分

## 测试方法

```bash
# 测试组别统计
python scripts/test_group_type_stats.py

# 测试职称统计
python scripts/test_leader_title_stats.py

# 测试品管工具分布
python scripts/test_method_distribution.py
```

## 注意事项

1. 所有统计数据基于已报名成功的项目
2. Map类型字段的键值对数量可能变化，前端需要动态处理
3. 如果某个统计维度没有数据，对应的Map可能为空对象 `{}`
4. groupTypeStats数组可能包含0-3个元素，取决于是否有该组别的报名
5. 平均分字段可能为null，表示还没有评分数据

## 版本历史

- v1.0 (2026-02-11): 新增 institutionCount 和 groupTypeStats 字段
- v0.9: 初始版本，包含基础统计字段
