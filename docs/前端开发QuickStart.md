# 前端开发 Quick Start

## 🚀 5分钟快速上手

### 第一步：理解认证机制

所有API都使用JWT Token认证，流程：

```javascript
// 1. 登录获取token
const response = await fetch('http://localhost:6031/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13800000009',
    name: '张三',
    title: '组委会主任',
    role: 'COMMITTEE'  // 角色决定权限
  })
});

const { data } = await response.json();
const token = data.token;

// 2. 保存token
localStorage.setItem('token', token);

// 3. 后续所有请求都带上token
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### 第二步：角色和权限

| 角色 | 角色代码 | 可以做什么 |
|-----|---------|-----------|
| **组委会** | COMMITTEE | 审批报名、分配评委、查看统计、推进赛事阶段 |
| **参赛者** | CONTESTANT | 提交报名、查看我的报名状态 |
| **评委** | REVIEWER | 查看评审任务、提交评分 |
| **运维** | OPS | 查看所有数据、系统管理 |

### 第三步：核心数据流

```
【报名流程】
参赛者登录 → 选择赛事+机构 → 填写表单 → 提交报名
          ↓
组委会审批 → 通过/驳回
          ↓
推进到评审阶段 → 分配评委
          ↓
评委打分 → 查看排名 → 公布结果
```

---

## 📱 三大页面开发指南

### 页面1: 参赛者报名页面

**需要的API:**

```javascript
// 1. 获取赛事列表（选择报哪个赛事）
GET /api/competitions?stage=REGISTER

// 2. 获取机构列表（选择所属机构）
GET /api/institutions

// 3. 提交报名
POST /api/registrations
{
  "competitionId": 1,
  "institutionId": 5,
  "projectName": "优化门诊预约流程品管圈",
  "contactPerson": "张医生",
  "contactPhone": "13800138000",
  "participantNames": "张医生,李护士,王技师",
  "activityType": "医疗类",
  "activityBackground": "门诊预约效率低...",
  "activityObjective": "缩短等待时间...",
  "activityProcess": "1.调查 2.分析...",
  "activityResult": "效率提升67%...",
  "projectSummary": "总结..."
}

// 4. 查看我的报名
GET /api/registrations/my
```

**页面结构:**
```
报名页面
├─ 顶部：选择赛事下拉框
├─ 基本信息区
│  ├─ 机构选择（下拉）
│  ├─ 项目名称（输入框）
│  ├─ 联系人/电话
│  └─ 参与人员（多人，逗号分隔）
├─ 活动详情区
│  ├─ 活动类型（下拉）
│  ├─ 活动背景（大文本框）
│  ├─ 活动目标（大文本框）
│  ├─ 活动过程（大文本框）
│  └─ 活动成果（大文本框）
├─ 项目总结区
│  └─ 项目总结（大文本框）
└─ 提交按钮

我的报名列表
├─ 表格展示
│  ├─ 项目名称
│  ├─ 状态（PENDING/APPROVED/REJECTED）
│  ├─ 提交时间
│  └─ 操作（查看详情）
```

---

### 页面2: 组委会管理页面

**需要的API:**

```javascript
// 1. 待审批列表
GET /api/admin/registrations?status=PENDING

// 2. 审批（通过）
PUT /api/admin/registrations/{id}/status
{ "status": "APPROVED" }

// 3. 审批（驳回）
PUT /api/admin/registrations/{id}/status
{ "status": "REJECTED", "rejectReason": "材料不完整" }

// 4. 获取评委池
GET /api/admin/reviewers
GET /api/admin/reviewers?expertBackground=MEDICAL  // 按背景筛选

// 5. 分配评审任务
POST /api/admin/reviews/assign
{
  "registrationId": 10,
  "reviewerId": 6,
  "reviewType": "INITIAL"  // INITIAL(初审) or FINAL(终审)
}

// 6. 查看评审进度
GET /api/admin/reviews/summary?competitionId=1

