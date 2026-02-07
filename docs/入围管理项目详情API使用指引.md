# 入围管理-项目详情API使用指引

## 问题现象

用户在入围管理页面点击项目详情，看到：
- ✅ 总分显示正确：88.0
- ❌ 分项得分全部显示 "-"（计划、问题、行动、成效、回顾、运作、展示）
- ❌ 亮点显示"暂无亮点"
- ❌ 改进建议未显示

**实际情况**：后端数据是完整的！是前端调用或解析有问题。

---

## 正确的API

### API路径

```
GET /api/registrations/{registrationId}/review-details
```

### 请求示例

```http
GET /api/registrations/106/review-details
Authorization: Bearer {token}
```

### 完整返回结构

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

---

## 数据结构说明

### 返回数组

`data` 是一个数组，包含3个阶段的评分数据：
1. `stage: "BOOK"` - 书审阶段
2. `stage: "INTERVIEW"` - 面谈阶段
3. `stage: "FINAL"` - 决赛阶段

### 字段说明

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| stage | String | 评审阶段 | `BOOK`/`INTERVIEW`/`FINAL` |
| taskCount | Integer | 分配的评审任务数 | 2 |
| scoredCount | Integer | 已完成评审数 | 1 |
| **avgPlan** | Double | 计划维度平均分 | 18.0 |
| **avgProblem** | Double | 问题维度平均分 | 17.0 |
| **avgAction** | Double | 行动维度平均分 | 19.0 |
| **avgSuccess** | Double | 成效维度平均分 | 18.0 |
| **avgReview** | Double | 回顾维度平均分 | 16.0 |
| **avgOperation** | Double | 运作维度平均分 | 0.0 |
| **avgPresentation** | Double | 展示维度平均分 | 0.0 |
| **avgTotal** | Double | 总分平均分 | 88.0 |
| **highlights** | Array[String] | 评委给出的亮点 | ["项目主题明确..."] |
| **weaknesses** | Array[String] | 评委给出的改进建议 | ["建议进一步..."] |

### 重要说明

1. **未评审阶段的字段为null或空数组**
   - `avgPlan`, `avgProblem` 等字段为 `null`
   - `highlights`, `weaknesses` 为空数组 `[]`

2. **已评审阶段的字段有值**
   - 数值类型字段为具体分数（可能是0.0）
   - 数组类型字段包含评委意见

---

## 前端解析逻辑

### 步骤1: 获取指定阶段数据

```javascript
// 调用API
const response = await axios.get(`/api/registrations/${registrationId}/review-details`, {
  headers: { Authorization: `Bearer ${token}` }
});

const allStages = response.data.data;

// 获取书审阶段数据
const bookStage = allStages.find(stage => stage.stage === 'BOOK');

// 获取面谈阶段数据
const interviewStage = allStages.find(stage => stage.stage === 'INTERVIEW');
```

### 步骤2: 显示分项得分

```javascript
// 书审分项得分
const bookScores = {
  plan: bookStage?.avgPlan || null,
  problem: bookStage?.avgProblem || null,
  action: bookStage?.avgAction || null,
  success: bookStage?.avgSuccess || null,
  review: bookStage?.avgReview || null,
  operation: bookStage?.avgOperation || null,
  presentation: bookStage?.avgPresentation || null,
  total: bookStage?.avgTotal || null
};

// 显示逻辑
// 如果分数为null，显示 "-"
// 如果分数为0，显示 "0.0"
// 如果分数有值，显示具体分数
```

### 步骤3: 显示评委意见

```javascript
// 书审亮点
const bookHighlights = bookStage?.highlights || [];
// 如果数组为空，显示"暂无亮点"
// 如果数组有值，遍历显示

// 书审改进建议
const bookWeaknesses = bookStage?.weaknesses || [];
// 如果数组为空，显示"暂无改进建议"
// 如果数组有值，遍历显示
```

---

## 完整示例代码

### Vue 3示例

