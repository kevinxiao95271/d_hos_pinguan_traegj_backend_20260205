# 按label筛选功能实现说明

> 实现日期：2026-02-07  
> 功能：支持前端直接传递label（如"品管圈-课题达成"）进行筛选  
> 状态：✅ 已实现，待测试

---

## 📋 需求背景

**原问题**：
- 报名106在项目列表中存在
- 按品管工具"品管圈-课题达成"筛选时返回空结果
- 数据库中存储的是code（如`qc_topic`），前端显示的是label（如"品管圈-课题达成"）

**原解决方案**：
- 前端需要维护label→code映射表
- 筛选时传递code而不是label

**新需求**：
- 用户要求后端支持直接传递label进行筛选
- 前端不需要维护映射表

---

## ✅ 实现方案

### 1. API修改

**接口**：`GET /api/admin/registrations/filter`

**新增参数**：
- `methodLabel`：品管工具标签（如"品管圈-课题达成"）
- `subjectTypeLabel`：选题类型标签（如"教育训练"）

**参数优先级**：
- 如果同时传递code和label，优先使用code
- 如果只传递label，后端自动转换为code

### 2. 代码修改

#### 修改文件1：`AdminRegistrationController.java`

```java
@GetMapping("/filter")
@Operation(summary = "后台报名筛选（支持按code或label筛选）")
public ApiResponse<List<RegistrationFilterItem>> filter(
        @RequestParam Long competitionId,
        @RequestParam(required = false) GroupType groupType,
        @RequestParam(required = false) String groupCode,
        @RequestParam(required = false) String projectName,
        @RequestParam(required = false) String institutionName,
        @RequestParam(required = false) String methodCode,
        @RequestParam(required = false) String methodLabel,      // 新增
        @RequestParam(required = false) String subjectTypeCode,
        @RequestParam(required = false) String subjectTypeLabel) { // 新增
    return ApiResponse.ok(registrationService.filterRegistrations(
            competitionId,
            groupType,
            groupCode,
            projectName,
            institutionName,
            methodCode,
            methodLabel,      // 新增
            subjectTypeCode,
            subjectTypeLabel  // 新增
    ));
}
```

#### 修改文件2：`RegistrationService.java`

**核心逻辑**：

1. **label到code转换**
   ```java
   // 如果传了methodLabel，转换为methodCode（支持多个匹配）
   List<String> methodCodes = dictionaryItemRepository
           .findByTypeAndActiveOrderByIdAsc("method", true)
           .stream()
           .filter(item -> methodLabel.trim().equals(item.getLabel()))
           .map(item -> item.getCode())
           .collect(Collectors.toList());
   ```

2. **处理多个匹配**
   - 如果一个label对应多个code（如"品管圈-课题达成"对应`method_2`和`qc_topic`）
   - 分别查询每个code的结果
   - 合并结果并去重

3. **查询逻辑**
   ```java
   if (methodCodes.size() > 1) {
       // 多个code匹配，分别查询并合并
       for (String code : methodCodes) {
           List<RegistrationFilterItem> partialItems = 
               registrationRepository.filterRegistrations(..., code, ...);
           // 去重后添加到结果
       }
   } else if (methodCodes.size() == 1) {
       // 单个code匹配，正常查询
       methodCodeValue = methodCodes.get(0);
       items = registrationRepository.filterRegistrations(...);
   }
   ```

---

## 🎯 使用示例

### 示例1：按label筛选（新功能）

```javascript
// 前端直接传递label
const response = await axios.get('/api/admin/registrations/filter', {
  params: {
    competitionId: 21,
    methodLabel: '品管圈-课题达成'  // 直接传label
  },
  headers: {
    Authorization: `Bearer ${token}`
  }
});

// 返回所有使用"品管圈-课题达成"的报名
// 包括method_2和qc_topic两种code的数据
```

### 示例2：按code筛选（旧方式，仍然支持）

```javascript
const response = await axios.get('/api/admin/registrations/filter', {
  params: {
    competitionId: 21,
    methodCode: 'qc_topic'  // 传code
  },
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

### 示例3：同时传code和label（code优先）

```javascript
const response = await axios.get('/api/admin/registrations/filter', {
  params: {
    competitionId: 21,
    methodCode: 'qc_topic',           // code优先
    methodLabel: '品管圈-课题达成'      // label被忽略
  },
  headers: {
    Authorization: `Bearer ${token}`
  }
});

