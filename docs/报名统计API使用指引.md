# 报名统计API使用指引

## 接口概述

**接口地址**: `GET /api/admin/stats/summary`

**请求方法**: GET

**输入参数**: 无（自动返回最新赛事的数据）

**功能**: 获取最新赛事的报名统计汇总数据，包括地区分布、主题类型分布、评分统计等。

**权限**: 需要登录（任何角色）

**说明**: 
- 接口自动查询ID最大的赛事（最新赛事）
- 不需要传递任何参数
- 如需查询指定赛事，请联系后端添加 `competitionId` 参数支持

## 接口调用

### 请求示例

```javascript
// JavaScript/TypeScript
const response = await fetch('/api/admin/stats/summary', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const result = await response.json();
```

### 响应格式

```json
{
  "success": true,
  "data": {
    "competitionId": 21,
    "competitionName": "2026浙江品管大赛",
    "registrationCount": 45,
    "toolTypeCount": 8,
    "reviewerCount": 19,
    "reviewerInstitutionCount": 11,
    "bookReviewTaskCount": 45,
    "bookReviewUnscoredCount": 10,
    "regionCounts": {
      "杭州": 17,
      "舟山": 15,
      "宁波": 3,
      "温州": 2,
      "绍兴": 2,
      "嘉兴": 1,
      "湖州": 1,
      "金华": 1,
      "衢州": 1,
      "台州": 1,
      "丽水": 1
    },
    "subjectTypeCounts": {
      "医疗安全": 15,
      "服务流程": 12,
      "教育训练": 8,
      "成本控制": 5,
      "其他": 5
    },
    "avgPlan": 18.5,
    "avgProblem": 17.8,
    "avgAction": 19.2,
    "avgSuccess": 18.9,
    "avgReview": 17.5,
    "avgOperation": 16.8,
    "avgPresentation": 15.2
  },
  "message": null
}
```

## 数据字段说明

### 基础统计

| 字段 | 类型 | 说明 |
|------|------|------|
| `competitionId` | Number | 赛事ID |
| `competitionName` | String | 赛事名称 |
| `registrationCount` | Number | 报名总数 |
| `toolTypeCount` | Number | 使用的品管工具种类数 |
| `reviewerCount` | Number | 评委总数 |
| `reviewerInstitutionCount` | Number | 评委所属机构数 |
| `bookReviewTaskCount` | Number | 书审任务总数 |
| `bookReviewUnscoredCount` | Number | 未评分的书审任务数 |

### 分布统计

| 字段 | 类型 | 说明 |
|------|------|------|
| `regionCounts` | Object | 地区分布，key为地区名，value为报名数 |
| `subjectTypeCounts` | Object | 主题类型分布，key为主题类型，value为报名数 |

### 平均分数

| 字段 | 类型 | 说明 |
|------|------|------|
| `avgPlan` | Number | 计划平均分 |
| `avgProblem` | Number | 问题平均分 |
| `avgAction` | Number | 行动平均分 |
| `avgSuccess` | Number | 成功平均分 |
| `avgReview` | Number | 评审平均分 |
| `avgOperation` | Number | 操作平均分 |
| `avgPresentation` | Number | 展示平均分 |

## 前端使用示例

### Vue 3 + ECharts 示例

#### 1. 地区分布饼图

