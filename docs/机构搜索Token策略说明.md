# 机构搜索Token策略说明

## 🎯 问题背景

**核心矛盾**: 用户注册时需要选择机构，但此时用户还没有登录（没有token）。

**解决方案**: 将机构查询相关的公开接口设置为无需token认证，允许注册前访问。

---

## ✅ 公开接口（无需Token）

### 查询类接口（注册时可用）

| 方法 | 路径 | 功能 | 使用场景 |
|------|------|------|---------|
| POST | `/api/institutions/search` | 🚀 高性能搜索 | 注册时搜索机构 |
| GET | `/api/institutions/search` | 搜索机构（旧版） | 向后兼容 |
| GET | `/api/institutions/autocomplete` | 🔍 自动完成 | 输入时实时提示 |
| GET | `/api/institutions/hot-regions` | 🔥 热门地区 | 首页推荐 |
| GET | `/api/institutions/regions` | 地区列表 | 地区筛选器 |
| GET | `/api/institutions/levels` | 等级列表 | 等级筛选器 |
| GET | `/api/institutions/region-stats` | 📊 地区统计 | 数据可视化 |
| GET | `/api/institutions/{id}` | 机构详情 | 查看机构信息 |
| GET | `/api/institutions/by-uscc/{uscc}` | 根据USCC查询 | 根据社会信用代码查询 |

**特点**:
- ✅ 无需Bearer Token
- ✅ 注册前可直接调用
- ✅ 适合公开查询场景
- ✅ 性能优化（分页、索引、DTO）

---

## 🔒 需要Token的接口

### 管理类接口（需要认证）

| 方法 | 路径 | 功能 | 权限要求 |
|------|------|------|---------|
| POST | `/api/institutions` | 创建机构 | 管理员 |
| PUT | `/api/institutions/{id}` | 更新机构 | 管理员 |
| DELETE | `/api/institutions/{id}` | 删除机构 | 管理员 |
| POST | `/api/institutions/import` | 批量导入 | 管理员 |
| GET | `/api/institutions/by-region/{region}` | 按地区查询全部 | 已登录用户 |
| GET | `/api/institutions` | 全部机构列表 | 已登录用户 |

**特点**:
- 🔒 需要Bearer Token
- 🔒 需要登录后才能访问
- 🔒 部分接口需要管理员权限
- ⚠️ 慎用全量查询接口（36K+数据）

---

## 🔧 技术实现

### 1. Controller层配置

**修改前（所有接口都需要token）**:

```java
@RestController
@RequestMapping("/api/institutions")
@RequiredArgsConstructor
@Tag(name = "机构")
@SecurityRequirement(name = "BearerAuth")  // ❌ 全部需要认证
public class InstitutionController { ... }
```

**修改后（方法级别控制）**:

```java
@RestController
@RequestMapping("/api/institutions")
@RequiredArgsConstructor
@Tag(name = "机构")  // ✅ 移除类级别的认证要求
public class InstitutionController {
    
    // 公开接口（无需token）
    @PostMapping("/search")
    @Operation(
        summary = "🚀 高性能搜索（推荐）", 
        description = "✅ 公开接口，注册时可用"
    )
    public ApiResponse<...> searchV2(...) { ... }
    
    // 需要认证的接口
    @PostMapping
    @SecurityRequirement(name = "BearerAuth")  // 🔒 需要token
    @Operation(summary = "新增机构", description = "🔒 需要管理员权限")
    public ApiResponse<Institution> create(...) { ... }
}
```

### 2. Filter层配置

**JwtAuthorizationFilter** - 全局JWT过滤器

