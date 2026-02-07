# 评委任务查看功能 - API变更说明

**变更日期**: 2026-02-07  
**变更范围**: 评委任务分配查看功能 - 支持多维度筛选

---

## 一、需求背景

书审评委分配、面谈评委分配、决赛评委分配，都需要一个"已分配任务查看"按钮。点击后展示所有已分配任务的列表，并支持以下筛选维度：

1. **分组**（竞赛组别：BASIC/COMPREHENSIVE/ADVANCED，分组代码：A1/A2/A3/B2等）
2. **专家**（评委ID/姓名）
3. **品管工具**（methodCode：qc_topic, qfd, method_5等）

---

## 二、API变更详情

### 变更的API

**接口**: `GET /api/reviews/tasks/stage`

**变更前**：只支持3个基础参数
```
GET /api/reviews/tasks/stage?competitionId={id}&stage={stage}&status={status}
```

**变更后**：新增4个筛选参数
```
GET /api/reviews/tasks/stage?competitionId={id}&stage={stage}&status={status}&groupType={type}&groupCode={code}&reviewerId={id}&methodCode={code}
```

---

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `competitionId` | Long | ✅ 是 | 赛事ID | 21 |
| `stage` | String(Enum) | ✅ 是 | 评审阶段 | BOOK / INTERVIEW / FINAL |
| `status` | String(Enum) | ❌ 否 | 任务状态 | PENDING / SCORED |
| **`groupType`** | String(Enum) | ❌ 否 | **[新增] 竞赛组别** | BASIC / COMPREHENSIVE / ADVANCED |
| **`groupCode`** | String | ❌ 否 | **[新增] 分组代码** | A1 / A2 / A3 / B2 |
| **`reviewerId`** | Long | ❌ 否 | **[新增] 评委ID** | 6 |
| **`methodCode`** | String | ❌ 否 | **[新增] 品管工具代码** | qc_topic / qfd / method_5 |

**评审阶段 (`stage`) 枚举值**:
- `BOOK` - 书审
- `INTERVIEW` - 面谈
- `FINAL` - 决赛

**任务状态 (`status`) 枚举值**:
- `PENDING` - 待评审
- `SCORED` - 已评审

**竞赛组别 (`groupType`) 枚举值**:
- `BASIC` - 基层组
- `COMPREHENSIVE` - 综合组
- `ADVANCED` - 高级组

---

### 响应数据

#### 变更前的响应字段

```json
{
  "success": true,
  "data": [
    {
      "id": 115,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第二医院（浙二医院）",
      "institutionLevel": "三级甲等",
      "stage": "BOOK",
      "status": "SCORED",
      "createdAt": "2026-02-06T18:12:37.447"
    }
  ]
}
```

#### 变更后的响应字段（新增7个字段）

```json
{
  "success": true,
  "data": [
    {
      "id": 115,
      "registrationId": 106,
      "projectName": "护理交接班规范化-1",
      "institutionName": "浙江大学医学院附属第二医院（浙二医院）",
      "institutionLevel": "三级甲等",
      "groupType": "BASIC",              // ✨ 新增：竞赛组别
      "groupCode": "A1",                 // ✨ 新增：分组代码
      "stage": "BOOK",
      "status": "SCORED",
      "createdAt": "2026-02-06T18:12:37.447",
      "reviewerId": 6,                   // ✨ 新增：评委ID
      "reviewerName": "李明华",          // ✨ 新增：评委姓名
      "reviewerInstitutionName": "浙江省中医院",  // ✨ 新增：评委单位
      "methodCode": "qc_topic",          // ✨ 新增：品管工具代码
      "methodLabel": "品管圈-课题达成"   // ✨ 新增：品管工具名称
    }
  ]
}
```

**新增字段说明**：

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `groupType` | String | 竞赛组别（BASIC/COMPREHENSIVE/ADVANCED） | "BASIC" |
| `groupCode` | String | 分组代码 | "A1" |
| `reviewerId` | Long | 评委ID | 6 |
| `reviewerName` | String | 评委姓名 | "李明华" |
| `reviewerInstitutionName` | String | 评委所属机构名称 | "浙江省中医院" |
| `methodCode` | String | 品管工具代码 | "qc_topic" |
| `methodLabel` | String | 品管工具中文名称 | "品管圈-课题达成" |

---

## 三、使用示例

### 示例1：基础查询（无筛选）

获取赛事21书审阶段的所有任务。

**请求**:
```http
GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK
Authorization: Bearer {token}
```

**响应**: 返回所有书审任务（6条）

---

### 示例2：按竞赛组别筛选

仅查看"基层组"的任务。

**请求**:
```http
GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK&groupType=BASIC
Authorization: Bearer {token}
```

**响应**: 返回BASIC组的任务（6条）