```vue
<template>
  <div>
    <h2>{{ competitionName }} - 报名统计</h2>
    
    <!-- 地区分布饼图 -->
    <div ref="regionChartRef" style="width: 600px; height: 400px;"></div>
    
    <!-- 主题类型分布饼图 -->
    <div ref="subjectChartRef" style="width: 600px; height: 400px;"></div>
    
    <!-- 评分雷达图 -->
    <div ref="scoreChartRef" style="width: 600px; height: 400px;"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const regionChartRef = ref(null);
const subjectChartRef = ref(null);
const scoreChartRef = ref(null);
const competitionName = ref('');

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await fetch('/api/admin/stats/summary', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      const data = result.data;
      competitionName.value = data.competitionName;
      
      // 绘制地区分布饼图
      drawRegionChart(data.regionCounts);
      
      // 绘制主题类型分布饼图
      drawSubjectChart(data.subjectTypeCounts);
      
      // 绘制评分雷达图
      drawScoreChart(data);
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

// 绘制地区分布饼图
const drawRegionChart = (regionCounts) => {
  const chart = echarts.init(regionChartRef.value);
  
  // 转换数据格式
  const data = Object.entries(regionCounts).map(([name, value]) => ({
    name,
    value
  }));
  
  // 按数量排序
  data.sort((a, b) => b.value - a.value);
  
  const option = {
    title: {
      text: '地区分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: data.map(item => item.name)
    },
    series: [
      {
        name: '报名数',
        type: 'pie',
        radius: '50%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {c} ({d}%)'
        }
      }
    ]
  };
  
  chart.setOption(option);
};

// 绘制主题类型分布饼图
const drawSubjectChart = (subjectTypeCounts) => {
  const chart = echarts.init(subjectChartRef.value);
  
  const data = Object.entries(subjectTypeCounts).map(([name, value]) => ({
    name,
    value
  }));
  
  data.sort((a, b) => b.value - a.value);
  
  const option = {
    title: {
      text: '主题类型分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: data.map(item => item.name)
    },
    series: [
      {
        name: '报名数',
        type: 'pie',
        radius: ['40%', '70%'], // 环形饼图
        avoidLabelOverlap: false,
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        }
      }
    ]
  };
  
  chart.setOption(option);
};

// 绘制评分雷达图
const drawScoreChart = (data) => {
  const chart = echarts.init(scoreChartRef.value);
  
  const option = {
    title: {
      text: '平均评分',
      left: 'center'
    },
    tooltip: {},
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
    series: [
      {
        name: '平均分',
        type: 'radar',
        data: [
          {
            value: [
              data.avgPlan,
              data.avgProblem,
              data.avgAction,
              data.avgSuccess,
              data.avgReview,
              data.avgOperation,
              data.avgPresentation
            ],
            name: '平均分'
          }
        ]
      }
    ]
  };
  
  chart.setOption(option);
};

onMounted(() => {
  fetchStats();
});
</script>
```

#### 2. React + ECharts 示例

```jsx
import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts';

function StatsCharts() {
  const regionChartRef = useRef(null);
  const subjectChartRef = useRef(null);
  const [competitionName, setCompetitionName] = useState('');
  
  useEffect(() => {
    fetchStats();
  }, []);
  
  const fetchStats = async () => {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('/api/admin/stats/summary', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        const data = result.data;
        setCompetitionName(data.competitionName);
        
        drawRegionChart(data.regionCounts);
        drawSubjectChart(data.subjectTypeCounts);
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    }
  };
  
  const drawRegionChart = (regionCounts) => {
    const chart = echarts.init(regionChartRef.current);
    
    const data = Object.entries(regionCounts).map(([name, value]) => ({
      name,
      value
    }));
    
    data.sort((a, b) => b.value - a.value);
    
    const option = {
      title: {
        text: '地区分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '报名数',
          type: 'pie',
          radius: '50%',
          data: data,
          label: {
            formatter: '{b}: {c} ({d}%)'
          }
        }
      ]
    };
    
    chart.setOption(option);
  };
  
  const drawSubjectChart = (subjectTypeCounts) => {
    const chart = echarts.init(subjectChartRef.current);
    
    const data = Object.entries(subjectTypeCounts).map(([name, value]) => ({
      name,
      value
    }));
    
    data.sort((a, b) => b.value - a.value);
    
    const option = {
      title: {
        text: '主题类型分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          name: '报名数',
          type: 'pie',
          radius: ['40%', '70%'],
          data: data,
          label: {
            formatter: '{b}: {d}%'
          }
        }
      ]
    };
    
    chart.setOption(option);
  };
  
  return (
    <div>
      <h2>{competitionName} - 报名统计</h2>
      <div ref={regionChartRef} style={{ width: '600px', height: '400px' }}></div>
      <div ref={subjectChartRef} style={{ width: '600px', height: '400px' }}></div>
    </div>
  );
}

export default StatsCharts;
```

### 3. 使用 Chart.js 的示例

