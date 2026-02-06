# API最终修复说明

**日期:** 2026-02-06 21:35  
**版本:** v3.1 - 字段名修复

---

## ✅ 本次修复

### 问题: 成员信息字段名不匹配

**错误现象:**
```json
PUT /api/registrations/142/members
{
  "members": [...]  // ❌ 前端发送 members
}
// 返回 400错误
```

**原因:**  
后端DTO定义的字段名是 `items`，但前端使用的是 `members`

**修复:**
```java
// 修改前
public class MemberUpsertRequest {
    private List<MemberItem> items;  // ❌ 字段名 items
}

// 修改后
public class MemberUpsertRequest {
    private List<MemberItem> members;  // ✅ 改为 members
}
```

---

## 📝 正确的请求格式

### 1. 更新成员信息 ✅

```javascript
PUT /api/registrations/142/members

// 正确请求
{
  "members": [  // ✅ 使用 members
    {
      "name": "张三",
      "title": "主管护师",
      "role": "PARTICIPANT",
      "department": "内科"
    },
    {
      "name": "王五",
      "title": "副主任护师",
      "role": "MENTOR"
      // department 可选，MENTOR也可以不填
    }
  ]
}

// 返回
{
  "success": true,
  "data": [
    { "id": 1, "name": "张三", "title": "主管护师", ... },
    { "id": 2, "name": "王五", "title": "副主任护师", ... }
  ]
}
```

**字段验证:**
- ✅ `name` - 必填，不能为空字符串
- ✅ `title` - 必填，不能为空字符串
- ✅ `role` - 必填，枚举值 PARTICIPANT 或 MENTOR
- ⭕ `department` - 可选，可以不填或为null

---

### 2. 更新活动说明

```javascript
PUT /api/registrations/142/activity

// 正确请求（使用正确的code值）
{
  "theme": "提高门诊预约效率",
  "keywords": "门诊,预约,效率",
  
  // 选题类型 - 使用 subject_type_X 格式
  "subjectTypeCode": "subject_type_1",  // ✅ 不是 PATIENT_CARE
  "subjectTypeOther": null,
  
  // 方法 - 常见值
  "methodCode": "PDCA",  // ✅ PDCA, DMAIC, LEAN 等
  "methodOther": null,
  
  // 改善经验 - 使用 experience_X 格式
  "experienceImproveCode": "experience_1",
  "experienceImproveOther": null,
  
  // 质量主题 - 使用 quality_topic_X 格式
  "qualityTopicCode": "quality_topic_1",
  "qualityTopicOther": null,
  
  // 团队信息
  "avgWorkYears": 6,
  "avgAge": 32,
  "crossDepartment": false
}

// 返回
{
  "success": true,
  "data": {
    "id": 10,
    "theme": "提高门诊预约效率",
    ...
  }
}
```

---

## 🔍 字典Code值说明

### 常见错误

❌ **错误示例:**
```json
{
  "subjectTypeCode": "PATIENT_CARE",  // ❌ 这不是正确的格式
  "methodCode": "pdca"                // ❌ 小写可能不对
}
```

✅ **正确示例:**
```json
{
  "subjectTypeCode": "subject_type_1",  // ✅ 使用下划线格式
  "methodCode": "PDCA"                  // ✅ 大写
}
```

### 字典Code建议值

| 字段 | 格式/示例 | 说明 |
|-----|----------|------|
| subjectTypeCode | `subject_type_1`, `subject_type_2` | 选题类型 |
| methodCode | `PDCA`, `DMAIC`, `LEAN` | 改进方法 |
| experienceImproveCode | `experience_1`, `experience_2` | 改善经验 |
| qualityTopicCode | `quality_topic_1`, `quality_topic_2` | 质量主题 |

### 获取正确的字典值

如果系统有字典接口，建议先获取：

```javascript
// 获取选题类型字典
GET /api/dictionaries?category=subjectType
// 返回可用的 code 列表

// 获取方法字典
GET /api/dictionaries?category=method

// 获取改善经验字典
GET /api/dictionaries?category=experienceImprove

// 获取质量主题字典
GET /api/dictionaries?category=qualityTopic
```

---

## 🧪 完整测试用例

```javascript
// 1. 登录
POST /api/auth/login
{
  "phone": "13900000001",
  "name": "测试参赛者",
  "role": "CONTESTANT"
}

// 2. 创建报名
POST /api/registrations
{
  "competitionId": 21,
  "institutionId": 1,
  "projectName": "优化门诊预约流程",
  "groupType": "BASIC"
}
// 返回 registrationId = 142

// 3. 更新成员信息（使用正确的字段名）
PUT /api/registrations/142/members
{
  "members": [  // ✅ 字段名是 members
    {
      "name": "张三",
      "title": "主管护师",
      "role": "PARTICIPANT",
      "department": "内科"
    },
    {
      "name": "王五",
      "title": "副主任护师",
      "role": "MENTOR"
    }
  ]
}
// 期望返回 200

// 4. 更新活动说明（使用正确的code值）
PUT /api/registrations/142/activity
{
  "theme": "提高门诊预约效率",
  "keywords": "门诊,预约,效率",
  "subjectTypeCode": "subject_type_1",  // ✅ 不是 PATIENT_CARE
  "methodCode": "PDCA",
  "experienceImproveCode": "experience_1",
  "qualityTopicCode": "quality_topic_1",
  "avgWorkYears": 6,
  "avgAge": 32,
  "crossDepartment": false
}
// 期望返回 200

// 5. 提交审核
POST /api/registrations/142/submit
// 期望返回 200，状态变为 SUBMITTED
```

---

## 📋 修改文件清单

1. `MemberUpsertRequest.java`
   - 字段名: `items` → `members`
   - 添加错误提示信息

2. `RegistrationService.java`
   - 方法调用: `request.getItems()` → `request.getMembers()`

---

## 🎯 关键修复点

1. **字段名统一**
   - 前端发送 `members`
   - 后端接收 `members`
   - ✅ 名称一致

2. **Code值格式**
   - 使用下划线格式: `subject_type_1`
   - 不使用驼峰或其他格式: ~~PATIENT_CARE~~

3. **字段验证**
   - name, title: `@NotBlank` (不能为空字符串)
   - role: `@NotNull` (必须有值)
   - department: 可选

---

**修复完成！重新编译后即可测试！** 🚀
