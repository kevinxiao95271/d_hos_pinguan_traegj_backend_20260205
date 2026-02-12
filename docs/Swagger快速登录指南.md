# Swagger快速登录指南

## 访问地址
```
http://localhost:6031/swagger-ui/index.html
```

## 登录步骤（图文说明）

### 步骤1: 找到登录接口
1. 打开Swagger页面
2. 找到 **"认证"** 分组
3. 点击展开 `POST /api/auth/login` 接口

### 步骤2: 点击Try it out
点击右侧的蓝色按钮 **"Try it out"**

### 步骤3: 填写登录信息

在Request body输入框中，填写以下JSON（管理员账号）：

```json
{
  "phone": "13800000041",
  "name": "CommitteeAdmin A",
  "role": "COMMITTEE_ADMIN"
}
```

### 步骤4: 执行登录
点击蓝色的 **"Execute"** 按钮

### 步骤5: 复制Token
在Response body中找到token字段，复制整个token值（很长的一串字符）

示例响应：
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Iiwicm9sZSI6IkNPTU1JVFRFRV9BRE1JTiIsImlhdCI6MTc3MDgxNjMxMSwiZXhwIjoxNzcwOTAyNzExfQ.CDSHKPUSrNtA_26GKhudDiVXmaq5C2PZr3O9hMUuZTc"
  }
}
```

复制 `data.token` 的完整值

### 步骤6: 设置Authorization
1. 滚动到页面顶部
2. 找到右上角的 **"Authorize"** 按钮（锁图标🔒）
3. 点击它

### 步骤7: 输入Token
在弹出的对话框中：
1. 找到 **"BearerAuth (http, Bearer)"** 部分
2. 在 **"Value"** 输入框中输入：
   ```
   Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0Iiwicm9sZSI6IkNPTU1JVFRFRV9BRE1JTiIsImlhdCI6MTc3MDgxNjMxMSwiZXhwIjoxNzcwOTAyNzExfQ.CDSHKPUSrNtA_26GKhudDiVXmaq5C2PZr3O9hMUuZTc
   ```
   **注意**: 必须以 `Bearer ` 开头（Bearer后面有一个空格）

3. 点击 **"Authorize"** 按钮
4. 点击 **"Close"** 关闭对话框

### 步骤8: 测试其他接口
现在你可以测试任何需要认证的接口了！

例如测试 `GET /api/admin/reviews/tasks`:
1. 找到该接口并展开
2. 点击 "Try it out"
3. 填写参数：
   - competitionId: 21
   - stage: BOOK
4. 点击 "Execute"
5. 查看返回结果

## 常用测试账号

### 管理员（推荐）
```json
{
  "phone": "13800000041",
  "name": "CommitteeAdmin A",
  "role": "COMMITTEE_ADMIN"
}
```
**权限**: 可以访问所有管理接口

### 评审专家
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
**权限**: 可以查看和评审分配给自己的任务

### 参赛者
```json
{
  "phone": "13900000001",
  "name": "张三",
  "title": "主治医师",
  "role": "CONTESTANT",
  "institutionId": 1
}
```
**权限**: 可以提交和管理自己的报名项目

## 常见问题

### ❌ 401 Unauthorized错误
**原因**: Token未设置或已过期

**解决方法**:
1. 确认已点击Authorize按钮设置Token
2. 确认Token格式正确（必须以`Bearer `开头）
3. 如果Token过期，重新登录获取新Token

### ❌ 400 Bad Request错误
**原因**: 请求参数格式错误

**解决方法**:
1. 检查JSON格式是否正确（注意逗号、引号）
2. 确认必填字段都已填写：
   - phone（必填）
   - name（必填）
   - role（必填，必须是CONTESTANT/REVIEWER/COMMITTEE_ADMIN/ADMIN之一）

### ❌ 500 Internal Server Error错误
**原因**: 服务器内部错误

**解决方法**:
1. 检查服务器是否正常运行
2. 查看服务器日志
3. 联系后端开发人员

## 快捷操作

### 快速复制管理员登录JSON
```json
{"phone":"13800000041","name":"CommitteeAdmin A","role":"COMMITTEE_ADMIN"}
```

### 快速复制Token格式
```
Bearer <你的token>
```

## 提示

1. **Token有效期**: 24小时，过期后需要重新登录
2. **多个Tab**: 如果在多个浏览器Tab中使用Swagger，每个Tab需要单独设置Authorization
3. **刷新页面**: 刷新页面后Authorization会丢失，需要重新设置
4. **复制Token**: 复制Token时注意不要包含引号和多余空格

## 视频教程

如果文字说明不够清楚，可以录制一个简短的操作视频：
1. 打开Swagger页面
2. 登录获取Token
3. 设置Authorization
4. 测试一个接口

## 相关文档

- [Swagger登录使用指引](./Swagger登录使用指引.md) - 详细版
- [已分配任务API使用指引](./已分配任务API使用指引.md)
- [评审专家API变更-前端对接清单](./评审专家API变更-前端对接清单.md)
