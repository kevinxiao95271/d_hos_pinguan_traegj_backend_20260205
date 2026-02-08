# 历史数据查询API文档

## 概述

历史数据查询接口用于查询 `pinguan_his_data` 表中的历史参赛数据。该接口是独立功能，不与其他业务表关联。

## 权限要求

**仅限以下角色访问：**
- `COMMITTEE_ADMIN` - 组委会管理员
- `OPS` - 系统运维

其他角色（如 REVIEWER、CONTESTANT 等）无权访问此接口。

## 接口信息

### 基本信息

- **接口路径**: `/api/historical-data`
- **请求方法**: `GET`
- **认证方式**: Bearer Token (JWT)
- **返回格式**: JSON

### 请求头

```
Authorization: Bearer {token}
```

## 请求参数

所有参数均为可选，支持组合查询。

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| region | String | 否 | 地区关键词（从机构地址中模糊匹配） | 杭州 |
| competitionGroup | String | 否 | 组别（精确匹配） | 综合组 |
| circleName | String | 否 | 品管工具/圈名（模糊匹配） | 肾利圈 |
| dataStatus | String | 否 | 入围状态（精确匹配） | 已提交 |
| institutionName | String | 否 | 医院名称（模糊匹配） | 人民医院 |
| projectName | String | 否 | 项目名称（模糊匹配） | 提高 |
| year | String | 否 | 年份 | 2025 |
| page | Integer | 否 | 页码（从0开始） | 0 |
| size | Integer | 否 | 每页大小 | 20 |
| sortBy | String | 否 | 排序字段 | id |
| sortDirection | String | 否 | 排序方向（ASC/DESC） | DESC |

### 默认值

- `page`: 0
- `size`: 20
- `sortBy`: id
- `sortDirection`: DESC

## 响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": 1,
        "dataStatus": "已提交",
        "inputPerson": "刘海燕",
        "inputDate": "2025-02-20",
        "year": "2025",
        "groupName": "C10",
        "projectCode": "20250001",
        "competitionGroup": "基层组(基层组积分方式同综合组)",
        "projectName": "万物生磷 磷危不惧 三位一体联动提高腹膜透析患者血磷达标率",
        "institutionName": "龙泉市人民医院",
        "institutionLevel": "二甲",
        "institutionAddress": "龙泉市东茶路699号",
        "totalBeds": "900张",
        "hospitalContactName": "邱吉凤",
        "hospitalContactTitle": "主任医师",
        "hospitalContactPhone": "13506825221",
        "hospitalContactEmail": "372535918@qq.com",
        "projectLeaderName": "刘海燕",
        "projectLeaderTitle": "主管护师",
        "projectLeaderPhone": "13735936552",
        "projectLeaderEmail": "zi.601@qq.com",
        "circleName": "肾利圈"
      }
    ],
    "pageable": {
      "sort": {
        "sorted": true,
        "unsorted": false,
        "empty": false
      },
      "pageNumber": 0,
      "pageSize": 20,
      "offset": 0,
      "paged": true,
      "unpaged": false
    },
    "totalPages": 91,
    "totalElements": 1818,
    "last": false,
    "number": 0,
    "sort": {
      "sorted": true,
      "unsorted": false,
      "empty": false
    },
    "size": 20,
    "numberOfElements": 20,
    "first": true,
    "empty": false
  },
  "message": null
}
```

### 权限不足响应

```json
{
  "success": false,
  "data": null,
  "message": "无权访问历史数据，仅限组委会管理员和系统运维"
}
```

## 使用示例

### 1. 基本查询（第一页，每页10条）

```bash
GET /api/historical-data?page=0&size=10
```

### 2. 按地区筛选

```bash
GET /api/historical-data?region=杭州&page=0&size=20
```

### 3. 按组别筛选

```bash
GET /api/historical-data?competitionGroup=综合组&page=0&size=20
```

### 4. 按医院筛选

```bash
GET /api/historical-data?institutionName=人民医院&page=0&size=20
```

### 5. 组合筛选

```bash
GET /api/historical-data?competitionGroup=综合组&region=杭州&page=0&size=20
```

### 6. 自定义排序

```bash
GET /api/historical-data?sortBy=projectCode&sortDirection=ASC&page=0&size=20
```

## Python 示例代码

```python
import requests

