# 前端调整指引 - 评委评分详情API

**发布日期**: 2026-02-07  
**影响范围**: 入围管理页面 - 项目详情展示  
**紧急程度**: 中等（有废弃API需要迁移）

---

## 📋 变更概览

### 新增API（1个）
✨ **GET** `/api/registrations/{id}/reviewer-scores?stage={BOOK|INTERVIEW|FINAL}`  
**功能**: 返回指定项目每个评委的详细评分记录

### 废弃API（1个）
❌ **GET** `/api/admin/reviews/feedback?competitionId={id}&stage={stage}`  
**状态**: 已标记为 `@Deprecated`，建议立即迁移到新API

### 保留API（不受影响）
✅ **GET** `/api/registrations/{id}/review-details` - 汇总平均分（建议保留使用）  
✅ **GET** `/api/admin/reviews/rankings` - 排行榜  
✅ **GET** `/api/admin/reviews/shortlist` - 入围筛选

---

## ❌ 废弃API详情

### GET /api/admin/reviews/feedback

**废弃原因**: 新API完全覆盖并超越了此API的功能

#### 旧API请求
```javascript
// ❌ 不推荐（已废弃）
const response = await axios.get('/api/admin/reviews/feedback', {
  params: {
    competitionId: 21,
    stage: 'BOOK'
  },
  headers: { Authorization: `Bearer ${token}` }
});

// 需要筛选出指定项目
const projectFeedback = response.data.data.filter(
  item => item.registrationId === 106
);
```

#### 旧API返回
```json
{
  "success": true,
  "data": [
    {
      "registrationId": 106,
      "projectName": "护理质量持续改进",
      "institutionName": "浙江大学医学院附属第一医院",
      "stage": "BOOK",
      "reviewerId": 21,
      "reviewerName": "张三",
      "total": 88,           // ✅ 有总分
      "highlight": "...",    // ✅ 有亮点
      "weakness": "..."      // ✅ 有改进建议
    }
  ]
}
```

#### 旧API不足
- ❌ **缺少分项评分**（plan, problem, action等7个维度）
- ❌ **缺少评委单位、职称**
- ❌ **缺少评审时间**
- ❌ **需要按赛事查询**，返回所有项目，需前端筛选

---

## ✨ 新API详情

### GET /api/registrations/{id}/reviewer-scores

#### API信息
- **路径**: `/api/registrations/{registrationId}/reviewer-scores`
- **方法**: GET
- **权限**: 需要登录（Bearer Token）

#### 请求参数

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `registrationId` | Long | 是 | 报名ID（路径参数） | 106 |
| `stage` | String | 否 | 评审阶段（查询参数） | BOOK / INTERVIEW / FINAL |

#### 请求示例

```javascript
// ✅ 推荐：获取项目106的所有评委评分（所有阶段）
const response = await axios.get('/api/registrations/106/reviewer-scores', {
  headers: { Authorization: `Bearer ${token}` }
});

// ✅ 推荐：只获取书审阶段评分
const bookResponse = await axios.get('/api/registrations/106/reviewer-scores', {
  params: { stage: 'BOOK' },
  headers: { Authorization: `Bearer ${token}` }
});

// ✅ 推荐：只获取面谈阶段评分
const interviewResponse = await axios.get('/api/registrations/106/reviewer-scores', {
  params: { stage: 'INTERVIEW' },
  headers: { Authorization: `Bearer ${token}` }
});
```

#### 返回结构

```json
{
  "success": true,
  "data": [
    {
      "stage": "BOOK",
      "reviewerId": 21,
      "reviewerName": "张三",
      "reviewerTitle": "主任医师",
      "reviewerInstitutionId": 1,
      "reviewerInstitutionName": "浙江大学医学院附属第一医院",
      "reviewerInstitutionLevel": "三级甲等",
      "scores": {
        "plan": 18,
        "problem": 17,
        "action": 19,
        "success": 18,
        "review": 16,
        "operation": 0,
        "presentation": 0,
        "total": 88
      },
      "highlight": "项目主题明确，改进措施得当，成效显著。实施过程规范，数据收集完整，对比分析清晰。团队协作良好。",
      "weakness": "建议进一步量化成本效益分析。可以增加更多的跨部门协作案例。持续改进机制可以更完善。",
      "submittedAt": "2026-02-05T14:30:00"
    },
    {
      "stage": "BOOK",
      "reviewerId": 22,
      "reviewerName": "李四",
      "reviewerTitle": "副主任医师",
      "reviewerInstitutionId": 2,
      "reviewerInstitutionName": "浙江省人民医院",
      "reviewerInstitutionLevel": "三级甲等",
      "scores": {
        "plan": 19,
        "problem": 18,
        "action": 20,
        "success": 19,
        "review": 17,
        "operation": 0,
        "presentation": 0,
        "total": 93
      },
      "highlight": "数据详实，逻辑严密，具有很好的推广价值",
      "weakness": "建议补充长期跟踪数据",
      "submittedAt": "2026-02-06T10:15:00"
    }
  ],
  "message": null
}
```

