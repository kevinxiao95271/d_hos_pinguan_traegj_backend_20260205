# API返回机构等级字段说明

**更新时间**: 2026-02-07  
**更新内容**: 所有返回机构信息的API新增 `level`（医院等级）字段

---

## 📋 修改概述

为了支持前端显示医院等级信息，我们在所有返回机构信息的API响应中新增了 `level` 字段。

---

## 🔄 修改的API列表

### 1. 登录接口 - 新增2个字段 ⭐

**接口**: `POST /api/auth/login`

**新增字段**:
- ✅ `institutionRegion` - 机构地区
- ✅ `institutionLevel` - 医院等级

**修改前**:
```json
{
  "code": 200,
  "data": {
    "id": 150,
    "phone": "13900000001",
    "name": "张三",
    "title": "护理部主任",
    "role": "CONTESTANT",
    "institutionId": 34,
    "institutionName": "杭州市临安区第三人民医院",
    "institutionCode": "INS-0034",
    "institutionUscc": "12330185470362268D",
    "expertBackground": null,
    "token": "eyJhbGc..."
  }
}
```

**修改后**:
```json
{
  "code": 200,
  "data": {
    "id": 150,
    "phone": "13900000001",
    "name": "张三",
    "title": "护理部主任",
    "role": "CONTESTANT",
    "institutionId": 34,
    "institutionName": "杭州市临安区第三人民医院",
    "institutionCode": "INS-0034",
    "institutionUscc": "12330185470362268D",
    "institutionRegion": "杭州",              ← 新增：地区
    "institutionLevel": "三级乙等",           ← 新增：医院等级
    "expertBackground": null,
    "token": "eyJhbGc..."
  }
}
```

---

### 2. 报名详情接口 - institution对象新增1个字段 ⭐

**接口**: `GET /api/registrations/{id}`

**新增字段**:
- ✅ `institution.level` - 医院等级

**修改前**:
```json
{
  "code": 200,
  "data": {
    "registration": {
      "id": 140,
      "projectName": "降低患者跌倒发生率",
      "groupType": "GRASSROOTS",
      "status": "APPROVED"
    },
    "institution": {
      "id": 34,
      "name": "杭州市临安区第三人民医院",
      "code": "INS-0034",
      "uscc": "12330185470362268D",
      "region": "杭州"
    },
    "members": [...],
    "activityInfo": {...}
  }
}
```

**修改后**:
```json
{
  "code": 200,
  "data": {
    "registration": {
      "id": 140,
      "projectName": "降低患者跌倒发生率",
      "groupType": "GRASSROOTS",
      "status": "APPROVED"
    },
    "institution": {
      "id": 34,
      "name": "杭州市临安区第三人民医院",
      "code": "INS-0034",
      "uscc": "12330185470362268D",
      "region": "杭州",
      "level": "三级乙等"                      ← 新增：医院等级
    },
    "members": [...],
    "activityInfo": {...}
  }
}
```

---

### 3. 机构列表接口 - 每个机构对象新增1个字段 ⭐

**接口**: `GET /api/institutions`

**新增字段**:
- ✅ `level` - 医院等级

**修改前**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "浙江大学医学院附属第二医院（浙二医院）",
      "code": "INS-0001",
      "uscc": "1233000047053349XG",
      "region": null,
      "createdAt": "2026-02-04T23:45:40"
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
      "id": 1,
      "name": "浙江大学医学院附属第二医院（浙二医院）",
      "code": "INS-0001",
      "uscc": "1233000047053349XG",
      "region": null,
      "level": "三级甲等",                     ← 新增：医院等级
      "createdAt": "2026-02-04T23:45:40"
    }
  ]
}
```

---

### 4. 机构详情接口 - 新增1个字段 ⭐

**接口**: `GET /api/institutions/{id}`

**新增字段**:
- ✅ `level` - 医院等级

**修改后**:
```json
{
  "code": 200,
  "data": {
    "id": 34,
    "name": "杭州市临安区第三人民医院",
    "code": "INS-0034",
    "uscc": "12330185470362268D",
    "region": "杭州",
    "level": "三级乙等",                      ← 新增：医院等级
    "createdAt": "2026-02-07T10:00:00"
  }
}
```

---

### 5. 后台导出机构接口 - 新增1个字段 ⭐

**接口**: `GET /api/admin/institutions/export`

**权限**: 仅限OPS角色

**新增字段**:
- ✅ `level` - 医院等级

**修改后**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 34,
      "name": "杭州市临安区第三人民医院",
      "code": "INS-0034",
      "uscc": "12330185470362268D",
      "region": "杭州",
      "level": "三级乙等",                    ← 新增：医院等级
      "createdAt": "2026-02-07T10:00:00"
    }
  ]
}
```

---

## 📊 新增字段详细说明

### 字段名称

| 位置 | 字段名 | 类型 | 说明 |
|------|--------|------|------|
| LoginResponse | `institutionRegion` | String | 机构地区 |
| LoginResponse | `institutionLevel` | String | 医院等级 |
| InstitutionInfo | `level` | String | 医院等级 |
| Institution实体 | `level` | String | 医院等级 |

### 字段值示例

| 等级 | 示例 |
|------|------|
| 三级甲等 | `"三级甲等"` |
| 三级乙等 | `"三级乙等"` |
| 未填写 | `null` 或 `""` |

---

## 🎯 前端使用指南

### 1. 登录后获取机构等级