```vue
<template>
  <div class="detail-modal">
    <!-- 书审评分 -->
    <div class="section">
      <h3>书审评分</h3>
      <table>
        <tr>
          <th>计划</th>
          <th>问题</th>
          <th>行动</th>
          <th>成效</th>
          <th>回顾</th>
          <th>运作</th>
          <th>展示</th>
          <th>总分</th>
        </tr>
        <tr>
          <td>{{ formatScore(bookData?.avgPlan) }}</td>
          <td>{{ formatScore(bookData?.avgProblem) }}</td>
          <td>{{ formatScore(bookData?.avgAction) }}</td>
          <td>{{ formatScore(bookData?.avgSuccess) }}</td>
          <td>{{ formatScore(bookData?.avgReview) }}</td>
          <td>{{ formatScore(bookData?.avgOperation) }}</td>
          <td>{{ formatScore(bookData?.avgPresentation) }}</td>
          <td>{{ formatScore(bookData?.avgTotal) }}</td>
        </tr>
      </table>
      
      <!-- 评委意见 -->
      <div class="opinions">
        <div class="highlights">
          <h4>✨ 亮点</h4>
          <p v-if="bookData?.highlights?.length === 0">暂无亮点</p>
          <ul v-else>
            <li v-for="(item, index) in bookData?.highlights" :key="index">
              {{ item }}
            </li>
          </ul>
        </div>
        
        <div class="weaknesses">
          <h4>💡 改进建议</h4>
          <p v-if="bookData?.weaknesses?.length === 0">暂无改进建议</p>
          <ul v-else>
            <li v-for="(item, index) in bookData?.weaknesses" :key="index">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </div>
    
    <!-- 面谈评分（同样结构） -->
    <div class="section">
      <h3>面谈评分</h3>
      <!-- 同上 -->
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const props = defineProps({
  registrationId: Number
});

const bookData = ref(null);
const interviewData = ref(null);

const formatScore = (score) => {
  if (score === null || score === undefined) {
    return '-';
  }
  return score.toFixed(1);
};

const loadDetail = async () => {
  try {
    const response = await axios.get(
      `/api/registrations/${props.registrationId}/review-details`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
    
    const allStages = response.data.data;
    
    // 找到书审阶段
    bookData.value = allStages.find(stage => stage.stage === 'BOOK');
    
    // 找到面谈阶段
    interviewData.value = allStages.find(stage => stage.stage === 'INTERVIEW');
    
  } catch (error) {
    console.error('加载详情失败:', error);
  }
};

onMounted(() => {
  loadDetail();
});
</script>
```

---

## 常见问题排查

### 问题1: 分项得分显示 "-"

**原因**：前端可能在访问字段时出错

**排查**：
1. 检查是否正确找到了 `stage === 'BOOK'` 的数据
2. 检查字段名是否正确（是 `avgPlan` 不是 `plan`）
3. 检查是否用了 `?.` 可选链操作符
4. 打开浏览器控制台，查看 `response.data.data` 的完整结构

### 问题2: 亮点显示"暂无亮点"但实际有数据

**原因**：可能判断逻辑有误

**正确判断**：
```javascript
// ❌ 错误
if (!highlights) { ... }

// ✅ 正确
if (!highlights || highlights.length === 0) { ... }

// ✅ 更好
if (Array.isArray(highlights) && highlights.length > 0) { ... }
```

### 问题3: 只显示总分，不显示分项

**原因**：可能只访问了 `avgTotal` 字段

**解决**：确保访问所有分项字段：
- `avgPlan`
- `avgProblem`
- `avgAction`
- `avgSuccess`
- `avgReview`
- `avgOperation`
- `avgPresentation`

---

## 验证步骤

### 1. 在浏览器控制台验证API返回

```javascript
// 在浏览器控制台执行
fetch('/api/registrations/106/review-details', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(data => {
  console.log('完整数据:', data);
  console.log('书审阶段:', data.data.find(s => s.stage === 'BOOK'));
});
```

### 2. 检查返回数据

应该看到：
```javascript
{
  stage: "BOOK",
  avgPlan: 18.0,         // ✅ 有值
  avgProblem: 17.0,      // ✅ 有值
  avgAction: 19.0,       // ✅ 有值
  avgSuccess: 18.0,      // ✅ 有值
  avgReview: 16.0,       // ✅ 有值
  avgTotal: 88.0,        // ✅ 有值
  highlights: ["项目主题明确..."],  // ✅ 有数据
  weaknesses: ["建议进一步..."]     // ✅ 有数据
}
```

### 3. 检查前端代码

确认以下几点：
- ✅ API路径正确：`/api/registrations/{id}/review-details`
- ✅ 从数组中找到正确的stage：`data.find(s => s.stage === 'BOOK')`
- ✅ 字段名拼写正确：`avgPlan`, `avgProblem` 等
- ✅ 处理了null值：`score === null ? '-' : score.toFixed(1)`
- ✅ 处理了空数组：`highlights.length === 0 ? '暂无' : 显示列表`

---

## 测试验证结果

**后端数据（已验证）**：
- ✅ API返回完整数据
- ✅ 分项得分：计划18.0, 问题17.0, 行动19.0, 成效18.0, 回顾16.0
- ✅ 总分：88.0
- ✅ 亮点：1条（"项目主题明确，改进措施得当，成效显著..."）
- ✅ 改进建议：1条（"建议进一步量化成本效益分析..."）

**结论**：
- 后端数据完全正确✅
- 问题出在前端解析或显示❌
- 请按上述指引检查前端代码

---

## 快速修复检查清单

- [ ] API路径是否正确？`/api/registrations/{id}/review-details`
- [ ] 是否正确解析了返回的数组结构？`data.data`
- [ ] 是否找到了书审阶段数据？`find(s => s.stage === 'BOOK')`
- [ ] 字段名是否正确？`avgPlan`, `avgProblem`, `avgAction`...
- [ ] 是否处理了null值？显示"-"而不是报错
- [ ] 是否正确判断了空数组？`highlights.length === 0`
- [ ] 浏览器控制台是否有错误？检查Network和Console

---

## 联系支持

如果按上述步骤仍然无法解决，请提供：
1. 浏览器控制台的Network截图（API请求和响应）
2. 浏览器控制台的错误信息
3. 前端代码中处理该API的相关代码片段