// 7. 查看排名
GET /api/admin/reviews/ranking?competitionId=1

// 8. 推进赛事阶段
PUT /api/admin/competitions/{id}/stage
{ "stage": "REVIEW" }  // REGISTER→REVIEW→INTERVIEW→FINISHED
```

**页面结构:**
```
组委会工作台
├─ 左侧导航
│  ├─ 报名审批
│  ├─ 评委管理
│  ├─ 任务分配
│  ├─ 评审进度
│  └─ 统计数据
│
├─ 报名审批页
│  ├─ 筛选器（状态/机构）
│  ├─ 报名列表
│  └─ 详情弹窗
│     ├─ 项目信息展示
│     └─ 通过/驳回按钮
│
├─ 任务分配页
│  ├─ 左边：待分配报名列表（33个）
│  ├─ 右边：评委池（16个）
│  │  ├─ 筛选：按背景（医疗/管理/护理）
│  │  └─ 筛选：按分组（A1/B1/B2）
│  └─ 拖拽或点击分配
│
└─ 评审进度页
   ├─ 进度表格
   │  ├─ 项目名
   │  ├─ 已评/总评委数
   │  ├─ 平均分
   │  └─ 状态（进行中/已完成）
   └─ 排名列表
      ├─ 排名
      ├─ 项目名
      ├─ 机构
      └─ 平均分
```

---

### 页面3: 评委评审页面

**需要的API:**

```javascript
// 1. 获取我的评审任务
GET /api/reviews/my-tasks

// 2. 提交评分
POST /api/reviews/{id}/score
{
  "score": 88.5,  // 0-100分
  "comment": "项目设计合理，数据详实..."
}
```

**页面结构:**
```
评委工作台
├─ 我的任务列表
│  ├─ 待评审（未打分）
│  └─ 已完成（已打分）
│
└─ 评审详情页
   ├─ 项目信息展示
   │  ├─ 项目名称
   │  ├─ 机构名称
   │  ├─ 活动背景
   │  ├─ 活动过程
   │  └─ 活动成果
   ├─ 评分区
   │  ├─ 分数输入框（0-100）
   │  └─ 评语文本框
   └─ 提交按钮
```

---

## 🔧 实用代码片段

### 统一的API调用封装

```javascript
// api.js - 统一封装
const API_BASE = 'http://localhost:6031';

export async function apiCall(url, options = {}) {
  const token = localStorage.getItem('token');
  
  const defaultOptions = {
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
      ...options.headers
    }
  };
  
  try {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      ...defaultOptions
    });
    
    // 401自动跳转登录
    if (response.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
      return null;
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.message || '操作失败');
    }
    
    return data.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

// 使用示例
import { apiCall } from './api';

// GET请求
const institutions = await apiCall('/api/institutions');

// POST请求
const result = await apiCall('/api/registrations', {
  method: 'POST',
  body: JSON.stringify(formData)
});

// PUT请求
await apiCall(`/api/admin/registrations/${id}/status`, {
  method: 'PUT',
  body: JSON.stringify({ status: 'APPROVED' })
});
```

### React Hooks示例

```javascript
// useAuth.js - 认证Hook
import { useState, useEffect } from 'react';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('userInfo');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
  }, []);
  
  const login = async (phone, name, title, role) => {
    const response = await fetch('http://localhost:6031/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, name, title, role })
    });
    
    const { data } = await response.json();
    localStorage.setItem('token', data.token);
    localStorage.setItem('userInfo', JSON.stringify(data));
    setToken(data.token);
    setUser(data);
    return data;
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    setToken(null);
    setUser(null);
  };
  
  return { user, token, login, logout };
}

