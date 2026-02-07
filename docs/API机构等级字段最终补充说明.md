# API机构等级字段最终补充说明

**更新时间**: 2026-02-07  
**更新内容**: 响应前端测试反馈，补充剩余3个API的机构等级字段

---

## 📋 本次补充的API（2个有效）

### 1. GET /api/registrations/my - 我的报名列表 ⭐

**角色**: 参赛者  
**新增字段**: 
- `data[i].institutionName` (String) - 机构名称
- `data[i].institutionLevel` (String) - 医院等级

**修改前**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 140,
      "competitionId": 1,
      "institutionId": 34,
      "projectName": "降低患者跌倒发生率",
      "groupType": "GRASSROOTS",
      "status": "APPROVED"
    }
  ]
}
```

**修改后**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 140,
      "competitionId": 1,
      "institutionId": 34,
      "institutionName": "杭州市临安区第三人民医院",  ← 新增
      "institutionLevel": "三级乙等",                ← 新增
      "applicantId": 150,
      "projectName": "降低患者跌倒发生率",
      "groupType": "GRASSROOTS",
      "groupCode": "group_a",
      "status": "APPROVED",
      "submittedAt": "2026-02-06T14:30:00",
      "createdAt": "2026-02-05T10:00:00"
    }
  ]
}
```

---

### 2. GET /api/reviews/tasks/stage - 按阶段查询评审任务 ⭐

**角色**: 评审专家、组委会  
**新增字段**: 
- `data[i].registrationId` (Long) - 报名ID
- `data[i].projectName` (String) - 项目名称
- `data[i].institutionName` (String) - 机构名称
- `data[i].institutionLevel` (String) - 医院等级

**修改前**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 101,
      "stage": "BOOK",
      "status": "PENDING",
      "createdAt": "2026-02-06T10:00:00"
    }
  ]
}
```

**修改后**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 101,
      "registrationId": 5,                          ← 新增
      "projectName": "优化门诊预约流程",              ← 新增
      "institutionName": "浙江大学医学院附属第一医院", ← 新增
      "institutionLevel": "三级甲等",                ← 新增
      "stage": "BOOK",
      "status": "PENDING",
      "createdAt": "2026-02-06T10:00:00"
    }
  ]
}
```

---

### 3. GET /api/registrations/{id}/review-results - 报名评审结果 ℹ️

**说明**: 此API返回的是按阶段统计的评审结果汇总，不包含具体的报名项目信息，因此**不需要添加** `institutionLevel` 字段。

**返回示例**:
```json
{
  "code": 200,
  "data": [
    {
      "stage": "BOOK",
      "taskCount": 3,
      "scoredCount": 2,
      "avgTotal": 88.5
    },
    {
      "stage": "INTERVIEW",
      "taskCount": 2,
      "scoredCount": 1,
      "avgTotal": 85.0
    }
  ]
}
```

**说明**: 这是统计信息，不是项目列表，无需机构等级字段。

---

## 📊 修改统计

### 新增的DTO（1个）
- ✅ `MyRegistrationItem.java` - 我的报名列表项

### 修改的DTO（1个）
- ✅ `ReviewTaskItem.java` - 评审任务项（之前已修改）

### 修改的Controller（2个）
1. ✅ `RegistrationController.java` - `myRegistrations()` 方法
2. ✅ `ReviewController.java` - `listByStage()` 方法

### 修改的Service（2个）
1. ✅ `RegistrationService.java` - `listByApplicant()` 方法
2. ✅ `ReviewService.java` - `listTasksByStage()` 方法

---

## 🎯 完整API清单（12个）

### 已添加机构等级字段的API