# 1. 登录获取 token
login_url = "http://localhost:6031/api/auth/login"
login_data = {
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
}
response = requests.post(login_url, json=login_data)
token = response.json()['data']['token']

# 2. 查询历史数据
api_url = "http://localhost:6031/api/historical-data"
headers = {"Authorization": f"Bearer {token}"}
params = {
    "region": "杭州",
    "competitionGroup": "综合组",
    "page": 0,
    "size": 20
}
response = requests.get(api_url, headers=headers, params=params)
result = response.json()

if result['success']:
    data = result['data']
    print(f"总记录数: {data['totalElements']}")
    print(f"总页数: {data['totalPages']}")
    for item in data['content']:
        print(f"- {item['institutionName']}: {item['projectName']}")
```

## JavaScript 示例代码

```javascript
// 1. 登录获取 token
const loginResponse = await fetch('http://localhost:6031/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '13800000041',
    name: 'CommitteeAdmin A',
    role: 'COMMITTEE_ADMIN'
  })
});
const loginData = await loginResponse.json();
const token = loginData.data.token;

// 2. 查询历史数据
const params = new URLSearchParams({
  region: '杭州',
  competitionGroup: '综合组',
  page: 0,
  size: 20
});

const response = await fetch(`http://localhost:6031/api/historical-data?${params}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const result = await response.json();

if (result.success) {
  console.log(`总记录数: ${result.data.totalElements}`);
  console.log(`总页数: ${result.data.totalPages}`);
  result.data.content.forEach(item => {
    console.log(`- ${item.institutionName}: ${item.projectName}`);
  });
}
```

## 数据字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 记录ID |
| dataStatus | String | 数据状态（如：已提交、已保存） |
| inputPerson | String | 录入人 |
| inputDate | String | 录入日期 |
| year | String | 年份 |
| groupName | String | 组名 |
| projectCode | String | 项目编号 |
| competitionGroup | String | 竞赛组别 |
| projectName | String | 项目名称 |
| institutionName | String | 机构名称 |
| institutionLevel | String | 机构级别 |
| institutionAddress | String | 机构地址 |
| totalBeds | String | 床位数 |
| hospitalContactName | String | 医院联系人姓名 |
| hospitalContactTitle | String | 医院联系人职称 |
| hospitalContactPhone | String | 医院联系人电话 |
| hospitalContactEmail | String | 医院联系人邮箱 |
| projectLeaderName | String | 项目负责人姓名 |
| projectLeaderTitle | String | 项目负责人职称 |
| projectLeaderPhone | String | 项目负责人电话 |
| projectLeaderEmail | String | 项目负责人邮箱 |
| circleName | String | 圈名 |

## 测试账号

### 组委会管理员（有权限）
- 手机号: 13800000041
- 姓名: CommitteeAdmin A
- 角色: COMMITTEE_ADMIN

### 评委（无权限）
- 手机号: 13800000021
- 姓名: 李明华
- 角色: REVIEWER

## 注意事项

1. **权限控制**: 只有 COMMITTEE_ADMIN 和 OPS 角色可以访问此接口
2. **独立功能**: 此接口不与其他业务表关联，数据来源于独立的 `pinguan_his_data` 表
3. **分页**: 建议使用分页查询，避免一次性加载过多数据
4. **模糊查询**: region、circleName、institutionName、projectName 支持模糊匹配
5. **精确查询**: competitionGroup、dataStatus、year 为精确匹配
6. **排序**: 可按任意字段排序，默认按 id 降序

## Swagger 文档

访问 http://localhost:6031/swagger 查看完整的 API 文档和在线测试。

## 统计信息

- 总记录数: 1818 条
- 主要组别: 综合组(1249条)、基层组(569条)
- 主要地区: 杭州(363条)、温州、宁波等
- 数据年份: 2024-2025

## 更新日志

### 2026-02-08
- ✅ 创建历史数据查询接口
- ✅ 实现多条件筛选功能
- ✅ 实现分页和排序
- ✅ 添加权限控制（仅限 COMMITTEE_ADMIN 和 OPS）
- ✅ 完成接口测试