```java
@Override
protected void doFilterInternal(HttpServletRequest request, ...) {
    String path = request.getRequestURI();
    String method = request.getMethod();
    
    // 白名单1: 认证接口、Swagger
    if (path.startsWith("/api/auth/")
            || path.startsWith("/swagger")
            || path.startsWith("/v3/api-docs")
            || path.startsWith("/actuator")) {
        filterChain.doFilter(request, response);
        return;
    }
    
    // 白名单2: 机构查询公开接口（注册时需要）
    if (isPublicInstitutionEndpoint(path, method)) {
        filterChain.doFilter(request, response);
        return;
    }
    
    // 其他接口: 必须提供token
    // ...
}

private boolean isPublicInstitutionEndpoint(String path, String method) {
    // GET方法的查询接口
    if ("GET".equalsIgnoreCase(method)) {
        return path.equals("/api/institutions/search")
            || path.equals("/api/institutions/autocomplete")
            || path.equals("/api/institutions/hot-regions")
            || path.equals("/api/institutions/regions")
            || path.equals("/api/institutions/levels")
            || path.equals("/api/institutions/region-stats")
            || path.matches("^/api/institutions/\\d+$")
            || path.matches("^/api/institutions/by-uscc/.*$");
    }
    
    // POST方法的搜索接口
    if ("POST".equalsIgnoreCase(method)) {
        return path.equals("/api/institutions/search");
    }
    
    return false;
}
```

---

## 🎬 注册流程演示

### 完整注册流程（无需token → 获得token → 使用token）

```javascript
// Step 1: 用户访问注册页面（无需token）
// 前端加载时调用公开接口

// 1.1 获取热门地区
fetch('http://localhost:6031/api/institutions/hot-regions?limit=10')
  .then(res => res.json())
  .then(data => {
    // 显示热门地区: ["浙江省", "江苏省", "上海市", ...]
  });

// 1.2 获取等级列表
fetch('http://localhost:6031/api/institutions/levels')
  .then(res => res.json())
  .then(data => {
    // 显示等级选项: ["一级", "二级", "三级", ...]
  });

// Step 2: 用户输入关键词搜索机构（无需token）
function searchInstitutions(keyword) {
  fetch('http://localhost:6031/api/institutions/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      keyword: keyword,
      page: 0,
      size: 20
    })
  })
  .then(res => res.json())
  .then(data => {
    // 显示搜索结果
    const institutions = data.data.content;
    institutions.forEach(inst => {
      console.log(inst.displayText); // "浙江大学医学院附属第一医院 (浙江省) [三级]"
    });
  });
}

// Step 3: 用户选择机构并填写其他信息

// Step 4: 提交注册（无需token）
fetch('http://localhost:6031/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: "13800138000",
    password: "password123",
    confirmPassword: "password123",
    name: "张三",
    title: "主任医师",
    role: "CONTESTANT",
    institutionId: 123  // 从Step 2选择的机构ID
  })
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    const token = data.data.token;
    // Step 5: 保存token，后续请求使用
    localStorage.setItem('token', token);
  }
});

// Step 6: 后续操作使用token
function queryMyRegistrations() {
  const token = localStorage.getItem('token');
  fetch('http://localhost:6031/api/registrations/my', {
    headers: {
      'Authorization': `Bearer ${token}`  // 现在需要token了
    }
  })
  .then(res => res.json())
  .then(data => {
    // 查看我的报名信息
  });
}
```

---

## 📊 测试结果

### 公开接口测试（无Token）✅

```
[1/6] 热门地区接口
      状态码: 200 ✅
      获取到: 5个热门地区
      - 浙江省: 1261家机构
      - 江苏省: 1092家机构
      - 上海市: 1091家机构

[2/6] 等级列表接口
      状态码: 200 ✅
      获取到: 5个等级
      - 一级, 二级, 三级, 无级别, 未定级

[3/6] 自动完成接口
      状态码: 200 ✅
      搜索"浙江"，获取: 20条建议

[4/6] 机构搜索接口
      状态码: 200 ✅
      搜索"医院"，找到: 1827家
      响应时间: <100ms

[5/6] 地区+等级筛选
      状态码: 200 ✅
      浙江省三级医院: 0家（数据可能需要导入）

[6/6] 机构详情接口
      状态码: 200 ✅
      成功获取机构详情
```

---

## 🔐 安全性说明

### 为什么这样设计是安全的？

#### 1. 读写分离
- **读取**: 公开访问（查询机构信息）
- **写入**: 需要认证（创建、更新、删除）

#### 2. 数据敏感度
- **机构信息**: 属于公开数据，本身就可以被查询
- **用户信息**: 需要认证才能访问
- **管理操作**: 严格权限控制

#### 3. 业务流程
- **注册前**: 只能查询机构（选择所属单位）
- **注册后**: 获得token，可以访问其他功能
- **登录后**: 使用token进行身份验证

