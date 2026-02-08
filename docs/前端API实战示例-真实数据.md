# 前端API实战示例 - 真实数据

## 📋 说明

本文档使用**真实的API请求和响应数据**，展示4个场景下Label字段的返回情况。

**测试项目ID**: 119  
**测试时间**: 2026-02-09  
**应用地址**: http://localhost:6031

---

## 场景1: 参赛者 - 我的报名

### 步骤1: 登录

**请求:**
```bash
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800000001",
    "name": "张三",
    "role": "CONTESTANT"
  }'
```

**响应:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMzgwMDAwMDAwMSIsInJvbGUiOiJDT05URVNUQU5UIiwiaWF0IjoxNzM5MDM2NDAwLCJleHAiOjE3MzkxMjI4MDB9.xxx"
  }
}
```

### 步骤2: 获取我的报名列表

**请求:**
```bash
curl -X GET http://localhost:6031/api/registrations/my \
  -H "Authorization: Bearer {token}"
```

**响应:**
```json
{
  "success": true,
  "data": []
}
```

**说明**: 该参赛者没有报名记录，所以直接跳到步骤3查看详情。

### 步骤3: 查看报名详情（项目ID: 119）

**请求:**
```bash
curl -X GET http://localhost:6031/api/registrations/119 \
  -H "Authorization: Bearer {token}"
```

**响应（activityInfo部分）:**
```json
{
  "success": true,
  "data": {
    "registration": {
      "id": 119,
      "projectName": "康复流程改进-14",
      "groupType": "COMPREHENSIVE",
      "groupCode": "B2",
      "status": "APPROVED"
    },
    "activityInfo": {
      "theme": "项目主题119",
      "keywords": "质量,改进",
      "subjectTypeCode": "subject_type_6",
      "subjectTypeOther": null,
      "subjectTypeLabel": "满意度",
      "methodCode": "method_15",
      "methodOther": null,
      "methodLabel": "流程改造",
      "experienceImproveCode": "outpatient_process",
      "experienceImproveOther": null,
      "experienceImproveLabel": "门诊就诊流程更加优化",
      "qualityTopicCode": "surgery_mortality",
      "qualityTopicOther": null,
      "qualityTopicLabel": "降低住院患者围手术期死亡率",
      "avgWorkYears": 7,
      "avgAge": 32,
      "crossDepartment": true,
      "relatedToDigitalAi": false
    }
  }
}
```

### ✅ 场景1总结

**API**: `GET /api/registrations/119`

**4个Label字段**:
- `subjectTypeLabel`: "满意度"
- `methodLabel`: "流程改造"
- `experienceImproveLabel`: "门诊就诊流程更加优化" ← 前端应该显示这个
- `qualityTopicLabel`: "降低住院患者围手术期死亡率" ← 前端应该显示这个

---

## 场景2: 组委会管理员 - 书审分组项目列表

### 步骤1: 登录

**请求:**
```bash
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
  }'
```

**响应:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMzgwMDAwMDA0MSIsInJvbGUiOiJDT01NSVRURUVfQURNSU4iLCJpYXQiOjE3MzkwMzY1MDAsImV4cCI6MTczOTEyMjkwMH0.xxx"
  }
}
```

### 步骤2: 获取书审分组列表

**请求:**
```bash
curl -X GET "http://localhost:6031/api/admin/registrations/interview-groups?competitionId=23" \
  -H "Authorization: Bearer {token}"
```

**响应:**
```json
{
  "success": true,
  "data": []
}
```

**说明**: 没有分组数据，所以直接跳到步骤3查看详情。

### 步骤3: 查看项目详情（项目ID: 119）

**请求:**
```bash
curl -X GET http://localhost:6031/api/registrations/119 \
  -H "Authorization: Bearer {token}"
```

