# 安全配置说明

## 重要提示

本项目的敏感配置文件已从git仓库中移除，请按以下步骤配置：

## 1. 配置应用程序

复制配置文件模板：
```bash
cp src/main/resources/application.yml.example src/main/resources/application.yml
```

编辑 `application.yml` 填入真实的数据库连接信息。

## 2. 配置Python脚本

### 方式1：使用环境变量（推荐）

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件填入真实信息，然后在运行脚本前加载：

**Windows PowerShell:**
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
```

**Linux/Mac:**
```bash
export $(cat .env | xargs)
```

### 方式2：使用配置文件

复制配置文件模板：
```bash
cp scripts/db_config.example.py scripts/db_config.py
```

编辑 `scripts/db_config.py` 填入真实信息。

## 3. 已忽略的敏感文件

以下文件已添加到 `.gitignore`，不会被提交到git：

- `.env`
- `scripts/db_config.py`
- `src/main/resources/application.yml`

## 4. 注意事项

- ⚠️ 永远不要将包含真实密码的文件提交到git
- ⚠️ 不要在代码中硬编码密码
- ⚠️ 使用环境变量或配置文件管理敏感信息
- ⚠️ 定期更换密码

## 5. 如果已经提交了敏感信息

如果不小心提交了敏感信息到git，需要：

1. 立即更改密码
2. 使用 `git filter-repo` 或 `BFG Repo-Cleaner` 清理git历史
3. 强制推送到远程仓库

```bash
# 使用 BFG Repo-Cleaner（推荐）
bfg --replace-text passwords.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```