#### 返回字段说明

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `stage` | String | 评审阶段 | BOOK / INTERVIEW / FINAL |
| `reviewerId` | Long | 评委ID | 21 |
| `reviewerName` | String | 评委姓名 | 张三 |
| `reviewerTitle` | String | 评委职称 | 主任医师 |
| `reviewerInstitutionId` | Long | 评委机构ID | 1 |
| `reviewerInstitutionName` | String | 评委机构名称 | 浙江大学医学院附属第一医院 |
| `reviewerInstitutionLevel` | String | 评委机构等级 | 三级甲等 |
| `scores` | Object | 评分详情对象 | 见下表 |
| `highlight` | String | 亮点评语 | 项目主题明确... |
| `weakness` | String | 改进建议 | 建议进一步... |
| `submittedAt` | DateTime | 评审时间 | 2026-02-05T14:30:00 |

#### scores对象字段说明

| 字段 | 类型 | 说明 | 满分 | 示例值 |
|------|------|------|------|--------|
| `plan` | Integer | 计划维度得分 | 20 | 18 |
| `problem` | Integer | 问题维度得分 | 20 | 17 |
| `action` | Integer | 行动维度得分 | 20 | 19 |
| `success` | Integer | 成效维度得分 | 15 | 18 |
| `review` | Integer | 回顾维度得分 | 10 | 16 |
| `operation` | Integer | 运作维度得分 | 10 | 0 |
| `presentation` | Integer | 展示维度得分 | 5 | 0 |
| `total` | Integer | 总分 | 100 | 88 |

---

## 🔄 前端迁移方案

### 方案A: 完全替换（推荐）⭐

**适用场景**: 需要展示每个评委的详细评分

**迁移步骤**:

1. **找到所有调用废弃API的地方**
   ```bash
   # 搜索项目中所有调用
   grep -r "admin/reviews/feedback" src/
   ```

2. **替换为新API**
   ```javascript
   // ❌ 旧代码
   const getFeedback = async (competitionId, stage) => {
     const response = await axios.get('/api/admin/reviews/feedback', {
       params: { competitionId, stage }
     });
     return response.data.data.filter(item => item.registrationId === currentProjectId);
   };
   
   // ✅ 新代码
   const getReviewerScores = async (registrationId, stage = null) => {
     const params = stage ? { stage } : {};
     const response = await axios.get(`/api/registrations/${registrationId}/reviewer-scores`, {
       params
     });
     return response.data.data;
   };
   ```

3. **调整数据展示逻辑**
   ```javascript
   // ✅ 新代码展示
   const reviewerScores = await getReviewerScores(106, 'BOOK');
   
   reviewerScores.forEach(reviewer => {
     console.log(`评委: ${reviewer.reviewerName}（${reviewer.reviewerInstitutionName}）`);
     console.log(`职称: ${reviewer.reviewerTitle}`);
     console.log(`总分: ${reviewer.scores.total}分`);
     console.log(`计划: ${reviewer.scores.plan}分`);
     console.log(`问题: ${reviewer.scores.problem}分`);
     console.log(`行动: ${reviewer.scores.action}分`);
     console.log(`成效: ${reviewer.scores.success}分`);
     console.log(`回顾: ${reviewer.scores.review}分`);
     console.log(`亮点: ${reviewer.highlight}`);
     console.log(`改进建议: ${reviewer.weakness}`);
     console.log(`评审时间: ${reviewer.submittedAt}`);
   });
   ```

---

### 方案B: 渐进式迁移（保守）

**适用场景**: 多个页面使用，希望逐步迁移

