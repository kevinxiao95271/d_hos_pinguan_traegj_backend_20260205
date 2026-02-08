# 统计API快速参考

## 🚀 快速开始

### 接口信息
```
GET /api/admin/stats/summary
```

**输入参数**: 无

**说明**: 接口自动返回最新赛事（ID最大）的统计数据

### 请求示例
```javascript
fetch('/api/admin/stats/summary', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### 响应数据结构
```javascript
{
  success: true,
  data: {
    // 基础统计
    competitionId: 21,
    competitionName: "2026浙江品管大赛",
    registrationCount: 45,
    toolTypeCount: 8,
    reviewerCount: 19,
    reviewerInstitutionCount: 11,
    bookReviewTaskCount: 45,
    bookReviewUnscoredCount: 10,
    
    // 地区分布 (Object)
    regionCounts: {
      "杭州": 17,
      "舟山": 15,
      "宁波": 3,
      // ...
    },
    
    // 主题类型分布 (Object)
    subjectTypeCounts: {
      "医疗安全": 15,
      "服务流程": 12,
      // ...
    },
    
    // 平均分数
    avgPlan: 18.5,
    avgProblem: 17.8,
    avgAction: 19.2,
    avgSuccess: 18.9,
    avgReview: 17.5,
    avgOperation: 16.8,
    avgPresentation: 15.2
  }
}
```

## 📊 饼图数据转换

### 地区分布饼图
```javascript
// 1. 转换为数组格式
const regionData = Object.entries(data.regionCounts)
  .map(([name, value]) => ({ name, value }));

// 2. 按数量排序
regionData.sort((a, b) => b.value - a.value);

// 3. 用于 ECharts
const option = {
  series: [{
    type: 'pie',
    data: regionData
  }]
};
```

### 主题类型饼图
```javascript
// 环形饼图
const subjectData = Object.entries(data.subjectTypeCounts)
  .map(([name, value]) => ({ name, value }))
  .sort((a, b) => b.value - a.value);

const option = {
  series: [{
    type: 'pie',
    radius: ['40%', '70%'], // 环形
    data: subjectData
  }]
};
```

## 🎨 常用图表配置

### ECharts 饼图模板
```javascript
{
  title: {
    text: '地区分布',
    left: 'center'
  },
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [{
    name: '报名数',
    type: 'pie',
    radius: '60%',
    data: regionData,
    label: {
      formatter: '{b}\n{c} ({d}%)'
    }
  }]
}
```

### Chart.js 饼图模板
```javascript
new Chart(ctx, {
  type: 'pie',
  data: {
    labels: Object.keys(regionCounts),
    datasets: [{
      data: Object.values(regionCounts),
      backgroundColor: [
        '#FF6384', '#36A2EB', '#FFCE56',
        '#4BC0C0', '#9966FF', '#FF9F40'
      ]
    }]
  }
})
```

## 📈 雷达图配置

### 评分雷达图
```javascript
{
  radar: {
    indicator: [
      { name: '计划', max: 20 },
      { name: '问题', max: 20 },
      { name: '行动', max: 20 },
      { name: '成功', max: 20 },
      { name: '评审', max: 20 },
      { name: '操作', max: 20 },
      { name: '展示', max: 20 }
    ]
  },
  series: [{
    type: 'radar',
    data: [{
      value: [
        data.avgPlan,
        data.avgProblem,
        data.avgAction,
        data.avgSuccess,
        data.avgReview,
        data.avgOperation,
        data.avgPresentation
      ]
    }]
  }]
}
```

## 💡 实用技巧

### 1. 数据为空处理
```javascript
if (!regionCounts || Object.keys(regionCounts).length === 0) {
  // 显示"暂无数据"
  return;
}
```

### 2. 计算百分比
```javascript
const total = Object.values(regionCounts)
  .reduce((sum, count) => sum + count, 0);

const percentage = (count / total * 100).toFixed(1) + '%';
```

### 3. Top N + 其他
```javascript
const topN = 5;
const sorted = Object.entries(regionCounts)
  .sort(([, a], [, b]) => b - a);

const top = sorted.slice(0, topN);
const others = sorted.slice(topN);

if (others.length > 0) {
  const otherTotal = others.reduce((sum, [, v]) => sum + v, 0);
  top.push(['其他', otherTotal]);
}
```

### 4. 颜色方案
```javascript
// 浙江11市配色方案
const colors = [
  '#5470c6', // 杭州 - 蓝色
  '#91cc75', // 宁波 - 绿色
  '#fac858', // 温州 - 黄色
  '#ee6666', // 绍兴 - 红色
  '#73c0de', // 嘉兴 - 浅蓝
  '#3ba272', // 湖州 - 深绿
  '#fc8452', // 金华 - 橙色
  '#9a60b4', // 衢州 - 紫色
  '#ea7ccc', // 舟山 - 粉色
  '#5470c6', // 台州 - 蓝色
  '#91cc75'  // 丽水 - 绿色
];
```

## 🔗 相关资源

- **完整文档**: [报名统计API使用指引.md](./报名统计API使用指引.md)
- **在线示例**: [统计图表示例.html](./统计图表示例.html)
- **ECharts文档**: https://echarts.apache.org/zh/index.html
- **Chart.js文档**: https://www.chartjs.org/

## ⚠️ 注意事项

1. **权限**: 需要登录后才能访问
2. **赛事**: 当前只返回最新赛事数据
3. **地区**: 已修正，不会出现"其他"或"未知"
4. **缓存**: 建议前端缓存5分钟

## 📞 技术支持

如有问题，请查看：
- [机构地区修正完成报告](./机构地区修正完成报告.md)
- [地区信息问题总结](./地区信息问题总结.md)

---
**更新时间**: 2026-02-08