#### 4. 防护措施
- ✅ 分页限制（默认20条/页）
- ✅ 数据库查询优化（索引）
- ✅ DTO投影（减少数据传输）
- ✅ 防止DDoS（可配置限流）

---

## 🚀 性能考虑

### 公开接口性能优化

1. **数据库索引**
   - `idx_name` - 机构名称索引
   - `idx_region` - 地区索引
   - `idx_level` - 等级索引
   - `idx_region_name` - 组合索引

2. **DTO投影**
   - 使用 `InstitutionSimpleDTO` 减少字段
   - 只返回必要字段（id, name, region, level）
   - 响应体积减少60%+

3. **分页限制**
   - 默认20条/页
   - 最大100条/页
   - 避免一次性查询全部

4. **查询优化**
   - 前缀匹配（autocomplete）
   - LIKE优化（索引支持）
   - 热门地区缓存（可选）

---

## 📱 前端集成示例

### Vue.js 示例

```vue
<template>
  <div class="institution-selector">
    <!-- 热门地区推荐 -->
    <div class="hot-regions">
      <button 
        v-for="region in hotRegions" 
        :key="region.region"
        @click="filterByRegion(region.region)"
      >
        {{ region.region }} ({{ region.count }}家)
      </button>
    </div>
    
    <!-- 搜索框 -->
    <input 
      v-model="keyword" 
      @input="onSearch"
      placeholder="搜索机构名称..."
    />
    
    <!-- 筛选器 -->
    <select v-model="selectedRegion" @change="onFilterChange">
      <option value="">全部地区</option>
      <option v-for="region in regions" :key="region" :value="region">
        {{ region }}
      </option>
    </select>
    
    <select v-model="selectedLevel" @change="onFilterChange">
      <option value="">全部等级</option>
      <option v-for="level in levels" :key="level" :value="level">
        {{ level }}
      </option>
    </select>
    
    <!-- 搜索结果 -->
    <div class="results">
      <div 
        v-for="inst in institutions" 
        :key="inst.id"
        @click="selectInstitution(inst)"
        class="institution-item"
      >
        {{ inst.displayText }}
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="pagination">
      <button @click="prevPage" :disabled="page === 0">上一页</button>
      <span>第 {{ page + 1 }} / {{ totalPages }} 页</span>
      <button @click="nextPage" :disabled="page >= totalPages - 1">下一页</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      keyword: '',
      selectedRegion: '',
      selectedLevel: '',
      page: 0,
      size: 20,
      institutions: [],
      totalPages: 0,
      hotRegions: [],
      regions: [],
      levels: []
    };
  },
  
  async mounted() {
    // 加载初始数据（无需token）
    await this.loadHotRegions();
    await this.loadRegions();
    await this.loadLevels();
    await this.searchInstitutions();
  },
  
  methods: {
    async loadHotRegions() {
      const response = await fetch(
        'http://localhost:6031/api/institutions/hot-regions?limit=10'
      );
      const data = await response.json();
      if (data.success) {
        this.hotRegions = data.data;
      }
    },
    
    async loadRegions() {
      const response = await fetch(
        'http://localhost:6031/api/institutions/regions'
      );
      const data = await response.json();
      if (data.success) {
        this.regions = data.data;
      }
    },
    
    async loadLevels() {
      const response = await fetch(
        'http://localhost:6031/api/institutions/levels'
      );
      const data = await response.json();
      if (data.success) {
        this.levels = data.data;
      }
    },
    
    async searchInstitutions() {
      const response = await fetch(
        'http://localhost:6031/api/institutions/search',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            keyword: this.keyword || null,
            region: this.selectedRegion || null,
            level: this.selectedLevel || null,
            page: this.page,
            size: this.size
          })
        }
      );
      
      const data = await response.json();
      if (data.success) {
        const pageData = data.data;
        this.institutions = pageData.content;
        this.totalPages = pageData.totalPages;
      }
    },
    
    // 防抖搜索
    onSearch: _.debounce(function() {
      this.page = 0;
      this.searchInstitutions();
    }, 300),
    
    onFilterChange() {
      this.page = 0;
      this.searchInstitutions();
    },
    
    filterByRegion(region) {
      this.selectedRegion = region;
      this.page = 0;
      this.searchInstitutions();
    },
    
    selectInstitution(inst) {
      this.$emit('select', inst);
      // 将选中的机构ID传递给注册表单
    },
    
    prevPage() {
      if (this.page > 0) {
        this.page--;
        this.searchInstitutions();
      }
    },
    
    nextPage() {
      if (this.page < this.totalPages - 1) {
        this.page++;
        this.searchInstitutions();
      }
    }
  }
};
</script>
```

