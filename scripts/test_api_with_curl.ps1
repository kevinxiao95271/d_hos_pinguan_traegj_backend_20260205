# 前端API测试脚本 - 使用真实项目ID 119
# 用于验证Label字段是否正确返回

Write-Host "================================================================================" -ForegroundColor White
Write-Host "前端API测试 - Label字段验证" -ForegroundColor White
Write-Host "================================================================================" -ForegroundColor White
Write-Host ""

$BASE_URL = "http://localhost:6031"
$PROJECT_ID = 119

Write-Host "步骤1: 登录评委账号" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------------------------------"
Write-Host "请求: POST $BASE_URL/api/auth/login"
Write-Host ""

$loginBody = @{
    phone = "13900000001"
    name = "李明华"
    role = "REVIEWER"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/api/auth/login" `
        -Method Post `
        -ContentType "application/json" `
        -Body $loginBody
    
    Write-Host ($loginResponse | ConvertTo-Json -Depth 10) -ForegroundColor Gray
    Write-Host ""
    
    $token = $loginResponse.data.token
    
    if ($token) {
        Write-Host "✅ 登录成功" -ForegroundColor Green
        Write-Host "Token: $($token.Substring(0, [Math]::Min(30, $token.Length)))..."
        Write-Host ""
    } else {
        Write-Host "❌ 登录失败，无法获取token" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ 登录请求失败: $_" -ForegroundColor Red
    exit 1
}

Write-Host "步骤2: 获取项目详情（项目ID: $PROJECT_ID）" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------------------------------"
Write-Host "请求: GET $BASE_URL/api/registrations/$PROJECT_ID"
Write-Host ""

try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $detailResponse = Invoke-RestMethod -Uri "$BASE_URL/api/registrations/$PROJECT_ID" `
        -Method Get `
        -Headers $headers
    
    Write-Host ($detailResponse | ConvertTo-Json -Depth 10) -ForegroundColor Gray
    Write-Host ""
    
    $activityInfo = $detailResponse.data.activityInfo
    
    Write-Host "================================================================================" -ForegroundColor White
    Write-Host "Label字段检查" -ForegroundColor White
    Write-Host "================================================================================" -ForegroundColor White
    Write-Host ""
    
    # 检查主题类型
    Write-Host "【主题类型】" -ForegroundColor Yellow
    if ($activityInfo.subjectTypeLabel) {
        Write-Host "  ✅ subjectTypeLabel: $($activityInfo.subjectTypeLabel)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ subjectTypeLabel: 缺失" -ForegroundColor Red
    }
    Write-Host ""
    
    # 检查运用手法
    Write-Host "【运用手法】" -ForegroundColor Yellow
    if ($activityInfo.methodLabel) {
        Write-Host "  ✅ methodLabel: $($activityInfo.methodLabel)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ methodLabel: 缺失" -ForegroundColor Red
    }
    Write-Host ""
    
    # 检查改善就医环境
    Write-Host "【改善就医环境】" -ForegroundColor Yellow
    if ($activityInfo.experienceImproveLabel) {
        Write-Host "  ✅ experienceImproveLabel: $($activityInfo.experienceImproveLabel)" -ForegroundColor Green
        Write-Host "  📝 前端应该显示: $($activityInfo.experienceImproveLabel)" -ForegroundColor Cyan
    } else {
        Write-Host "  ❌ experienceImproveLabel: 缺失" -ForegroundColor Red
    }
    Write-Host ""
    
    # 检查医疗质量相关主题
    Write-Host "【医疗质量相关主题】" -ForegroundColor Yellow
    if ($activityInfo.qualityTopicLabel) {
        Write-Host "  ✅ qualityTopicLabel: $($activityInfo.qualityTopicLabel)" -ForegroundColor Green
        Write-Host "  📝 前端应该显示: $($activityInfo.qualityTopicLabel)" -ForegroundColor Cyan
    } else {
        Write-Host "  ❌ qualityTopicLabel: 缺失" -ForegroundColor Red
    }
    Write-Host ""
    
    Write-Host "================================================================================" -ForegroundColor White
    Write-Host "前端代码示例" -ForegroundColor White
    Write-Host "================================================================================" -ForegroundColor White
    Write-Host ""
    
    Write-Host "❌ 错误的前端代码（会显示Code）:" -ForegroundColor Red
    Write-Host '```vue'
    Write-Host '<div>{{ activityInfo.experienceImproveCode }}</div>'
    Write-Host '<div>{{ activityInfo.qualityTopicCode }}</div>'
    Write-Host '```'
    Write-Host ""
    
    Write-Host "✅ 正确的前端代码（会显示Label）:" -ForegroundColor Green
    Write-Host '```vue'
    Write-Host '<div>{{ activityInfo.experienceImproveLabel || activityInfo.experienceImproveCode }}</div>'
    Write-Host '<div>{{ activityInfo.qualityTopicLabel || activityInfo.qualityTopicCode }}</div>'
    Write-Host '```'
    Write-Host ""
    
    Write-Host "================================================================================" -ForegroundColor White
    Write-Host "测试完成" -ForegroundColor White
    Write-Host "================================================================================" -ForegroundColor White
    
    if ($activityInfo.experienceImproveLabel -and $activityInfo.qualityTopicLabel) {
        Write-Host "✅ 后端API正确返回了所有Label字段" -ForegroundColor Green
        Write-Host "✅ 前端可以直接使用Label字段" -ForegroundColor Green
        Write-Host ""
        Write-Host "如果前端显示的是Code（如 experience_1），说明前端代码有问题！" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 部分Label字段缺失，请联系后端开发人员" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ 获取详情失败: $_" -ForegroundColor Red
    exit 1
}
