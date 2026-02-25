# 机构选择API快速参考

> 36,000+ 家医疗机构，高性能搜索方案

## 🚀 推荐接口（按使用频率排序）

### 1. 高性能搜索（主力接口）★★★★★

```http
POST /api/institutions/search
Content-Type: application/json
Authorization: Bearer {token}

{
  "keyword": "人民医院",      // 可选：关键词（名称或地区）
  "region": "杭州市",         // 可选：地区筛选
  "level": "三甲",            // 可选：等级筛选
  "page": 0,                  // 页码（从0开始）
  "size": 20,                 // 每页大小（建议10-50）
  "sortBy": "name",           // 排序字段：name/region/level
  "sortDirection": "ASC"      // ASC/DESC
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 123,
        "name": "杭州市第一人民医院",
        "region": "杭州市",
        "level": "三甲",
        "usccLast4": "234X",
        "displayText": "杭州市第一人民医院 (杭州市) [三甲]"
      }
    ],
    "totalElements": 844,    // 总记录数
    "totalPages": 43,        // 总页数
    "number": 0,             // 当前页码
    "size": 20,              // 每页大小
    "numberOfElements": 20,  // 当前页数据量
    "first": true,           // 是否第一页
    "last": false            // 是否最后一页
  }
}
```

**性能**: 100-300ms  
**适用**: 下拉选择、模糊搜索、分页加载

---

### 2. 自动完成（输入建议）★★★★

```http
GET /api/institutions/autocomplete?prefix=杭州
Authorization: Bearer {token}
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "杭州市第一人民医院",
      "region": "杭州市",
      "level": "三甲",
      "displayText": "杭州市第一人民医院 (杭州市) [三甲]"
    }
    // 最多返回20条
  ]
}
```

**性能**: < 150ms  
**适用**: 输入框实时建议

---

### 3. 热门地区★★★

```http
GET /api/institutions/hot-regions?limit=10
Authorization: Bearer {token}
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "region": "台州市",
      "count": 1261
    },
    {
      "region": "温州市",
      "count": 1092
    }
    // ...
  ]
}
```

**性能**: < 100ms  
**适用**: 首页地区快捷选择

---

### 4. 获取所有地区★★

```http
GET /api/institutions/regions
Authorization: Bearer {token}
```

**响应**:
```json
{
  "success": true,
  "data": [
    "台州市",
    "温州市",
    "绍兴市",
    // ... 共96个地区
  ]
}
```

**性能**: < 100ms  
**适用**: 地区下拉选择

---

### 5. 获取所有等级★

```http
GET /api/institutions/levels
Authorization: Bearer {token}
```

**响应**:
```json
{
  "success": true,
  "data": [
    "三甲",
    "二甲",
    "三乙",
    "二乙",
    // ...
  ]
}
```

---

## 📱 前端使用示例

### Vue.js 快速集成

```vue
<template>
  <div>
    <!-- 步骤1: 选择地区 -->
    <el-select v-model="region" @change="onRegionChange" placeholder="选择地区">
      <el-option v-for="r in regions" :key="r" :value="r" :label="r"/>
    </el-select>
    
    <!-- 步骤2: 搜索机构 -->
    <el-input 
      v-model="keyword" 
      @input="debounceSearch" 
      placeholder="输入机构名称"
      clearable/>
    
    <!-- 步骤3: 选择机构 -->
    <el-select v-model="selectedInstitution" filterable remote>
      <el-option 
        v-for="inst in institutions" 
        :key="inst.id" 
        :value="inst.id"
        :label="inst.displayText"/>
    </el-select>
  </div>
</template>

<script>
import { debounce } from 'lodash';

export default {
  data() {
    return {
      region: null,
      keyword: '',
      regions: [],
      institutions: [],
      selectedInstitution: null
    };
  },
  
  methods: {
    // 加载地区
    async loadRegions() {
      const res = await this.$http.get('/api/institutions/regions');
      this.regions = res.data.data;
    },
    
    // 搜索机构（带防抖）
    debounceSearch: debounce(async function() {
      await this.searchInstitutions();
    }, 500),
    
    async searchInstitutions() {
      const res = await this.$http.post('/api/institutions/search', {
        keyword: this.keyword,
        region: this.region,
        page: 0,
        size: 20
      });
      this.institutions = res.data.data.content;
    },
    
    onRegionChange() {
      this.keyword = '';
      this.searchInstitutions();
    }
  },
  
  mounted() {
    this.loadRegions();
  }
};
</script>
```