// 只使用methodCode='qc_topic'进行筛选
```

---

## 📊 测试场景

### 测试数据

数据库中有两个label都是"品管圈-课题达成"：
- `method_2` → 品管圈-课题达成
- `qc_topic` → 品管圈-课题达成

报名数据：
- 报名106：methodCode=`qc_topic`
- 报名114：methodCode=`qc_topic`

### 测试用例

| 测试项 | 参数 | 预期结果 |
|--------|------|----------|
| 按code筛选 | `methodCode=qc_topic` | 返回2个报名（106, 114） |
| 按label筛选 | `methodLabel=品管圈-课题达成` | 返回2个报名（106, 114） |
| 同时传code和label | `methodCode=qc_topic&methodLabel=PDCA` | 返回2个报名（使用code） |
| 按其他label筛选 | `methodLabel=PDCA` | 返回3个报名 |
| 无效label | `methodLabel=不存在的工具` | 返回0个报名 |

### 测试脚本

```bash
# 启动服务器
mvn spring-boot:run

# 运行测试脚本
python scripts/test_label_filter.py
```

---

## 🔧 前端使用指南

### 方式1：直接使用label（推荐）

```vue
<template>
  <el-select v-model="selectedMethod" @change="filterByMethod">
    <el-option label="品管圈-课题达成" value="品管圈-课题达成" />
    <el-option label="PDCA" value="PDCA" />
    <el-option label="5S" value="5S" />
  </el-select>
</template>

<script setup>
async function filterByMethod(label) {
  const response = await axios.get('/api/admin/registrations/filter', {
    params: {
      competitionId: 21,
      methodLabel: label  // 直接传label，无需转换
    }
  });
  
  registrations.value = response.data.data;
}
</script>
```

### 方式2：继续使用code（兼容旧代码）

```vue
<template>
  <el-select v-model="selectedMethodCode" @change="filterByMethod">
    <el-option label="品管圈-课题达成" value="qc_topic" />
    <el-option label="PDCA" value="pdca" />
    <el-option label="5S" value="5s" />
  </el-select>
</template>

<script setup>
async function filterByMethod(code) {
  const response = await axios.get('/api/admin/registrations/filter', {
    params: {
      competitionId: 21,
      methodCode: code  // 传code
    }
  });
  
  registrations.value = response.data.data;
}
</script>
```

---

## ⚠️ 注意事项

### 1. 重复label处理

如果一个label对应多个code（如"品管圈-课题达成"对应`method_2`和`qc_topic`）：
- 后端会自动查询所有匹配的code
- 合并结果并去重
- 前端无需特殊处理

### 2. 参数优先级

- `methodCode` > `methodLabel`
- `subjectTypeCode` > `subjectTypeLabel`
- 如果同时传递，优先使用code

### 3. 性能考虑

- 单个code匹配：1次数据库查询
- 多个code匹配：N次数据库查询（N为匹配的code数量）
- 建议：如果已知code，优先使用code参数

### 4. 兼容性

- ✅ 完全向后兼容
- ✅ 旧代码无需修改
- ✅ 新旧方式可以共存

---

## 📖 API文档

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| competitionId | Long | ✅ | 赛事ID | 21 |
| groupType | String | ❌ | 组别类型 | BASIC |
| groupCode | String | ❌ | 组代码 | A1 |
| projectName | String | ❌ | 项目名称（模糊匹配） | 护理 |
| institutionName | String | ❌ | 机构名称（模糊匹配） | 浙江 |
| **methodCode** | String | ❌ | **品管工具代码** | **qc_topic** |
| **methodLabel** | String | ❌ | **品管工具标签（新增）** | **品管圈-课题达成** |
| **subjectTypeCode** | String | ❌ | **选题类型代码** | **education** |
| **subjectTypeLabel** | String | ❌ | **选题类型标签（新增）** | **教育训练** |

### 返回数据

```typescript
interface RegistrationFilterItem {
  registrationId: number;
  projectName: string;
  institutionName: string;
  groupType: string;
  groupCode: string;
  submittedAt: string;
  subjectTypeCode: string;
  methodCode: string;
  subjectTypeLabel: string;
  methodLabel: string;
  applicantName: string;
}
```

---

## ✅ 总结

### 实现的功能

1. ✅ 支持按label筛选
2. ✅ 支持按code筛选（兼容旧方式）
3. ✅ 处理重复label（自动查询所有匹配的code）
4. ✅ 参数优先级（code优先于label）
5. ✅ 完全向后兼容

### 前端优势

1. ✅ 无需维护label→code映射表
2. ✅ 代码更简洁
3. ✅ 更易维护
4. ✅ 用户体验更好

### 测试状态

- ✅ 代码已实现
- ⏳ 待启动服务器测试
- 📝 测试脚本：`scripts/test_label_filter.py`

---

## 🚀 下一步

1. **启动服务器**
   ```bash
   mvn spring-boot:run
   ```

2. **运行测试**
   ```bash
   python scripts/test_label_filter.py
   ```

3. **验证结果**
   - 按code筛选：成功
   - 按label筛选：成功
   - 同时传code和label：code优先
   - 多个匹配的label：正确合并结果

4. **前端集成**
   - 修改筛选组件
   - 直接传递label
   - 测试功能

---

**实现完成！前端现在可以直接传递label进行筛选，无需维护映射表。** ✅