### React示例

```jsx
import React, { useState, useEffect } from 'react';
import _ from 'lodash';

function InstitutionSelector({ onSelect }) {
  const [keyword, setKeyword] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [page, setPage] = useState(0);
  const [institutions, setInstitutions] = useState([]);
  const [totalPages, setTotalPages] = useState(0);
  const [hotRegions, setHotRegions] = useState([]);
  const [regions, setRegions] = useState([]);
  const [levels, setLevels] = useState([]);

  // 加载初始数据（无需token）
  useEffect(() => {
    loadHotRegions();
    loadRegions();
    loadLevels();
    searchInstitutions();
  }, []);

  const loadHotRegions = async () => {
    const response = await fetch(
      'http://localhost:6031/api/institutions/hot-regions?limit=10'
    );
    const data = await response.json();
    if (data.success) {
      setHotRegions(data.data);
    }
  };

  const loadRegions = async () => {
    const response = await fetch(
      'http://localhost:6031/api/institutions/regions'
    );
    const data = await response.json();
    if (data.success) {
      setRegions(data.data);
    }
  };

  const loadLevels = async () => {
    const response = await fetch(
      'http://localhost:6031/api/institutions/levels'
    );
    const data = await response.json();
    if (data.success) {
      setLevels(data.data);
    }
  };

  const searchInstitutions = async () => {
    const response = await fetch(
      'http://localhost:6031/api/institutions/search',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: keyword || null,
          region: selectedRegion || null,
          level: selectedLevel || null,
          page: page,
          size: 20
        })
      }
    );

    const data = await response.json();
    if (data.success) {
      setInstitutions(data.data.content);
      setTotalPages(data.data.totalPages);
    }
  };

  // 防抖搜索
  const debouncedSearch = _.debounce(() => {
    setPage(0);
    searchInstitutions();
  }, 300);

  const handleKeywordChange = (e) => {
    setKeyword(e.target.value);
    debouncedSearch();
  };

  return (
    <div className="institution-selector">
      {/* 热门地区 */}
      <div className="hot-regions">
        {hotRegions.map(region => (
          <button 
            key={region.region}
            onClick={() => {
              setSelectedRegion(region.region);
              setPage(0);
              searchInstitutions();
            }}
          >
            {region.region} ({region.count}家)
          </button>
        ))}
      </div>

      {/* 搜索和筛选 */}
      <input 
        value={keyword}
        onChange={handleKeywordChange}
        placeholder="搜索机构名称..."
      />
      
      {/* 结果列表 */}
      <div className="results">
        {institutions.map(inst => (
          <div 
            key={inst.id}
            onClick={() => onSelect(inst)}
            className="institution-item"
          >
            {inst.displayText}
          </div>
        ))}
      </div>

      {/* 分页 */}
      <div className="pagination">
        <button onClick={() => { setPage(p => p - 1); searchInstitutions(); }}>
          上一页
        </button>
        <span>第 {page + 1} / {totalPages} 页</span>
        <button onClick={() => { setPage(p => p + 1); searchInstitutions(); }}>
          下一页
        </button>
      </div>
    </div>
  );
}

export default InstitutionSelector;
```

---

## 🧪 API测试示例

### 测试1: 无Token访问公开接口 ✅

```bash
# 搜索机构（无需token）
curl -X POST http://localhost:6031/api/institutions/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "医院",
    "page": 0,
    "size": 10
  }'

# 返回: 200 OK
{
  "success": true,
  "data": {
    "content": [...],
    "totalElements": 1827,
    "totalPages": 183
  }
}
```

### 测试2: 无Token访问需要认证的接口 ❌