| # | API | 角色 | 新增字段 | 状态 |
|---|-----|------|---------|------|
| 1 | POST /api/auth/login | 所有 | institutionRegion, institutionLevel | ✅ |
| 2 | GET /api/registrations/{id} | 参赛者/专家 | institution.level | ✅ |
| 3 | GET /api/registrations/my | 参赛者 | institutionName, institutionLevel | ✅ 本次 |
| 4 | GET /api/institutions | OPS | level | ✅ |
| 5 | GET /api/institutions/{id} | 公开 | level | ✅ |
| 6 | GET /api/admin/institutions/export | OPS | level | ✅ |
| 7 | GET /api/reviews/my-tasks | 评审专家 | institutionLevel | ✅ |
| 8 | GET /api/reviews/tasks/stage | 评审专家/组委会 | registrationId, projectName, institutionName, institutionLevel | ✅ 本次 |
| 9 | GET /api/admin/registrations/filter | 组委会 | institutionLevel | ✅ |
| 10 | GET /api/admin/reviews/rankings | 组委会 | institutionLevel | ✅ |
| 11 | GET /api/admin/reviews/reviewers | 组委会 | institutionLevel | ✅ |
| 12 | GET /api/registrations/{id}/review-results | 参赛者/专家 | 无需添加（统计数据） | ℹ️ |

---

## 💻 前端使用示例

### 1. 我的报名列表
```javascript
// 获取我的报名
const response = await fetch('/api/registrations/my', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: registrations } = await response.json();

// 显示机构等级
registrations.forEach(reg => {
  console.log(`${reg.projectName} - ${reg.institutionName} (${reg.institutionLevel})`);
});

// Vue 模板示例
<template>
  <div v-for="reg in registrations" :key="reg.id">
    <h3>{{ reg.projectName }}</h3>
    <p>机构: {{ reg.institutionName }} ({{ reg.institutionLevel }})</p>
    <p>状态: {{ reg.status }}</p>
  </div>
</template>
```

