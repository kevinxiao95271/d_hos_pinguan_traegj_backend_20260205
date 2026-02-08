# 测试服务是否正常运行

Write-Host "=== 品管大赛评审系统 - 服务测试 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 测试健康检查
Write-Host "1. 测试健康检查..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:6031/actuator/health" -Method Get
    Write-Host "   ✓ 健康状态: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 健康检查失败: $_" -ForegroundColor Red
}

# 2. 测试 Swagger UI
Write-Host ""
Write-Host "2. 测试 Swagger UI..." -ForegroundColor Yellow
try {
    $swagger = Invoke-WebRequest -Uri "http://localhost:6031/swagger" -Method Get
    if ($swagger.StatusCode -eq 200) {
        Write-Host "   ✓ Swagger UI 可访问 (HTTP $($swagger.StatusCode))" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Swagger UI 访问失败: $_" -ForegroundColor Red
}

# 3. 测试 OpenAPI 文档
Write-Host ""
Write-Host "3. 测试 OpenAPI 文档..." -ForegroundColor Yellow
try {
    $apiDocs = Invoke-RestMethod -Uri "http://localhost:6031/v3/api-docs" -Method Get
    Write-Host "   ✓ OpenAPI 版本: $($apiDocs.openapi)" -ForegroundColor Green
    Write-Host "   ✓ API 标题: $($apiDocs.info.title)" -ForegroundColor Green
    Write-Host "   ✓ API 版本: $($apiDocs.info.version)" -ForegroundColor Green
    
    # 统计 API 端点数量
    $pathCount = ($apiDocs.paths | Get-Member -MemberType NoteProperty).Count
    Write-Host "   ✓ API 端点数量: $pathCount" -ForegroundColor Green
} catch {
    Write-Host "   ✗ OpenAPI 文档获取失败: $_" -ForegroundColor Red
}

# 4. 测试认证端点（不需要 token）
Write-Host ""
Write-Host "4. 测试登录接口..." -ForegroundColor Yellow
try {
    $loginBody = @{
        phone = "13800000021"
        password = "123456"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:6031/api/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    if ($response.success) {
        Write-Host "   ✓ 登录成功" -ForegroundColor Green
        Write-Host "   ✓ 用户: $($response.data.name)" -ForegroundColor Green
        Write-Host "   ✓ 角色: $($response.data.role)" -ForegroundColor Green
        Write-Host "   ✓ Token 已生成" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ 登录测试失败: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== 测试完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Yellow
Write-Host "  - Swagger UI: http://localhost:6031/swagger" -ForegroundColor White
Write-Host "  - 健康检查: http://localhost:6031/actuator/health" -ForegroundColor White
Write-Host "  - API 文档: http://localhost:6031/v3/api-docs" -ForegroundColor White