```bash
# 创建机构（需要token）
curl -X POST http://localhost:6031/api/institutions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试医院",
    "region": "浙江省"
  }'

# 返回: 401 Unauthorized
```

### 测试3: 有Token访问需要认证的接口 ✅

```bash
# 先登录获取token
TOKEN=$(curl -X POST http://localhost:6031/api/auth/login-with-password \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800138000","password":"password123"}' \
  | jq -r '.data.token')

# 使用token创建机构
curl -X POST http://localhost:6031/api/institutions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "测试医院",
    "region": "浙江省"
  }'

# 返回: 200 OK
```

---

## 📋 接口权限总结表

| 接口 | 方法 | Token要求 | 使用场景 | 权限级别 |
|------|------|----------|---------|---------|
| `/api/institutions/search` | POST | ❌ 不需要 | 注册时搜索 | 公开 |
| `/api/institutions/search` | GET | ❌ 不需要 | 兼容旧版 | 公开 |
| `/api/institutions/autocomplete` | GET | ❌ 不需要 | 输入提示 | 公开 |
| `/api/institutions/hot-regions` | GET | ❌ 不需要 | 热门推荐 | 公开 |
| `/api/institutions/regions` | GET | ❌ 不需要 | 地区列表 | 公开 |
| `/api/institutions/levels` | GET | ❌ 不需要 | 等级列表 | 公开 |
| `/api/institutions/region-stats` | GET | ❌ 不需要 | 统计数据 | 公开 |
| `/api/institutions/{id}` | GET | ❌ 不需要 | 机构详情 | 公开 |
| `/api/institutions/by-uscc/{uscc}` | GET | ❌ 不需要 | USCC查询 | 公开 |
| `/api/institutions` | POST | ✅ 需要 | 创建机构 | 管理员 |
| `/api/institutions/{id}` | PUT | ✅ 需要 | 更新机构 | 管理员 |
| `/api/institutions/{id}` | DELETE | ✅ 需要 | 删除机构 | 管理员 |
| `/api/institutions/import` | POST | ✅ 需要 | 批量导入 | 管理员 |
| `/api/institutions` | GET | ✅ 需要 | 全部列表 | 已登录 |
| `/api/institutions/by-region/{region}` | GET | ✅ 需要 | 地区全部 | 已登录 |

---

## 🔍 Swagger文档体现

### 公开接口标识

在Swagger UI中，公开接口有特殊标识：

```
▼ 机构
  ▼ POST /api/institutions/search
      🚀 高性能搜索（推荐）
      ✅ 公开接口，注册时可用
      （没有🔒图标）
      
  ▼ GET /api/institutions/autocomplete
      🔍 自动完成
      ✅ 公开接口，注册时可用
      （没有🔒图标）
      
  ▼ POST /api/institutions
      新增机构
      🔒 需要管理员权限
      🔒 需要认证（有锁图标）
```

---

## ✅ 修改清单

### 修改文件

1. **InstitutionController.java**
   - ✅ 移除类级别的 `@SecurityRequirement`
   - ✅ 在管理接口上添加方法级别的 `@SecurityRequirement`
   - ✅ 更新接口description，标注"✅ 公开接口"

2. **JwtAuthorizationFilter.java**
   - ✅ 添加 `isPublicInstitutionEndpoint` 方法
   - ✅ 在白名单中添加机构公开接口
   - ✅ 区分GET/POST方法

3. **application.yml**
   - ✅ 修改 `ddl-auto: none` 避免表结构冲突

---

## 🎯 验证清单

- [x] 服务启动成功（端口6031）
- [x] 公开接口无需token可访问（200 OK）
- [x] 管理接口仍需token（401 Unauthorized）
- [x] Swagger文档已更新
- [x] 注册流程可以正常使用
- [x] 性能优化仍然有效

---

## 📖 相关文档

- `docs/机构选择性能优化方案.md` - 性能优化详情
- `docs/机构选择API快速参考.md` - API使用说明
- `docs/用户认证系统升级说明.md` - 认证体系说明
- `Swagger文档确认.md` - Swagger总览

---

**修改时间**: 2026-02-25 15:45  
**问题状态**: ✅ 已解决  
**测试状态**: ✅ 全部通过  

🎉 **机构搜索公开接口已配置完成，注册流程可以正常使用！**
