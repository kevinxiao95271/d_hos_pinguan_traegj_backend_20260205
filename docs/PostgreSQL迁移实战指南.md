# PostgreSQL 迁移实战指南

## 数据量确认

✅ **数据量非常小，迁移很快！**

- 总记录数：2,426 条
- 数据库大小：2.14 MB
- 最大表：pinguan_his_data (1,818条)
- 迁移时间：5-10分钟

## 方案选择

### 推荐：pgLoader（最简单）

**优点**：
- ✅ 一条命令搞定
- ✅ 自动转换所有语法
- ✅ 自动创建表结构
- ✅ 速度快（5-10分钟）

**缺点**：
- ❌ 需要安装pgLoader

### 备选：手动导出导入

**优点**：
- ✅ 不需要额外工具
- ✅ 可控性强

**缺点**：
- ❌ 需要手动处理SQL语法差异
- ❌ 稍微慢一点（10-15分钟）

---

## 方案1: 使用 pgLoader（推荐）

### 步骤1: 安装 pgLoader

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install pgloader

# CentOS/RHEL
sudo yum install pgloader

# macOS
brew install pgloader

# Docker（如果服务器没有安装）
docker pull dimitri/pgloader
```

### 步骤2: 准备PostgreSQL数据库

```bash
# 连接PostgreSQL
psql -h your-pg-host -U postgres

# 创建数据库
CREATE DATABASE d_hos_pinguan_traegj_20260205;

# 创建用户（如果需要）
CREATE USER pinguan_user WITH PASSWORD 'your_password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE d_hos_pinguan_traegj_20260205 TO pinguan_user;

# 退出
\q
```

### 步骤3: 执行迁移（一条命令）

```bash
pgloader \
  mysql://root:Yiguo9527_@gz-cdb-bq7gk3k5.sql.tencentcdb.com:63606/d_hos_pinguan_traegj_20260205 \
  postgresql://pinguan_user:your_password@your-pg-host:5432/d_hos_pinguan_traegj_20260205
```

**预计时间：5-10分钟**

### 步骤4: 验证数据

```bash
# 连接PostgreSQL
psql -h your-pg-host -U pinguan_user -d d_hos_pinguan_traegj_20260205

# 检查表数量
\dt

# 检查记录数
SELECT 
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

# 应该看到：
# pinguan_his_data: 1818
# registration_members: 187
# dictionary_items: 110
# 等等...
```

---

## 方案2: 手动导出导入

### 步骤1: 导出MySQL数据

```bash
mysqldump \
  -h gz-cdb-bq7gk3k5.sql.tencentcdb.com \
  -P 63606 \
  -u root \
  -pYiguo9527_ \
  --single-transaction \
  --skip-lock-tables \
  --no-tablespaces \
  d_hos_pinguan_traegj_20260205 > mysql_dump.sql
```

### 步骤2: 转换SQL语法

创建转换脚本 `convert_to_pg.py`:

```python
#!/usr/bin/env python3
import re

