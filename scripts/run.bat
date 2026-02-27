@echo off
echo Starting Spring Boot Service...
echo.

set PINGUAN_DS1_URL=jdbc:mysql://gz-cdb-bq7gk3k5.sql.tencentcdb.com:63606/d_hos_pinguan_traegj_20260205?useUnicode=true^&characterEncoding=UTF-8^&serverTimezone=Asia/Shanghai
set PINGUAN_DS1_USER=root
set PINGUAN_DS1_PASSWORD=Yiguo9527_

echo Environment variables set:
echo URL: %PINGUAN_DS1_URL%
echo USER: %PINGUAN_DS1_USER%
echo.

mvn spring-boot:run
