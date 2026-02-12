# Swagger登录使用指引

## 访问地址

```
http://localhost:6031/swagger-ui/index.html
```

## 登录步骤

### 1. 找到登录接口

在Swagger页面中找到 **认证** 分组，展开 `POST /api/auth/login` 接口

### 2. 点击 "Try it out"

点击右侧的 "Try it out" 按钮，使请求体变为可编辑状态

### 3. 填写请求参数

根据不同角色填写以下参数：

#### 管理员账号（COMMITTEE_ADMIN）
```json
{
  "phone": "13800000041",
  "name": "CommitteeAdmin A",
  "role": "COMMITTEE_ADMIN"
}
```

#### 参赛者账号（CONTESTANT）
```json
{
  "phone": "13900000001",
  "name": "张三",
  "title": "主治医师",
  "role": "CONTESTANT",
  "institutionId": 1
}
```

#### 评审专家账号（REVIEWER）
```json
{
  "phone": "13800000006",
  "name": "李明华",
  "title": "主任医师",
  "role": "REVIEWER",
  "institutionId": 2,
  "expertBackground": "MEDICAL"
}
```

### 4. 执行请求

点击 "Execute" 按钮

### 5. 获取Token

从响应中复制token值：

```json
{
  "success": true,
  "data": {
    "id": 4,
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "title": null,
    "role": "COMMITTEE_ADMIN",
    "institutionId": null,
    "institutionName": null,
    "institutionCode": null,
    "institutionUscc": null,
    "expertBackground": null,
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Iiwicm9sZSI6IkNPTU1JVFRFRV9BRE1JTiIsImlhdCI6MTc3MDgxNjMxMSwiZXhwIjoxNzcwOTAyNzExfQ.CDSHKPUSrNtA_26GKhudDiVXmaq5C2PZr3O9hMUuZTc"
  },
  "message": null
}
```

复制 `data.token` 的值

### 6. 设置Authorization

在Swagger页面顶部找到 "Authorize" 按钮（锁图标），点击它

在弹出的对话框中：
- 找到 "BearerAuth (http, Bearer)" 部分
- 在 "Value" 输入框中输入：`Bearer <你的token>`
- 例如：`Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Iiwicm9sZSI6IkNPTU1JVFRFRV9BRE1JTiIsImlhdCI6MTc3MDgxNjMxMSwiZXhwIjoxNzcwOTAyNzExfQ.CDSHKPUSrNtA_26GKhudDiVXmaq5C2PZr3O9hMUuZTc`
- 点击 "Authorize" 按钮
- 点击 "Close" 关闭对话框

### 7. 测试其他接口

现在你可以测试任何需要认证的接口了，token会自动添加到请求头中

## 快速测试脚本

如果Swagger不好用，可以用这个Python脚本快速测试：

```python
import requests
import json

BASE_URL = "http://localhost:6031"

# 1. 登录
login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
})

print("登录响应:")
print(json.dumps(login_response.json(), ensure_ascii=False, indent=2))

# 2. 获取token
token = login_response.json()['data']['token']
print(f"\nToken: {token[:50]}...")

# 3. 使用token调用其他接口
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 示例：查询评审任务
tasks_response = requests.get(
    f"{BASE_URL}/api/admin/reviews/tasks",
    params={"competitionId": 21, "stage": "BOOK"},
    headers=headers
)

print("\n评审任务响应:")
print(json.dumps(tasks_response.json(), ensure_ascii=False, indent=2))
```

## 常见问题

### Q1: 为什么登录后还是401未授权？

A: 检查以下几点：
1. Token是否正确复制（不要有多余空格）
2. Authorization格式是否正确（必须是 `Bearer <token>`，注意Bearer后有空格）
3. Token是否过期（默认24小时有效期）

### Q2: 登录接口返回400错误？

A: 检查请求参数：
- `phone`: 必填，手机号格式
- `name`: 必填，姓名
- `role`: 必填，必须是以下之一：
  - `CONTESTANT` - 参赛者
  - `REVIEWER` - 评审专家
  - `COMMITTEE_ADMIN` - 管理员
  - `ADMIN` - 系统管理员

### Q3: 如何退出登录？

A: 前端删除保存的token即可。后端是无状态的JWT认证，不需要调用退出接口。

### Q4: Token有效期多久？

A: 默认24小时。过期后需要重新登录获取新token。

## 测试账号列表

### 管理员账号
```
手机: 13800000041
姓名: CommitteeAdmin A
角色: COMMITTEE_ADMIN
```

### 评审专家账号
```
手机: 13800000006
姓名: 李明华
角色: REVIEWER
机构ID: 2
专业背景: MEDICAL
```

```
手机: 13800000017
姓名: 孙丽娟
角色: REVIEWER
机构ID: 3
专业背景: MEDICAL
```

### 参赛者账号
根据需要创建，需要提供：
- phone: 手机号
- name: 姓名
- title: 职称（可选）
- role: CONTESTANT
- institutionId: 机构ID

## 完整的curl命令示例

### 登录
```bash
curl -X POST "http://localhost:6031/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800000041",
    "name": "CommitteeAdmin A",
    "role": "COMMITTEE_ADMIN"
  }'
```

### 使用Token调用接口
```bash
curl -X GET "http://localhost:6031/api/admin/reviews/tasks?competitionId=21&stage=BOOK" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Iiwicm9sZSI6IkNPTU1JVFRFRV9BRE1JTiIsImlhdCI6MTc3MDgxNjMxMSwiZXhwIjoxNzcwOTAyNzExfQ.CDSHKPUSrNtA_26GKhudDiVXmaq5C2PZr3O9hMUuZTc"
```

## 注意事项

1. **Token安全**: 不要在公共场合分享你的token
2. **HTTPS**: 生产环境必须使用HTTPS传输token
3. **过期处理**: 前端应该处理token过期的情况，提示用户重新登录
4. **角色权限**: 不同角色有不同的接口访问权限，使用正确的角色登录

## 相关文档

- [已分配任务API使用指引](./已分配任务API使用指引.md)
- [评审专家API变更-前端对接清单](./评审专家API变更-前端对接清单.md)
