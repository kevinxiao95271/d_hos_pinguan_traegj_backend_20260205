# 启动Spring Boot服务
Write-Host "正在启动服务..." -ForegroundColor Green

# 设置环境变量
$env:PINGUAN_DS1_URL="jdbc:mysql://gz-cdb-bq7gk3k5.sql.tencentcdb.com:63606/d_hos_pinguan_traegj_20260205?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai"
$env:PINGUAN_DS1_USER="root"
$env:PINGUAN_DS1_PASSWORD="Yiguo9527_"

Write-Host "环境变量已设置" -ForegroundColor Yellow
Write-Host "URL: $env:PINGUAN_DS1_URL" -ForegroundColor Cyan
Write-Host "USER: $env:PINGUAN_DS1_USER" -ForegroundColor Cyan

# 启动服务
mvn spring-boot:run