### 2. 按阶段查询评审任务
```javascript
// 获取书审阶段的所有任务
const response = await fetch('/api/reviews/tasks/stage?competitionId=1&stage=BOOK', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data: tasks } = await response.json();

// 显示任务列表（含机构等级）
tasks.forEach(task => {
  console.log(`${task.projectName} - ${task.institutionName} (${task.institutionLevel})`);
  console.log(`  报名ID: ${task.registrationId}, 状态: ${task.status}`);
});

// React 示例
function TaskList({ competitionId, stage }) {
  const [tasks, setTasks] = useState([]);
  
  useEffect(() => {
    fetch(`/api/reviews/tasks/stage?competitionId=${competitionId}&stage=${stage}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(r => r.json())
    .then(data => setTasks(data.data));
  }, [competitionId, stage]);
  
  return (
    <div>
      {tasks.map(task => (
        <div key={task.id}>
          <h4>{task.projectName}</h4>
          <p>机构: {task.institutionName} ({task.institutionLevel})</p>
          <p>报名ID: {task.registrationId}</p>
          <p>状态: {task.status}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔧 技术实现细节

### 1. MyRegistrationItem DTO
```java
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MyRegistrationItem {
    private Long id;
    private Long competitionId;
    private Long institutionId;
    private String institutionName;      // 新增
    private String institutionLevel;     // 新增
    private Long applicantId;
    private String projectName;
    private GroupType groupType;
    private String groupCode;
    private RegistrationStatus status;
    private LocalDateTime submittedAt;
    private LocalDateTime createdAt;
}
```

### 2. RegistrationService.listByApplicant()
```java
@Transactional(readOnly = true)
public List<MyRegistrationItem> listByApplicant(Long applicantId) {
    List<Registration> registrations = registrationRepository.findByApplicantId(applicantId);
    return registrations.stream()
            .map(reg -> MyRegistrationItem.builder()
                    .id(reg.getId())
                    .competitionId(reg.getCompetitionId())
                    .institutionId(reg.getInstitutionId())
                    .institutionName(reg.getInstitution() != null 
                        ? reg.getInstitution().getName() : null)
                    .institutionLevel(reg.getInstitution() != null 
                        ? reg.getInstitution().getLevel() : null)
                    // ... 其他字段
                    .build())
            .collect(Collectors.toList());
}
```

### 3. ReviewService.listTasksByStage()
```java
@Transactional(readOnly = true)
public List<ReviewTaskItem> listTasksByStage(Long competitionId, ReviewStage stage, ReviewStatus status) {
    List<ReviewTask> tasks;
    if (status == null) {
        tasks = reviewTaskRepository.findByStageAndRegistrationCompetitionId(stage, competitionId);
    } else {
        tasks = reviewTaskRepository.findByStageAndStatusAndRegistrationCompetitionId(stage, status, competitionId);
    }
    return tasks.stream()
            .map(task -> {
                Registration reg = task.getRegistration();
                return ReviewTaskItem.builder()
                        .id(task.getId())
                        .registrationId(reg != null ? reg.getId() : null)
                        .projectName(reg != null ? reg.getProjectName() : null)
                        .institutionName(reg != null && reg.getInstitution() != null 
                                ? reg.getInstitution().getName() : null)
                        .institutionLevel(reg != null && reg.getInstitution() != null 
                                ? reg.getInstitution().getLevel() : null)
                        .stage(task.getStage())
                        .status(task.getStatus())
                        .createdAt(task.getCreatedAt())
                        .build();
            })
            .collect(Collectors.toList());
}
```

---

## ⚠️ 注意事项

### 1. 需要重启后端服务
所有修改需要重启后端服务才能生效：

```bash
# 停止当前服务
# Ctrl+C

# 重新编译并启动
mvn clean package -DskipTests
mvn spring-boot:run
```

### 2. 字段可能为空
虽然当前所有42家机构都已填写等级（100%），但前端仍需处理空值：

```javascript
const level = item.institutionLevel || '未填写';
```

### 3. 懒加载问题
由于使用了 `@Transactional(readOnly = true)`，确保在事务中访问懒加载的 `institution` 字段，避免 `LazyInitializationException`。

---

## 📋 修改的文件清单

### 新增文件（1个）
- ✅ `src/main/java/com/trae/pinguan/web/dto/MyRegistrationItem.java`

### 修改文件（4个）
1. ✅ `src/main/java/com/trae/pinguan/web/RegistrationController.java`
   - `myRegistrations()` 方法返回类型改为 `List<MyRegistrationItem>`

2. ✅ `src/main/java/com/trae/pinguan/service/RegistrationService.java`
   - `listByApplicant()` 方法返回类型改为 `List<MyRegistrationItem>`
   - 添加机构名称和等级到返回数据

3. ✅ `src/main/java/com/trae/pinguan/web/ReviewController.java`
   - `listByStage()` 方法返回类型改为 `List<ReviewTaskItem>`

4. ✅ `src/main/java/com/trae/pinguan/service/ReviewService.java`
   - `listTasksByStage()` 方法返回类型改为 `List<ReviewTaskItem>`
   - 添加报名ID、项目名称、机构名称和等级到返回数据

---

## 🎉 总结

### 本次补充
- ✅ **2个API** 已补充机构等级及相关字段
- ✅ **1个API** 确认无需添加（统计数据）
- ✅ **1个DTO** 新增
- ✅ **2个Controller** 修改
- ✅ **2个Service** 修改

### 累计完成
- ✅ **12个API** 已添加或确认机构等级字段
- ✅ **7个DTO** 已添加 institutionLevel 字段
- ✅ **5个Controller** 已修改
- ✅ **4个Service** 已修改
- ✅ **1个Repository** 已修改
- ✅ **数据完整性**: 42家机构 100% 填写等级

### 下一步
⚠️ **需要重启后端服务以使修改生效**

```bash
mvn spring-boot:run
```

---

**文档生成时间**: 2026-02-07  
**维护人员**: 系统管理员  
**更新状态**: ✅ 完成，等待重启验证
