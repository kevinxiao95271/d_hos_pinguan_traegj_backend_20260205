================================================================================
                    服务重启与自测验证 - 快速指南
================================================================================

当前状态: ✅ 代码修改完成，需要配置数据库后启动验证

================================================================================
  问题诊断
================================================================================

启动失败原因: 环境变量未设置
错误: Driver com.mysql.cj.jdbc.Driver claims to not accept jdbcUrl, ${PINGUAN_DS1_URL}

================================================================================
  解决方案（3选1）
================================================================================

【方案1：设置环境变量】（推荐）

PowerShell命令:
$env:PINGUAN_DS1_URL='jdbc:mysql://gz-cdb-bq7gk3k5.sql.tencentcdb.com:63606/d_hos_pinguan_traegj_20260205'
$env:PINGUAN_DS1_USERNAME='root'
$env:PINGUAN_DS1_PASSWORD='Yiguo9527_'

然后启动:
mvn spring-boot:run

【方案2：修改配置文件】

编辑 src/main/resources/application.yml

app:
  datasource:
    active: ds1
    ds1:
      url: jdbc:mysql://gz-cdb-bq7gk3k5.sql.tencentcdb.com:63606/d_hos_pinguan_traegj_20260205
      username: root
      password: Yiguo9527_
      driver-class-name: com.mysql.cj.jdbc.Driver

【方案3：IDE配置】

IDEA: Run -> Edit Configurations -> Environment variables
添加: PINGUAN_DS1_URL, PINGUAN_DS1_USERNAME, PINGUAN_DS1_PASSWORD

================================================================================
  启动步骤
================================================================================

1. 配置数据库（上述3个方案选1个）
2. 启动服务: mvn spring-boot:run
3. 等待看到: Started PinguanBackendApplication
4. 运行测试: python scripts/test_all_institution_level_apis.py

================================================================================
  本次完成的修改
================================================================================

✅ 14个文件修改
✅ 12个API添加机构等级字段
✅ 编译成功
✅ 测试脚本已准备

详细信息请查看: docs/服务重启与自测验证报告.md

================================================================================