```vue
<template>
  <div>
    <h2>{{ competitionName }} - 报名统计</h2>
    
    <!-- 地区分布饼图 -->
    <canvas ref="regionChartRef"></canvas>
    
    <!-- 主题类型分布饼图 -->
    <canvas ref="subjectChartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { Chart, registerables } from 'chart.js';
import { useAuthStore } from '@/stores/auth';

Chart.register(...registerables);

const authStore = useAuthStore();
const regionChartRef = ref(null);
const subjectChartRef = ref(null);
const competitionName = ref('');

const fetchStats = async () => {
  try {
    const response = await fetch('/api/admin/stats/summary', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      const data = result.data;
      competitionName.value = data.competitionName;
      
      drawRegionChart(data.regionCounts);
      drawSubjectChart(data.subjectTypeCounts);
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
};

const drawRegionChart = (regionCounts) => {
  const labels = Object.keys(regionCounts);
  const data = Object.values(regionCounts);
  
  new Chart(regionChartRef.value, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        label: '报名数',
        data: data,
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)',
          'rgba(199, 199, 199, 0.8)',
          'rgba(83, 102, 255, 0.8)',
          'rgba(255, 99, 255, 0.8)',
          'rgba(99, 255, 132, 0.8)',
          'rgba(255, 206, 199, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '地区分布'
        },
        legend: {
          position: 'right'
        }
      }
    }
  });
};

const drawSubjectChart = (subjectTypeCounts) => {
  const labels = Object.keys(subjectTypeCounts);
  const data = Object.values(subjectTypeCounts);
  
  new Chart(subjectChartRef.value, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: '报名数',
        data: data,
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: '主题类型分布'
        },
        legend: {
          position: 'right'
        }
      }
    }
  });
};

onMounted(() => {
  fetchStats();
});
</script>
```

## 数据处理技巧

### 1. 地区数据排序

```javascript
// 按报名数降序排序
const sortedRegions = Object.entries(regionCounts)
  .sort(([, a], [, b]) => b - a)
  .map(([name, value]) => ({ name, value }));
```

### 2. 计算百分比

```javascript
const total = Object.values(regionCounts).reduce((sum, count) => sum + count, 0);

const regionsWithPercentage = Object.entries(regionCounts).map(([name, value]) => ({
  name,
  value,
  percentage: ((value / total) * 100).toFixed(1) + '%'
}));
```

### 3. 数据分组（Top N + 其他）

```javascript
// 显示前5名，其余归为"其他"
const topN = 5;
const sortedData = Object.entries(regionCounts)
  .sort(([, a], [, b]) => b - a);

const topRegions = sortedData.slice(0, topN);
const otherRegions = sortedData.slice(topN);

const chartData = [
  ...topRegions.map(([name, value]) => ({ name, value }))
];

if (otherRegions.length > 0) {
  const otherTotal = otherRegions.reduce((sum, [, value]) => sum + value, 0);
  chartData.push({ name: '其他', value: otherTotal });
}
```

## 常见问题

### Q1: 接口返回的是最新赛事，如何查询历史赛事？

A: 当前接口只支持查询最新赛事。如需查询历史赛事，请联系后端添加 `competitionId` 参数支持。

### Q2: 地区名称可能有哪些值？

A: 浙江省11个地级市：杭州、宁波、温州、绍兴、嘉兴、湖州、金华、衢州、舟山、台州、丽水

### Q3: 如果没有数据怎么办？

A: 检查返回的 `regionCounts` 和 `subjectTypeCounts` 是否为空对象，如果为空则显示"暂无数据"提示。

```javascript
if (Object.keys(regionCounts).length === 0) {
  // 显示"暂无数据"
  console.log('暂无地区分布数据');
}
```

### Q4: 如何处理响应式布局？

A: 使用 ECharts 的响应式配置：

```javascript
const chart = echarts.init(chartRef.value);

// 监听窗口大小变化
window.addEventListener('resize', () => {
  chart.resize();
});

// 组件卸载时移除监听
onUnmounted(() => {
  window.removeEventListener('resize', chart.resize);
  chart.dispose();
});
```

## 完整示例项目

查看完整的前端示例项目：`docs/前端调用示例.html`

## 相关文档

- [机构地区修正完成报告](./机构地区修正完成报告.md)
- [分组接口使用范例](./分组接口使用范例.md)
- [API完整使用指南](./API完整使用指南.md)

---
**更新时间**: 2026-02-08  
**接口版本**: v1.0  
**数据状态**: 地区信息已修正