---

### 示例3：按分组代码筛选

仅查看"A1分组"的任务。

**请求**:
```http
GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK&groupCode=A1
Authorization: Bearer {token}
```

**响应**: 返回A1分组的任务（3条）

---

### 示例4：按评委筛选

仅查看评委"李明华"（ID=6）的任务。

**请求**:
```http
GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK&reviewerId=6
Authorization: Bearer {token}
```

**响应**: 返回评委6的任务（1条）

---

### 示例5：按品管工具筛选

仅查看使用"品管圈-课题达成"工具的任务。

**请求**:
```http
GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK&methodCode=qc_topic
Authorization: Bearer {token}
```

**响应**: 返回使用qc_topic的任务（2条）

---

### 示例6：组合筛选

同时使用多个筛选条件：BASIC组 + A1分组 + PENDING状态。

**请求**:
```http
GET /api/reviews/tasks/stage?competitionId=21&stage=BOOK&groupType=BASIC&groupCode=A1&status=PENDING
Authorization: Bearer {token}
```

**响应**: 返回符合所有条件的任务（2条）

---

## 四、后端实现变更

### 1. DTO扩展

**文件**: `src/main/java/com/trae/pinguan/web/dto/ReviewTaskItem.java`

**新增字段**:
```java
private GroupType groupType;
private String groupCode;
private Long reviewerId;
private String reviewerName;
private String reviewerInstitutionName;
private String methodCode;
private String methodLabel;
```

---

### 2. Repository扩展

**文件**: `src/main/java/com/trae/pinguan/repository/ReviewTaskRepository.java`

**新增方法**: `findTasksWithFilters()`

支持多条件联合查询，使用`JOIN FETCH`优化性能，包含：
- `ReviewTask` → `Registration` → `Institution`
- `ReviewTask` → `Reviewer` → `Reviewer.Institution`

---

### 3. Service扩展

**文件**: `src/main/java/com/trae/pinguan/service/ReviewService.java`

**修改方法**: `listTasksByStage()`

- 新增7个参数：`groupType`, `groupCode`, `reviewerId`, `methodCode`等
- 调用新的Repository方法进行多条件查询
- 关联查询`ActivityInfo`获取品管工具信息
- 通过`DictionaryItem`将`methodCode`转换为`methodLabel`

---

### 4. Controller扩展

**文件**: `src/main/java/com/trae/pinguan/web/ReviewController.java`

**修改端点**: `GET /api/reviews/tasks/stage`

- 新增4个`@RequestParam`参数
- 更新接口文档（`@Operation`注解）

---

## 五、品管工具常用代码对照表

| 代码 (methodCode) | 名称 (methodLabel) |
|-------------------|--------------------|
| `qc_topic` | 品管圈-课题达成 |
| `qfd` | QFD |
| `method_5` | 根本原因分析 |
| `method_7` | 标杆学习 |
| `method_9` | QFD |

*完整列表请查询 `dictionary_items` 表，`type='method'`*

---

## 六、兼容性说明

### ✅ 向后兼容

本次变更**完全兼容**旧版API调用：

- 旧代码不传新参数，功能不受影响
- 新增字段自动返回，旧代码可忽略
- 无需修改现有API调用代码

### 🔄 建议升级

建议前端逐步升级，使用新增的筛选功能和字段，提升用户体验。

---

## 七、测试验证

已完成7项完整测试，全部通过：

- ✅ 基础查询（无筛选）
- ✅ 按竞赛组别筛选
- ✅ 按分组代码筛选
- ✅ 按评委筛选
- ✅ 按品管工具筛选
- ✅ 组合筛选（多条件）
- ✅ 多阶段支持（BOOK/INTERVIEW/FINAL）

**测试脚本**: `scripts/test_assigned_tasks_view.py`

---

## 八、注意事项

1. **权限要求**: 需要JWT Token认证，所有角色均可访问
2. **性能优化**: 已使用`JOIN FETCH`避免N+1查询问题
3. **空值处理**: 如果某项目未填写分组或品管工具，对应字段返回`null`
4. **大小写敏感**: 枚举值严格区分大小写（如`BOOK`不能写成`book`）

---

## 九、相关文档

- 前端开发指引: `docs/评委任务查看功能-前端开发指引.md`
- 测试脚本: `scripts/test_assigned_tasks_view.py`
- 数据库表结构: 
  - `review_tasks` - 评审任务
  - `registrations` - 报名信息（含分组）
  - `activity_infos` - 活动详情（含品管工具）
  - `user_accounts` - 用户信息（评委）
  - `dictionary_items` - 字典项（品管工具标签）

---

**变更完成日期**: 2026-02-07  
**后端开发**: AI Assistant  
**测试状态**: ✅ 全部通过
