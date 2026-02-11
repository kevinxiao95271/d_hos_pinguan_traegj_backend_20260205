# PostgreSQL迁移执行清单

## 目标信息

**源数据库**: MySQL 8.0
- 主机: gz-cdb-bq7gk3k5.sql.tencentcdb.com:63606
- 数据库: d_hos_pinguan_traegj_20260205
- 用户: root

**目标数据库**: PostgreSQL
- 主机: 119.167.165.27:5432
- 数据库: zjylzl
- Schema: zjylzl
- 用户: postgres
- 密码: zjylzl

---

## 迁移步骤清单

### 阶段1: 准备工作 (预计10分钟)

- [ ] 1.1 测试PostgreSQL连接
- [ ] 1.2 检查PostgreSQL版本和权限
- [ ] 1.3 创建Schema（如果不存在）
- [ ] 1.4 统计MySQL数据量
- [ ] 1.5 检查表结构和索引

### 阶段2: 数据导出 (预计5分钟)

- [ ] 2.1 导出MySQL表结构
- [ ] 2.2 导出MySQL数据（SQL格式）
- [ ] 2.3 验证导出文件完整性
- [ ] 2.4 统计导出数据量

### 阶段3: 结构转换 (预计10分钟)

- [ ] 3.1 转换数据类型
  - INT → INTEGER
  - BIGINT → BIGINT
  - VARCHAR → VARCHAR
  - TEXT → TEXT
  - DATETIME → TIMESTAMP
  - DECIMAL → NUMERIC
  - TINYINT → SMALLINT
  - ENUM → VARCHAR + CHECK约束

- [ ] 3.2 转换AUTO_INCREMENT → SERIAL
- [ ] 3.3 转换索引语法
- [ ] 3.4 转换外键约束
- [ ] 3.5 处理字符集（UTF8MB4 → UTF8）

### 阶段4: 数据导入 (预计10分钟)

- [ ] 4.1 创建PostgreSQL表结构
- [ ] 4.2 禁用约束和触发器
- [ ] 4.3 导入数据
- [ ] 4.4 启用约束和触发器
- [ ] 4.5 重建索引

### 阶段5: 数据验证 (预计10分钟)

- [ ] 5.1 验证表数量
- [ ] 5.2 验证每个表的记录数
- [ ] 5.3 验证关键字段数据
- [ ] 5.4 验证外键关系
- [ ] 5.5 验证索引

### 阶段6: 应用配置 (预计5分钟)

- [ ] 6.1 修改application.yml
  - 更改数据库驱动
  - 更改连接URL
  - 更改方言配置
- [ ] 6.2 添加PostgreSQL依赖（pom.xml）
- [ ] 6.3 更新JPA配置

### 阶段7: 测试验证 (预计15分钟)

- [ ] 7.1 编译应用
- [ ] 7.2 启动应用
- [ ] 7.3 测试登录功能
- [ ] 7.4 测试CRUD操作
- [ ] 7.5 测试统计查询
- [ ] 7.6 测试评分功能

### 阶段8: 性能优化 (预计10分钟)

- [ ] 8.1 分析查询计划
- [ ] 8.2 优化索引
- [ ] 8.3 更新统计信息
- [ ] 8.4 配置连接池

---

## 数据类型映射表

| MySQL类型 | PostgreSQL类型 | 说明 |
|-----------|---------------|------|
| INT | INTEGER | 4字节整数 |
| BIGINT | BIGINT | 8字节整数 |
| TINYINT | SMALLINT | 2字节整数 |
| VARCHAR(n) | VARCHAR(n) | 变长字符串 |
| TEXT | TEXT | 长文本 |
| DATETIME | TIMESTAMP | 时间戳 |
| DECIMAL(m,n) | NUMERIC(m,n) | 精确小数 |
| ENUM | VARCHAR + CHECK | 枚举类型 |
| BOOLEAN | BOOLEAN | 布尔值 |

---

## 关键配置变更

### pom.xml
```xml
<!-- 移除MySQL驱动 -->
<!-- <dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
</dependency> -->

<!-- 添加PostgreSQL驱动 -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

### application.yml
```yaml
spring:
  datasource:
    driver-class-name: org.postgresql.Driver
    url: jdbc:postgresql://119.167.165.27:5432/zjylzl?currentSchema=zjylzl
    username: postgres
    password: zjylzl
  jpa:
    database-platform: org.hibernate.dialect.PostgreSQLDialect
    properties:
      hibernate:
        default_schema: zjylzl
```

---

## 风险评估

### 高风险项
- ❌ 无 - 使用JPA抽象层，兼容性好

### 中风险项
- ⚠️ ENUM类型转换 - 需要改为VARCHAR + CHECK约束
- ⚠️ 自增ID - 需要使用SERIAL或SEQUENCE
- ⚠️ 日期时间函数 - 可能需要调整

### 低风险项
- ✅ 基本数据类型 - 完全兼容
- ✅ 外键约束 - 完全兼容
- ✅ 索引 - 完全兼容

---

## 回滚方案

### 如果迁移失败
1. 保留MySQL数据库不变
2. 恢复application.yml配置
3. 重新编译部署
4. 验证MySQL连接正常

### 备份策略
- MySQL数据库保持不变
- PostgreSQL可以重新导入
- 配置文件使用Git版本控制

---

## 预计时间

| 阶段 | 预计时间 |
|------|---------|
| 准备工作 | 10分钟 |
| 数据导出 | 5分钟 |
| 结构转换 | 10分钟 |
| 数据导入 | 10分钟 |
| 数据验证 | 10分钟 |
| 应用配置 | 5分钟 |
| 测试验证 | 15分钟 |
| 性能优化 | 10分钟 |
| **总计** | **75分钟** |

---

## 执行前确认

- [ ] MySQL数据库已备份
- [ ] PostgreSQL连接信息已确认
- [ ] 应用代码已提交Git
- [ ] 有足够时间完成迁移（至少2小时）
- [ ] 已通知相关人员

---

## 工具准备

### 需要的工具
- Python 3.x
- pymysql库
- psycopg2库
- pgloader（可选，用于快速迁移）

### 安装命令
```bash
pip install pymysql psycopg2-binary
```

---

**创建时间**: 2026-02-10  
**创建人**: Kiro AI  
**状态**: 待执行