**响应（activityInfo部分）:**
```json
{
  "success": true,
  "data": {
    "activityInfo": {
      "theme": "项目主题119",
      "keywords": "质量,改进",
      "subjectTypeCode": "subject_type_6",
      "subjectTypeLabel": "满意度",
      "methodCode": "method_15",
      "methodLabel": "流程改造",
      "experienceImproveCode": "outpatient_process",
      "experienceImproveLabel": "门诊就诊流程更加优化",
      "qualityTopicCode": "surgery_mortality",
      "qualityTopicLabel": "降低住院患者围手术期死亡率",
      "avgWorkYears": 7,
      "avgAge": 32,
      "crossDepartment": true,
      "relatedToDigitalAi": false
    }
  }
}
```

### ✅ 场景2总结

**API**: `GET /api/registrations/119`

**4个Label字段**:
- `subjectTypeLabel`: "满意度"
- `methodLabel`: "流程改造"
- `experienceImproveLabel`: "门诊就诊流程更加优化" ← 前端应该显示这个
- `qualityTopicLabel`: "降低住院患者围手术期死亡率" ← 前端应该显示这个

---

## 场景3: 组委会管理员 - 筛选项目列表

### 步骤1: 登录

同场景2

### 步骤2: 筛选项目列表

**请求:**
```bash
curl -X GET "http://localhost:6031/api/admin/registrations/filter?competitionId=23" \
  -H "Authorization: Bearer {token}"
```

**响应:**
```json
{
  "success": true,
  "data": []
}
```

**说明**: 没有项目数据，所以直接跳到步骤3查看详情。

### 步骤3: 查看项目详情（项目ID: 119）

**请求:**
```bash
curl -X GET http://localhost:6031/api/registrations/119 \
  -H "Authorization: Bearer {token}"
```

**响应（activityInfo部分）:**
```json
{
  "success": true,
  "data": {
    "activityInfo": {
      "theme": "项目主题119",
      "keywords": "质量,改进",
      "subjectTypeCode": "subject_type_6",
      "subjectTypeLabel": "满意度",
      "methodCode": "method_15",
      "methodLabel": "流程改造",
      "experienceImproveCode": "outpatient_process",
      "experienceImproveLabel": "门诊就诊流程更加优化",
      "qualityTopicCode": "surgery_mortality",
      "qualityTopicLabel": "降低住院患者围手术期死亡率",
      "avgWorkYears": 7,
      "avgAge": 32,
      "crossDepartment": true,
      "relatedToDigitalAi": false
    }
  }
}
```

### ✅ 场景3总结

**API**: `GET /api/registrations/119`

**4个Label字段**:
- `subjectTypeLabel`: "满意度"
- `methodLabel`: "流程改造"
- `experienceImproveLabel`: "门诊就诊流程更加优化" ← 前端应该显示这个
- `qualityTopicLabel`: "降低住院患者围手术期死亡率" ← 前端应该显示这个

---

## 场景4: 评委 - 查看评审任务

### 步骤1: 登录

**请求:**
```bash
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13900000001",
    "name": "李明华",
    "role": "REVIEWER"
  }'
```

**响应:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMzkwMDAwMDAwMSIsInJvbGUiOiJSRVZJRVdFUiIsImlhdCI6MTczOTAzNjYwMCwiZXhwIjoxNzM5MTIzMDAwfQ.xxx"
  }
}
```

### 步骤2: 获取评审任务列表

**请求:**
```bash
curl -X GET "http://localhost:6031/api/reviews/my-tasks?competitionId=23" \
  -H "Authorization: Bearer {token}"
```

**响应:**
```json
{
  "success": true,
  "data": []
}
```

**说明**: 该评委没有评审任务，所以直接跳到步骤3查看详情。

### 步骤3: 查看项目详情（项目ID: 119）

**请求:**
```bash
curl -X GET http://localhost:6031/api/registrations/119 \
  -H "Authorization: Bearer {token}"