with open('mysql_dump.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# 删除MySQL特定语法
sql = re.sub(r'ENGINE=\w+', '', sql)
sql = re.sub(r'DEFAULT CHARSET=\w+', '', sql)
sql = re.sub(r'COLLATE=\w+', '', sql)
sql = re.sub(r'AUTO_INCREMENT=\d+', '', sql)

# 转换数据类型
sql = sql.replace('TINYINT(1)', 'BOOLEAN')
sql = sql.replace('DATETIME', 'TIMESTAMP')

# 删除反引号（可选）
sql = sql.replace('`', '"')

with open('pg_dump.sql', 'w', encoding='utf-8') as f:
    f.write(sql)

print("转换完成！")
```

运行转换：
```bash
python convert_to_pg.py
```

### 步骤3: 导入PostgreSQL

```bash
psql \
  -h your-pg-host \
  -U pinguan_user \
  -d d_hos_pinguan_traegj_20260205 \
  -f pg_dump.sql
```

---

## 代码修改

### 1. 修改 pom.xml

```xml
<!-- 删除 -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <scope>runtime</scope>
</dependency>

<!-- 添加 -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
</dependency>
```

### 2. 修改 application.yml

```yaml
app:
  datasource:
    active: ds1
    ds1:
      url: jdbc:postgresql://your-pg-host:5432/d_hos_pinguan_traegj_20260205?currentSchema=public
      username: pinguan_user
      password: your_password
      driver-class-name: org.postgresql.Driver
    ds2:
      url: jdbc:postgresql://your-pg-host:5432/d_hos_pinguan_traegj_20260205?currentSchema=public
      username: pinguan_user
      password: your_password
      driver-class-name: org.postgresql.Driver
    ds3:
      url: jdbc:postgresql://your-pg-host:5432/d_hos_pinguan_traegj_20260205?currentSchema=public
      username: pinguan_user
      password: your_password
      driver-class-name: org.postgresql.Driver

# 可选：明确指定Dialect
spring:
  jpa:
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
```

### 3. 修改 CompetitionMergeTool.java

```java
// 第31行
// 修改前
Class.forName("com.mysql.cj.jdbc.Driver");

// 修改后
Class.forName("org.postgresql.Driver");
```

### 4. 编译打包

```bash
mvn clean package -DskipTests
```

---

## 测试验证

### 1. 启动应用

```bash
java -jar target/pinguan-backend-0.0.1-SNAPSHOT.jar
```

### 2. 检查启动日志

应该看到：
```
Using dialect: org.hibernate.dialect.PostgreSQLDialect
HikariPool-1 - Starting...
HikariPool-1 - Start completed.
Tomcat started on port(s): 6031 (http)
```

### 3. 测试API

```bash
# 健康检查
curl http://localhost:6031/actuator/health

# 登录测试
curl -X POST http://localhost:6031/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"13800000001","name":"张三","role":"CONTESTANT"}'

# 查询测试
curl http://localhost:6031/api/registrations/119 \
  -H "Authorization: Bearer {token}"
```

### 4. 数据验证

```python
# 运行测试脚本
python scripts/test_project_summary_fields.py
python scripts/test_method_distribution.py
```

---

## 完整迁移时间表

| 步骤 | 时间 | 说明 |
|------|------|------|
| 安装pgLoader | 5分钟 | 一次性工作 |
| 准备PG数据库 | 5分钟 | 创建数据库和用户 |
| 执行数据迁移 | 5-10分钟 | pgLoader自动迁移 |
| 修改代码 | 10分钟 | 3个文件，9行代码 |
| 编译打包 | 5分钟 | mvn package |
| 测试验证 | 15分钟 | 启动测试 |
| **总计** | **45-50分钟** | 完整迁移 |

---

## 回滚方案

如果迁移后发现问题，可以快速回滚：

### 方案1: 保留MySQL配置

```yaml
# 在application.yml中保留MySQL配置
app:
  datasource:
    active: ds1  # 改回 ds1 使用MySQL
    ds1:  # MySQL配置（保留）
      url: jdbc:mysql://...
      driver-class-name: com.mysql.cj.jdbc.Driver
    ds1-pg:  # PostgreSQL配置（新增）
      url: jdbc:postgresql://...
      driver-class-name: org.postgresql.Driver
```

### 方案2: Git回滚

```bash
git checkout HEAD~1  # 回到上一个版本
mvn clean package -DskipTests
```

---

## 常见问题

### Q1: pgLoader安装失败怎么办？
A: 使用Docker版本：
```bash
docker run --rm -it dimitri/pgloader \
  pgloader mysql://... postgresql://...
```

### Q2: 数据迁移失败怎么办？
A: 
1. 检查网络连接
2. 检查数据库权限
3. 查看pgLoader日志
4. 使用手动导出导入方案

### Q3: 字符串查询不区分大小写怎么办？
A: PostgreSQL默认区分大小写，如需不区分：
```java
@Query("SELECT u FROM UserAccount u WHERE LOWER(u.name) = LOWER(:name)")
```

### Q4: 性能有差异吗？
A: PostgreSQL通常性能更好，但建议：
1. 检查索引是否正确创建
2. 运行 ANALYZE 更新统计信息
3. 必要时调整查询

---

## 总结

✅ **数据量小** - 仅2.14MB，迁移很快  
✅ **工具成熟** - pgLoader自动处理所有差异  
✅ **风险低** - JPA抽象层保证兼容性  
✅ **时间短** - 45-50分钟完成全部迁移  
✅ **收益大** - PostgreSQL性能和功能更强  

**建议：立即迁移！**

---

**文档版本**: 1.0  
**更新时间**: 2026-02-09