### React 快速集成

```jsx
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';

function InstitutionSelector() {
  const [region, setRegion] = useState(null);
  const [keyword, setKeyword] = useState('');
  const [institutions, setInstitutions] = useState([]);
  
  // 搜索机构（带防抖）
  const searchInstitutions = debounce(async () => {
    const res = await fetch('/api/institutions/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        keyword: keyword,
        region: region,
        page: 0,
        size: 20
      })
    });
    const data = await res.json();
    setInstitutions(data.data.content);
  }, 500);
  
  useEffect(() => {
    if (keyword.length >= 2 || region) {
      searchInstitutions();
    }
  }, [keyword, region]);
  
  return (
    <div>
      <input 
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="输入机构名称"
      />
      
      <select value={region} onChange={(e) => setRegion(e.target.value)}>
        <option value="">选择地区</option>
        {/* 地区选项 */}
      </select>
      
      <ul>
        {institutions.map(inst => (
          <li key={inst.id}>{inst.displayText}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 🎯 使用场景

### 场景1: 地区优先（推荐）

```javascript
// 1. 加载热门地区
GET /api/institutions/hot-regions?limit=10

// 2. 用户选择地区后搜索
POST /api/institutions/search
{
  "region": "杭州市",
  "page": 0,
  "size": 20
}

// 3. 用户输入关键词进一步筛选
POST /api/institutions/search
{
  "keyword": "人民",
  "region": "杭州市",
  "page": 0,
  "size": 20
}
```

### 场景2: 直接搜索

```javascript
// 1. 用户输入关键词（至少2字符）
GET /api/institutions/autocomplete?prefix=杭州

// 2. 用户继续输入，执行完整搜索
POST /api/institutions/search
{
  "keyword": "杭州人民",
  "page": 0,
  "size": 20
}
```

### 场景3: 无限滚动

```javascript
let page = 0;

async function loadMore() {
  const res = await fetch('/api/institutions/search', {
    method: 'POST',
    body: JSON.stringify({
      keyword: keyword,
      region: region,
      page: page,
      size: 20
    })
  });
  
  const data = await res.json();
  institutions.push(...data.data.content);
  page++;
  
  // 判断是否还有更多
  if (data.data.last) {
    hasMore = false;
  }
}
```

---

## ⚡ 性能优化checklist

### 前端

- [ ] 使用防抖（500ms）
- [ ] 最少2个字符才搜索
- [ ] 使用虚拟滚动（列表>100条）
- [ ] 缓存已加载数据（30分钟）
- [ ] 保存最近使用（5条）
- [ ] 显示loading状态
- [ ] 错误处理和重试

### 后端

- [ ] 添加数据库索引
- [ ] 使用分页查询
- [ ] 限制每页大小（≤50）
- [ ] 使用DTO减少传输量
- [ ] 考虑Redis缓存
- [ ] 监控慢查询

---

## 🐛 常见问题

**Q: 搜索太慢？**  
A: 确保使用POST方式的search接口，并添加地区筛选条件

**Q: 返回数据太多？**  
A: 设置合理的size参数（建议20），使用分页

**Q: 用户输入时卡顿？**  
A: 使用防抖（debounce），延迟500ms

**Q: 某些地区机构太多？**  
A: 引导用户输入关键词进一步筛选

---

## 📞 技术支持

- **Swagger文档**: http://localhost:6031/swagger
- **性能测试**: `python scripts/test_institution_search_performance.py`
- **相关文档**: 
  - [性能优化方案](./机构选择性能优化方案.md)
  - [用户注册流程](./用户注册流程说明.md)

---

**版本**: 1.0  
**更新**: 2026-02-25