**步骤**:

1. **创建新的API封装函数**
   ```javascript
   // api/review.js
   
   // 新API
   export const getReviewerScoresByRegistration = async (registrationId, stage = null) => {
     const params = stage ? { stage } : {};
     const response = await axios.get(`/api/registrations/${registrationId}/reviewer-scores`, {
       params,
       headers: { Authorization: `Bearer ${getToken()}` }
     });
     return response.data;
   };
   
   // 旧API（保留但标记）
   /** @deprecated 请使用 getReviewerScoresByRegistration */
   export const getReviewFeedback = async (competitionId, stage) => {
     const response = await axios.get('/api/admin/reviews/feedback', {
       params: { competitionId, stage }
     });
     return response.data;
   };
   ```

2. **新页面使用新API**
   ```javascript
   // 新建的入围管理详情页
   import { getReviewerScoresByRegistration } from '@/api/review';
   
   const reviewerScores = await getReviewerScoresByRegistration(projectId, 'BOOK');
   ```

3. **旧页面逐步迁移**
   - 优先迁移高频页面
   - 测试通过后再迁移其他页面

---

## 📱 完整前端示例

### Vue 3 + TypeScript 示例

#### 1. 类型定义

```typescript
// types/review.ts

export interface ScoreBreakdown {
  plan: number;
  problem: number;
  action: number;
  success: number;
  review: number;
  operation: number;
  presentation: number;
  total: number;
}

export interface ReviewerScoreDetail {
  stage: 'BOOK' | 'INTERVIEW' | 'FINAL';
  reviewerId: number;
  reviewerName: string;
  reviewerTitle: string;
  reviewerInstitutionId: number;
  reviewerInstitutionName: string;
  reviewerInstitutionLevel: string;
  scores: ScoreBreakdown;
  highlight: string;
  weakness: string;
  submittedAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string | null;
}
```

#### 2. API封装

```typescript
// api/review.ts
import axios from 'axios';
import type { ReviewerScoreDetail, ApiResponse } from '@/types/review';

const API_BASE = 'http://localhost:6031/api';

export const reviewApi = {
  /**
   * 获取项目的评委评分详情
   * @param registrationId 报名ID
   * @param stage 评审阶段（可选）
   */
  async getReviewerScores(
    registrationId: number,
    stage?: 'BOOK' | 'INTERVIEW' | 'FINAL'
  ): Promise<ReviewerScoreDetail[]> {
    const params = stage ? { stage } : {};
    const response = await axios.get<ApiResponse<ReviewerScoreDetail[]>>(
      `${API_BASE}/registrations/${registrationId}/reviewer-scores`,
      { params }
    );
    return response.data.data;
  },
};
```

#### 3. Vue组件

