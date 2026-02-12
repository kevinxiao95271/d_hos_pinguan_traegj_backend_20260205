# 组别统计API - 新增字段说明

## API接口

```
GET /api/admin/stats/summary
GET /api/admin/stats/summary/{competitionId}
```

## 新增返回字段

### 1. institutionCount (Integer)
- 说明: 总机构数(已报名成功的机构,去重统计)
- 示例: 289

### 2. groupTypeStats (List<GroupTypeStats>)
- 说明: 组别统计列表,包含基层组、综合组、进阶组的详细统计
- 类型: 数组

## GroupTypeStats 对象结构

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| groupType | String | 组别类型枚举值 | "BASIC", "COMPREHENSIVE", "ADVANCED" |
| groupTypeName | String | 组别中文名称 | "基层组", "综合组", "进阶组" |
| institutionCount | Integer | 该组别的机构数 | 112 |
| projectCount | Integer | 该组别的项目数 | 250 |
| projectPercentage | Double | 项目占比(%) | 25.2 |
| avgProjectsPerInstitution | Double | 平均项目/机构 | 2.23 |

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
      "温州市": 100
    },
    "subjectTypeCounts": {
      "医疗质量": 200,
      "护理质量": 150
    },
    "methodCounts": {
      "PDCA": 300,
      "QCC": 200
    },
    "leaderTitleCounts": {
      "主任医师": 100,
      "副主任医师": 150
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

### 表格展示

```
总计 992 个项目  总计 289 个机构(已报名成功)

组别       机构数    项目数    项目占比    平均项目/机构
基层组     112       250       25.2%       2.23
综合组     183       644       64.9%       3.52
进阶组     60        98        9.9%        1.63
```

### 图表展示

1. 饼图: 显示各组别项目占比
2. 柱状图: 显示各组别机构数和项目数对比
3. 折线图: 显示平均项目/机构的趋势

## 注意事项

1. institutionCount 是去重后的机构总数
2. groupTypeStats 数组按顺序返回: 基层组 → 综合组 → 进阶组
3. projectPercentage 保留1位小数
4. avgProjectsPerInstitution 保留2位小数
5. 所有统计数据基于已报名成功的项目(status = APPROVED 或其他有效状态)

## 测试脚本

运行以下命令测试API:

```bash
python scripts/test_group_type_stats.py
```
