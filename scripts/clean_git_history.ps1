# 清理Git历史中的敏感信息
# 警告：这会重写Git历史，需要强制推送

Write-Host "警告：此操作将重写Git历史！" -ForegroundColor Red
Write-Host "建议先备份仓库" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "确认继续？(yes/no)"

if ($confirm -ne "yes") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit
}

Write-Host "开始清理..." -ForegroundColor Green

# 方法1：使用 git filter-branch（内置命令）
Write-Host "使用 git filter-branch 清理敏感文件..." -ForegroundColor Cyan

# 从历史中删除 application.yml
git filter-branch --force --index-filter `
  "git rm --cached --ignore-unmatch src/main/resources/application.yml" `
  --prune-empty --tag-name-filter cat -- --all

# 清理引用
git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host ""
Write-Host "清理完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 检查历史：git log --all --oneline" -ForegroundColor White
Write-Host "2. 强制推送：git push --force --all" -ForegroundColor White
Write-Host "3. 立即更改数据库密码！" -ForegroundColor Red
Write-Host ""
Write-Host "注意：所有协作者需要重新克隆仓库！" -ForegroundColor Red
