# 面谈得分列表 - API支持方案

## 一、需求分析

**需求**：面谈得分列表页面，样式与书审得分列表基本一致

**现状**：
- ✅ 已有书审得分列表接口：`GET /api/admin/reviews/book-scores`
- ❌ 没有面谈得分列表接口
- ⚠️  现有接口硬编码了`ReviewStage.BOOK`

## 二、现有接口分析

### 2.1 书审得分列表接口
```
GET /api/admin/reviews/book-scores
参数:
  - competitionId: 竞赛ID (必填)
  - status: 任务状态 (可选)
  - reviewerId: 评委ID (可选)
  - institutionId: 机构ID (可选)
  - groupType: 组别类型 (可选)

返回: List<BookScoreItem>
```

### 2.2 BookScoreItem 结构
```java
{
  "taskId": 115,
  "status": "SCORED",
  "registrationId": 123,
  "projectName": "护理交接班规范化",
  "institutionName": "浙江省人民医院",
  "institutionLevel": "三级甲等",
  "groupType": "BASIC",
  "groupCode": "A1",
  "reviewerId": 84,
  "reviewerName": "李明华",
  "reviewerTitle": "主任医师",
  "reviewerInstitutionName": "浙江大学医学院附属第一医院",
  "scoreId": 49,
  "plan": 12.0,
  "problem": 13.0,
  "action": 14.0,
  "success": 13.0,
  "review": 12.0,
  "operation": 13.0,
  "presentation": 14.0,
  "total": 91.0,
  "submittedAt": "2026-02-13T10:30:00",
  "createdAt": "2026-02-10T09:00:00"
}
```

### 2.3 核心逻辑
```java
// 硬编码了 BOOK 阶段
List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
    ReviewStage.BOOK, competitionId);
```

## 三、解决方案

### 方案1：新增面谈得分列表接口（推荐）

**优点**：
- 不影响现有书审接口
- 接口语义清晰
- 前端调用简单

**实现**：
```java
@GetMapping("/interview-scores")
@Operation(summary = "面谈得分列表")
public ApiResponse<List<BookScoreItem>> listInterviewScores(
        @RequestParam Long competitionId,
        @RequestParam(required = false) ReviewStatus status,
        @RequestParam(required = false) Long reviewerId,
        @RequestParam(required = false) Long institutionId,
        @RequestParam(required = false) GroupType groupType) {
    return ApiResponse.ok(reviewService.listInterviewScores(
            competitionId, status, reviewerId, institutionId, groupType));
}
```

**Service层**：
```java
@Transactional(readOnly = true)
public List<BookScoreItem> listInterviewScores(
        Long competitionId,
        ReviewStatus status,
        Long reviewerId,
        Long institutionId,
        GroupType groupType) {
    
    // 只改这一行：BOOK -> INTERVIEW
    List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
            ReviewStage.INTERVIEW, competitionId);
    
    // 其他逻辑完全相同
    // ... (与listBookScores相同的处理逻辑)
}
```

### 方案2：重构为通用接口

**优点**：
- 代码复用性高
- 支持所有阶段（书审、面谈、终审）
- 减少重复代码

**实现**：
```java
@GetMapping("/scores")
@Operation(summary = "评审得分列表（通用）")
public ApiResponse<List<BookScoreItem>> listScores(
        @RequestParam Long competitionId,
        @RequestParam ReviewStage stage,  // 新增：阶段参数
        @RequestParam(required = false) ReviewStatus status,
        @RequestParam(required = false) Long reviewerId,
        @RequestParam(required = false) Long institutionId,
        @RequestParam(required = false) GroupType groupType) {
    return ApiResponse.ok(reviewService.listScoresByStage(
            competitionId, stage, status, reviewerId, institutionId, groupType));
}
```

**Service层**：
```java
@Transactional(readOnly = true)
public List<BookScoreItem> listScoresByStage(
        Long competitionId,
        ReviewStage stage,  // 参数化阶段
        ReviewStatus status,
        Long reviewerId,
        Long institutionId,
        GroupType groupType) {
    
    // 使用参数化的stage
    List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
            stage, competitionId);
    
    // 其他逻辑完全相同
    // ...
}
```

**保留旧接口兼容性**：
```java
@GetMapping("/book-scores")
@Operation(summary = "书审得分列表")
public ApiResponse<List<BookScoreItem>> listBookScores(...) {
    // 调用通用接口
    return ApiResponse.ok(reviewService.listScoresByStage(
            competitionId, ReviewStage.BOOK, status, reviewerId, institutionId, groupType));
}
```

### 方案3：修改现有接口增加stage参数

**优点**：
- 最小改动
- 向后兼容

**实现**：
```java
@GetMapping("/book-scores")
@Operation(summary = "评审得分列表")
public ApiResponse<List<BookScoreItem>> listBookScores(
        @RequestParam Long competitionId,
        @RequestParam(required = false, defaultValue = "BOOK") ReviewStage stage,  // 新增，默认BOOK
        @RequestParam(required = false) ReviewStatus status,
        @RequestParam(required = false) Long reviewerId,
        @RequestParam(required = false) Long institutionId,
        @RequestParam(required = false) GroupType groupType) {
    return ApiResponse.ok(reviewService.listScoresByStage(
            competitionId, stage, status, reviewerId, institutionId, groupType));
}
```

