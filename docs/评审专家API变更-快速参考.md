# 评审专家API变更 - 快速参考

## 变更时间: 2026-02-11

---

## 📋 变更总览

| 变更类型 | 内容 |
|---------|------|
| 删除请求参数 | `reviewerGroupCode`, `interviewGroupCode` |
| 删除响应字段 | `reviewerGroupCode`, `interviewGroupCode` |
| 保留字段 | `expertBackground`（专业背景） |

---

## 🔄 API对照表

### 1. GET /api/admin/reviewers

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **请求参数** | `?institutionId=10&reviewerGroupCode=A1&interviewGroupCode=B2&expertBackground=临床医学` | `?institutionId=10&expertBackground=临床医学` |
| **响应字段** | 包含 `reviewerGroupCode`, `interviewGroupCode` | 不包含这两个字段 |

### 2. GET /api/admin/reviewers/list

同上（兼容路径）

### 3. GET /api/admin/reviews/reviewers

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **请求参数** | `?institutionId=10&reviewerGroupCode=A1&interviewGroupCode=B2&expertBackground=临床医学` | `?institutionId=10&expertBackground=临床医学` |
| **响应字段** | 包含 `reviewerGroupCode`, `interviewGroupCode` | 不包含这两个字段 |

### 4. GET /api/admin/reviews/book-scores

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **请求参数** | `?competitionId=21&status=SCORED&reviewerGroupCode=A1&groupType=BASIC` | `?competitionId=21&status=SCORED&groupType=BASIC` |
| **响应字段** | 无变化 | 无变化 |

---

## 📝 响应数据对比

### ReviewerListItem

```diff
{
  "id": 1,
  "phone": "13800138000",
  "name": "张三",
  "title": "主任医师",
  "institutionId": 10,
  "institutionName": "浙江大学医学院附属第一医院",
- "reviewerGroupCode": "A1",
- "interviewGroupCode": "B2",
  "expertBackground": "临床医学",
  "currentLoad": 5
}
```

---

## ✅ 前端修改清单

### 必须修改

- [ ] 删除请求参数：`reviewerGroupCode`, `interviewGroupCode`
- [ ] 删除筛选条件UI：书审分组、面谈分组
- [ ] 删除表格列：书审分组、面谈分组
- [ ] 更新TypeScript类型定义

### 保持不变

- [x] `expertBackground` 参数和字段
- [x] `institutionId` 参数和字段
- [x] `currentLoad` 字段

---

## 🚀 快速修改示例

### Vue 3

```javascript
// 删除
const filters = ref({
  institutionId: null,
  reviewerGroupCode: null,      // ❌ 删除
  interviewGroupCode: null,      // ❌ 删除
  expertBackground: null
});

// 改为
const filters = ref({
  institutionId: null,
  expertBackground: null         // ✅ 保留
});
```

### React

```javascript
// 删除
const [filters, setFilters] = useState({
  institutionId: null,
  reviewerGroupCode: null,       // ❌ 删除
  interviewGroupCode: null,       // ❌ 删除
  expertBackground: null
});

// 改为
const [filters, setFilters] = useState({
  institutionId: null,
  expertBackground: null          // ✅ 保留
});
```

### TypeScript

```typescript
// 删除
interface ReviewerListItem {
  id: number;
  phone: string;
  name: string;
  title: string;
  institutionId: number | null;
  institutionName: string | null;
  reviewerGroupCode: string | null;    // ❌ 删除
  interviewGroupCode: string | null;    // ❌ 删除
  expertBackground: string | null;
  currentLoad: number;
}

// 改为
interface ReviewerListItem {
  id: number;
  phone: string;
  name: string;
  title: string;
  institutionId: number | null;
  institutionName: string | null;
  expertBackground: string | null;     // ✅ 保留
  currentLoad: number;
}
```

---

## 🧪 测试命令

```bash
# 测试评委列表
curl "http://localhost:8080/api/admin/reviewers?expertBackground=临床医学" \
  -H "Authorization: Bearer TOKEN"

# 测试书审得分
curl "http://localhost:8080/api/admin/reviews/book-scores?competitionId=21" \
  -H "Authorization: Bearer TOKEN"
```

---

## ❓ 常见问题

**Q: 旧代码会报错吗？**  
A: 不会，但分组参数会被忽略

**Q: 如何筛选评委？**  
A: 使用 `expertBackground` 参数

**Q: 数据库字段删除了吗？**  
A: 没有，只是不再使用

---

**详细文档**: 参见 `评审专家API变更-前端对接清单.md`