```javascript
// 登录
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13900000001',
    name: '张三',
    title: '护理部主任',
    role: 'CONTESTANT',
    institutionId: 34
  })
});

const data = await response.json();

// 获取机构信息
const institutionRegion = data.data.institutionRegion;  // "杭州"
const institutionLevel = data.data.institutionLevel;    // "三级乙等"

// 显示
console.log(`${data.data.institutionName} - ${institutionLevel}`);
// 输出: "杭州市临安区第三人民医院 - 三级乙等"
```

### 2. 报名详情页显示机构等级

```javascript
// 获取报名详情
const response = await fetch(`/api/registrations/${registrationId}`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const data = await response.json();
const institution = data.data.institution;

// 显示机构信息
if (institution) {
  console.log(`医疗机构: ${institution.name}`);
  console.log(`机构代码: ${institution.code}`);
  console.log(`地区: ${institution.region || '未填写'}`);
  console.log(`等级: ${institution.level || '未填写'}`);  // 新增
}
```

### 3. 机构列表页显示等级

```vue
<template>
  <div v-for="institution in institutions" :key="institution.id">
    <h3>{{ institution.name }}</h3>
    <p>代码: {{ institution.code }}</p>
    <p>地区: {{ institution.region || '未填写' }}</p>
    <p>等级: {{ institution.level || '未填写' }}</p>  <!-- 新增 -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      institutions: []
    };
  },
  async mounted() {
    const response = await fetch('/api/institutions', {
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    const data = await response.json();
    this.institutions = data.data;
  }
};
</script>
```

---

## ⚠️ 注意事项

### 1. 字段可能为空
由于历史数据可能未填写等级信息，前端需要做好空值处理：

```javascript
// ✅ 推荐做法
const level = institution.level || '未填写';

// ✅ 或者使用可选链
const level = institution?.level ?? '未填写';
```

### 2. 数据完整性
目前数据统计：
- ✅ **41家机构已填写等级** (97.6%)
  - 三级甲等：34家
  - 三级乙等：7家
- ⚠️ **1家机构未填写等级** (2.4%)
  - 温州市第一人民医院 (ID: 5)

### 3. 向后兼容
- ✅ 新增字段不影响现有功能
- ✅ 旧版前端不获取 `level` 字段也能正常工作
- ✅ 新版前端可以选择性展示 `level` 字段

---

## 🔧 技术实现细节

### 1. 数据库层
```sql
-- institutions表已添加level字段
ALTER TABLE institutions 
ADD COLUMN level VARCHAR(32) COMMENT '医院等级（如：三级甲等）'
AFTER region;
```

### 2. 实体类层
```java
@Entity
@Table(name = "institutions")
public class Institution {
    // ... 其他字段
    
    @Column(length = 32)
    private String level;  // 新增字段
}
```

### 3. DTO层
```java
// InstitutionInfo.java
public class InstitutionInfo {
    private Long id;
    private String name;
    private String code;
    private String uscc;
    private String region;
    private String level;  // 新增字段
}

// LoginResponse.java
public class LoginResponse {
    // ... 其他字段
    private String institutionRegion;  // 新增字段
    private String institutionLevel;   // 新增字段
}
```

### 4. Service层
```java
// RegistrationService.java - getDetail()方法
institutionInfo = InstitutionInfo.builder()
    .id(inst.getId())
    .name(inst.getName())
    .code(inst.getCode())
    .uscc(inst.getUscc())
    .region(inst.getRegion())
    .level(inst.getLevel())  // 新增
    .build();
```

---

## 📋 修改文件清单

### 修改的文件（5个）
1. ✅ `src/main/java/com/trae/pinguan/domain/entity/Institution.java`
   - 新增 `level` 字段

2. ✅ `src/main/java/com/trae/pinguan/web/dto/InstitutionInfo.java`
   - 新增 `level` 字段

3. ✅ `src/main/java/com/trae/pinguan/web/dto/LoginResponse.java`
   - 新增 `institutionRegion` 字段
   - 新增 `institutionLevel` 字段

4. ✅ `src/main/java/com/trae/pinguan/service/RegistrationService.java`
   - 在 `getDetail()` 方法中添加 `level` 字段到 `InstitutionInfo`

5. ✅ `src/main/java/com/trae/pinguan/web/AuthController.java`
   - 在 `login()` 方法返回中添加 `institutionRegion` 和 `institutionLevel`

---

## 📊 影响的API汇总表

| API | 方法 | 路径 | 新增字段 | 影响范围 |
|-----|------|------|---------|---------|
| 登录接口 | POST | `/api/auth/login` | `institutionRegion`, `institutionLevel` | 所有角色登录 |
| 报名详情 | GET | `/api/registrations/{id}` | `institution.level` | 参赛者查看报名 |
| 机构列表 | GET | `/api/institutions` | `level` | 所有需要选择机构的场景 |
| 机构详情 | GET | `/api/institutions/{id}` | `level` | 查看机构详情 |
| 导出机构 | GET | `/api/admin/institutions/export` | `level` | OPS导出数据 |

---

## 🎉 总结

### 新增字段统计
- **LoginResponse**: 新增 2 个字段
  - `institutionRegion` (机构地区)
  - `institutionLevel` (医院等级)

- **InstitutionInfo**: 新增 1 个字段
  - `level` (医院等级)

- **Institution实体**: 新增 1 个字段
  - `level` (医院等级)

### 影响的API
- ✅ 5个API接口受影响
- ✅ 所有返回机构信息的地方都已添加等级字段
- ✅ 向后兼容，不影响现有功能

---

**文档生成时间**: 2026-02-07  
**维护人员**: 系统管理员  
**更新状态**: ✅ 完成
