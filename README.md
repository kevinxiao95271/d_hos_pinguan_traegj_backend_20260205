# 品管大赛评审系统 - 后端服务

**项目名称:** d_hos_pinguan_traegj_backend  
**Spring Boot版本:** 2.7.18  
**端口:** 6031  
**数据库:** MySQL 8.0 (Tencent Cloud)

---

## 📁 项目结构

```
d_hos_pinguan_traegj_backend_20260205/
├── src/                        # 源代码
│   ├── main/
│   │   ├── java/              # Java源码
│   │   │   └── com.trae.pinguan/
│   │   │       ├── config/    # 配置类（JWT、多数据源等）
│   │   │       ├── domain/    # 领域模型
│   │   │       │   ├── entity/    # 实体类
│   │   │       │   └── enums/     # 枚举
│   │   │       ├── repository/    # JPA数据访问层
│   │   │       ├── service/       # 业务逻辑层
│   │   │       ├── web/          # Web层
│   │   │       │   ├── dto/      # 数据传输对象
│   │   │       │   └── *.java    # Controller
│   │   │       └── PinguanBackendApplication.java
│   │   └── resources/
│   │       └── application.yml   # 配置文件
│   └── test/                  # 测试代码
├── docs/                      # 📄 所有文档
│   ├── API开发指引文档.md
│   ├── 前端开发QuickStart.md
│   ├── 评委端前端开发指引.md
│   ├── 评委池设计说明.md
│   ├── 书审得分功能开发指南.md
│   └── ...更多文档
├── scripts/                   # 🐍 Python脚本
│   ├── seed_and_test.py      # 数据初始化和测试
│   ├── test_*.py             # 各种测试脚本
│   └── ...更多脚本
├── data/                      # 数据文件
│   ├── exports/              # 导出数据
│   └── uploads/              # 上传文件
├── pom.xml                    # Maven配置
└── README.md                  # 本文件
```

---

## 🚀 快速启动

### 1. 环境要求

- Java 8+
- Maven 3.6+
- MySQL 8.0
- Python 3.8+ (用于运行测试脚本)

### 2. 配置数据库

**重要：请先配置数据库连接信息**

复制配置文件模板：
```bash
cp src/main/resources/application.yml.example src/main/resources/application.yml
```

编辑 `application.yml` 填入真实的数据库连接信息。

或者使用环境变量（Windows PowerShell）：

```powershell
$env:PINGUAN_DS1_URL="jdbc:mysql://your-host:port/database?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai"
$env:PINGUAN_DS1_USER="your-username"
$env:PINGUAN_DS1_PASSWORD="your-password"

# 可选：配置其他数据源
$env:PINGUAN_DS2_URL="jdbc:mysql://your-host:port/database?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai"
$env:PINGUAN_DS2_USER="your-username"
$env:PINGUAN_DS2_PASSWORD="your-password"

$env:PINGUAN_DS3_URL="jdbc:mysql://your-host:port/database?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai"
$env:PINGUAN_DS3_USER="your-username"
$env:PINGUAN_DS3_PASSWORD="your-password"
```

### 3. 启动服务

```bash
# 编译
mvn clean compile

# 启动（开发模式）
mvn spring-boot:run

# 或打包后启动
mvn clean package -DskipTests
java -jar target/pinguan-backend-0.0.1-SNAPSHOT.jar
```

服务启动后访问：
- **API文档:** http://localhost:6031/swagger
- **健康检查:** http://localhost:6031/actuator/health

---

## 📚 核心功能

### 用户角色

- **CONTESTANT** - 参赛者（报名、提交项目）
- **REVIEWER** - 评审专家（书审、面试、决赛评审）
- **COMMITTEE** - 组委会（任务分配、结果查看）
- **COMMITTEE_ADMIN** - 组委会管理员
- **OPS** - 系统运维（系统配置、数据管理）

### 主要模块

1. **认证授权** (`AuthController`)
   - JWT Token认证
   - 基于角色的访问控制

2. **报名管理** (`RegistrationController`)
   - 创建报名
   - 更新基本信息、成员、活动说明、总结
   - 提交审核

3. **评审管理** (`ReviewController`, `AdminReviewController`)
   - 任务分配（手动/自动）
   - 评审打分
   - 成绩查询

