# 评审专家列表 - institutionLevel字段快速参考

## 一句话总结
评审专家列表接口已添加 `institutionLevel` 字段，显示评审专家所属机构的等级。

## API变更

### 接口
```
GET /api/admin/reviewers
GET /api/admin/reviewers/list
```

### 新增字段
```json
{
  "institutionLevel": "三级甲等"  // 机构等级
}
```

## 完整响应示例

```json
{
  "success": true,
  "data": [
    {
      "id": 14,
      "phone": "13800002114",
      "name": "陈卫东",
      "title": "主任医师",
      "institutionId": 1,
      "institutionName": "浙江大学医学院附属第二医院（浙二医院）",
      "institutionLevel": "三级甲等",  ← 新增
      "expertBackground": "MEDICAL",
      "currentLoad": 0
    }
  ]
}
```

## 前端使用（3步）

### Step 1: API调用（无需修改）
```javascript
const { data } = await axios.get('/api/admin/reviewers');
const reviewers = data.data;
```

### Step 2: 显示机构等级
```javascript
// 方式1: 直接显示
<span>{reviewer.institutionLevel}</span>

// 方式2: 带默认值
<span>{reviewer.institutionLevel || '未设置'}</span>

// 方式3: 完整信息
<span>{reviewer.institutionName} ({reviewer.institutionLevel})</span>
```

### Step 3: 表格展示
```vue
<el-table-column prop="institutionLevel" label="机构等级" />
```

## 可能的值

- 三级甲等
- 三级乙等
- 二级甲等
- 二级乙等
- 一级甲等
- null（未设置）

## 测试验证

```bash
# 运行测试
python scripts/test_reviewer_institution_level.py
```

**测试结果**: ✅ 通过（21名评审专家，100%为三级甲等）

## 兼容性

- ✅ 向后兼容
- ✅ 新增字段，不影响现有功能
- ✅ 前端可选择性使用

## 部署状态

- ✅ 代码已提交（commit: d4068d7）
- ✅ 服务已重启
- ✅ 测试通过

## 详细文档

`docs/评审专家列表-机构等级字段添加.md`

---

**就这么简单！前端可以立即使用 `institutionLevel` 字段。** 🚀