```vue
<template>
  <div class="reviewer-scores">
    <h2>评委评分详情</h2>
    
    <!-- 阶段筛选 -->
    <div class="stage-filter">
      <button 
        v-for="stage in stages" 
        :key="stage.value"
        :class="{ active: currentStage === stage.value }"
        @click="currentStage = stage.value"
      >
        {{ stage.label }}
      </button>
    </div>
    
    <!-- 评委评分列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="reviewerScores.length === 0" class="empty">暂无评审数据</div>
    <div v-else class="scores-list">
      <div 
        v-for="reviewer in reviewerScores" 
        :key="reviewer.reviewerId"
        class="reviewer-card"
      >
        <!-- 评委信息 -->
        <div class="reviewer-info">
          <h3>{{ reviewer.reviewerName }}</h3>
          <p class="subtitle">{{ reviewer.reviewerTitle }} | {{ reviewer.reviewerInstitutionName }}</p>
          <span class="badge">{{ reviewer.reviewerInstitutionLevel }}</span>
        </div>
        
        <!-- 分项评分 -->
        <div class="scores-grid">
          <div class="score-item">
            <span class="label">计划</span>
            <span class="value">{{ reviewer.scores.plan }}分</span>
          </div>
          <div class="score-item">
            <span class="label">问题</span>
            <span class="value">{{ reviewer.scores.problem }}分</span>
          </div>
          <div class="score-item">
            <span class="label">行动</span>
            <span class="value">{{ reviewer.scores.action }}分</span>
          </div>
          <div class="score-item">
            <span class="label">成效</span>
            <span class="value">{{ reviewer.scores.success }}分</span>
          </div>
          <div class="score-item">
            <span class="label">回顾</span>
            <span class="value">{{ reviewer.scores.review }}分</span>
          </div>
          <div class="score-item">
            <span class="label">运作</span>
            <span class="value">{{ reviewer.scores.operation }}分</span>
          </div>
          <div class="score-item">
            <span class="label">展示</span>
            <span class="value">{{ reviewer.scores.presentation }}分</span>
          </div>
          <div class="score-item total">
            <span class="label">总分</span>
            <span class="value">{{ reviewer.scores.total }}分</span>
          </div>
        </div>
        
        <!-- 评语 -->
        <div class="comments">
          <div class="highlight">
            <h4>亮点</h4>
            <p>{{ reviewer.highlight }}</p>
          </div>
          <div class="weakness">
            <h4>改进建议</h4>
            <p>{{ reviewer.weakness }}</p>
          </div>
        </div>
        
        <!-- 评审时间 -->
        <div class="footer">
          <span class="time">评审时间: {{ formatTime(reviewer.submittedAt) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { reviewApi } from '@/api/review';
import type { ReviewerScoreDetail } from '@/types/review';

const props = defineProps<{
  projectId: number;
}>();

const stages = [
  { value: null, label: '全部' },
  { value: 'BOOK', label: '书审' },
  { value: 'INTERVIEW', label: '面谈' },
  { value: 'FINAL', label: '决赛' },
];

const currentStage = ref<'BOOK' | 'INTERVIEW' | 'FINAL' | null>(null);
const reviewerScores = ref<ReviewerScoreDetail[]>([]);
const loading = ref(false);

const fetchScores = async () => {
  loading.value = true;
  try {
    reviewerScores.value = await reviewApi.getReviewerScores(
      props.projectId,
      currentStage.value || undefined
    );
  } catch (error) {
    console.error('获取评委评分失败:', error);
  } finally {
    loading.value = false;
  }
};

const formatTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString('zh-CN');
};

watch(currentStage, fetchScores);

onMounted(fetchScores);
</script>

<style scoped>
.reviewer-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: white;
}

.reviewer-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.subtitle {
  color: #666;
  margin: 0 0 8px 0;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin: 20px 0;
}

.score-item {
  text-align: center;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.score-item.total {
  background: #fff3e0;
  grid-column: span 2;
}

.score-item .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.score-item .value {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #1976d2;
}

.comments {
  margin-top: 20px;
}

.comments h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
}

.highlight {
  margin-bottom: 12px;
}

.highlight p {
  color: #2e7d32;
  background: #e8f5e9;
  padding: 12px;
  border-radius: 4px;
}

.weakness p {
  color: #f57c00;
  background: #fff3e0;
  padding: 12px;
  border-radius: 4px;
}

.footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.time {
  font-size: 12px;
  color: #999;
}
</style>
```

#### 4. React + TypeScript 示例

```typescript
// hooks/useReviewerScores.ts
import { useState, useEffect } from 'react';
import { reviewApi } from '@/api/review';
import type { ReviewerScoreDetail } from '@/types/review';

export const useReviewerScores = (
  projectId: number,
  stage?: 'BOOK' | 'INTERVIEW' | 'FINAL'
) => {
  const [scores, setScores] = useState<ReviewerScoreDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchScores = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await reviewApi.getReviewerScores(projectId, stage);
        setScores(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchScores();
  }, [projectId, stage]);

  return { scores, loading, error };
};
```