// 使用
function App() {
  const { user, login, logout } = useAuth();
  
  if (!user) {
    return <LoginPage onLogin={login} />;
  }
  
  return (
    <div>
      <Header user={user} onLogout={logout} />
      <MainContent role={user.role} />
    </div>
  );
}
```

### Vue Composition API示例

```javascript
// useAuth.js - 认证Composable
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export function useAuth() {
  const user = ref(null);
  const token = ref(null);
  const router = useRouter();
  
  onMounted(() => {
    const savedToken = localStorage.getItem('token');
    const savedUser = localStorage.getItem('userInfo');
    if (savedToken && savedUser) {
      token.value = savedToken;
      user.value = JSON.parse(savedUser);
    }
  });
  
  const login = async (phone, name, title, role) => {
    const response = await fetch('http://localhost:6031/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, name, title, role })
    });
    
    const { data } = await response.json();
    localStorage.setItem('token', data.token);
    localStorage.setItem('userInfo', JSON.stringify(data));
    token.value = data.token;
    user.value = data;
    return data;
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    token.value = null;
    user.value = null;
    router.push('/login');
  };
  
  return { user, token, login, logout };
}
```

---

## 📊 当前测试数据

- **机构数量:** 33个（浙江省各医院）
- **赛事数量:** 6个
- **评委数量:** 16个
  - 医疗背景：2人
  - 未设置背景：14人
  - 初审分组：A1(7人)、B1(1人)、B2(6人)
- **报名数量:** 根据赛事阶段变化

### 测试账号

```javascript
// 组委会
{ phone: '13800000009', name: 'Committee', title: '组委会', role: 'COMMITTEE' }

// 参赛者
{ phone: '13800000001', name: 'Contestant', title: 'Doctor', role: 'CONTESTANT' }

// 评委
{ phone: '13800000021', name: 'Reviewer A', title: 'Expert', role: 'REVIEWER' }

// 运维
{ phone: '13800000051', name: 'OPS', title: 'Admin', role: 'OPS' }
```

---

## 🐛 常见问题

### Q1: 401 Unauthorized

**原因:** Token过期或未携带  
**解决:** 
```javascript
// 检查token是否存在
const token = localStorage.getItem('token');
if (!token) {
  // 跳转登录
  window.location.href = '/login';
}

// 检查请求头
headers: {
  'Authorization': `Bearer ${token}`  // 注意Bearer和token之间有空格
}
```

### Q2: 403 Forbidden

**原因:** 角色权限不足  
**解决:** 检查用户角色是否匹配接口要求
```javascript
// 检查用户角色
const user = JSON.parse(localStorage.getItem('userInfo'));
if (user.role !== 'COMMITTEE') {
  alert('您没有权限访问此功能');
}
```

### Q3: 报名提交失败

**原因:** 必填字段缺失  
**解决:** 
```javascript
// 提交前验证
const required = [
  'competitionId', 'institutionId', 'projectName',
  'contactPerson', 'contactPhone', 'participantNames',
  'activityType', 'activityBackground', 'activityObjective',
  'activityProcess', 'activityResult', 'projectSummary'
];

for (const field of required) {
  if (!formData[field]) {
    alert(`请填写${field}`);
    return;
  }
}
```

---

## 📚 完整文档链接

1. **API开发指引文档.md** - 完整的API列表和参数说明
2. **评委数据报告.md** - 评委池详细信息
3. **API示例数据.json** - 真实的返回数据示例
4. **Swagger文档** - http://localhost:6031/swagger （在线测试）

---

## ✅ 开发检查清单

- [ ] 登录功能（保存token到localStorage）
- [ ] 401自动跳转登录
- [ ] 根据角色显示不同菜单
- [ ] 报名表单（包含所有必填字段）
- [ ] 报名列表（我的报名/待审批）
- [ ] 审批功能（通过/驳回）
- [ ] 评委池展示（支持筛选）
- [ ] 任务分配界面
- [ ] 评审打分界面
- [ ] 进度查看页面
- [ ] 排名展示页面

---

**祝开发顺利！** 🎉

有问题随时查阅 `API开发指引文档.md` 或联系后端团队。
