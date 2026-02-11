# 评审任务API变更说明

## 变更概述

修改了 `GET /api/admin/reviews/tasks` 接口，使 `stage` 参数变为可选，支持查询所有环节的任务。

## 变更详情

### 1. Controller层变更

**文件**: `src/main/java/com/trae/pinguan/web/AdminReviewController.java`

**变更内容**:
```java
// 修改前
@GetMapping("/tasks")
public ApiResponse<List<AdminReviewTaskItem>> listTasks(
        @RequestParam Long competitionId,
        @RequestParam ReviewStage stage,  // 必填
        @RequestParam(required = false) ReviewStatus status)

// 修改后
@GetMapping("/tasks")
public ApiResponse<List<AdminReviewTaskItem>> listTasks(
        @RequestParam Long competitionId,
        @RequestParam(required = false) ReviewStage stage,  // 改为可选
        @RequestParam(required = false) ReviewStatus status)
```

### 2. Service层变更

**文件**: `src/main/java/com/trae/pinguan/service/ReviewService.java`

**方法**: `listTasksForAdmin(Long competitionId, ReviewStage stage, ReviewStatus status)`

**变更内容**:
- 支持 `stage` 参数为 `null`
- 支持 `status` 参数为 `null`
- 根据参数组合调用不同的Repository方法

**逻辑**:
```java
if (stage == null && status == null) {
    // 查询所有任务
    tasks = reviewTaskRepository.findByRegistrationCompetitionId(competitionId);
} else if (stage == null) {
    // 只按status筛选
    tasks = reviewTaskRepository.findByStatusAndRegistrationCompetitionId(status, competitionId);
} else if (status == null) {
    // 只按stage筛选
    tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
} else {
    // 同时按stage和status筛选
    tasks = reviewTaskRepository.findByStageAndStatusAndRegistrationCompetitionId(stage, status, competitionId);
}
```

### 3. Repository层变更

**文件**: `src/main/java/com/trae/pinguan/repository/ReviewTaskRepository.java`

**新增方法**:
```java
// 查询指定竞赛的所有任务
List<ReviewTask> findByRegistrationCompetitionId(Long competitionId);

// 按状态查询指定竞赛的任务
List<ReviewTask> findByStatusAndRegistrationCompetitionId(ReviewStatus status, Long competitionId);
```

## API使用示例

### 场景1: 查询书审环节所有任务
```http
GET /api/admin/reviews/tasks?competitionId=21&stage=BOOK
```

### 场景2: 查询面谈环节待确认任务
```http
GET /api/admin/reviews/tasks?competitionId=21&stage=INTERVIEW&status=PENDING
```

### 场景3: 查询所有环节的所有任务（新增功能）
```http
GET /api/admin/reviews/tasks?competitionId=21
```

### 场景4: 查询所有环节的待确认任务（新增功能）
```http
GET /api/admin/reviews/tasks?competitionId=21&status=PENDING
```

## 返回数据结构

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "stage": "BOOK",
      "status": "CONFIRMED",
      "createdAt": "2025-01-15T10:30:00",
      "registrationId": 100,
      "projectName": "项目名称",
      "institutionName": "医院名称",
      "groupType": "COMPREHENSIVE",
      "groupCode": "B1",
      "reviewerId": 5,
      "reviewerName": "评委姓名",
      "reviewerTitle": "主任医师",
      "reviewerInstitutionName": "评委所在医院",
      "reviewerGroupCode": null,
      "interviewGroupCode": null,
      "expertBackground": "临床医学"
    }
  ],
  "message": null
}
```

## 字段说明

### 任务信息
- `id`: 任务ID
- `stage`: 评审环节 (BOOK=书审, INTERVIEW=面谈, FINAL=终审)
- `status`: 任务状态 (PENDING=待确认, CONFIRMED=已确认, SCORED=已评分, RETURNED=已退回)
- `createdAt`: 创建时间

### 报名项目信息
- `registrationId`: 报名ID
- `projectName`: 项目名称
- `institutionName`: 参赛机构名称
- `groupType`: 组别类型 (BASIC=基层组, COMPREHENSIVE=综合组, ADVANCED=进阶组)
- `groupCode`: 组别代码 (如 A1, B2, C3)

### 评委信息
- `reviewerId`: 评委ID
- `reviewerName`: 评委姓名
- `reviewerTitle`: 评委职称
- `reviewerInstitutionName`: 评委所在机构
- `reviewerGroupCode`: 书审分组代码（已废弃，始终为null）
- `interviewGroupCode`: 面谈分组代码（已废弃，始终为null）
- `expertBackground`: 专业背景

## 注意事项

1. **服务器重启**: 代码变更后需要重启Spring Boot服务器才能生效
2. **向后兼容**: 原有的API调用方式（带stage参数）仍然有效
3. **分组字段废弃**: `reviewerGroupCode` 和 `interviewGroupCode` 字段已废弃，始终返回null
4. **专业背景**: 评委分配主要基于 `expertBackground` 字段，而非分组代码

## 部署步骤

1. 编译代码:
```bash
mvn clean compile -DskipTests
```

2. 重启Spring Boot服务器

3. 验证API:
```bash
python scripts/test_review_tasks_api.py
```

## 相关文档

- [评审专家分组字段删除说明](./评审专家分组字段删除说明.md)
- [评审专家API变更-前端对接清单](./评审专家API变更-前端对接清单.md)