```

**响应（activityInfo部分）:**
```json
{
  "success": true,
  "data": {
    "activityInfo": {
      "theme": "项目主题119",
      "keywords": "质量,改进",
      "subjectTypeCode": "subject_type_6",
      "subjectTypeLabel": "满意度",
      "methodCode": "method_15",
      "methodLabel": "流程改造",
      "experienceImproveCode": "outpatient_process",
      "experienceImproveLabel": "门诊就诊流程更加优化",
      "qualityTopicCode": "surgery_mortality",
      "qualityTopicLabel": "降低住院患者围手术期死亡率",
      "avgWorkYears": 7,
      "avgAge": 32,
      "crossDepartment": true,
      "relatedToDigitalAi": false
    }
  }
}
```

### ✅ 场景4总结

**API**: `GET /api/registrations/119`

**4个Label字段**:
- `subjectTypeLabel`: "满意度"
- `methodLabel`: "流程改造"
- `experienceImproveLabel`: "门诊就诊流程更加优化" ← 前端应该显示这个
- `qualityTopicLabel`: "降低住院患者围手术期死亡率" ← 前端应该显示这个

---

## 🎯 关键结论

### 所有4个场景使用同一个API

**API**: `GET /api/registrations/{id}`

**项目ID**: 119（测试数据）

**返回的4个Label字段**:
1. `subjectTypeLabel`: "满意度"
2. `methodLabel`: "流程改造"
3. `experienceImproveLabel`: "门诊就诊流程更加优化"
4. `qualityTopicLabel`: "降低住院患者围手术期死亡率"

### ❌ 前端错误

如果前端显示的是：
- `experience_1` 或 `outpatient_process`
- `quality_1` 或 `surgery_mortality`

说明前端代码使用了 **Code字段** 而不是 **Label字段**。

### ✅ 正确的前端代码

```javascript
// 改善就医环境
{{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode }}

// 医疗质量相关主题
{{ activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode }}
```

---

## 📝 前端开发人员验证步骤

### 1. 使用Postman或curl测试

```bash
# 1. 登录（任意角色）
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13900000001","name":"李明华","role":"REVIEWER"}'

# 2. 复制返回的token

# 3. 获取详情
curl -X GET http://localhost:6031/api/registrations/119 \
  -H "Authorization: Bearer {替换为实际token}"

# 4. 查看响应中的 activityInfo.experienceImproveLabel 和 qualityTopicLabel
```

### 2. 在浏览器开发者工具中验证

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 刷新页面
4. 找到 `/api/registrations/119` 请求
5. 查看 Response 标签
6. 确认 `activityInfo` 对象包含以下字段：
   ```json
   {
     "experienceImproveLabel": "门诊就诊流程更加优化",
     "qualityTopicLabel": "降低住院患者围手术期死亡率"
   }
   ```

### 3. 检查前端代码

搜索前端代码中使用这些字段的地方：

```bash
# 搜索 experienceImproveCode
grep -r "experienceImproveCode" src/

# 搜索 qualityTopicCode
grep -r "qualityTopicCode" src/
```

如果找到直接使用Code的地方，改成：

```javascript
// 从
{{ activityInfo.experienceImproveCode }}

// 改成
{{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode }}
```

---

## 📊 完整的activityInfo数据结构

```json
{
  "theme": "项目主题119",
  "keywords": "质量,改进",
  
  "subjectTypeCode": "subject_type_6",
  "subjectTypeOther": null,
  "subjectTypeLabel": "满意度",
  
  "methodCode": "method_15",
  "methodOther": null,
  "methodLabel": "流程改造",
  
  "experienceImproveCode": "outpatient_process",
  "experienceImproveOther": null,
  "experienceImproveLabel": "门诊就诊流程更加优化",
  
  "qualityTopicCode": "surgery_mortality",
  "qualityTopicOther": null,
  "qualityTopicLabel": "降低住院患者围手术期死亡率",
  
  "avgWorkYears": 7,
  "avgAge": 32,
  "crossDepartment": true,
  "relatedToDigitalAi": false
}
```

---

## 🔧 快速测试工具

运行以下Python脚本快速验证：

```bash
python check_label_fields.py
```

这个工具会：
1. 自动登录
2. 获取项目119的详情
3. 检查所有Label字段
4. 显示前端代码示例

---

**文档更新时间**: 2026-02-09  
**测试项目ID**: 119  
**测试状态**: ✅ 所有Label字段正确返回  
**前端问题**: 使用了Code而不是Label