4. **评委管理** (`AdminReviewerController`)
   - 评委池管理（书审/面试/决赛）
   - 评委信息维护

5. **赛事管理** (`CompetitionController`)
   - 赛事创建和配置
   - 阶段管理

6. **机构管理** (`InstitutionController`)
   - 机构信息维护

---

## 🧪 测试

### Python测试脚本

```bash
# 安装依赖
pip install pymysql requests

# 运行端到端测试
python scripts/e2e_full_flow_test.py

# 测试评委功能
python scripts/test_reviewer_api_detailed.py

# 初始化测试数据
python scripts/seed_and_test.py
```

### 测试账号

**评委账号（有任务）:**
- 手机号: 13800000021, 姓名: 李明华, 角色: REVIEWER
- 手机号: 13800002004, 姓名: 孙丽娟, 角色: REVIEWER

**组委会账号:**
- 手机号: 13800000009, 姓名: 组委会, 角色: COMMITTEE

**参赛者账号:**
- 手机号: 13900000001, 姓名: 测试参赛者1, 角色: CONTESTANT

---

## 📖 文档说明

所有文档位于 `docs/` 目录：

### 前端开发文档
- **前端开发QuickStart.md** - 快速上手指南
- **评委端前端开发指引.md** - 评委端详细指引
- **API开发指引文档.md** - 完整API文档

### 功能说明文档
- **书审得分功能开发指南.md** - 书审评分功能
- **评委池设计说明.md** - 评委管理机制
- **数据更新说明.md** - 数据变更记录

### 测试文档
- **评委测试账号.txt** - 测试账号清单
- **API示例数据.json** - API请求/响应示例

---

## 🔧 配置说明

### 多数据源配置

系统支持3个数据源，用于不同测试阶段：
- `ds1` - 主数据源（报名阶段）
- `ds2` - 测试数据源2（评审阶段）
- `ds3` - 测试数据源3（决赛阶段）

在 `application.yml` 中配置：

```yaml
app:
  datasource:
    active: ds1  # 当前使用的数据源
```

### JWT配置

```yaml
security:
  jwt:
    secret: ${PINGUAN_JWT_SECRET:pinguan-jwt-secret-20260205-abcdefghijklmnopqrstuvwxyz}
    expireMinutes: ${PINGUAN_JWT_EXPIRE:720}
```

---

## 🛠 常用命令

```bash
# 编译
mvn clean compile

# 打包（跳过测试）
mvn clean package -DskipTests

# 运行测试
mvn test

# 查看依赖树
mvn dependency:tree

# 清理临时文件
mvn clean
```

---

## 📊 数据库表结构

核心表：
- `user_accounts` - 用户账号（包含评委）
- `institutions` - 机构信息
- `competitions` - 赛事信息
- `registrations` - 报名信息
- `registration_members` - 报名成员
- `activity_infos` - 活动说明
- `project_summaries` - 项目总结
- `review_tasks` - 评审任务
- `review_scores` - 评审评分
- `material_files` - 材料文件

---

## ⚠️ 注意事项

1. **字符编码**: 所有地方使用UTF-8，避免GBK编码导致乱码
2. **角色检查**: 确保评审任务只分配给REVIEWER角色的用户
3. **事务管理**: 懒加载关联需要在@Transactional内访问
4. **性能优化**: 使用JOIN FETCH避免N+1查询问题
5. **机构回避**: 评委不能评审自己机构的项目

---

## 🤝 开发团队

- **后端开发**: Spring Boot 2.7 + JPA + MySQL
- **数据库**: Tencent Cloud MySQL 8.0
- **文档**: Swagger/OpenAPI 3.0
- **测试**: Python + PyMySQL

---

## 📝 更新日志

### 2026-02-06
- ✅ 修复评委登录问题（LazyInitializationException）
- ✅ 优化评委列表API性能（JOIN FETCH）
- ✅ 更新评委数据为真实中文姓名
- ✅ 清理错误的评审任务分配
- ✅ 完善前端开发文档

### 2026-02-05
- ✅ 修复参赛者报名API
- ✅ 实现书审评分功能
- ✅ 添加评委任务列表API
- ✅ 完善Swagger文档

---

## 📞 支持

如有问题，请查看 `docs/` 目录下的相关文档。

**Swagger API文档:** http://localhost:6031/swagger
