# 简单重启脚本

Write-Host "步骤2: 重启应用"
Write-Host "=" * 60

# 停止应用
Write-Host "`n1. 停止应用..."
$connections = Get-NetTCPConnection -LocalPort 6031 -ErrorAction SilentlyContinue
if ($connections) {
    $pid = $connections[0].OwningProcess
    Write-Host "找到进程 PID: $pid"
    Stop-Process -Id $pid -Force
    Start-Sleep -Seconds 3
    Write-Host "应用已停止"
}

# 编译
Write-Host "`n2. 编译应用..."
mvn clean package -DskipTests
if ($LASTEXITCODE -ne 0) {
    Write-Host "编译失败"
    exit 1
}
Write-Host "编译成功"

# 启动
Write-Host "`n3. 启动应用..."
$jar = Get-ChildItem -Path "target" -Filter "*.jar" -Exclude "*-sources.jar" | Select-Object -First 1
if ($jar) {
    Start-Process -FilePath "java" -ArgumentList "-jar", $jar.FullName -WindowStyle Hidden
    Write-Host "应用已启动，等待10秒..."
    Start-Sleep -Seconds 10
    Write-Host "完成"
}

Write-Host "`n下一步: python step1_simple_check.py"
