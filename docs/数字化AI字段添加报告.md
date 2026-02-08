# 数字化/AI字段添加报告

## 问题描述

用户反馈缺少"是否与数字化/人工智能应用相关主题"字段，这是一个Yes/No的勾选框。

## 解决方案

### 1. 数据库修改

在 `activity_infos` 表中添加新字段：

```sql
ALTER TABLE activity_infos 
ADD COLUMN related_to_digital_ai BOOLEAN NOT NULL DEFAULT FALSE 
COMMENT '是否与数字化/人工智能应用相关主题' 
AFTER cross_department;
```

**执行脚本**: `add_digital_ai_field.sql`

### 2. 后端代码修改

#### 2.1 实体类 (ActivityInfo.java)

添加字段：

```java
@Column(nullable = false)
private Boolean relatedToDigitalAi;
```

#### 2.2 DTO (ActivityInfoRequest.java)

添加字段：

```java
@NotNull(message = "是否与数字化/人工智能应用相关主题不能为空")
@Schema(example = "false", description = "是否与数字化/人工智能应用相关主题")
private Boolean relatedToDigitalAi;
```

#### 2.3 响应DTO (ActivityInfoDetailResponse.java)

添加字段：

```java
private Boolean relatedToDigitalAi;
```

#### 2.4 Service (RegistrationService.java)

在 `saveActivity` 方法中添加字段赋值：

```java
activityInfo.setRelatedToDigitalAi(request.getRelatedToDigitalAi());
```

在 `getDetail` 方法中添加字段返回：

```java
activityDetail = new ActivityInfoDetailResponse(
    // ... 其他字段
    activity.getCrossDepartment(),
    activity.getRelatedToDigitalAi(),  // 新增
    methodLabel
);
```

### 3. 影响的接口

#### 3.1 提交活动信息
- **接口**: `POST /api/registrations/{id}/activity`
- **变化**: 请求体中需要包含 `relatedToDigitalAi` 字段

**请求示例**:
```json
{
  "registrationId": 119,
  "theme": "改善门诊就诊流程",
  "keywords": "流程优化,患者满意度",
  "subjectTypeCode": "subject_type_1",
  "methodCode": "method_15",
  "experienceImproveCode": "outpatient_process",
  "qualityTopicCode": "adverse_event_report",
  "avgWorkYears": 7,
  "avgAge": 32,
  "crossDepartment": true,
  "relatedToDigitalAi": false
}
```

#### 3.2 查看报名详情
- **接口**: `GET /api/registrations/{id}`
- **变化**: 返回的 `activityInfo` 对象中包含 `relatedToDigitalAi` 字段

**返回示例**:
```json
{
  "success": true,
  "data": {
    "registration": {...},
    "institution": {...},
    "members": [...],
    "activityInfo": {
      "theme": "活动主题",
      "keywords": "关键词",
      "subjectTypeCode": "subject_type_1",
      "methodCode": "method_15",
      "experienceImproveCode": "outpatient_process",
      "qualityTopicCode": "adverse_event_report",
      "avgWorkYears": 7,
      "avgAge": 32,
      "crossDepartment": true,
      "relatedToDigitalAi": false
    },
    "projectSummary": {...},
    "materials": [...]
  }
}
```

## 数据迁移说明

### 现有数据处理

- 新字段设置为 `NOT NULL DEFAULT FALSE`
- 所有现有数据的该字段将自动设置为 `false`
- 不影响现有数据的完整性

### 前端适配

前端需要：

1. **表单提交**：添加一个复选框（Checkbox）
   - 标签：是否与数字化/人工智能应用相关主题
   - 字段名：`relatedToDigitalAi`
   - 类型：Boolean
   - 默认值：false

2. **详情展示**：显示该字段的值
   - true → "是"
   - false → "否"

## 完整字段列表

### ActivityInfo 实体（10个字段）

| 字段名 | 类型 | 说明 | 必填 |
|-------|------|------|------|
| theme | String | 活动主题 | ✅ |
| keywords | String | 关键词 | ✅ |
| subjectTypeCode | String | 主题类型代码 | ✅ |
| subjectTypeOther | String | 主题类型其他说明 | ❌ |
| methodCode | String | 运用手法代码 | ✅ |
| methodOther | String | 运用手法其他说明 | ❌ |
| experienceImproveCode | String | 改善就医环境代码 | ✅ |
| experienceImproveOther | String | 改善就医环境其他说明 | ❌ |
| qualityTopicCode | String | 医疗质量主题代码 | ✅ |
| qualityTopicOther | String | 医疗质量主题其他说明 | ❌ |
| avgWorkYears | Integer | 平均工作年限 | ✅ |
| avgAge | Integer | 平均年龄 | ✅ |
| crossDepartment | Boolean | 是否跨部门 | ✅ |
| **relatedToDigitalAi** | **Boolean** | **是否与数字化/AI相关** | **✅ NEW!** |

## 部署步骤

1. **执行SQL脚本**
   ```bash
   mysql -u root -p pinguan_competition_23 < add_digital_ai_field.sql
   ```

2. **重新编译应用**
   ```bash
   mvn clean package
   ```

3. **重启应用**
   停止现有应用，启动新版本

4. **验证**
   - 测试提交活动信息接口
   - 测试查看报名详情接口
   - 确认新字段正常工作

## 注意事项

1. **默认值**：新字段默认为 `false`，所有现有数据都是 `false`
2. **必填字段**：前端提交时必须包含该字段
3. **数据类型**：Boolean类型，只能是 `true` 或 `false`
4. **向后兼容**：不影响现有功能

## 相关文件

### 代码文件
- `src/main/java/com/trae/pinguan/domain/entity/ActivityInfo.java`
- `src/main/java/com/trae/pinguan/web/dto/ActivityInfoRequest.java`
- `src/main/java/com/trae/pinguan/web/dto/ActivityInfoDetailResponse.java`
- `src/main/java/com/trae/pinguan/service/RegistrationService.java`

### 脚本和文档
- `add_digital_ai_field.sql` - 数据库迁移脚本
- `docs/数字化AI字段添加报告.md` - 本文档

## 测试建议

### 测试用例

1. **提交新报名**
   - 勾选"是" → `relatedToDigitalAi: true`
   - 不勾选 → `relatedToDigitalAi: false`

2. **查看报名详情**
   - 验证字段正确显示

3. **编辑报名**
   - 修改该字段的值
   - 验证保存成功

4. **旧数据兼容性**
   - 查看旧报名的详情
   - 验证该字段显示为 `false`
