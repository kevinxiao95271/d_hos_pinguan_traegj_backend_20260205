# 重启应用脚本

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "步骤2: 重启应用" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan

# 查找应用进程
Write-Host "`n1. 查找应用进程..." -ForegroundColor White
$port = 6031
$process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
if ($process) {
    $pid = $process.OwningProcess
    Write-Host "✅ 找到应用进程 PID: $pid" -ForegroundColor Green
    
    # 停止进程
    Write-Host "`n2. 停止应用..." -ForegroundColor White
    Stop-Process -Id $pid -Force
    Start-Sleep -Seconds 3
    Write-Host "✅ 应用已停止" -ForegroundColor Green
} else {
    Write-Host "⚠️  未找到运行在端口 $port 的应用" -ForegroundColor Yellow
}

# 重新编译
Write-Host "`n3. 重新编译应用..." -ForegroundColor White
Write-Host "执行: mvn clean package -DskipTests" -ForegroundColor Gray
$compileResult = & mvn clean package -DskipTests 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 编译成功" -ForegroundColor Green
} else {
    Write-Host "❌ 编译失败" -ForegroundColor Red
    Write-Host $compileResult
    exit 1
}

# 启动应用
Write-Host "`n4. 启动应用..." -ForegroundColor White
$jarFile = Get-ChildItem -Path "target" -Filter "*.jar" -Exclude "*-sources.jar","*-javadoc.jar" | Select-Object -First 1

if ($jarFile) {
    Write-Host "找到JAR文件: $($jarFile.Name)" -ForegroundColor Gray
    Write-Host "启动应用..." -ForegroundColor Gray
    
    # 在后台启动应用
    Start-Process -FilePath "java" -ArgumentList "-jar", $jarFile.FullName -WindowStyle Hidden
    
    Write-Host "⏳ 等待应用启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # 检查应用是否启动
    $newProcess = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($newProcess) {
        Write-Host "✅ 应用启动成功！" -ForegroundColor Green
    } else {
        Write-Host "⚠️  应用可能还在启动中，请稍后检查" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ 未找到JAR文件" -ForegroundColor Red
    exit 1
}

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "✅ 应用重启完成！" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan

Write-Host "`n下一步: 运行测试脚本验证" -ForegroundColor Yellow
Write-Host "python step1_simple_check.py" -ForegroundColor Gray