```typescript
// components/ReviewerScoresPanel.tsx
import React from 'react';
import { useReviewerScores } from '@/hooks/useReviewerScores';

interface Props {
  projectId: number;
  stage?: 'BOOK' | 'INTERVIEW' | 'FINAL';
}

export const ReviewerScoresPanel: React.FC<Props> = ({ projectId, stage }) => {
  const { scores, loading, error } = useReviewerScores(projectId, stage);

  if (loading) return <div>加载中...</div>;
  if (error) return <div>加载失败: {error.message}</div>;
  if (scores.length === 0) return <div>暂无评审数据</div>;

  return (
    <div className="reviewer-scores">
      {scores.map(reviewer => (
        <div key={reviewer.reviewerId} className="reviewer-card">
          <div className="reviewer-info">
            <h3>{reviewer.reviewerName}</h3>
            <p>{reviewer.reviewerTitle} | {reviewer.reviewerInstitutionName}</p>
            <span className="badge">{reviewer.reviewerInstitutionLevel}</span>
          </div>
          
          <div className="scores-grid">
            <ScoreItem label="计划" value={reviewer.scores.plan} />
            <ScoreItem label="问题" value={reviewer.scores.problem} />
            <ScoreItem label="行动" value={reviewer.scores.action} />
            <ScoreItem label="成效" value={reviewer.scores.success} />
            <ScoreItem label="回顾" value={reviewer.scores.review} />
            <ScoreItem label="运作" value={reviewer.scores.operation} />
            <ScoreItem label="展示" value={reviewer.scores.presentation} />
            <ScoreItem label="总分" value={reviewer.scores.total} isTotal />
          </div>
          
          <div className="comments">
            <div className="highlight">
              <h4>亮点</h4>
              <p>{reviewer.highlight}</p>
            </div>
            <div className="weakness">
              <h4>改进建议</h4>
              <p>{reviewer.weakness}</p>
            </div>
          </div>
          
          <div className="footer">
            <span className="time">
              评审时间: {new Date(reviewer.submittedAt).toLocaleString('zh-CN')}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

const ScoreItem: React.FC<{ label: string; value: number; isTotal?: boolean }> = ({ 
  label, 
  value, 
  isTotal 
}) => (
  <div className={`score-item ${isTotal ? 'total' : ''}`}>
    <span className="label">{label}</span>
    <span className="value">{value}分</span>
  </div>
);
```

---

## ⚠️ 注意事项

### 1. 权限控制
```javascript
// 新API需要登录token
const response = await axios.get('/api/registrations/106/reviewer-scores', {
  headers: { 
    Authorization: `Bearer ${token}` 
  }
});
```

### 2. 空数据处理
```javascript
// 当项目还未评审时，返回空数组
if (reviewerScores.length === 0) {
  // 显示"暂无评审数据"或"待评审"状态
}
```

### 3. 按阶段展示
```javascript
// 建议提供阶段切换功能
const stages = ['BOOK', 'INTERVIEW', 'FINAL'];
const [currentStage, setCurrentStage] = useState('BOOK');

// 根据当前阶段获取数据
const scores = await reviewApi.getReviewerScores(projectId, currentStage);
```

### 4. 平均分计算（如需要）
```javascript
// 如果需要显示平均分，前端自己计算
const calculateAverage = (scores: ReviewerScoreDetail[]) => {
  if (scores.length === 0) return 0;
  
  const totalSum = scores.reduce((sum, reviewer) => sum + reviewer.scores.total, 0);
  return (totalSum / scores.length).toFixed(1);
};

// 或者继续使用旧的 /review-details API获取平均分（推荐）
const avgScores = await reviewApi.getReviewDetails(projectId);
```

---

## 🎯 迁移检查清单

### 开发阶段
- [ ] 搜索项目中所有调用 `/admin/reviews/feedback` 的地方
- [ ] 更新API封装函数
- [ ] 更新类型定义（TypeScript）
- [ ] 更新组件调用逻辑
- [ ] 更新数据展示UI

### 测试阶段
- [ ] 测试获取所有阶段评分
- [ ] 测试按阶段过滤（BOOK, INTERVIEW, FINAL）
- [ ] 测试无数据情况（空数组）
- [ ] 测试scores对象的7个维度显示
- [ ] 测试评委信息完整性
- [ ] 测试评审时间格式化

### 上线阶段
- [ ] 确认所有页面已迁移
- [ ] 移除废弃API的调用代码
- [ ] 更新API文档
- [ ] 通知团队成员

---

## 📞 技术支持

如有问题，请联系后端开发团队：

- 新API文档: `/swagger` 或 `/api-docs`
- 测试脚本: `scripts/test_reviewer_scores_api.py`
- 技术文档: `docs/入围管理API废弃与替换说明.md`

---

## 📝 更新日志

**v1.0 - 2026-02-07**
- ✨ 新增 GET `/api/registrations/{id}/reviewer-scores` API
- ❌ 废弃 GET `/api/admin/reviews/feedback` API
- 📚 提供完整的前端迁移指引和示例代码

---

**文档编写人**: AI Assistant  
**最后更新**: 2026-02-07
