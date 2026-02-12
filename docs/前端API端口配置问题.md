# 前端API端口配置问题

## 问题描述

前端调用评分接口时出现500错误：
```
:6039/api/reviews/scores:1  Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

## 问题根源

**端口不匹配**：
- 前端配置的API端口：`6039`
- 后端实际运行端口：`6031`

## 解决方案

### 方案1: 修改前端配置（推荐）

修改前端项目中的API基础URL配置，将端口从6039改为6031。

通常在以下文件中：
- `.env` 或 `.env.development`
- `src/config/api.js` 或类似配置文件
- `src/utils/request.js` 中的baseURL

**修改示例**：
```javascript
// 修改前
const BASE_URL = 'http://localhost:6039'

// 修改后
const BASE_URL = 'http://localhost:6031'
```

或者在`.env`文件中：
```
# 修改前
VITE_API_BASE_URL=http://localhost:6039

# 修改后
VITE_API_BASE_URL=http://localhost:6031
```

### 方案2: 修改后端端口

如果必须使用6039端口，修改后端配置：

**文件**: `src/main/resources/application.properties` 或 `application.yml`

```properties
# 修改前
server.port=6031

# 修改后
server.port=6039
```

然后重启后端服务。

## 验证步骤

### 1. 确认后端端口
```bash
# 查看后端运行端口
curl http://localhost:6031/swagger-ui/index.html
```

如果返回200，说明后端运行在6031端口。

### 2. 测试API接口
```bash
# 测试登录接口
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000041","name":"CommitteeAdmin A","role":"COMMITTEE_ADMIN"}'
```

### 3. 测试评分接口
```bash
# 先登录获取token
TOKEN="<你的token>"

# 测试评分接口（需要有效的reviewTaskId）
curl -X POST http://localhost:6031/api/reviews/scores \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "reviewTaskId": 115,
    "plan": 10.0,
    "problem": 10.0,
    "action": 10.0,
    "success": 10.0,
    "review": 10.0,
    "operation": 10.0,
    "presentation": 10.0,
    "highlight": "亮点",
    "weakness": "不足"
  }'
```

## 当前配置

### 后端配置
- 运行端口：`6031`
- Swagger地址：`http://localhost:6031/swagger-ui/index.html`
- API基础路径：`http://localhost:6031/api`

### 前端需要配置
- API基础URL：`http://localhost:6031`
- 或使用环境变量：`VITE_API_BASE_URL=http://localhost:6031`

## 常见问题

### Q1: 如何查看前端当前配置的API地址？

A: 在浏览器开发者工具的Network标签中查看请求的完整URL。

### Q2: 修改前端配置后需要重启吗？

A: 是的，修改环境变量或配置文件后需要重启前端开发服务器。

### Q3: 为什么会出现端口不匹配？

A: 可能原因：
1. 前端配置文件中硬编码了旧端口
2. 环境变量未更新
3. 后端端口被修改但前端未同步

### Q4: 如何避免这个问题？

A: 建议：
1. 使用环境变量管理API地址
2. 在README中明确说明端口配置
3. 前后端开发人员保持沟通

## 相关文档

- [登录接口测试报告](./登录接口测试报告.md)
- [Swagger快速登录指南](./Swagger快速登录指南.md)
- [已分配任务API使用指引](./已分配任务API使用指引.md)

## 测试脚本

创建一个测试脚本验证评分接口：

```python
#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:6031"  # 确保使用正确的端口

# 1. 登录
login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "phone": "13800000006",
    "name": "李明华",
    "role": "REVIEWER",
    "institutionId": 2,
    "expertBackground": "MEDICAL"
})

token = login_response.json()['data']['token']
headers = {"Authorization": f"Bearer {token}"}

# 2. 提交评分
score_data = {
    "reviewTaskId": 115,
    "plan": 10.0,
    "problem": 10.0,
    "action": 10.0,
    "success": 10.0,
    "review": 10.0,
    "operation": 10.0,
    "presentation": 10.0,
    "highlight": "项目计划清晰",
    "weakness": "数据分析不够深入"
}

score_response = requests.post(
    f"{BASE_URL}/api/reviews/scores",
    json=score_data,
    headers=headers
)

print(f"状态码: {score_response.status_code}")
print(f"响应: {json.dumps(score_response.json(), ensure_ascii=False, indent=2)}")
```

## 总结

问题的根本原因是前端配置的API端口（6039）与后端实际运行端口（6031）不匹配。

**推荐解决方案**：修改前端配置，将API基础URL改为 `http://localhost:6031`