## 四、推荐方案：方案1

**理由**：
1. 接口语义清晰：`/book-scores` vs `/interview-scores`
2. 不影响现有接口，向后兼容
3. 前端调用简单，不需要传递stage参数
4. 代码改动最小，风险最低

## 五、实施步骤

### Step 1: Service层新增方法
```java
// ReviewService.java
@Transactional(readOnly = true)
public List<BookScoreItem> listInterviewScores(
        Long competitionId,
        ReviewStatus status,
        Long reviewerId,
        Long institutionId,
        GroupType groupType) {
    
    // 复制listBookScores的逻辑，只改stage
    List<ReviewTask> tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(
            ReviewStage.INTERVIEW, competitionId);
    
    // ... 其他逻辑完全相同
}
```

### Step 2: Controller层新增接口
```java
// AdminReviewController.java
@GetMapping("/interview-scores")
@Operation(summary = "面谈得分列表")
public ApiResponse<List<BookScoreItem>> listInterviewScores(
        @RequestParam Long competitionId,
        @RequestParam(required = false) ReviewStatus status,
        @RequestParam(required = false) Long reviewerId,
        @RequestParam(required = false) Long institutionId,
        @RequestParam(required = false) GroupType groupType) {
    return ApiResponse.ok(reviewService.listInterviewScores(
            competitionId, status, reviewerId, institutionId, groupType));
}
```

### Step 3: 测试验证
```python
# 测试脚本
import requests

BASE_URL = "http://localhost:6031"

# 1. 登录
admin_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
})
token = admin_resp.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 2. 查询面谈得分列表
interview_scores = requests.get(
    f"{BASE_URL}/api/admin/reviews/interview-scores",
    params={"competitionId": 21},
    headers=headers
)

print(f"面谈得分数量: {len(interview_scores.json()['data'])}")
```

## 六、前端对接

### 6.1 书审得分列表（现有）
```javascript
// 书审得分列表
const fetchBookScores = async () => {
  const response = await axios.get('/api/admin/reviews/book-scores', {
    params: {
      competitionId: 21,
      status: 'SCORED',  // 可选
      groupType: 'BASIC'  // 可选
    }
  });
  return response.data.data;
};
```

### 6.2 面谈得分列表（新增）
```javascript
// 面谈得分列表
const fetchInterviewScores = async () => {
  const response = await axios.get('/api/admin/reviews/interview-scores', {
    params: {
      competitionId: 21,
      status: 'SCORED',  // 可选
      groupType: 'ADVANCED'  // 可选，面谈通常是进阶组
    }
  });
  return response.data.data;
};
```

### 6.3 通用组件复用
```vue
<template>
  <ScoreList 
    :stage="stage" 
    :scores="scores" 
    @refresh="fetchScores"
  />
</template>

<script>
export default {
  data() {
    return {
      stage: 'BOOK',  // 或 'INTERVIEW'
      scores: []
    };
  },
  methods: {
    async fetchScores() {
      const endpoint = this.stage === 'BOOK' 
        ? '/api/admin/reviews/book-scores'
        : '/api/admin/reviews/interview-scores';
      
      const response = await axios.get(endpoint, {
        params: { competitionId: this.competitionId }
      });
      
      this.scores = response.data.data;
    }
  }
};
</script>
```

## 七、数据差异说明

### 7.1 书审 vs 面谈

| 维度 | 书审 (BOOK) | 面谈 (INTERVIEW) |
|------|------------|------------------|
| 阶段 | ReviewStage.BOOK | ReviewStage.INTERVIEW |
| 参与项目 | 所有组别 | 通常只有进阶组 (ADVANCED) |
| 评分标准 | 7项指标 | 7项指标（相同） |
| 数据结构 | BookScoreItem | BookScoreItem（相同） |

### 7.2 面谈特殊逻辑

在自动分配任务时，面谈阶段有特殊处理：
```java
// ReviewService.autoAssign()
if (request.getStage() == ReviewStage.INTERVIEW 
    && registration.getGroupType() != GroupType.ADVANCED) {
    continue;  // 面谈只分配进阶组项目
}
```

## 八、测试清单

- [ ] 新增`listInterviewScores`方法到ReviewService
- [ ] 新增`/interview-scores`接口到AdminReviewController
- [ ] 编译通过
- [ ] 单元测试：查询面谈得分列表
- [ ] 集成测试：完整流程测试
- [ ] Swagger文档验证
- [ ] 前端对接测试

## 九、预估工时

| 任务 | 工时 |
|------|------|
| Service层新增方法 | 15分钟 |
| Controller层新增接口 | 10分钟 |
| 编译和自测 | 15分钟 |
| 测试脚本编写 | 20分钟 |
| 文档更新 | 10分钟 |
| **总计** | **70分钟** |

## 十、总结

**答案**：✅ 现有API可以支持，但需要新增面谈得分列表接口

**原因**：
- 现有`listBookScores`硬编码了`BOOK`阶段
- 数据结构和逻辑完全相同，只需改变stage参数

**推荐方案**：
- 新增`GET /api/admin/reviews/interview-scores`接口
- 复用`BookScoreItem`数据结构
- 前端可以复用书审得分列表的组件和样式

**实施难度**：⭐ 简单（复制粘贴+改一行代码）

**风险评估**：低（不影响现有接口，纯新增功能）
